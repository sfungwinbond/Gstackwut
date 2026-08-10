# Knowledge-work recipes

These recipes are starting prompts, not rigid forms. Replace paths, outputs, and
decision criteria with the real task.

## Turn PDFs into a cited comparison workbook

1. Put the original PDFs in one input folder and leave them unchanged.
2. Ask `pdf-forensics` to classify their text layers and extract the relevant
   tables with page-level provenance.
3. Ask `spreadsheet-lab` to build the model and perform a compatibility pass.

```text
$pdf-forensics Inspect inputs/*.pdf. Extract market size, growth, margins,
customer segments, methodology, publication date, and page number. Flag OCR or
table cells that require visual confirmation. Save structured CSV plus notes.

$spreadsheet-lab Turn the extraction into market_entry.xlsx. Put raw evidence,
assumptions, calculations, scenarios, and charts on separate tabs. Make uncertain
estimates visually distinct, add source notes, validate relationships, recalculate
with LibreOffice, and render every sheet for inspection.
```

Why split it: extraction confidence and workbook logic are different review
problems. Keeping an evidence table prevents a polished chart from hiding a weak
source.

## Build an editable executive deck

```text
$technical-deck Read market_entry.xlsx and the source PDFs. Create a seven-slide
executive deck: recommendation, market attractiveness, ability to win, scenario
economics, value levers, implementation roadmap, and risks. Use native PowerPoint
objects, mark estimates, validate the package, and render-check every slide.
```

The starter script under `skills/technical-deck/scripts/` demonstrates an
answer-first matrix, roadmap, exact-value table, notes, and a native chart. The
downloadable [fictional example deck](../examples/executive-consulting-demo.pptx)
is its output.

## Research a tool or vendor decision

```text
$research-brief Compare three candidate tools for our documented requirements.
Use current official documentation and primary benchmarks where available.
Separate verified facts, calculations, inferences, and recommendations; include
dates, conflicts, switching costs, and the evidence that would change the choice.
```

The useful output is a decision aid: recommendation first, sources beside claims,
and uncertainty that a reviewer can interrogate.

## Analyze tabular data without losing reproducibility

```text
$data-lab Analyze events.parquet. Preserve the raw file, profile schema and
missingness, define the observation grain, check time leakage, compare against a
simple baseline, and produce a parameterized notebook plus exact summary tables.
```

Start outside the agent if useful:

```bash
wut python skills/data-lab/scripts/profile_table.py events.parquet
wut lab
```

## Publish code and notebooks as HTML

```text
$publish-docs Build a documentation site from this repository. Include one
beginner tutorial, task-oriented how-tos, generated API reference, and an
architecture explanation. Test local links and make the complete build one
command. Use Quarto only if notebook execution or multi-format output requires it.
```

The specialist chooses among Quarto, MkDocs, Sphinx, pdoc, Doxygen, JSDoc,
TypeDoc, and Pandoc based on source and output—not fashion.

## Move a code change through quality gates

```text
$code-build Implement the requested change with focused tests and no unrelated
cleanup.

$debug-lab Reproduce and root-cause the remaining failure; do not guess.

$review-gate Review the final diff for correctness, compatibility, and missing
tests. Report actionable findings only.

$ship-check Check the exact artifact and release state. Stop before external
publication unless I explicitly authorize it.
```

Each specialist has a narrow responsibility, so “build,” “debug,” “review,” and
“release” do not collapse into one opaque leap.

See [getting started](getting-started.md), the [command reference](commands.md),
[persistence design](why-persistent.md), or the [README](../README.md).
