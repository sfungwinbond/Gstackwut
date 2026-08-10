#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
import re
import sys
from html.parser import HTMLParser
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


class LandingPageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[str] = []
        self.title_depth = 0
        self.title_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"] or "")
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"] or "")
        if tag == "title":
            self.title_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.title_depth = max(0, self.title_depth - 1)

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_text.append(data)


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


def validate_readme_examples(errors: list[str]) -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    heading = "## Twelve-specialist consulting walkthrough"
    if heading not in text:
        fail(errors, "README.md: missing twelve-specialist consulting walkthrough")
        return
    section = text.split(heading, 1)[1].split("\n## ", 1)[0]
    for name in sorted(EXPECTED_SKILLS):
        if f"#### `{name}`" not in section:
            fail(errors, f"README.md: missing example heading for {name}")
        if f"${name}" not in section:
            fail(errors, f"README.md: missing invocation example for {name}")
    if "fictional" not in section.lower() or "no client or proprietary data" not in section.lower():
        fail(errors, "README.md: consulting walkthrough must state its fictional, non-client basis")


def validate_public_examples(errors: list[str]) -> None:
    text_paths = [
        ROOT / "examples/consulting-engagement.mmd",
        ROOT / "examples/market-entry-scorecard.csv",
        ROOT / "skills/technical-deck/scripts/new_technical_deck.mjs",
    ]
    for path in text_paths:
        if "fictional" not in path.read_text(encoding="utf-8").lower():
            fail(errors, f"{path.relative_to(ROOT)}: must state that the example is fictional")


def validate_landing_page(errors: list[str]) -> None:
    path = ROOT / "site/index.html"
    if not path.is_file():
        fail(errors, "missing site/index.html")
        return

    text = path.read_text(encoding="utf-8")
    parser = LandingPageParser()
    parser.feed(text)

    duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicate_ids:
        fail(errors, f"site/index.html: duplicate ids {duplicate_ids}")

    id_set = set(parser.ids)
    for required_id in {"main", "new-mac-start", "work", "specialists", "install", "questions"}:
        if required_id not in id_set:
            fail(errors, f"site/index.html: missing required section id {required_id!r}")
    for target in parser.links:
        if target.startswith("#") and target[1:] not in id_set:
            fail(errors, f"site/index.html: broken page anchor {target}")

    normalized_title = " ".join("".join(parser.title_text).split())
    if "WutPack" not in normalized_title or "small business" not in normalized_title.lower():
        fail(errors, "site/index.html: title must name WutPack and the small-business audience")

    required_fragments = [
        "MIT licensed",
        "install.sh | bash",
        "The honest boundary",
        "Apple silicon and Intel",
        "Codex or Claude Code",
        "Command-Space",
        "Terminal shows no dots",
        "wut doctor",
        "Do I need to be a programmer?",
        *EXPECTED_SKILLS,
    ]
    for fragment in required_fragments:
        if fragment not in text:
            fail(errors, f"site/index.html: missing required content {fragment!r}")

    forbidden_fragments = ["lorem ipsum", "chip erase", "serial flash", "W77Q"]
    lowered = text.lower()
    for fragment in forbidden_fragments:
        if fragment.lower() in lowered:
            fail(errors, f"site/index.html: contains forbidden product-specific content {fragment!r}")


def validate_repository(errors: list[str]) -> None:
    required = [
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "VERSION",
        "install.sh",
        "setup",
        "bin/wut",
        "examples/consulting-engagement.mmd",
        "examples/agent-workflow.puml",
        "examples/market-entry-scorecard.csv",
        "examples/executive-consulting-demo.pptx",
        "docs/images/editable-executive-roadmap.png",
        "site/index.html",
        "site/favicon.svg",
        "site/robots.txt",
        "site/sitemap.xml",
        ".github/workflows/pages.yml",
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
        validate_readme_examples(errors)
        validate_public_examples(errors)
        validate_landing_page(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
