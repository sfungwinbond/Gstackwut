#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
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

EXPECTED_TOOLPACKS = {
    "profession": {
        "psychiatry": (1, "Psychiatrists", "At least USD 239,200 median annual pay (2024)"),
        "surgery": (2, "Surgeons, all other", "At least USD 239,200 median annual pay (2024)"),
        "dermatology": (3, "Dermatologists", "At least USD 239,200 median annual pay (2024)"),
        "pediatric-surgery": (4, "Pediatric surgeons", "At least USD 239,200 median annual pay (2024)"),
        "prosthodontics": (5, "Prosthodontists", "At least USD 239,200 median annual pay (2024)"),
        "anesthesiology": (6, "Anesthesiologists", "At least USD 239,200 median annual pay (2024)"),
        "emergency-medicine": (7, "Emergency medicine physicians", "At least USD 239,200 median annual pay (2024)"),
        "radiology": (8, "Radiologists", "At least USD 239,200 median annual pay (2024)"),
        "ophthalmology": (9, "Ophthalmologists, except pediatric", "At least USD 239,200 median annual pay (2024)"),
        "pathology": (10, "Physicians, pathologists", "At least USD 239,200 median annual pay (2024)"),
    },
    "finance": {
        "finance-management": (1, "Financial managers", "USD 186,910 annual mean wage (May 2025)"),
        "finance-advisory": (2, "Personal financial advisors", "USD 156,670 annual mean wage (May 2025)"),
        "finance-risk": (3, "Financial risk specialists", "USD 124,420 annual mean wage (May 2025)"),
        "finance-investment-analysis": (4, "Financial and investment analysts", "USD 116,800 annual mean wage (May 2025)"),
        "finance-examination": (5, "Financial examiners", "USD 106,240 annual mean wage (May 2025)"),
        "finance-credit": (6, "Credit analysts", "USD 100,850 annual mean wage (May 2025)"),
        "finance-budget": (7, "Budget analysts", "USD 96,370 annual mean wage (May 2025)"),
        "finance-accounting": (8, "Accountants and auditors", "USD 94,750 annual mean wage (May 2025)"),
        "finance-underwriting": (9, "Insurance underwriters", "USD 93,700 annual mean wage (May 2025)"),
        "finance-lending": (10, "Loan officers", "USD 87,790 annual mean wage (May 2025)"),
    },
    "engineering": {
        "engineering-hardware": (1, "Computer hardware engineers", "USD 155,020 median annual pay (2024)"),
        "engineering-petroleum": (2, "Petroleum engineers", "USD 141,280 median annual pay (2024)"),
        "engineering-aerospace": (3, "Aerospace engineers", "USD 134,830 median annual pay (2024)"),
        "engineering-nuclear": (4, "Nuclear engineers", "USD 127,520 median annual pay (2024)"),
        "engineering-chemical": (5, "Chemical engineers", "USD 121,860 median annual pay (2024)"),
        "engineering-electrical": (6, "Electrical and electronics engineers", "USD 118,780 median annual pay (2024)"),
        "engineering-safety": (7, "Health and safety engineers", "USD 109,660 median annual pay (2024)"),
        "engineering-materials": (8, "Materials engineers", "USD 108,310 median annual pay (2024)"),
        "engineering-biomedical": (9, "Bioengineers and biomedical engineers", "USD 106,950 median annual pay (2024)"),
        "engineering-marine": (10, "Marine engineers and naval architects", "USD 105,670 median annual pay (2024)"),
    },
}
TOOLPACK_DIRECTORIES = {"profession": "professions", "finance": "finance", "engineering": "engineering"}

EXPECTED_TOOL_EXAMPLES = {
    "libreoffice",
    "chromium",
    "quarto",
    "drawio",
    "inkscape",
    "codex",
    "claude-code",
    "openpyxl",
    "xlsxwriter",
    "python-docx",
    "python-pptx",
    "cairosvg",
    "pandoc",
    "poppler",
    "qpdf",
    "mupdf",
    "ocrmypdf",
    "tesseract",
    "imagemagick",
    "ffmpeg",
    "pandas",
    "polars",
    "apache-arrow",
    "duckdb",
    "scipy",
    "scikit-learn",
    "statsmodels",
    "jupyterlab",
    "playwright",
    "selenium",
    "scrapy",
    "pptxgenjs",
    "mermaid",
    "graphviz",
    "plantuml",
    "typst",
    "mkdocs",
    "sphinx",
    "pdoc",
    "doxygen",
    "jsdoc",
    "typedoc",
    "github-cli",
    "ripgrep",
    "fd",
    "fzf",
    "jq",
    "yq",
    "shellcheck",
    "shfmt",
    "delta",
    "hyperfine",
    "just",
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


class ToolpackCatalogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.pack_ids: list[str] = []
        self.pack_categories: list[str] = []
        self.links: list[str] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.append(attributes["id"] or "")
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"] or "")
        if tag == "article" and "data-pack" in attributes:
            self.pack_ids.append(attributes.get("id") or "")
            self.pack_categories.append(attributes.get("data-category") or "")


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
            display_name = re.search(
                r'^  display_name: "([^"]+)"$', prompt, re.MULTILINE
            )
            if not display_name:
                fail(errors, f"{agent_file.relative_to(ROOT)}: missing display_name")
            elif not display_name.group(1).startswith("[wutlabs] "):
                fail(
                    errors,
                    f"{agent_file.relative_to(ROOT)}: display_name must start with "
                    "'[wutlabs] '",
                )
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


def manifest_values(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def validate_agent_cli_policy(errors: list[str]) -> None:
    expected_node_agents = ["@openai/codex", "@anthropic-ai/claude-code"]
    node_agents = manifest_values(ROOT / "manifests/node-agents.txt")
    if node_agents != expected_node_agents:
        fail(
            errors,
            "manifests/node-agents.txt: only Codex and Claude Code are allowed; "
            f"got {node_agents}",
        )

    python_agents = manifest_values(ROOT / "manifests/python-agents.txt")
    if "aider-chat" in python_agents:
        fail(errors, "manifests/python-agents.txt: Aider must not be installed")

    if "huggingface-hub<1" not in python_agents:
        fail(
            errors,
            "manifests/python-agents.txt: huggingface-hub must stay below 1.x "
            "while Pydantic AI requests its retired inference extra",
        )

    node_tools = manifest_values(ROOT / "manifests/node-tools.txt")
    deprecated_node_tools = {
        "@modelcontextprotocol/inspector",
        "@modelcontextprotocol/inspector@^2",
        "@modelcontextprotocol/server-filesystem",
    }
    found_deprecated_node_tools = sorted(deprecated_node_tools.intersection(node_tools))
    if found_deprecated_node_tools:
        fail(
            errors,
            "manifests/node-tools.txt: warning-producing MCP tools must stay retired; "
            f"got {found_deprecated_node_tools}",
        )

    expected_retired_node = [
        "@google/gemini-cli",
        "opencode-ai",
        "@openhands/agent-canvas",
        "@modelcontextprotocol/inspector",
        "@modelcontextprotocol/server-filesystem",
    ]
    retired_node = manifest_values(ROOT / "manifests/node-retired.txt")
    if retired_node != expected_retired_node:
        fail(
            errors,
            "manifests/node-retired.txt: stale Node packages must be removed; "
            f"got {retired_node}",
        )

    current_install_docs = [
        ROOT / "setup",
        ROOT / "README.md",
        ROOT / "docs/commands.md",
        ROOT / "docs/why-persistent.md",
        ROOT / "site/index.html",
    ]
    retired_agents = (
        "hermes",
        "goose",
        "gemini cli",
        "opencode",
        "agent canvas",
        "aider",
    )
    for path in current_install_docs:
        text = path.read_text(encoding="utf-8")
        for agent in retired_agents:
            if re.search(rf"\b{agent}\b", text, re.IGNORECASE):
                fail(errors, f"{path.relative_to(ROOT)}: still references retired agent CLI {agent!r}")


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


def validate_toolpacks(errors: list[str]) -> None:
    required_fields = {
        "slug",
        "category",
        "rank",
        "profession",
        "pay",
        "description",
        "specialists",
        "tools",
    }
    for category, expected_packs in EXPECTED_TOOLPACKS.items():
        pack_dir = ROOT / "packs" / TOOLPACK_DIRECTORIES[category]
        actual = {path.stem for path in pack_dir.glob("*.md")}
        expected = set(expected_packs)
        if actual != expected:
            fail(errors, f"{category} toolpack set differs: expected={sorted(expected)} actual={sorted(actual)}")
            continue

        ranks: set[int] = set()
        for slug, (expected_rank, expected_profession, expected_pay) in expected_packs.items():
            path = pack_dir / f"{slug}.md"
            text = path.read_text(encoding="utf-8")
            match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
            if not match:
                fail(errors, f"{path.relative_to(ROOT)}: missing YAML frontmatter")
                continue
            fields: dict[str, str] = {}
            for line in match.group(1).splitlines():
                if ":" not in line:
                    fail(errors, f"{path.relative_to(ROOT)}: malformed frontmatter line {line!r}")
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
            if set(fields) != required_fields:
                fail(errors, f"{path.relative_to(ROOT)}: toolpack fields differ")
            if fields.get("slug") != slug:
                fail(errors, f"{path.relative_to(ROOT)}: slug does not match filename")
            if fields.get("category") != category:
                fail(errors, f"{path.relative_to(ROOT)}: category does not match directory")
            if fields.get("profession") != expected_profession:
                fail(errors, f"{path.relative_to(ROOT)}: profession differs from salary snapshot")
            if fields.get("pay") != expected_pay:
                fail(errors, f"{path.relative_to(ROOT)}: pay differs from salary snapshot")
            try:
                rank = int(fields.get("rank", ""))
            except ValueError:
                fail(errors, f"{path.relative_to(ROOT)}: rank must be an integer")
            else:
                ranks.add(rank)
                if rank != expected_rank:
                    fail(errors, f"{path.relative_to(ROOT)}: rank differs from source order")

            specialists = {value.strip() for value in fields.get("specialists", "").split(",")}
            if len(specialists) < 4 or not specialists.issubset(EXPECTED_SKILLS):
                fail(errors, f"{path.relative_to(ROOT)}: specialists must name at least four WutPack skills")
            tools = [value.strip() for value in fields.get("tools", "").split(",") if value.strip()]
            if len(tools) < 6:
                fail(errors, f"{path.relative_to(ROOT)}: must name at least six deterministic tools")

            for heading in ("## Workflow", "## Deliverables", "## Safety boundary", "## Starter prompt"):
                if heading not in text:
                    fail(errors, f"{path.relative_to(ROOT)}: missing {heading}")
            lowered = text.lower()
            for fragment in ("does not", "review"):
                if fragment not in lowered:
                    fail(errors, f"{path.relative_to(ROOT)}: missing safety language {fragment!r}")
            if category == "profession" and "de-identified" not in lowered:
                fail(errors, f"{path.relative_to(ROOT)}: clinical pack must require de-identification")
            if category == "finance" and "not " not in lowered:
                fail(errors, f"{path.relative_to(ROOT)}: finance pack must disclaim advice")
            if category == "engineering" and "safety" not in lowered:
                fail(errors, f"{path.relative_to(ROOT)}: engineering pack must address safety")

        if ranks != set(range(1, 11)):
            fail(errors, f"{category} toolpack ranks must be exactly 1-10; got {sorted(ranks)}")

    methodology = (ROOT / "docs/profession-packs.md").read_text(encoding="utf-8")
    for fragment in (
        "https://www.bls.gov/ooh/highest-paying.htm",
        "https://www.bls.gov/news.release/ocwage.t01.htm",
        "https://www.bls.gov/ooh/architecture-and-engineering/",
        "https://www.ilo.org/sites/default/files/2024-11/GWR-2024_Layout_E_RGB_Web.pdf",
        "not mislabeled global facts",
    ):
        if fragment not in methodology:
            fail(errors, f"docs/profession-packs.md: missing methodology detail {fragment!r}")


def validate_tool_gallery(errors: list[str]) -> None:
    gallery = ROOT / "site/tool-examples"
    pages = {path.stem for path in gallery.glob("*.html")}
    if pages != EXPECTED_TOOL_EXAMPLES:
        fail(
            errors,
            f"site/tool-examples: expected={sorted(EXPECTED_TOOL_EXAMPLES)} actual={sorted(pages)}",
        )

    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_gallery_links = set(
        re.findall(
            r"https://sfungwinbond\.github\.io/Gstackwut/tool-examples/([a-z0-9-]+)\.html",
            readme_text,
        )
    )
    if readme_gallery_links != EXPECTED_TOOL_EXAMPLES:
        fail(errors, "README.md: every tool example must have a direct live-site link")

    evidence_path = gallery / "evidence.json"
    if not evidence_path.is_file():
        fail(errors, "site/tool-examples/evidence.json: missing tool evidence manifest")
        return
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(errors, f"site/tool-examples/evidence.json: invalid JSON: {exc}")
        return

    if evidence.get("tool_count") != 53 or evidence.get("exercised_count") != 52:
        fail(errors, "site/tool-examples/evidence.json: expected 53 pages and 52 exercised tools")
    records = evidence.get("tools", [])
    if not isinstance(records, list) or len(records) != 53:
        fail(errors, "site/tool-examples/evidence.json: must contain 53 tool records")
        return
    records_by_slug = {record.get("slug"): record for record in records if isinstance(record, dict)}
    if set(records_by_slug) != EXPECTED_TOOL_EXAMPLES:
        fail(errors, "site/tool-examples/evidence.json: record slugs differ from HTML pages")
    installed_only = [
        record.get("slug") for record in records if record.get("status") == "installed-only"
    ]
    if installed_only != ["claude-code"]:
        fail(errors, "site/tool-examples/evidence.json: Claude Code must be the only installed-only page")
    codex = records_by_slug.get("codex", {})
    if codex.get("status") != "passed" or "authenticated" not in codex.get("note", ""):
        fail(errors, "site/tool-examples/evidence.json: Codex must record the authenticated real run")

    required_assets = [
        gallery / "assets/gallery.css",
        gallery / "assets/gallery.js",
        gallery / "artifacts/codex-decision.json",
    ]
    for path in required_assets:
        if not path.is_file():
            fail(errors, f"missing {path.relative_to(ROOT)}")

    for slug in sorted(EXPECTED_TOOL_EXAMPLES):
        page = gallery / f"{slug}.html"
        text = page.read_text(encoding="utf-8")
        if "../index.html#tool-gallery" not in text:
            fail(errors, f"{page.relative_to(ROOT)}: missing gallery return link")
        if 'href="assets/gallery.css"' not in text or 'src="assets/gallery.js"' not in text:
            fail(errors, f"{page.relative_to(ROOT)}: missing shared gallery assets")
        if any(fragment in text for fragment in ("/Users/", "/var/folders/", "/private/tmp/")):
            fail(errors, f"{page.relative_to(ROOT)}: leaks an absolute local path")

    evidence_text = evidence_path.read_text(encoding="utf-8")
    if any(fragment in evidence_text for fragment in ("/Users/", "/var/folders/", "/private/tmp/")):
        fail(errors, "site/tool-examples/evidence.json: leaks an absolute local path")

    generated_size = sum(path.stat().st_size for path in gallery.rglob("*") if path.is_file())
    if generated_size > 8_000_000:
        fail(errors, f"site/tool-examples: generated gallery exceeds 8 MB ({generated_size} bytes)")


def validate_toolpack_catalog(errors: list[str]) -> None:
    path = ROOT / "site/toolpacks.html"
    if not path.is_file():
        fail(errors, "missing site/toolpacks.html")
        return

    text = path.read_text(encoding="utf-8")
    parser = ToolpackCatalogParser()
    parser.feed(text)
    expected_slugs = {
        slug for category in EXPECTED_TOOLPACKS.values() for slug in category
    }
    if set(parser.pack_ids) != expected_slugs or len(parser.pack_ids) != 30:
        fail(errors, "site/toolpacks.html: must render each of the 30 packs exactly once")
    for category in EXPECTED_TOOLPACKS:
        if parser.pack_categories.count(category) != 10:
            fail(errors, f"site/toolpacks.html: expected 10 {category} catalog rows")

    duplicate_ids = sorted({value for value in parser.ids if parser.ids.count(value) > 1})
    if duplicate_ids:
        fail(errors, f"site/toolpacks.html: duplicate ids {duplicate_ids}")

    expected_sources = {
        f"https://github.com/sfungwinbond/Gstackwut/blob/main/packs/{TOOLPACK_DIRECTORIES[category]}/{slug}.md"
        for category, packs in EXPECTED_TOOLPACKS.items()
        for slug in packs
    }
    if not expected_sources.issubset(set(parser.links)):
        fail(errors, "site/toolpacks.html: every pack must link to its Markdown source")

    for category, packs in EXPECTED_TOOLPACKS.items():
        for slug, (_, profession, pay) in packs.items():
            for fragment in (f'id="{slug}"', html.escape(profession), html.escape(pay)):
                if fragment not in text:
                    fail(errors, f"site/toolpacks.html: {slug} is missing {fragment!r}")

    for fragment in (
        'href="assets/toolpacks.css"',
        'src="assets/toolpacks.js"',
        "A transparent U.S. proxy, not a fake world ranking.",
        "No Claude call is made.",
        "https://www.bls.gov/ooh/highest-paying.htm",
        "https://www.bls.gov/news.release/ocwage.t01.htm",
        "https://www.bls.gov/ooh/architecture-and-engineering/",
        "https://www.ilo.org/sites/default/files/2024-11/GWR-2024_Layout_E_RGB_Web.pdf",
    ):
        if fragment not in text:
            fail(errors, f"site/toolpacks.html: missing required content {fragment!r}")

    check = subprocess.run(
        [sys.executable, str(ROOT / "tools/build_toolpack_catalog.py"), "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if check.returncode:
        fail(errors, check.stderr.strip() or check.stdout.strip())


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
    for required_id in {"main", "new-mac-start", "work", "career-packs", "tool-gallery", "specialists", "install", "questions"}:
        if required_id not in id_set:
            fail(errors, f"site/index.html: missing required section id {required_id!r}")
    for target in parser.links:
        if target.startswith("#") and target[1:] not in id_set:
            fail(errors, f"site/index.html: broken page anchor {target}")

    gallery_links = {
        Path(target).stem
        for target in parser.links
        if target.startswith("tool-examples/") and target.endswith(".html")
    }
    if gallery_links != EXPECTED_TOOL_EXAMPLES:
        fail(errors, "site/index.html: every tool example must be linked directly from the homepage")
    if parser.links.count("toolpacks.html") < 2:
        fail(errors, "site/index.html: career toolpack catalog must be linked from navigation and content")
    for target in ("toolpacks.html#profession", "toolpacks.html#finance", "toolpacks.html#engineering"):
        if target not in parser.links:
            fail(errors, f"site/index.html: missing toolpack collection link {target}")

    normalized_title = " ".join("".join(parser.title_text).split())
    if "WutPack" not in normalized_title or "small business" not in normalized_title.lower():
        fail(errors, "site/index.html: title must name WutPack and the small-business audience")

    install_command = (
        '/usr/bin/curl -fsSL https://raw.githubusercontent.com/sfungwinbond/Gstackwut/main/install.sh '
        '| env PATH="/usr/bin:/bin:/usr/sbin:/sbin" /bin/bash'
    )
    if text.count(install_command) != 2:
        fail(errors, "site/index.html: safe installer command must match in the terminal and copy action")

    required_fragments = [
        "MIT licensed",
        "summary_large_image",
        "social-card.png",
        "The honest boundary",
        "Apple silicon and Intel",
        "Codex or Claude Code",
        "Does it install Codex and Claude Code?",
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

    social_card = ROOT / "site/social-card.png"
    if social_card.is_file():
        data = social_card.read_bytes()
        if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
            fail(errors, "site/social-card.png: must be a valid PNG")
        else:
            width = int.from_bytes(data[16:20], "big")
            height = int.from_bytes(data[20:24], "big")
            if (width, height) != (1280, 640):
                fail(errors, f"site/social-card.png: expected 1280x640, got {width}x{height}")
            if len(data) > 1_000_000:
                fail(errors, "site/social-card.png: must remain under 1 MB")

    indexnow_key = "f2816059f4e9897a617c4f65de3dee83"
    key_path = ROOT / f"site/{indexnow_key}.txt"
    if key_path.is_file() and key_path.read_text(encoding="utf-8").strip() != indexnow_key:
        fail(errors, f"{key_path.relative_to(ROOT)}: key contents must match its filename")


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
        "docs/profession-packs.md",
        "docs/release-v0.2.0.md",
        "site/index.html",
        "site/toolpacks.html",
        "site/assets/toolpacks.css",
        "site/assets/toolpacks.js",
        "site/favicon.svg",
        "site/social-card.png",
        "site/tool-examples/evidence.json",
        "site/tool-examples/assets/gallery.css",
        "site/tool-examples/assets/gallery.js",
        "tools/build_tool_gallery.py",
        "tools/build_toolpack_catalog.py",
        "tools/tool_gallery_decision.schema.json",
        "site/f2816059f4e9897a617c4f65de3dee83.txt",
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
        validate_agent_cli_policy(errors)
        validate_repository(errors)
        validate_readme_examples(errors)
        validate_public_examples(errors)
        validate_toolpacks(errors)
        validate_tool_gallery(errors)
        validate_toolpack_catalog(errors)
        validate_landing_page(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
