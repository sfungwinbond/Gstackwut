#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "research-brief",
    "spreadsheet-lab",
    "pdf-forensics",
    "technical-deck",
    "data-lab",
    "publish-docs",
    "system-diagram",
    "document-studio",
    "code-build",
    "debug-lab",
    "review-gate",
    "ship-check",
}


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return {}
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            fail(errors, f"{path.relative_to(ROOT)}: malformed frontmatter line {line!r}")
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip()
    if set(fields) != {"name", "description"}:
        fail(errors, f"{path.relative_to(ROOT)}: frontmatter must contain only name and description")
    return fields


def validate_skills(errors: list[str]) -> None:
    actual = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    if actual != EXPECTED_SKILLS:
        fail(errors, f"skill set differs: expected={sorted(EXPECTED_SKILLS)} actual={sorted(actual)}")
    for name in sorted(EXPECTED_SKILLS):
        skill_file = ROOT / "skills" / name / "SKILL.md"
        agent_file = ROOT / "skills" / name / "agents" / "openai.yaml"
        if not skill_file.is_file():
            fail(errors, f"missing {skill_file.relative_to(ROOT)}")
            continue
        fields = frontmatter(skill_file, errors)
        if fields.get("name") != name:
            fail(errors, f"{skill_file.relative_to(ROOT)}: name does not match directory")
        description = fields.get("description", "")
        if len(description) < 60 or "Use " not in description:
            fail(errors, f"{skill_file.relative_to(ROOT)}: description lacks trigger detail")
        if not agent_file.is_file():
            fail(errors, f"missing {agent_file.relative_to(ROOT)}")
        else:
            prompt = agent_file.read_text(encoding="utf-8")
            if f"${name}" not in prompt:
                fail(errors, f"{agent_file.relative_to(ROOT)}: default prompt must mention ${name}")


def validate_links(errors: list[str]) -> None:
    markdown_files = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^(?:https?|mailto):", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                fail(errors, f"{path.relative_to(ROOT)}: broken local link {raw_target}")


def validate_manifests(errors: list[str]) -> None:
    for path in sorted((ROOT / "manifests").glob("*.txt")):
        values = [
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        duplicates = sorted({value for value in values if values.count(value) > 1})
        if duplicates:
            fail(errors, f"{path.relative_to(ROOT)}: duplicates {duplicates}")


def validate_repository(errors: list[str]) -> None:
    required = [
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "VERSION",
        "install.sh",
        "setup",
        "bin/wut",
        "examples/flash-architecture.mmd",
        "examples/agent-workflow.puml",
        "examples/technical-diagram-demo.pptx",
        "docs/images/editable-timing-diagram.png",
    ]
    for relative in required:
        if not (ROOT / relative).exists():
            fail(errors, f"missing {relative}")
    for relative in ("install.sh", "setup", "bin/wut", "tests/test-shell.sh"):
        if not os.access(ROOT / relative, os.X_OK):
            fail(errors, f"{relative}: must be executable")
    for path in [ROOT / "README.md", *ROOT.glob("docs/*.md"), *ROOT.glob("skills/*/SKILL.md")]:
        text = path.read_text(encoding="utf-8")
        if re.search(r"\b(?:TODO|TBD|FIXME)\b", text, re.IGNORECASE):
            fail(errors, f"{path.relative_to(ROOT)}: unfinished placeholder")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skills-only", action="store_true")
    args = parser.parse_args()
    errors: list[str] = []
    validate_skills(errors)
    if not args.skills_only:
        validate_links(errors)
        validate_manifests(errors)
        validate_repository(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
