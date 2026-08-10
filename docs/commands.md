# Command reference

`wut` is a stable entry point into the managed workbench. Run `wut help` for the
same summary in a terminal.

## Inspection

| Command | Behavior |
|---|---|
| `wut doctor` | Checks core binaries, LibreOffice, Python environments, and host skill directories |
| `wut doctor --headless` | Runs the same check without requiring a desktop LibreOffice installation |
| `wut paths` | Prints source, state, cache, Python, and Node locations |
| `wut skills` | Lists installed specialists and their trigger descriptions |
| `wut routes` | Maps common scenarios to specialist names |
| `wut version` | Prints the installed WutPack version |

## Work commands

| Command | Behavior |
|---|---|
| `wut python ARGS...` | Runs managed knowledge-work Python |
| `wut agent-python ARGS...` | Runs the separate agent-framework Python |
| `wut lab ARGS...` | Starts managed JupyterLab |
| `wut deck [OUTPUT.pptx]` | Generates an editable fictional consulting-deck example |
| `wut diagram INPUT.mmd OUTPUT.svg` | Renders Mermaid through the private Node prefix |
| `wut render FILE [OUTPUT_DIR]` | Converts an Office document to PDF with headless LibreOffice |
| `wut ocr INPUT.pdf OUTPUT.pdf` | Deskews, rotates, and OCRs a PDF with OCRmyPDF |

Commands use `exec`, so signals and exit codes come from the underlying tool.

## Maintenance

### `wut setup [options]`

Re-runs setup from the persistent source at `~/.local/share/wutpack`. Existing
Homebrew packages are skipped; managed Python and Node packages are upgraded.

### `wut update [options]`

Downloads the current repository source and then re-runs setup. The same setup
options are accepted.

### Setup options

| Option | Meaning |
|---|---|
| `--host auto|codex|claude|both` | Select skill destinations; `auto` detects installed hosts |
| `--profile core|full` | Choose the lighter or maximal package layer |
| `--skills-only` | Refresh skills and the `wut` shim without package-manager work |
| `--skip-casks` | Omit LibreOffice, Chromium, Quarto, draw.io, and Inkscape |
| `--skip-ai-clis` | Omit Codex and Claude Code CLI installation |
| `--with-extras` | Add Ollama and Docker Desktop |
| `--dry-run` | Print package and filesystem actions without applying them |

## Environment overrides

These are primarily useful for testing or managed deployments:

| Variable | Default |
|---|---|
| `WUTPACK_INSTALL_ROOT` | `~/.local/share/wutpack` |
| `WUTPACK_STATE_ROOT` | `~/Library/Application Support/WutPack` |
| `WUTPACK_CACHE_ROOT` | `~/Library/Caches/WutPack` |
| `WUTPACK_BIN_DIR` | `~/.local/bin` |
| `WUTPACK_BRANCH` | `main` |
| `WUTPACK_REF` | unset; exact Git ref used by clean-runner verification |

`WUTPACK_TEST_ROOT` relocates all user-relative paths and exists for isolated
verification. It is not needed for a normal install.

See [getting started](getting-started.md), [workflow recipes](how-to-workflows.md),
[persistence design](why-persistent.md), or the [README](../README.md).
