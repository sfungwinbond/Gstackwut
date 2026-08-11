# Command reference

`wut` is a stable entry point into the managed workbench. Run `wut help` for the
same summary in a terminal.

## Inspection

| Command | Behavior |
|---|---|
| `wut doctor` | Checks core binaries, managed deck/diagram dependencies, installed source and all 30 toolpacks, Python environments, and complete host skill sets |
| `wut doctor --headless` | Runs the same check without requiring a desktop LibreOffice installation |
| `wut paths` | Prints source, state, cache, Python, and Node locations |
| `wut skills` | Lists installed specialists and their trigger descriptions |
| `wut routes` | Maps common scenarios to specialist names |
| `wut packs [CATEGORY]` | Lists all 30 career toolpacks or the profession, finance, or engineering category |
| `wut pack NAME [ACTION]` | Shows a profession pack, prints its tools or prompt, or launches interactive Codex |
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

## Profession toolpacks

```bash
wut packs
wut packs finance
wut packs engineering
wut pack pathology tools
wut pack pathology prompt "Map a de-identified specimen workflow."
wut pack pathology codex "Map a de-identified specimen workflow."
```

The available categories are `profession`, `finance`, and `engineering`; the
available actions are `show` (the default), `tools`, `prompt`, and `codex`.
Only the explicit `codex` action launches an agent; it uses the normal interactive
Codex authentication and permission flow. See the
[selection methodology and safety boundaries](profession-packs.md).

## Website proof gallery

The public gallery is generated from real local tool runs. Rebuild all 53 proof
pages and make one authenticated, read-only Codex call with:

```bash
wut python tools/build_tool_gallery.py --real-ai
```

Claude Code is deliberately recorded as installed-only and is never invoked by
the gallery builder. To reproduce the site without another model call, pass a
previously schema-validated Codex result with `--codex-result FILE`. Validate
the generated links, layouts, media, and responsive behavior with:

```bash
wut python tools/check_tool_gallery.py
```

## Maintenance

### `wut setup [options]`

Re-runs setup from the persistent source at `~/.local/share/wutpack`. Existing
Homebrew packages are skipped; managed Python and Node packages are upgraded.

### `wut update [options]`

Downloads and validates the current repository source, stages it beside the
installed tree, and swaps it into place under a per-install lock before
re-running setup. A failed activation restores the previous source; once a
valid source is active, it remains available for repair even if setup does not
complete. The same setup options are accepted, and `--dry-run` does not activate
the downloaded source.

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
