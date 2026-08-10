---
name: document-studio
description: Create, edit, inspect, and convert professional Word and OpenDocument files while preserving headings, tables, lists, page layout, styles, images, and document structure. Use for .docx or .odt reports, memos, specifications, templates, mail merges, conversions, and compatibility repairs.
---

# Document Studio

Build the document from named styles and semantic structure.

## Workflow

1. Inspect the existing styles, sections, headers, footers, tables, media, comments, and relationships before editing.
2. Use `python-docx` for targeted `.docx` edits, Pandoc for structure-first conversion, and LibreOffice for normalization and render checks.
3. Apply named paragraph and character styles instead of local formatting. Use real headings, lists, captions, and table headers.
4. Preserve sections and page breaks intentionally. Embed media and use alt text when the library supports it.
5. Convert to PDF and inspect every page. Check widows, orphan headings, table splits, clipped images, and missing fonts.
6. Deliver a new file unless overwrite was requested.

Read `references/word-compatibility.md` before changing complex layouts, tracked changes, fields, or macros.

## Quality Gate

- Keep heading levels in order.
- Verify table width and repeat header rows across pages.
- Use Windows-safe fonts for cross-platform delivery.
- State when a library cannot preserve tracked changes or advanced Word fields.
