# Changelog

All notable changes to WutPack are documented here.

## Unreleased

### Changed

- Prefixed every Codex skill display name with `[wutlabs]` so WutPack
  specialists are clearly identified in skill lists and invocation chips.
- Setup now exactly synchronizes managed Python environments, preventing retired
  packages from leaving incompatible dependencies behind.
- Kept Hugging Face Hub on its compatible 0.x line while Pydantic AI still
  requests the removed `inference` extra.
- Added a final reminder to open a new terminal and an
  `Author: WUTLABS SUNNYVALE CA` footer to installer output.

### Removed

- Hermes, Goose, Gemini CLI, OpenCode, Agent Canvas, and Aider from setup. Codex
  and Claude Code are now the only AI coding CLIs installed by default.
- MCP Inspector and the filesystem MCP server from setup because their current
  dependency trees emit upstream deprecation warnings. Existing stale copies are
  removed during setup.

## [0.1.0] - 2026-08-10

### Added

- One-command macOS bootstrap with persistent Homebrew, Python, Node, browser,
  Office, PDF, diagram, data-science, publishing, and agent-tool layers.
- Twelve scenario specialists installed natively for Codex and Claude Code.
- `wut` commands for health checks, updates, notebooks, diagrams, editable
  PowerPoint examples, Office rendering, and PDF OCR.
- Isolated-install tests, package validators, GitHub Actions validation, and
  example knowledge-work artifacts.
- Clean-runner verification on Apple silicon and Intel macOS hosts, including
  artifact generation, dependency checks, and idempotent repair.
- A beginner-focused GitHub Pages launch site, social share card, structured
  metadata, sitemap, and IndexNow search notification.
- A README walkthrough with a concrete fictional consulting example for every
  one of the twelve specialists.
- `wut doctor --headless` for CI and server-style installations without desktop
  applications.

### Changed

- Replaced the former domain-specific sample dataset, diagram, deck, and preview
  with a fully fictional market-entry and value-creation consulting case.
