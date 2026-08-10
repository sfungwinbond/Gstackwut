---
name: pdf-forensics
description: Inspect, extract, OCR, compare, repair, split, merge, and normalize PDF files with evidence about what changed. Use for scanned PDFs, broken PDFs, datasheets, table extraction, searchable-PDF creation, metadata inspection, page rendering, and PDF-to-text or PDF-to-image workflows.
---

# PDF Forensics

Diagnose the PDF before choosing a tool.

## Workflow

1. Run `scripts/pdf_report.sh INPUT.pdf` to inspect page count, encryption, metadata, fonts, images, and structural warnings.
2. Determine whether each page has a usable text layer. Use `pdftotext` for digital text, `pdfimages` for embedded raster assets, and OCRmyPDF for scanned pages.
3. Use `qpdf` for structural repair, encryption changes, page selection, and linearization. Use `mutool` for rendering or object-level inspection.
4. Extract tables with Camelot only when ruled lines or stable geometry support it. Validate every row against the rendered page.
5. Write a derivative file by default. Preserve the original and record the commands used.
6. Re-run the report, render representative pages, and compare page count and visible content.

Read `references/decision-tree.md` when extraction quality is uncertain.

## Quality Gate

- Never assume successful text extraction means correct reading order.
- Do not OCR an already-good text layer unless there is a specific reason.
- Preserve page size, rotation, bookmarks, and metadata when they matter.
- State any pages or tables that still require human verification.
