---
name: spreadsheet-lab
description: Create, edit, audit, chart, and repair Excel workbooks while preserving formulas, styles, merged cells, print settings, and Windows Excel compatibility. Use for .xlsx and .xlsm analysis, financial or engineering models, comparison tables, chart tabs, formula checks, recalculation, and workbook normalization.
---

# Spreadsheet Lab

Treat the workbook as a model with presentation, not a bag of cells.

## Workflow

1. Inspect workbook structure, defined names, formulas, charts, external links, merged cells, hidden sheets, and protection before editing.
2. Identify inputs, calculations, outputs, units, and source notes. Preserve unknown content unless the user asks to replace it.
3. Use `openpyxl` for targeted edits to an existing workbook and XlsxWriter for new report-style workbooks. Keep macros only with a macro-preserving path.
4. Put exact data in tables and use native Excel charts for comparisons. Use a common scale, meaningful units, and source/assumption notes.
5. Never treat cached formula values as fresh calculations. Recalculate with LibreOffice when formulas change.
6. Run `scripts/validate_xlsx.py OUTPUT.xlsx`, then open/save or export through LibreOffice for Windows-critical delivery.

Read `references/compatibility.md` before editing charts, formulas, macros, or files that previously failed to open in Windows.

## Quality Gate

- Confirm sheet names, dimensions, formulas, charts, and relationship targets.
- Make estimates visually distinct from sourced or calculated values.
- Check for `#REF!`, broken external links, silently converted dates, and text-formatted numbers.
- Deliver a new file unless overwrite was explicitly requested.
