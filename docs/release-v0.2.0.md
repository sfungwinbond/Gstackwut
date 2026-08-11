# WutPack 0.2: 30 career toolpacks join the verified Mac AI workbench

**SUNNYVALE, Calif. — August 11, 2026** — WutPack today released version 0.2,
adding 30 career-oriented toolpacks and a searchable public catalog to its
open-source macOS knowledge-work workbench.

The Wut CLI now lets users list, inspect, and prepare work with ten toolpacks in
each of three collections: a general high-pay snapshot, finance, and
engineering. Every pack selects existing WutPack specialists and deterministic
local tools, defines a role-specific workflow and deliverables, provides a
copy-ready starter prompt, and states which decisions require qualified human
review.

## What shipped

- `wut packs [all|profession|finance|engineering]` lists the 30 packs.
- `wut pack NAME [show|tools|prompt|codex]` inspects a pack, emits its prompt, or
  explicitly launches the authenticated Codex CLI with that context.
- A public catalog at
  https://sfungwinbond.github.io/Gstackwut/toolpacks.html searches all 30 packs
  by role, task, specialist, and tool.
- Every catalog entry links to its Markdown source, selected specialists, local
  tools, salary label, and exact CLI command.
- The main WutPack site links both the new catalog and 53 visual tool-proof
  pages.

## Evidence, not a worldwide salary claim

No single authoritative table ranks detailed professions consistently across
the world. WutPack therefore labels the collections as U.S. salary snapshots:

- The general high-pay collection follows the first ten rows of the U.S. Bureau
  of Labor Statistics highest-paying occupations table and its 2024 median-pay
  bracket.
- The finance collection uses May 2025 U.S. OEWS annual mean wages for named
  finance roles.
- The engineering collection sorts detailed engineering occupations by 2024
  U.S. median annual pay.
- The ILO Global Wage Report supplies cross-country context but not a fabricated
  detailed global top-ten list.

The exact source, date, wage measure, exclusions, and limitations are published
in the [methodology](https://github.com/sfungwinbond/Gstackwut/blob/main/docs/profession-packs.md).

## Safety and professional review

The packs speed up research, analysis, documentation, diagrams, and artifact
creation. They do not inherit a professional license.

- Clinical packs require fictional or properly de-identified inputs and prohibit
  patient-specific diagnosis, treatment, diagnostic interpretation, and live
  triage.
- Finance packs do not execute trades, approve credit, bind coverage, certify
  accounts, or provide individualized financial, tax, legal, or investment
  advice.
- Engineering packs do not certify designs, set live controls, authorize release
  or hazardous work, or replace independent engineering and safety review.

## Verified tool surface

WutPack's public gallery contains 53 visual proof pages based on real local runs
against fictional fixtures. Fifty-two tools were exercised. Claude Code remains
an installed-only record because it was not authenticated or invoked. Codex is
the only agent CLI launched by the new toolpack action, and only after the user
explicitly chooses `codex`.

## Availability

WutPack 0.2 is available now under the MIT License:

- Website: https://sfungwinbond.github.io/Gstackwut/
- Career catalog: https://sfungwinbond.github.io/Gstackwut/toolpacks.html
- Source and install instructions: https://github.com/sfungwinbond/Gstackwut

WutPack currently supports macOS on Apple silicon and Intel. Model providers,
agent subscriptions, and optional third-party services retain their own terms
and pricing.
