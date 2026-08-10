#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"
EXPECTED_VERSION="$(cat "$REPO_ROOT/VERSION")"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wutpack-test.XXXXXX")"
INSTALL_ROOT="$TEST_ROOT/.local/share/wutpack"

cleanup() {
  case "$TEST_ROOT" in
    "${TMPDIR:-/tmp}"/wutpack-test.*) rm -rf -- "$TEST_ROOT" ;;
  esac
}
trap cleanup EXIT INT TERM

while IFS= read -r script; do
  /bin/bash -n "$script"
done < <(find "$REPO_ROOT" -type f \( -name '*.sh' -o -path "$REPO_ROOT/setup" -o -path "$REPO_ROOT/bin/wut" \))

python3 "$REPO_ROOT/skills/technical-deck/scripts/validate_pptx.py" \
  "$REPO_ROOT/examples/executive-consulting-demo.pptx" >/dev/null

if "$REPO_ROOT/setup" --host >/dev/null 2>&1; then
  printf 'setup accepted a missing --host value\n' >&2
  exit 1
fi
if "$REPO_ROOT/setup" --profile >/dev/null 2>&1; then
  printf 'setup accepted a missing --profile value\n' >&2
  exit 1
fi

WUTPACK_SOURCE_DIR="$REPO_ROOT" \
WUTPACK_TEST_ROOT="$TEST_ROOT" \
WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" \
  /bin/bash "$REPO_ROOT/install.sh" --skills-only --host both

test -L "$TEST_ROOT/.local/bin/wut"
grep -Fxq 'WutPack managed source v1' "$INSTALL_ROOT/.wutpack-install"
CANONICAL_INSTALL_ROOT="$(CDPATH= cd -- "$INSTALL_ROOT" && pwd -P)"
test "$(readlink "$TEST_ROOT/.local/bin/wut")" = "$CANONICAL_INSTALL_ROOT/bin/wut"
SYMLINK_WUT="$TEST_ROOT/.local/bin/wut"
test "$(WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" version)" = "$EXPECTED_VERSION"
WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" paths | \
  grep -Fq "source=$CANONICAL_INSTALL_ROOT"
test "$(WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" skills | wc -l | tr -d ' ')" = "12"
WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" setup --help | grep -Fq -- '--skills-only'

mkdir -p "$TEST_ROOT/link-one" "$TEST_ROOT/link-two"
ln -s ../link-two/wut "$TEST_ROOT/link-one/wut"
ln -s ../.local/bin/wut "$TEST_ROOT/link-two/wut"
test "$(WUTPACK_TEST_ROOT="$TEST_ROOT" "$TEST_ROOT/link-one/wut" version)" = \
  "$EXPECTED_VERSION"

NODE_STUB_DIR="$TEST_ROOT/Library/Application Support/WutPack/npm-global/bin"
NODE_STUB_LOG="$TEST_ROOT/deck-node-args.txt"
DECK_OUTPUT="$TEST_ROOT/deck-output.pptx"
mkdir -p "$NODE_STUB_DIR"
cat > "$NODE_STUB_DIR/node" <<'EOF'
#!/usr/bin/env bash
printf '%s\n' "$@" > "$WUTPACK_NODE_STUB_LOG"
EOF
chmod +x "$NODE_STUB_DIR/node"
WUTPACK_NODE_STUB_LOG="$NODE_STUB_LOG" WUTPACK_TEST_ROOT="$TEST_ROOT" \
  "$SYMLINK_WUT" deck "$DECK_OUTPUT"
test "$(sed -n '1p' "$NODE_STUB_LOG")" = \
  "$CANONICAL_INSTALL_ROOT/skills/technical-deck/scripts/new_technical_deck.mjs"
test "$(sed -n '2p' "$NODE_STUB_LOG")" = "--output=$DECK_OUTPUT"
if WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" deck one.pptx extra \
  >/dev/null 2>&1; then
  printf 'wut deck accepted too many arguments\n' >&2
  exit 1
fi
if WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" render one two three \
  >/dev/null 2>&1; then
  printf 'wut render accepted too many arguments\n' >&2
  exit 1
fi
DIAGRAM_FAILURE_LOG="$TEST_ROOT/diagram-missing-cli.log"
if WUTPACK_TEST_ROOT="$TEST_ROOT" "$SYMLINK_WUT" diagram \
  "$REPO_ROOT/examples/consulting-engagement.mmd" "$TEST_ROOT/diagram.svg" \
  >"$DIAGRAM_FAILURE_LOG" 2>&1; then
  printf 'wut diagram passed without its managed Mermaid CLI\n' >&2
  exit 1
fi
grep -Fq 'Mermaid CLI is not installed' "$DIAGRAM_FAILURE_LOG"

UPDATE_STUB_BIN="$TEST_ROOT/update-stub"
UPDATE_FAILURE_LOG="$TEST_ROOT/update-download-failure.log"
mkdir -p "$UPDATE_STUB_BIN"
cat > "$UPDATE_STUB_BIN/curl" <<'EOF'
#!/usr/bin/env bash
exit 22
EOF
chmod +x "$UPDATE_STUB_BIN/curl"
if env PATH="$UPDATE_STUB_BIN:/usr/bin:/bin" WUTPACK_TEST_ROOT="$TEST_ROOT" \
  "$SYMLINK_WUT" update --skills-only >"$UPDATE_FAILURE_LOG" 2>&1; then
  printf 'wut update passed after its installer download failed\n' >&2
  exit 1
fi
grep -Fq 'Could not download the WutPack installer' "$UPDATE_FAILURE_LOG"

test -f "$TEST_ROOT/.codex/skills/technical-deck/SKILL.md"
test -f "$TEST_ROOT/.claude/skills/spreadsheet-lab/SKILL.md"
test "$(find "$TEST_ROOT/.codex/skills" -name SKILL.md | wc -l | tr -d ' ')" = "12"
test "$(find "$TEST_ROOT/.claude/skills" -name SKILL.md | wc -l | tr -d ' ')" = "12"
grep -Fxq 'WutPack managed skill v1: code-build' \
  "$TEST_ROOT/.codex/skills/code-build/.wutpack-skill"

touch "$TEST_ROOT/.codex/skills/code-build/retired-upstream-helper.sh"
WUTPACK_TEST_ROOT="$TEST_ROOT" "$INSTALL_ROOT/setup" --skills-only --host both >/dev/null
test ! -e "$TEST_ROOT/.codex/skills/code-build/retired-upstream-helper.sh"
test "$(grep -cF '# >>> WutPack persistent tools >>>' "$TEST_ROOT/.zprofile")" = "1"
test "$(grep -cF '# >>> WutPack persistent tools >>>' "$TEST_ROOT/.zshrc")" = "1"
/bin/zsh -n "$TEST_ROOT/.zprofile"
/bin/zsh -n "$TEST_ROOT/.zshrc"

THIRD_PARTY_ROOT="$TEST_ROOT/third-party-skill-user"
THIRD_PARTY_SKILL="$THIRD_PARTY_ROOT/.codex/skills/code-build"
THIRD_PARTY_LOG="$TEST_ROOT/third-party-skill.log"
mkdir -p "$THIRD_PARTY_SKILL/agents"
cat > "$THIRD_PARTY_SKILL/SKILL.md" <<'EOF'
---
name: code-build
description: A third-party skill that happens to use the same generic name.
---

Keep this user-owned content.
EOF
cat > "$THIRD_PARTY_SKILL/agents/openai.yaml" <<'EOF'
interface:
  display_name: "Third Party Builder"
  short_description: "Not managed by WutPack"
  default_prompt: "Use $code-build for a custom workflow."
EOF
touch "$THIRD_PARTY_SKILL/user-owned-file"
if WUTPACK_TEST_ROOT="$THIRD_PARTY_ROOT" "$INSTALL_ROOT/setup" \
  --skills-only --host codex >"$THIRD_PARTY_LOG" 2>&1; then
  printf 'setup replaced a third-party skill with a generic matching name\n' >&2
  exit 1
fi
grep -Fq 'Refusing to replace a skill not owned by WutPack' "$THIRD_PARTY_LOG"
test -e "$THIRD_PARTY_SKILL/user-owned-file"

PARTIAL_PROFILE_ROOT="$TEST_ROOT/partial-profile-user"
mkdir -p "$PARTIAL_PROFILE_ROOT"
printf '%s\n%s\n' \
  'export BEFORE_WUTPACK=1' \
  '# >>> WutPack persistent tools >>>' > "$PARTIAL_PROFILE_ROOT/.zprofile"
WUTPACK_TEST_ROOT="$PARTIAL_PROFILE_ROOT" "$INSTALL_ROOT/setup" \
  --skills-only --host codex >/dev/null
test "$(grep -cF '# >>> WutPack persistent tools >>>' "$PARTIAL_PROFILE_ROOT/.zprofile")" = "1"
test "$(grep -cF '# <<< WutPack persistent tools <<<' "$PARTIAL_PROFILE_ROOT/.zprofile")" = "1"
grep -Fq 'export BEFORE_WUTPACK=1' "$PARTIAL_PROFILE_ROOT/.zprofile"
grep -Fq 'npm-global/bin' "$PARTIAL_PROFILE_ROOT/.zprofile"
/bin/zsh -n "$PARTIAL_PROFILE_ROOT/.zprofile"

SYMLINK_PROFILE_ROOT="$TEST_ROOT/symlink-profile-user"
SYMLINK_PROFILE_TARGETS="$TEST_ROOT/symlink-profile-targets"
mkdir -p "$SYMLINK_PROFILE_ROOT" "$SYMLINK_PROFILE_TARGETS"
touch "$SYMLINK_PROFILE_TARGETS/zprofile" "$SYMLINK_PROFILE_TARGETS/zshrc"
ln -s ../symlink-profile-targets/zprofile "$SYMLINK_PROFILE_ROOT/.zprofile"
ln -s ../symlink-profile-targets/zshrc "$SYMLINK_PROFILE_ROOT/.zshrc"
WUTPACK_TEST_ROOT="$SYMLINK_PROFILE_ROOT" "$INSTALL_ROOT/setup" \
  --skills-only --host codex >/dev/null
test -L "$SYMLINK_PROFILE_ROOT/.zprofile"
test -L "$SYMLINK_PROFILE_ROOT/.zshrc"
grep -Fq '# <<< WutPack persistent tools <<<' "$SYMLINK_PROFILE_TARGETS/zprofile"
grep -Fq '# <<< WutPack persistent tools <<<' "$SYMLINK_PROFILE_TARGETS/zshrc"

WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" \
  "$INSTALL_ROOT/bin/wut" routes | grep -Fq 'technical-deck'
test "$(WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" "$INSTALL_ROOT/bin/wut" version)" = "$EXPECTED_VERSION"
WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" \
  "$INSTALL_ROOT/bin/wut" doctor --help | grep -Fq -- '--headless'
if WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" \
  "$INSTALL_ROOT/bin/wut" doctor --not-a-real-option >/dev/null 2>&1; then
  printf 'wut doctor accepted an unknown option\n' >&2
  exit 1
fi

DOCTOR_LOG="$TEST_ROOT/doctor-missing-host-skills.log"
if WUTPACK_TEST_ROOT="$TEST_ROOT/no-host-user" \
  WUTPACK_STATE_ROOT="$TEST_ROOT/no-host-state" \
  "$SYMLINK_WUT" doctor --headless >"$DOCTOR_LOG" 2>&1; then
  printf 'wut doctor passed with no installed host skills\n' >&2
  exit 1
fi
grep -Fq "[ok]   WutPack source   $CANONICAL_INSTALL_ROOT" "$DOCTOR_LOG"
grep -Fq '[miss] host skills' "$DOCTOR_LOG"
grep -Fq '[miss] pptxgenjs' "$DOCTOR_LOG"

mkdir -p "$TEST_ROOT/no-host-state/npm-global/lib/node_modules/pptxgenjs"
printf '{}\n' > \
  "$TEST_ROOT/no-host-state/npm-global/lib/node_modules/pptxgenjs/package.json"
if WUTPACK_TEST_ROOT="$TEST_ROOT/no-host-user" \
  WUTPACK_STATE_ROOT="$TEST_ROOT/no-host-state" \
  "$SYMLINK_WUT" doctor --headless >/dev/null 2>&1; then
  printf 'wut doctor passed with a partial managed pptxgenjs package\n' >&2
  exit 1
fi

MALICIOUS_CWD="$TEST_ROOT/malicious-cwd"
MALICIOUS_SENTINEL="$TEST_ROOT/local-pptxgenjs-executed"
mkdir -p "$MALICIOUS_CWD/node_modules/pptxgenjs"
cat > "$MALICIOUS_CWD/node_modules/pptxgenjs/index.js" <<EOF
require("node:fs").writeFileSync("$MALICIOUS_SENTINEL", "executed");
EOF
(
  cd "$MALICIOUS_CWD"
  WUTPACK_TEST_ROOT="$TEST_ROOT/no-host-user" \
    WUTPACK_STATE_ROOT="$TEST_ROOT/no-host-state" \
    "$SYMLINK_WUT" doctor --headless >/dev/null 2>&1 || true
)
test ! -e "$MALICIOUS_SENTINEL"

PARTIAL_HOME="$TEST_ROOT/partial-host-user"
mkdir -p "$PARTIAL_HOME/.codex/skills"
for skill_dir in "$INSTALL_ROOT"/skills/*; do
  [ "$(basename "$skill_dir")" = "technical-deck" ] && continue
  ditto "$skill_dir" "$PARTIAL_HOME/.codex/skills/$(basename "$skill_dir")"
done
PARTIAL_DOCTOR_LOG="$TEST_ROOT/doctor-partial-host-skills.log"
if WUTPACK_TEST_ROOT="$PARTIAL_HOME" \
  WUTPACK_STATE_ROOT="$TEST_ROOT/no-host-state" \
  "$SYMLINK_WUT" doctor --headless >"$PARTIAL_DOCTOR_LOG" 2>&1; then
  printf 'wut doctor passed with an incomplete host skill installation\n' >&2
  exit 1
fi
grep -Fq '[miss] Codex skills     11/12' "$PARTIAL_DOCTOR_LOG"

PARTIAL_SOURCE="$TEST_ROOT/partial-source"
mkdir -p "$PARTIAL_SOURCE/skills"
cp "$INSTALL_ROOT/VERSION" "$PARTIAL_SOURCE/VERSION"
ditto "$INSTALL_ROOT/skills/code-build" "$PARTIAL_SOURCE/skills/code-build"
PARTIAL_SOURCE_LOG="$TEST_ROOT/doctor-partial-source.log"
WUTPACK_INSTALL_ROOT="$PARTIAL_SOURCE" WUTPACK_TEST_ROOT="$PARTIAL_HOME" \
  "$INSTALL_ROOT/bin/wut" doctor --headless >"$PARTIAL_SOURCE_LOG" 2>&1 || true
grep -Fq '[miss] packaged skills  1/12' "$PARTIAL_SOURCE_LOG"

BROKEN_SOURCE="$TEST_ROOT/broken-source"
mkdir -p "$BROKEN_SOURCE/skills"
for broken_command in version skills setup deck; do
  if WUTPACK_INSTALL_ROOT="$BROKEN_SOURCE" "$INSTALL_ROOT/bin/wut" \
    "$broken_command" >/dev/null 2>&1; then
    printf 'wut %s passed with an incomplete source tree\n' "$broken_command" >&2
    exit 1
  fi
done

CORRUPT_SETUP_SOURCE="$TEST_ROOT/corrupt-setup-source"
mkdir -p "$CORRUPT_SETUP_SOURCE"
cp "$REPO_ROOT/setup" "$CORRUPT_SETUP_SOURCE/setup"
chmod +x "$CORRUPT_SETUP_SOURCE/setup"
CORRUPT_SETUP_HOME="$TEST_ROOT/corrupt-setup-user"
if WUTPACK_TEST_ROOT="$CORRUPT_SETUP_HOME" "$CORRUPT_SETUP_SOURCE/setup" \
  --skills-only --host codex >/dev/null 2>&1; then
  printf 'setup passed with a partial source tree\n' >&2
  exit 1
fi
test ! -e "$CORRUPT_SETUP_HOME"

SETUP_FAILURE_LOG="$TEST_ROOT/setup-required-path-failure.log"
if WUTPACK_TEST_ROOT=/dev/null "$REPO_ROOT/setup" --skills-only --host both \
  >"$SETUP_FAILURE_LOG" 2>&1; then
  printf 'setup reported success after required filesystem operations failed\n' >&2
  exit 1
fi
grep -Fq 'Could not create WutPack state directories' "$SETUP_FAILURE_LOG"
if grep -Fq 'WutPack setup complete' "$SETUP_FAILURE_LOG"; then
  printf 'setup printed a success message after a fatal failure\n' >&2
  exit 1
fi

CONFLICT_ROOT="$TEST_ROOT/setup-command-conflict"
mkdir -p "$CONFLICT_ROOT/.local/bin"
cp "$REPO_ROOT/VERSION" "$CONFLICT_ROOT/.local/bin/wut"
CONFLICT_LOG="$TEST_ROOT/setup-command-conflict.log"
if WUTPACK_TEST_ROOT="$CONFLICT_ROOT" "$REPO_ROOT/setup" --skills-only --host codex \
  >"$CONFLICT_LOG" 2>&1; then
  printf 'setup passed without installing its required wut command\n' >&2
  exit 1
fi
grep -Fq 'Cannot install wut because a non-symlink already exists' "$CONFLICT_LOG"

PROFILE_ROOT="$TEST_ROOT/setup-profile-failure"
mkdir -p "$PROFILE_ROOT/.zprofile"
PROFILE_FAILURE_LOG="$TEST_ROOT/setup-profile-failure.log"
if WUTPACK_TEST_ROOT="$PROFILE_ROOT" "$REPO_ROOT/setup" --skills-only --host codex \
  >"$PROFILE_FAILURE_LOG" 2>&1; then
  printf 'setup passed without updating its required shell profile\n' >&2
  exit 1
fi
grep -Fq 'Could not update shell profile' "$PROFILE_FAILURE_LOG"

EARLY_CONFLICT_ROOT="$TEST_ROOT/setup-early-command-conflict"
EARLY_CONFLICT_BIN="$EARLY_CONFLICT_ROOT/.local/bin"
EARLY_CONFLICT_BREW_LOG="$TEST_ROOT/setup-early-command-conflict-brew.log"
mkdir -p "$EARLY_CONFLICT_BIN"
cp "$REPO_ROOT/VERSION" "$EARLY_CONFLICT_BIN/wut"
cat > "$EARLY_CONFLICT_BIN/brew" <<'EOF'
#!/usr/bin/env bash
printf 'brew ran\n' >> "$WUTPACK_EARLY_CONFLICT_BREW_LOG"
exit 0
EOF
chmod +x "$EARLY_CONFLICT_BIN/brew"
if env PATH="$EARLY_CONFLICT_BIN:/usr/bin:/bin" \
  WUTPACK_EARLY_CONFLICT_BREW_LOG="$EARLY_CONFLICT_BREW_LOG" \
  WUTPACK_TEST_ROOT="$EARLY_CONFLICT_ROOT" /bin/bash "$REPO_ROOT/setup" \
  --profile core --host codex --skip-casks --skip-ai-clis >/dev/null 2>&1; then
  printf 'setup passed with an existing non-symlink wut command\n' >&2
  exit 1
fi
test ! -e "$EARLY_CONFLICT_BREW_LOG"

OPTIONAL_ROOT="$TEST_ROOT/setup-optional-failure"
OPTIONAL_STUB_BIN="$TEST_ROOT/setup-optional-stubs"
OPTIONAL_FAILURE_LOG="$TEST_ROOT/setup-optional-failure.log"
mkdir -p "$OPTIONAL_STUB_BIN"
cat > "$OPTIONAL_STUB_BIN/brew" <<'EOF'
#!/usr/bin/env bash
if [ "${1:-}" = "list" ]; then
  [ "${3:-}" != "git" ]
  exit
fi
if [ "${1:-}" = "install" ] && [ "${2:-}" = "git" ]; then exit 1; fi
exit 0
EOF
cat > "$OPTIONAL_STUB_BIN/uv" <<'EOF'
#!/usr/bin/env bash
exit 1
EOF
chmod +x "$OPTIONAL_STUB_BIN/brew" "$OPTIONAL_STUB_BIN/uv"
if env PATH="$OPTIONAL_STUB_BIN:/usr/bin:/bin" WUTPACK_TEST_ROOT="$OPTIONAL_ROOT" \
  /bin/bash "$REPO_ROOT/setup" --profile core --host codex --skip-casks --skip-ai-clis \
  >"$OPTIONAL_FAILURE_LOG" 2>&1; then
  printf 'setup reported success after optional package failures\n' >&2
  exit 1
fi
grep -Fq 'WutPack setup incomplete' "$OPTIONAL_FAILURE_LOG"
grep -Fq 'Completed with ' "$OPTIONAL_FAILURE_LOG"
if grep -Fq 'WutPack setup complete' "$OPTIONAL_FAILURE_LOG"; then
  printf 'setup printed a success message after optional package failures\n' >&2
  exit 1
fi

PIPE_USER_ROOT="$TEST_ROOT/piped-user"
PIPE_INSTALL_ROOT="$TEST_ROOT/piped-source"
printf '' | WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$PIPE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$PIPE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host both >/dev/null
test -L "$PIPE_USER_ROOT/.local/bin/wut"

STALE_INSTALL_ROOT="$TEST_ROOT/stale-source"
STALE_USER_ROOT="$TEST_ROOT/stale-user"
WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null
touch "$STALE_INSTALL_ROOT/removed-upstream-file"
WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null
test ! -e "$STALE_INSTALL_ROOT/removed-upstream-file"
test -z "$(find "$TEST_ROOT" -maxdepth 1 -name '.wutpack-*' -print -quit)"

SETUP_FAILURE_SOURCE="$TEST_ROOT/setup-failure-source"
ditto "$REPO_ROOT" "$SETUP_FAILURE_SOURCE"
cat > "$SETUP_FAILURE_SOURCE/setup" <<'EOF'
#!/usr/bin/env bash
exit 42
EOF
chmod +x "$SETUP_FAILURE_SOURCE/setup"
touch "$STALE_INSTALL_ROOT/previous-install-marker"
setup_failure_status=0
WUTPACK_SOURCE_DIR="$SETUP_FAILURE_SOURCE" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || setup_failure_status=$?
test "$setup_failure_status" = "42"
test ! -e "$STALE_INSTALL_ROOT/previous-install-marker"
grep -Fxq 'WutPack managed source v1' "$STALE_INSTALL_ROOT/.wutpack-install"
grep -Fq 'exit 42' "$STALE_INSTALL_ROOT/setup"
test -L "$STALE_USER_ROOT/.local/bin/wut"
test -e "$STALE_USER_ROOT/.local/bin/wut"
test -z "$(find "$TEST_ROOT" -maxdepth 1 -name '.wutpack-*' -print -quit)"

FIRST_FAILURE_SOURCE="$TEST_ROOT/first-install-failure-source"
FIRST_FAILURE_ROOT="$TEST_ROOT/first-install-failure-root"
FIRST_FAILURE_USER="$TEST_ROOT/first-install-failure-user"
ditto "$REPO_ROOT" "$FIRST_FAILURE_SOURCE"
cat > "$FIRST_FAILURE_SOURCE/setup" <<'EOF'
#!/usr/bin/env bash
project_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
mkdir -p "$WUTPACK_TEST_ROOT/.local/bin"
ln -sfn "$project_root/bin/wut" "$WUTPACK_TEST_ROOT/.local/bin/wut"
exit 42
EOF
chmod +x "$FIRST_FAILURE_SOURCE/setup"
first_failure_status=0
WUTPACK_SOURCE_DIR="$FIRST_FAILURE_SOURCE" WUTPACK_TEST_ROOT="$FIRST_FAILURE_USER" \
  WUTPACK_INSTALL_ROOT="$FIRST_FAILURE_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || first_failure_status=$?
test "$first_failure_status" = "42"
grep -Fxq 'WutPack managed source v1' "$FIRST_FAILURE_ROOT/.wutpack-install"
test -L "$FIRST_FAILURE_USER/.local/bin/wut"
test -e "$FIRST_FAILURE_USER/.local/bin/wut"

WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null
touch "$STALE_INSTALL_ROOT/previous-install-marker"

MV_STUB_BIN="$TEST_ROOT/mv-failure-stub"
MV_STUB_COUNT="$TEST_ROOT/mv-failure-count"
mkdir -p "$MV_STUB_BIN"
cat > "$MV_STUB_BIN/mv" <<'EOF'
#!/usr/bin/env bash
count=0
[ ! -f "$WUTPACK_MV_STUB_COUNT" ] || read -r count < "$WUTPACK_MV_STUB_COUNT"
count=$((count + 1))
printf '%s\n' "$count" > "$WUTPACK_MV_STUB_COUNT"
[ "$count" -ne 2 ] || exit 73
exec /bin/mv "$@"
EOF
chmod +x "$MV_STUB_BIN/mv"
mv_failure_status=0
env PATH="$MV_STUB_BIN:/usr/bin:/bin" WUTPACK_MV_STUB_COUNT="$MV_STUB_COUNT" \
  WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || mv_failure_status=$?
test "$mv_failure_status" = "73"
test -e "$STALE_INSTALL_ROOT/previous-install-marker"
grep -Fq 'WutPack setup currently supports macOS only' "$STALE_INSTALL_ROOT/setup"
test ! -e "$TEST_ROOT/.stale-source.install-lock"
test -z "$(find "$TEST_ROOT" -maxdepth 1 -name '.wutpack-*' -print -quit)"

INSTALL_SIGNAL_STUB_BIN="$TEST_ROOT/install-signal-stub"
INSTALL_SIGNAL_COUNT="$TEST_ROOT/install-signal-count"
mkdir -p "$INSTALL_SIGNAL_STUB_BIN"
cat > "$INSTALL_SIGNAL_STUB_BIN/mv" <<'EOF'
#!/usr/bin/env bash
count=0
[ ! -f "$WUTPACK_INSTALL_SIGNAL_COUNT" ] || \
  read -r count < "$WUTPACK_INSTALL_SIGNAL_COUNT"
count=$((count + 1))
printf '%s\n' "$count" > "$WUTPACK_INSTALL_SIGNAL_COUNT"
if [ "$count" -eq 2 ]; then
  kill -TERM "$PPID"
  exit 0
fi
exec /bin/mv "$@"
EOF
chmod +x "$INSTALL_SIGNAL_STUB_BIN/mv"
install_signal_status=0
env PATH="$INSTALL_SIGNAL_STUB_BIN:/usr/bin:/bin" \
  WUTPACK_INSTALL_SIGNAL_COUNT="$INSTALL_SIGNAL_COUNT" \
  WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || install_signal_status=$?
test "$install_signal_status" = "143"
test -e "$STALE_INSTALL_ROOT/previous-install-marker"
test ! -e "$TEST_ROOT/.stale-source.install-lock"

RECOVERY_PARENT="$(CDPATH= cd -- "$TEST_ROOT" && pwd -P)"
RECOVERY_STAGE="$RECOVERY_PARENT/.wutpack-stage.interrupted"
RECOVERY_BACKUP="$RECOVERY_PARENT/.wutpack-backup.interrupted"
RECOVERY_LOCK="$RECOVERY_PARENT/.stale-source.install-lock"
mkdir -p "$RECOVERY_STAGE" "$RECOVERY_BACKUP" "$RECOVERY_LOCK"
chmod 700 "$RECOVERY_STAGE" "$RECOVERY_BACKUP" "$RECOVERY_LOCK"
mv "$STALE_INSTALL_ROOT" "$RECOVERY_BACKUP/previous"
printf '%s\n' '999999' > "$RECOVERY_LOCK/pid"
printf '%s\n' 'stale process start' > "$RECOVERY_LOCK/start"
printf '%s\n' "$RECOVERY_STAGE" > "$RECOVERY_LOCK/stage"
printf '%s\n' "$RECOVERY_BACKUP" > "$RECOVERY_LOCK/backup"
printf '%s\n' '1' > "$RECOVERY_LOCK/had-previous"
RECOVERY_STUB_BIN="$TEST_ROOT/recovery-stub"
mkdir -p "$RECOVERY_STUB_BIN"
cat > "$RECOVERY_STUB_BIN/ditto" <<'EOF'
#!/usr/bin/env bash
exit 91
EOF
chmod +x "$RECOVERY_STUB_BIN/ditto"
recovery_status=0
env PATH="$RECOVERY_STUB_BIN:/usr/bin:/bin" \
  WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || recovery_status=$?
test "$recovery_status" = "91"
test -e "$STALE_INSTALL_ROOT/previous-install-marker"
test ! -e "$RECOVERY_STAGE"
test ! -e "$RECOVERY_BACKUP"
test ! -e "$RECOVERY_LOCK"

FRESH_RECOVERY_ROOT="$RECOVERY_PARENT/fresh-recovery-root"
FRESH_RECOVERY_STAGE="$RECOVERY_PARENT/.wutpack-stage.fresh-interrupted"
FRESH_RECOVERY_LOCK="$RECOVERY_PARENT/.fresh-recovery-root.install-lock"
mkdir -p "$FRESH_RECOVERY_STAGE" "$FRESH_RECOVERY_LOCK"
chmod 700 "$FRESH_RECOVERY_STAGE" "$FRESH_RECOVERY_LOCK"
printf '%s\n' '999999' > "$FRESH_RECOVERY_LOCK/pid"
printf '%s\n' 'stale process start' > "$FRESH_RECOVERY_LOCK/start"
printf '%s\n' "$FRESH_RECOVERY_STAGE" > "$FRESH_RECOVERY_LOCK/stage"
printf '%s\n' '0' > "$FRESH_RECOVERY_LOCK/had-previous"
fresh_recovery_status=0
env PATH="$RECOVERY_STUB_BIN:/usr/bin:/bin" \
  WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$FRESH_RECOVERY_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1 || fresh_recovery_status=$?
test "$fresh_recovery_status" = "91"
test ! -e "$FRESH_RECOVERY_ROOT"
test ! -e "$FRESH_RECOVERY_STAGE"
test ! -e "$FRESH_RECOVERY_LOCK"

touch "$STALE_INSTALL_ROOT/dry-run-preserved-marker"
WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex --dry-run >/dev/null
test -e "$STALE_INSTALL_ROOT/dry-run-preserved-marker"

UNOWNED_INSTALL_ROOT="$TEST_ROOT/not-a-wutpack-install"
mkdir -p "$UNOWNED_INSTALL_ROOT"
touch "$UNOWNED_INSTALL_ROOT/user-data"
if WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$UNOWNED_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1; then
  printf 'installer replaced a directory not owned by WutPack\n' >&2
  exit 1
fi
test -e "$UNOWNED_INSTALL_ROOT/user-data"

INSTALL_LOCK_ROOT="$TEST_ROOT/.stale-source.install-lock"
mkdir -p "$INSTALL_LOCK_ROOT"
chmod 700 "$INSTALL_LOCK_ROOT"
printf '%s\n' "$$" > "$INSTALL_LOCK_ROOT/pid"
printf '%s\n' 'unavailable' > "$INSTALL_LOCK_ROOT/start"
if WUTPACK_SOURCE_DIR="$REPO_ROOT" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1; then
  printf 'installer ignored an active per-root lock\n' >&2
  exit 1
fi
test -e "$STALE_INSTALL_ROOT/previous-install-marker"
rm -f "$INSTALL_LOCK_ROOT/pid" "$INSTALL_LOCK_ROOT/start"
rmdir "$INSTALL_LOCK_ROOT"

SIGNAL_SOURCE="$TEST_ROOT/signal-source"
SIGNAL_USER="$TEST_ROOT/signal-user"
SIGNAL_STUB_BIN="$TEST_ROOT/signal-stub"
SIGNAL_MKDIR_COUNT="$TEST_ROOT/signal-mkdir-count"
ditto "$REPO_ROOT" "$SIGNAL_SOURCE"
mkdir -p "$SIGNAL_STUB_BIN"
cat > "$SIGNAL_STUB_BIN/mkdir" <<'EOF'
#!/usr/bin/env bash
count=0
[ ! -f "$WUTPACK_SIGNAL_MKDIR_COUNT" ] || \
  read -r count < "$WUTPACK_SIGNAL_MKDIR_COUNT"
count=$((count + 1))
printf '%s\n' "$count" > "$WUTPACK_SIGNAL_MKDIR_COUNT"
/bin/mkdir "$@" || exit $?
[ "$count" -ne 2 ] || kill -TERM "$PPID"
EOF
chmod +x "$SIGNAL_STUB_BIN/mkdir"
signal_status=0
env PATH="$SIGNAL_STUB_BIN:/usr/bin:/bin" \
  WUTPACK_SIGNAL_MKDIR_COUNT="$SIGNAL_MKDIR_COUNT" \
  WUTPACK_TEST_ROOT="$SIGNAL_USER" /bin/bash "$SIGNAL_SOURCE/setup" \
  --skills-only --host codex >/dev/null 2>&1 || signal_status=$?
test "$signal_status" = "143"
test ! -e "$TEST_ROOT/.signal-source.install-lock"
test ! -e "$SIGNAL_USER/.local/bin/wut"

PARTIAL_INSTALL_SOURCE="$TEST_ROOT/partial-install-source"
mkdir -p "$PARTIAL_INSTALL_SOURCE"
cp "$REPO_ROOT/setup" "$PARTIAL_INSTALL_SOURCE/setup"
if WUTPACK_SOURCE_DIR="$PARTIAL_INSTALL_SOURCE" WUTPACK_TEST_ROOT="$STALE_USER_ROOT" \
  WUTPACK_INSTALL_ROOT="$STALE_INSTALL_ROOT" /bin/bash "$REPO_ROOT/install.sh" \
  --skills-only --host codex >/dev/null 2>&1; then
  printf 'installer accepted a partial source tree\n' >&2
  exit 1
fi
test -e "$STALE_INSTALL_ROOT/previous-install-marker"
test -z "$(find "$TEST_ROOT" -maxdepth 1 -name '.wutpack-*' -print -quit)"

DRY_ROOT="$TEST_ROOT/dry-run-user"
WUTPACK_TEST_ROOT="$DRY_ROOT" "$REPO_ROOT/setup" --skills-only --host both --dry-run >/dev/null
test ! -e "$DRY_ROOT"

FRESH_DRY_ROOT="$TEST_ROOT/fresh-dry-run-user"
FRESH_DRY_LOG="$TEST_ROOT/fresh-dry-run.log"
env PATH=/usr/bin:/bin:/usr/sbin:/sbin WUTPACK_TEST_ROOT="$FRESH_DRY_ROOT" \
  /bin/bash "$REPO_ROOT/setup" --dry-run --skip-casks --skip-ai-clis >"$FRESH_DRY_LOG"
test ! -e "$FRESH_DRY_ROOT"
test "$(grep -c 'python-ml\.txt' "$FRESH_DRY_LOG")" = "1"
grep -Eq 'python-core\.txt .*python-ml\.txt' "$FRESH_DRY_LOG"
grep -Fq 'brew install node' "$FRESH_DRY_LOG"
grep -Fq 'brew install pandoc' "$FRESH_DRY_LOG"
grep -Fq 'brew install sqlite' "$FRESH_DRY_LOG"
grep -Eq 'uv pip install .*--upgrade --exact --strict' "$FRESH_DRY_LOG"
grep -Fq 'npm uninstall --global' "$FRESH_DRY_LOG"
grep -Fq '@modelcontextprotocol/server-filesystem' "$FRESH_DRY_LOG"
test "$(tail -n 2 "$FRESH_DRY_LOG" | head -n 1)" = \
  'IMPORTANT: Open a new terminal before using WutPack, then run: wut doctor'
test "$(tail -n 1 "$FRESH_DRY_LOG")" = 'Author: WUTLABS SUNNYVALE CA'

printf 'Shell and isolated-install checks passed.\n'
