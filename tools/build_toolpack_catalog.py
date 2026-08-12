#!/usr/bin/env python3
"""Build the public career-toolpack catalog from pack frontmatter."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site/toolpacks.html"
GITHUB_ROOT = "https://github.com/sfungwinbond/Gstackwut/blob/main"

CATEGORIES = (
    {
        "slug": "profession",
        "directory": "professions",
        "number": "01",
        "title": "General high-pay snapshot",
        "short": "High-pay",
        "basis": "First ten entries in the BLS highest-paying occupations table, using 2024 U.S. median annual pay.",
        "rank_label": "source order",
        "boundary": "Use fictional or properly de-identified inputs. These packs do not diagnose, treat, triage, or replace licensed clinical review.",
    },
    {
        "slug": "finance",
        "directory": "finance",
        "number": "02",
        "title": "Finance snapshot",
        "short": "Finance",
        "basis": "Financial managers plus nine detailed finance roles from the May 2025 U.S. OEWS annual mean wage table.",
        "rank_label": "finance order",
        "boundary": "These packs create analysis and drafts. They do not provide individualized advice, execute trades, approve credit, or issue audit opinions.",
    },
    {
        "slug": "engineering",
        "directory": "engineering",
        "number": "03",
        "title": "Engineering snapshot",
        "short": "Engineering",
        "basis": "Detailed engineering occupations sorted by 2024 U.S. median annual pay in the BLS engineering table.",
        "rank_label": "pay order",
        "boundary": "These packs do not certify designs, set live controls, authorize release, or replace independent engineering and safety review.",
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when site/toolpacks.html is not current",
    )
    return parser.parse_args()


def read_pack(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError(f"{path}: missing frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, separator, value = line.partition(":")
        if not separator:
            raise ValueError(f"{path}: malformed frontmatter line {line!r}")
        fields[key.strip()] = value.strip()
    return fields


def escaped(value: str) -> str:
    return html.escape(value, quote=True)


def render_pack(fields: dict[str, str], category: dict[str, str]) -> str:
    slug = fields["slug"]
    profession = fields["profession"]
    specialists = [value.strip() for value in fields["specialists"].split(",")]
    tools = [value.strip() for value in fields["tools"].split(",")]
    searchable = " ".join(
        [slug, profession, fields["description"], fields["pay"], *specialists, *tools]
    ).lower()
    tool_markup = "".join(f"<span>{escaped(tool)}</span>" for tool in tools)
    specialist_markup = " · ".join(escaped(value) for value in specialists)
    source_path = f"packs/{category['directory']}/{slug}.md"
    command = f"wut pack {slug}"
    return f"""        <article class="pack-row" id="{escaped(slug)}" data-pack data-category="{escaped(category['slug'])}" data-search="{escaped(searchable)}">
          <div class="pack-rank" aria-label="{escaped(category['rank_label'])} {int(fields['rank'])}">
            <strong>{int(fields['rank']):02d}</strong>
            <span>{escaped(category['rank_label'])}</span>
          </div>
          <div class="pack-body">
            <div class="pack-title-line">
              <h3>{escaped(profession)}</h3>
              <span class="pack-category">{escaped(category['short'])}</span>
            </div>
            <p class="pack-pay">{escaped(fields['pay'])}</p>
            <p class="pack-description" data-pretext>{escaped(fields['description'])}</p>
            <dl class="pack-route">
              <div><dt>Routes through</dt><dd>{specialist_markup}</dd></div>
            </dl>
            <div class="pack-tools" aria-label="Selected deterministic tools">{tool_markup}</div>
            <div class="pack-actions">
              <code>{escaped(command)}</code>
              <button type="button" data-copy-command="{escaped(command)}">Copy command</button>
              <a href="{GITHUB_ROOT}/{escaped(source_path)}">Read pack source <span aria-hidden="true">→</span></a>
            </div>
          </div>
        </article>"""


def render_group(category: dict[str, str], packs: list[dict[str, str]]) -> str:
    rows = "\n".join(render_pack(pack, category) for pack in packs)
    slug = category["slug"]
    return f"""    <section class="pack-group" id="{escaped(slug)}" data-pack-group="{escaped(slug)}" aria-labelledby="{escaped(slug)}-title">
      <header class="pack-group-heading">
        <span class="group-number">{escaped(category['number'])}</span>
        <div>
          <p class="group-kicker">10 CLI toolpacks</p>
          <h2 id="{escaped(slug)}-title">{escaped(category['title'])}</h2>
          <p>{escaped(category['basis'])}</p>
        </div>
        <p class="group-boundary"><strong>Boundary</strong>{escaped(category['boundary'])}</p>
      </header>
      <div class="pack-list">
{rows}
      </div>
    </section>"""


def build() -> str:
    rendered_groups: list[str] = []
    for category in CATEGORIES:
        directory = ROOT / "packs" / category["directory"]
        packs = [read_pack(path) for path in directory.glob("*.md")]
        packs.sort(key=lambda pack: int(pack["rank"]))
        if len(packs) != 10:
            raise ValueError(f"{directory}: expected 10 packs, found {len(packs)}")
        rendered_groups.append(render_group(category, packs))

    groups = "\n\n".join(rendered_groups)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#101714">
  <meta name="description" content="Browse 30 Wut CLI career toolpacks for high-pay clinical work, finance, and engineering, each with transparent salary context and human-review boundaries.">
  <meta property="og:type" content="website">
  <meta property="og:title" content="30 Wut CLI career toolpacks | WutPack">
  <meta property="og:description" content="Search 30 role-shaped toolchains and copy the exact Wut CLI command for each one.">
  <meta property="og:url" content="https://sfungwinbond.github.io/Gstackwut/toolpacks.html">
  <meta property="og:image" content="https://sfungwinbond.github.io/Gstackwut/social-card.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="canonical" href="https://sfungwinbond.github.io/Gstackwut/toolpacks.html">
  <link rel="icon" href="favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&amp;family=IBM+Plex+Mono:wght@400;500;600&amp;family=Instrument+Serif:ital@0;1&amp;display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/toolpacks.css">
  <title>30 Wut CLI career toolpacks | WutPack</title>
</head>
<body>
  <a class="skip-link" href="#catalog">Skip to toolpacks</a>

  <header class="site-header">
    <nav class="nav shell" aria-label="Primary navigation">
      <a class="brand" href="index.html" aria-label="WutPack home">
        <span class="brand-mark" aria-hidden="true">W</span>
        <span>WutPack</span>
        <span class="brand-version">knowledge workbench</span>
      </a>
      <div class="nav-links">
        <a href="index.html">Home</a>
        <a class="nav-current" href="#catalog" aria-current="page">30 toolpacks</a>
        <a class="nav-secondary" href="index.html#tool-gallery">53 tool proofs</a>
        <a class="nav-secondary" href="index.html#specialists">13 specialists</a>
        <a href="https://github.com/sfungwinbond/Gstackwut">GitHub</a>
      </div>
    </nav>
  </header>

  <main id="main">
    <section class="hero">
      <div class="shell hero-grid">
        <div class="hero-copy">
          <p class="eyebrow">Wut CLI · 30 career toolpacks</p>
          <h1>Start with the role. <em>Bring your judgment.</em></h1>
          <p data-pretext>Each pack combines WutPack specialists, deterministic local tools, a role-specific workflow, concrete deliverables, and a hard human-review boundary.</p>
          <div class="hero-actions">
            <a class="button" href="#catalog">Browse all 30</a>
            <a class="button secondary" href="https://github.com/sfungwinbond/Gstackwut/blob/main/docs/profession-packs.md">Read the salary method</a>
          </div>
        </div>
        <div class="command-panel" aria-label="Career toolpack command examples">
          <div class="command-title"><span>Terminal</span><span>real CLI</span></div>
          <pre><code><span class="prompt">$</span> wut packs
<span class="prompt">$</span> wut packs finance
<span class="prompt">$</span> wut pack finance-risk tools
<span class="prompt">$</span> wut pack finance-risk codex \
  "Stress-test a fictional portfolio"</code></pre>
          <p>Codex launches only when you choose <code>codex</code>. No Claude call is made.</p>
        </div>
      </div>
      <div class="shell stat-strip" aria-label="Catalog totals">
        <div><strong>30</strong><span>toolpacks</span></div>
        <div><strong>10 + 10 + 10</strong><span>three ranked snapshots</span></div>
        <div><strong>0</strong><span>hidden model calls</span></div>
      </div>
    </section>

    <section class="method-strip" aria-labelledby="method-title">
      <div class="shell method-grid">
        <p class="eyebrow">Salary context</p>
        <div>
          <h2 id="method-title">A transparent U.S. proxy, not a fake world ranking.</h2>
          <p data-pretext>Detailed jobs are not ranked consistently worldwide. The catalog uses current published U.S. BLS snapshots and keeps wage type, year, ordering, and exclusions visible. The ILO global wage report supplies the cross-country caution.</p>
        </div>
        <div class="source-links" aria-label="Salary sources">
          <a href="https://www.bls.gov/ooh/highest-paying.htm">BLS high-pay table <span aria-hidden="true">↗</span></a>
          <a href="https://www.bls.gov/news.release/ocwage.t01.htm">BLS finance wages <span aria-hidden="true">↗</span></a>
          <a href="https://www.bls.gov/ooh/architecture-and-engineering/">BLS engineering table <span aria-hidden="true">↗</span></a>
          <a href="https://www.ilo.org/sites/default/files/2024-11/GWR-2024_Layout_E_RGB_Web.pdf">ILO global context <span aria-hidden="true">↗</span></a>
        </div>
      </div>
    </section>

    <section class="catalog shell" id="catalog" aria-labelledby="catalog-title">
      <div class="catalog-heading">
        <div>
          <p class="eyebrow">Search the source of truth</p>
          <h2 id="catalog-title">Pick the work, then inspect the pack.</h2>
        </div>
        <p>Search by profession, task, specialist, or tool. Every result links to its reviewed Markdown source.</p>
      </div>

      <div class="catalog-controls">
        <label for="pack-search">Find a profession or tool</label>
        <div class="search-row">
          <input id="pack-search" type="search" placeholder="Try risk, radiology, Python, diagrams…" autocomplete="off" data-pack-search>
          <span data-pack-count aria-live="polite">30 packs</span>
        </div>
        <div class="filter-row" aria-label="Filter toolpacks">
          <button type="button" data-pack-filter="all" aria-pressed="true">All 30</button>
          <button type="button" data-pack-filter="profession" aria-pressed="false">High-pay 10</button>
          <button type="button" data-pack-filter="finance" aria-pressed="false">Finance 10</button>
          <button type="button" data-pack-filter="engineering" aria-pressed="false">Engineering 10</button>
        </div>
      </div>

{groups}

      <p class="empty-state" data-pack-empty hidden>No pack matches that search. Try a profession, specialist, or tool name.</p>
    </section>

    <section class="review-section">
      <div class="shell review-grid">
        <div>
          <p class="eyebrow">Built-in boundary</p>
          <h2>The CLI accelerates the work. It does not inherit the license.</h2>
        </div>
        <div class="review-steps">
          <div><strong>01</strong><span>Use fictional, de-identified, or approved data.</span></div>
          <div><strong>02</strong><span>Keep assumptions, units, sources, and uncertainty visible.</span></div>
          <div><strong>03</strong><span>Require the accountable professional to review and approve.</span></div>
        </div>
      </div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="shell footer-grid">
      <p>WutPack is an independent MIT-licensed project. Salary snapshots are research context, not career, clinical, financial, or engineering advice.</p>
      <div>
        <a href="index.html">Main site</a>
        <a href="https://github.com/sfungwinbond/Gstackwut/releases/tag/v0.2.0">Release 0.2</a>
        <a href="https://github.com/sfungwinbond/Gstackwut/blob/main/docs/profession-packs.md">Methodology</a>
        <a href="https://github.com/sfungwinbond/Gstackwut">GitHub</a>
      </div>
    </div>
  </footer>

  <script type="module" src="assets/toolpacks.js"></script>
</body>
</html>
"""


def main() -> int:
    args = parse_args()
    rendered = build()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("site/toolpacks.html is stale; run tools/build_toolpack_catalog.py")
        print("Career toolpack catalog is current.")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
