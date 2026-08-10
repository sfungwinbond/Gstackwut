#!/usr/bin/env bash

set -euo pipefail

if [ "$(uname -s)" != "Darwin" ]; then
  printf 'WutPack currently supports macOS only.\n' >&2
  exit 1
fi

REPOSITORY="sfungwinbond/Gstackwut"
BRANCH="${WUTPACK_BRANCH:-main}"
USER_HOME="${WUTPACK_TEST_ROOT:-$HOME}"
INSTALL_ROOT="${WUTPACK_INSTALL_ROOT:-$USER_HOME/.local/share/wutpack}"
TEMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/wutpack-bootstrap.XXXXXX")"

cleanup() {
  case "$TEMP_ROOT" in
    "${TMPDIR:-/tmp}"/wutpack-bootstrap.*) rm -rf -- "$TEMP_ROOT" ;;
  esac
}
trap cleanup EXIT INT TERM

printf '\n  WutPack: fetching the Mac AI workbench...\n\n'

if [ -n "${WUTPACK_SOURCE_DIR:-}" ]; then
  SOURCE_ROOT="$WUTPACK_SOURCE_DIR"
else
  ARCHIVE="$TEMP_ROOT/source.tar.gz"
  curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location \
    "https://github.com/$REPOSITORY/archive/refs/heads/$BRANCH.tar.gz" \
    --output "$ARCHIVE"
  tar -xzf "$ARCHIVE" -C "$TEMP_ROOT"
  SOURCE_ROOT="$(find "$TEMP_ROOT" -mindepth 1 -maxdepth 1 -type d -name 'Gstackwut-*' -print -quit)"
fi

if [ -z "${SOURCE_ROOT:-}" ] || [ ! -f "$SOURCE_ROOT/setup" ]; then
  printf 'WutPack bootstrap could not find setup in %s\n' "$SOURCE_ROOT" >&2
  exit 1
fi

mkdir -p "$INSTALL_ROOT"
ditto "$SOURCE_ROOT" "$INSTALL_ROOT"
chmod +x "$INSTALL_ROOT/setup" "$INSTALL_ROOT/bin/wut"

if [ -r /dev/tty ] && [ -w /dev/tty ]; then
  "$INSTALL_ROOT/setup" "$@" </dev/tty
else
  "$INSTALL_ROOT/setup" "$@"
fi
