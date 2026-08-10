#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)"
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
  "$REPO_ROOT/examples/technical-diagram-demo.pptx" >/dev/null

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
CANONICAL_INSTALL_ROOT="$(CDPATH= cd -- "$INSTALL_ROOT" && pwd -P)"
test "$(readlink "$TEST_ROOT/.local/bin/wut")" = "$CANONICAL_INSTALL_ROOT/bin/wut"
test -f "$TEST_ROOT/.codex/skills/technical-deck/SKILL.md"
test -f "$TEST_ROOT/.claude/skills/spreadsheet-lab/SKILL.md"
test "$(find "$TEST_ROOT/.codex/skills" -name SKILL.md | wc -l | tr -d ' ')" = "12"
test "$(find "$TEST_ROOT/.claude/skills" -name SKILL.md | wc -l | tr -d ' ')" = "12"

WUTPACK_TEST_ROOT="$TEST_ROOT" "$INSTALL_ROOT/setup" --skills-only --host both >/dev/null
test "$(grep -cF '# >>> WutPack persistent tools >>>' "$TEST_ROOT/.zprofile")" = "1"
test "$(grep -cF '# >>> WutPack persistent tools >>>' "$TEST_ROOT/.zshrc")" = "1"
/bin/zsh -n "$TEST_ROOT/.zprofile"
/bin/zsh -n "$TEST_ROOT/.zshrc"

WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" \
  "$INSTALL_ROOT/bin/wut" routes | grep -Fq 'technical-deck'
test "$(WUTPACK_TEST_ROOT="$TEST_ROOT" WUTPACK_INSTALL_ROOT="$INSTALL_ROOT" "$INSTALL_ROOT/bin/wut" version)" = "0.1.0"

DRY_ROOT="$TEST_ROOT/dry-run-user"
WUTPACK_TEST_ROOT="$DRY_ROOT" "$REPO_ROOT/setup" --skills-only --host both --dry-run >/dev/null
test ! -e "$DRY_ROOT"

FRESH_DRY_ROOT="$TEST_ROOT/fresh-dry-run-user"
env PATH=/usr/bin:/bin:/usr/sbin:/sbin WUTPACK_TEST_ROOT="$FRESH_DRY_ROOT" \
  /bin/bash "$REPO_ROOT/setup" --dry-run --skip-casks --skip-ai-clis >/dev/null
test ! -e "$FRESH_DRY_ROOT"

printf 'Shell and isolated-install checks passed.\n'
