---
name: code-build
description: Implement a scoped feature, refactor, integration, script, or repository change with repository-aware planning, minimal edits, tests, and a clear handoff. Use when the user asks to build, add, change, migrate, automate, or implement code rather than merely explain or review it.
---

# Code Build

## Workflow

1. Read repository instructions and map the affected entry points, tests, dependencies, and public behavior.
2. Restate the expected outcome and identify the smallest complete change. Ask only when a missing decision would materially change behavior.
3. Preserve unrelated user changes. Edit through existing abstractions and conventions.
4. Add or update tests for the user-visible behavior and important failure paths.
5. Run the narrowest relevant checks first, then the broader project checks.
6. Report the outcome, files changed, verification evidence, and any remaining risk.

## Boundaries

- Do not commit, push, publish, deploy, message others, or change external systems unless the user requested it.
- Do not hide incomplete work behind a passing narrow test.
- Do not broaden scope into unrelated cleanup.
