---
name: ship-check
description: Prepare a code or document change for release by checking tests, build artifacts, versioning, changelog, documentation, package contents, migration safety, rollback, and post-release verification. Use for release readiness, packaging, preflight checks, or a dry run before commit, push, merge, publish, or deploy.
---

# Ship Check

Make release state explicit before crossing an external boundary.

## Workflow

1. Identify the exact artifact, target version, destination, and irreversible steps.
2. Review the complete intended diff and confirm generated files, dependencies, migrations, configuration, and secrets handling.
3. Run the project test, lint, type, build, package, and documentation checks that apply.
4. Inspect the produced archive, binary, image, document, or installer rather than trusting a successful build message.
5. Write a release note that states behavior changes, compatibility, migration steps, and rollback.
6. Stop before commit, push, merge, publish, or deploy unless the user explicitly authorized that action.

## Output

Return a clear READY, NOT READY, or READY WITH RISKS verdict with evidence and the exact next command. Never describe an untested artifact as ready.
