#!/usr/bin/env python3
"""Build the standalone WutPack security engineering lab."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_ROOT.parents[1]
TEMPLATE = SKILL_ROOT / "assets" / "security-lab-template.html"


def render() -> str:
    version_path = REPO_ROOT / "VERSION"
    version = version_path.read_text(encoding="utf-8").strip() if version_path.is_file() else "source"
    source = TEMPLATE.read_text(encoding="utf-8")
    return source.replace("{{WUTPACK_VERSION}}", version)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="HTML output path")
    parser.add_argument("--check", action="store_true", help="fail if output is missing or stale")
    args = parser.parse_args()

    expected = render()
    if args.check:
        if not args.output.is_file():
            print(f"missing generated security lab: {args.output}", file=sys.stderr)
            return 1
        if args.output.read_text(encoding="utf-8") != expected:
            print(f"stale generated security lab: {args.output}", file=sys.stderr)
            return 1
        print(f"security lab is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(f"wrote {args.output} ({len(expected.encode('utf-8'))} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
