#!/usr/bin/env bash

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  printf 'WutPack currently supports macOS only.\n' >&2
  exit 1
fi

REPOSITORY="sfungwinbond/Gstackwut"
BRANCH="${WUTPACK_BRANCH:-main}"
REF="${WUTPACK_REF:-}"
USER_HOME="${WUTPACK_TEST_ROOT:-$HOME}"
INSTALL_ROOT="${WUTPACK_INSTALL_ROOT:-$USER_HOME/.local/share/wutpack}"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wutpack-bootstrap.XXXXXX")"
STAGED_ROOT=""
BACKUP_CONTAINER=""
INSTALL_PARENT=""
LOCK_ROOT=""
HAVE_LOCK=0
SWAP_ACTIVE=0
HAD_PREVIOUS=0
KEEP_BACKUP=0
DRY_RUN_REQUESTED=0
EXPECTED_SKILLS=(
  code-build
  data-lab
  debug-lab
  document-studio
  pdf-forensics
  publish-docs
  research-brief
  review-gate
  ship-check
  spreadsheet-lab
  system-diagram
  technical-deck
)

validate_source_tree() {
  local root="$1"
  local required_file
  local skill_name
  local skill_dir
  local skill_count=0

  for required_file in \
    VERSION install.sh setup bin/wut \
    manifests/brew-formulae.txt manifests/brew-casks.txt \
    manifests/brew-extras.txt manifests/node-tools.txt \
    manifests/node-agents.txt manifests/node-retired.txt \
    manifests/python-core.txt manifests/python-ml.txt \
    manifests/python-agents.txt \
    skills/technical-deck/scripts/new_technical_deck.mjs; do
    if [ ! -f "$root/$required_file" ]; then
      printf 'WutPack source is incomplete: missing %s\n' "$required_file" >&2
      return 1
    fi
  done

  for skill_name in "${EXPECTED_SKILLS[@]}"; do
    if [ ! -f "$root/skills/$skill_name/SKILL.md" ]; then
      printf 'WutPack source is incomplete: missing skill %s\n' "$skill_name" >&2
      return 1
    fi
  done

  for skill_dir in "$root"/skills/*; do
    [ -d "$skill_dir" ] || continue
    case "$(basename "$skill_dir")" in
      code-build|data-lab|debug-lab|document-studio|pdf-forensics|publish-docs|research-brief|review-gate|ship-check|spreadsheet-lab|system-diagram|technical-deck)
        skill_count=$((skill_count + 1))
        ;;
      *)
        printf 'WutPack source contains an unexpected skill: %s\n' \
          "$(basename "$skill_dir")" >&2
        return 1
        ;;
    esac
  done

  if [ "$skill_count" -ne "${#EXPECTED_SKILLS[@]}" ]; then
    printf 'WutPack source is incomplete: found %s/%s required skills\n' \
      "$skill_count" "${#EXPECTED_SKILLS[@]}" >&2
    return 1
  fi
}

is_wutpack_install() {
  local root="$1"

  if [ -f "$root/.wutpack-install" ] && \
    grep -Fxq 'WutPack managed source v1' "$root/.wutpack-install"; then
    return 0
  fi

  [ -f "$root/VERSION" ] && \
    [ -f "$root/install.sh" ] && \
    [ -f "$root/setup" ] && \
    [ -f "$root/bin/wut" ] && \
    [ -d "$root/skills" ] && \
    grep -Fq 'WutPack setup' "$root/setup" && \
    grep -Fq 'WutPack control command' "$root/bin/wut"
}

is_safe_lock_dir() {
  local lock_dir="$1"
  local owner_uid
  local lock_mode

  [ -d "$lock_dir" ] && [ ! -L "$lock_dir" ] || return 1
  owner_uid="$(stat -f '%u' "$lock_dir" 2>/dev/null)" || return 1
  lock_mode="$(stat -f '%Lp' "$lock_dir" 2>/dev/null)" || return 1
  [ "$owner_uid" = "$(id -u)" ] && [ "$lock_mode" = "700" ]
}

is_managed_install_temp() {
  local path="$1"
  local prefix="$2"
  local path_parent
  local path_name

  [ -n "$INSTALL_PARENT" ] && [ -n "$path" ] || return 1
  path_parent="$(dirname -- "$path")"
  path_name="$(basename -- "$path")"
  [ "$path_parent" = "$INSTALL_PARENT" ] || return 1
  [ "$path" = "$INSTALL_PARENT/$path_name" ] || return 1
  case "$path_name" in "$prefix"*) ;; *) return 1 ;; esac
  [ ! -L "$path" ]
  if [ -e "$path" ]; then
    is_safe_lock_dir "$path" || return 1
  fi
}

process_start_time() {
  ps -p "$1" -o lstart= 2>/dev/null | \
    sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

write_lock_owner() {
  local lock_dir="$1"
  local start_time
  start_time="$(process_start_time "$$" || true)"
  [ -n "$start_time" ] || start_time="unavailable"
  printf '%s\n' "$$" > "$lock_dir/pid" || return 1
  printf '%s\n' "$start_time" > "$lock_dir/start" || return 1
}

lock_owner_status() {
  local lock_dir="$1"
  local owner_pid
  local owner_start
  local current_start

  [ -f "$lock_dir/pid" ] && [ -f "$lock_dir/start" ] || return 2
  IFS= read -r owner_pid < "$lock_dir/pid" || return 2
  case "$owner_pid" in ''|*[!0-9]*) return 2 ;; esac
  IFS= read -r owner_start < "$lock_dir/start" || return 2
  [ -n "$owner_start" ] || return 2
  kill -0 "$owner_pid" 2>/dev/null || return 1
  current_start="$(process_start_time "$owner_pid" || true)"
  if [ "$owner_start" = "unavailable" ] || [ -z "$current_start" ]; then
    return 0
  fi
  [ "$current_start" = "$owner_start" ]
}

recover_interrupted_install() {
  local stale_stage=""
  local stale_backup=""
  local stale_had_previous=""

  [ ! -f "$LOCK_ROOT/stage" ] || \
    IFS= read -r stale_stage < "$LOCK_ROOT/stage"
  [ ! -f "$LOCK_ROOT/backup" ] || \
    IFS= read -r stale_backup < "$LOCK_ROOT/backup"
  [ ! -f "$LOCK_ROOT/had-previous" ] || \
    IFS= read -r stale_had_previous < "$LOCK_ROOT/had-previous"

  if [ -e "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ]; then
    if [ ! -d "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ] || \
      ! is_wutpack_install "$INSTALL_ROOT"; then
      printf 'Cannot recover interrupted WutPack update: unsafe install root %s\n' \
        "$INSTALL_ROOT" >&2
      return 1
    fi
  else
    case "$stale_had_previous" in
      0) ;;
      1)
        is_managed_install_temp "$stale_backup" '.wutpack-backup.' || {
          printf 'Cannot recover WutPack backup path: %s\n' "$stale_backup" >&2
          return 1
        }
        if [ ! -d "$stale_backup/previous" ] || \
          [ -L "$stale_backup/previous" ] || \
          ! is_wutpack_install "$stale_backup/previous"; then
          printf 'Cannot recover the previous WutPack source from %s\n' \
            "$stale_backup" >&2
          return 1
        fi
        mv "$stale_backup/previous" "$INSTALL_ROOT" || return 1
        ;;
      *)
        printf 'Cannot determine the interrupted WutPack activation state.\n' >&2
        return 1
        ;;
    esac
  fi

  if [ -n "$stale_stage" ]; then
    is_managed_install_temp "$stale_stage" '.wutpack-stage.' || {
      printf 'Refusing unsafe staged-source cleanup path: %s\n' "$stale_stage" >&2
      return 1
    }
    rm -rf -- "$stale_stage"
  fi
  if [ -n "$stale_backup" ]; then
    is_managed_install_temp "$stale_backup" '.wutpack-backup.' || {
      printf 'Refusing unsafe WutPack backup cleanup path: %s\n' "$stale_backup" >&2
      return 1
    }
      if [ -d "$stale_backup/previous" ] && \
        { [ -L "$stale_backup/previous" ] || \
          ! is_wutpack_install "$stale_backup/previous"; }; then
        printf 'Refusing unsafe WutPack backup cleanup: %s\n' "$stale_backup" >&2
        return 1
      fi
      rm -rf -- "$stale_backup"
  fi
}

acquire_install_lock() {
  local owner_state=0
  local recovery_state=0
  local recovery_dir="$LOCK_ROOT/recovery"

  if mkdir -m 700 "$LOCK_ROOT" 2>/dev/null; then
    HAVE_LOCK=1
    write_lock_owner "$LOCK_ROOT" || \
      { printf 'Could not initialize the WutPack install lock: %s\n' "$LOCK_ROOT" >&2; return 1; }
    return 0
  fi

  if ! is_safe_lock_dir "$LOCK_ROOT"; then
    printf 'WutPack found an unsafe install lock at %s; refusing recovery.\n' \
      "$LOCK_ROOT" >&2
    return 1
  fi

  lock_owner_status "$LOCK_ROOT" || owner_state=$?
  case "$owner_state" in
    0)
      printf 'Another WutPack install or update is active (lock: %s).\n' \
        "$LOCK_ROOT" >&2
      return 1
      ;;
    2)
      printf 'WutPack found an unreadable install lock at %s; verify no setup is running, then remove it.\n' \
        "$LOCK_ROOT" >&2
      return 1
      ;;
  esac

  if [ -d "$recovery_dir" ]; then
    is_safe_lock_dir "$recovery_dir" || {
      printf 'WutPack found an unsafe recovery lock at %s\n' "$recovery_dir" >&2
      return 1
    }
    lock_owner_status "$recovery_dir" || recovery_state=$?
    case "$recovery_state" in
      0)
        printf 'Another WutPack process is recovering %s\n' "$INSTALL_ROOT" >&2
        return 1
        ;;
      1)
        rm -f -- "$recovery_dir/pid" "$recovery_dir/start"
        rmdir "$recovery_dir" 2>/dev/null || {
          printf 'Could not reclaim stale recovery lock: %s\n' "$recovery_dir" >&2
          return 1
        }
        ;;
      *)
        printf 'WutPack found an unreadable recovery lock at %s\n' "$recovery_dir" >&2
        return 1
        ;;
    esac
  fi

  mkdir -m 700 "$recovery_dir" 2>/dev/null || {
    printf 'Another WutPack process claimed recovery for %s\n' "$INSTALL_ROOT" >&2
    return 1
  }
  write_lock_owner "$recovery_dir" || {
    printf 'Could not initialize recovery for %s\n' "$INSTALL_ROOT" >&2
    return 1
  }
  recover_interrupted_install || return 1

  rm -f -- "$LOCK_ROOT/pid" "$LOCK_ROOT/start" "$LOCK_ROOT/stage" \
    "$LOCK_ROOT/backup" "$LOCK_ROOT/had-previous"
  rm -f -- "$recovery_dir/pid" "$recovery_dir/start"
  rmdir "$recovery_dir" || return 1
  HAVE_LOCK=1
  write_lock_owner "$LOCK_ROOT" || return 1
}

run_source_setup() {
  local root="$1"
  local status=0
  shift
  if { exec 3<>/dev/tty; } 2>/dev/null; then
    if [ "$HAVE_LOCK" -eq 1 ]; then
      WUTPACK_INSTALL_LOCK_HELD="$LOCK_ROOT" \
        /bin/bash "$root/setup" "$@" <&3 || status=$?
    else
      /bin/bash "$root/setup" "$@" <&3 || status=$?
    fi
    exec 3>&-
    return "$status"
  fi
  if [ "$HAVE_LOCK" -eq 1 ]; then
    WUTPACK_INSTALL_LOCK_HELD="$LOCK_ROOT" /bin/bash "$root/setup" "$@"
  else
    /bin/bash "$root/setup" "$@"
  fi
}

rollback_install() {
  local failed_root

  [ "$SWAP_ACTIVE" -eq 1 ] || return 0
  failed_root="$BACKUP_CONTAINER/failed"

  if [ "$HAD_PREVIOUS" -eq 1 ] && [ -e "$BACKUP_CONTAINER/previous" ]; then
    if [ -e "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ]; then
      if ! mv "$INSTALL_ROOT" "$failed_root"; then
        printf 'WutPack could not move the failed install out of the way.\n' >&2
        KEEP_BACKUP=1
        return 1
      fi
    fi
    if ! mv "$BACKUP_CONTAINER/previous" "$INSTALL_ROOT"; then
      printf 'WutPack could not restore the previous install. Backup preserved at %s\n' \
        "$BACKUP_CONTAINER/previous" >&2
      KEEP_BACKUP=1
      return 1
    fi
  fi

  SWAP_ACTIVE=0
}

cleanup() {
  local status=$?
  trap - EXIT
  if ! rollback_install; then status=1; fi
  if is_managed_install_temp "$STAGED_ROOT" '.wutpack-stage.'; then
    rm -rf -- "$STAGED_ROOT"
  fi
  if [ "$KEEP_BACKUP" -eq 0 ]; then
    if is_managed_install_temp "$BACKUP_CONTAINER" '.wutpack-backup.'; then
      rm -rf -- "$BACKUP_CONTAINER"
    fi
  fi
  if [ "$HAVE_LOCK" -eq 1 ] && [ "$KEEP_BACKUP" -eq 0 ]; then
    rm -f -- "$LOCK_ROOT/pid" "$LOCK_ROOT/start" "$LOCK_ROOT/stage" \
      "$LOCK_ROOT/backup" "$LOCK_ROOT/had-previous"
    rmdir "$LOCK_ROOT" 2>/dev/null || true
  elif [ "$HAVE_LOCK" -eq 1 ]; then
    printf 'WutPack recovery is required; install lock preserved at %s\n' \
      "$LOCK_ROOT" >&2
  fi
  case "$TEMP_ROOT" in
    "${TMPDIR:-/tmp}"/wutpack-bootstrap.*) rm -rf -- "$TEMP_ROOT" ;;
  esac
  exit "$status"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

printf '\n  WutPack: fetching the Mac AI workbench...\n\n'

for installer_arg in "$@"; do
  [ "$installer_arg" = "--dry-run" ] && DRY_RUN_REQUESTED=1
done

if [ -n "${WUTPACK_SOURCE_DIR:-}" ]; then
  SOURCE_ROOT="$WUTPACK_SOURCE_DIR"
else
  ARCHIVE="$TEMP_ROOT/source.tar.gz"
  if [ -n "$REF" ]; then
    ARCHIVE_URL="https://github.com/$REPOSITORY/archive/$REF.tar.gz"
  else
    ARCHIVE_URL="https://github.com/$REPOSITORY/archive/refs/heads/$BRANCH.tar.gz"
  fi
  curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location \
    "$ARCHIVE_URL" \
    --output "$ARCHIVE"
  tar -xzf "$ARCHIVE" -C "$TEMP_ROOT"
  SOURCE_ROOT="$(find "$TEMP_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'Gstackwut-*' -print -quit)"
fi

if [ -z "${SOURCE_ROOT:-}" ] || [ ! -d "$SOURCE_ROOT" ]; then
  printf 'WutPack bootstrap could not find its source tree in %s\n' \
    "${SOURCE_ROOT:-<unknown>}" >&2
  exit 1
fi

SOURCE_ROOT="$(CDPATH= cd -- "$SOURCE_ROOT" && pwd -P)"
validate_source_tree "$SOURCE_ROOT"

if [ "$DRY_RUN_REQUESTED" -eq 1 ]; then
  run_source_setup "$SOURCE_ROOT" "$@"
  exit $?
fi

case "$INSTALL_ROOT" in
  ''|/) printf 'Refusing unsafe WutPack install root: %s\n' "$INSTALL_ROOT" >&2; exit 1 ;;
esac
INSTALL_PARENT="$(dirname -- "$INSTALL_ROOT")"
INSTALL_NAME="$(basename -- "$INSTALL_ROOT")"
case "$INSTALL_NAME" in
  ''|.|..) printf 'Refusing unsafe WutPack install root: %s\n' "$INSTALL_ROOT" >&2; exit 1 ;;
esac
mkdir -p "$INSTALL_PARENT"
INSTALL_PARENT="$(CDPATH= cd -- "$INSTALL_PARENT" && pwd -P)"
INSTALL_ROOT="$INSTALL_PARENT/$INSTALL_NAME"

if [ "$SOURCE_ROOT" = "$INSTALL_ROOT" ]; then
  printf 'WutPack source and install roots must be different: %s\n' "$INSTALL_ROOT" >&2
  exit 1
fi
if { [ -e "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ]; } && \
  { [ ! -d "$INSTALL_ROOT" ] || [ -L "$INSTALL_ROOT" ]; }; then
  printf 'WutPack install root must be a real directory: %s\n' "$INSTALL_ROOT" >&2
  exit 1
fi
if [ -d "$INSTALL_ROOT" ] && ! is_wutpack_install "$INSTALL_ROOT"; then
  printf 'Refusing to replace a directory not owned by WutPack: %s\n' \
    "$INSTALL_ROOT" >&2
  exit 1
fi

LOCK_ROOT="$INSTALL_PARENT/.$INSTALL_NAME.install-lock"
acquire_install_lock

if [ -d "$INSTALL_ROOT" ]; then
  HAD_PREVIOUS=1
else
  HAD_PREVIOUS=0
fi
printf '%s\n' "$HAD_PREVIOUS" > "$LOCK_ROOT/had-previous"

STAGED_ROOT="$(mktemp -d "$INSTALL_PARENT/.wutpack-stage.XXXXXX")"
printf '%s\n' "$STAGED_ROOT" > "$LOCK_ROOT/stage"
ditto "$SOURCE_ROOT" "$STAGED_ROOT"
validate_source_tree "$STAGED_ROOT"
chmod +x "$STAGED_ROOT/setup" "$STAGED_ROOT/bin/wut"
printf '%s\n' 'WutPack managed source v1' > "$STAGED_ROOT/.wutpack-install"

BACKUP_CONTAINER="$(mktemp -d "$INSTALL_PARENT/.wutpack-backup.XXXXXX")"
printf '%s\n' "$BACKUP_CONTAINER" > "$LOCK_ROOT/backup"
SWAP_ACTIVE=1
if [ "$HAD_PREVIOUS" -eq 1 ]; then
  mv "$INSTALL_ROOT" "$BACKUP_CONTAINER/previous"
fi
mv "$STAGED_ROOT" "$INSTALL_ROOT"
STAGED_ROOT=""
SWAP_ACTIVE=0

setup_status=0
run_source_setup "$INSTALL_ROOT" "$@" || setup_status=$?

if [ "$setup_status" -ne 0 ]; then
  printf 'WutPack source is installed, but setup did not complete. Re-run: %s/setup\n' \
    "$INSTALL_ROOT" >&2
  exit "$setup_status"
fi
