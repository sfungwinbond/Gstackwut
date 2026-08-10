# Getting started

This tutorial starts with a fresh macOS account and ends with a visible,
validated artifact. WutPack supports Codex and Claude Code; you need at least one
of them installed or installable.

## 1. Install the workbench

```bash
curl -fsSL https://raw.githubusercontent.com/sfungwinbond/Gstackwut/main/install.sh | bash
```

The installer may ask for normal Homebrew authorization. It does not ask for API
keys or copy credentials. Open a new terminal when it finishes.

On Apple silicon, setup uses native Homebrew under `/opt/homebrew`, even when an
older Intel installation is earlier on `PATH`. It refreshes Homebrew before
installing packages and retries cask-definition compatibility failures once.

For a smaller first pass:

```bash
git clone https://github.com/sfungwinbond/Gstackwut.git
cd Gstackwut
./setup --profile core
```

## 2. Check the result

```bash
wut doctor
wut routes
```

`doctor` prints the path of each major tool and reports missing layers. `routes`
shows the specialist to use for each kind of work.

## 3. Create an editable PowerPoint artifact

```bash
wut deck first-executive-roadmap.pptx
wut render first-executive-roadmap.pptx ./rendered
```

Open the deck in PowerPoint or LibreOffice Impress. Its components are native
shapes, connectors, text, and charts rather than one flattened screenshot. The
PDF in `rendered/` is an independent layout check.

## 4. Ask through your agent

In Codex:

```text
$technical-deck Turn the fictional market-entry scorecard into an answer-first
executive deck with a where-to-play matrix, value case, and 12-month roadmap.
Keep every element editable and render-check the result.
```

In Claude Code:

```text
/technical-deck Turn the fictional market-entry scorecard into an answer-first
executive deck with a where-to-play matrix, value case, and 12-month roadmap.
Keep every element editable and render-check the result.
```

Skills can also be selected automatically from natural-language requests. An
explicit name is useful when you want a particular workflow or quality gate.

## 5. Try the data environment

```bash
wut python skills/data-lab/scripts/profile_table.py examples/market-entry-scorecard.csv
wut lab
```

The first command produces a deterministic schema and missingness report. The
second opens JupyterLab from the managed knowledge environment.

Next: use the [workflow recipes](how-to-workflows.md), scan the [command reference](commands.md),
or read [why the tools persist](why-persistent.md). Return to the [README](../README.md).
