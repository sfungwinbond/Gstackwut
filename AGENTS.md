# Repository guidance

WutPack is a macOS bootstrapper and scenario-skill collection for Codex and
Claude Code.

- Keep `install.sh`, `setup`, and `bin/wut` compatible with macOS Bash 3.2.
- Keep setup idempotent and store user-managed environments under
  `~/Library/Application Support/WutPack`.
- Never add credentials, API keys, or automatic account configuration.
- Add package names to the manifest files instead of hard-coding them in setup.
- Keep each skill concise. Put deterministic helpers in `scripts/` and detailed
  patterns in `references/`.
- Run `make test` before committing.
- Do not publish, deploy, or modify user repositories unless the user explicitly
  requests it.
