---
name: review-gate
description: Review a pull request, branch, commit, patch, or working-tree diff for correctness, regressions, unsafe assumptions, missing tests, compatibility problems, and operational risk. Use when the user asks for code review, PR review, diff review, pre-merge checks, or an independent assessment of a change.
---

# Review Gate

Review the change, not the author's style.

## Workflow

1. Read repository guidance and determine the base and changed surface.
2. Inspect the complete diff plus enough surrounding code, tests, schemas, and callers to understand behavior.
3. Trace inputs through state changes and outputs. Check error paths, concurrency, migrations, compatibility, and cleanup.
4. Run focused tests or static checks when they materially validate a suspicion.
5. Report only actionable findings. Order them by severity and include file, line, failure scenario, user impact, and a concrete direction for repair.

## Boundaries

- Do not edit the code unless the user asks for fixes.
- Do not call preferences, naming taste, or hypothetical hardening a defect.
- If there are no findings, say so and name the remaining untested risk.
