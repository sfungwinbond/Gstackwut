# PDF decision tree

1. `pdfinfo` fails: try `qpdf --check`, then `qpdf INPUT --replace-input` only on a copy.
2. Text selects correctly: use `pdftotext -layout` and compare reading order with a render.
3. Text is empty or gibberish: render at 300 DPI and run OCRmyPDF with deskew and rotation detection.
4. The PDF contains tables: try text extraction first, Camelot for ruled tables, and OCR plus manual validation for scans.
5. Fonts or symbols are wrong: inspect `pdffonts`; render to image for visual evidence and avoid claiming exact character recovery.
6. File opens on one platform only: normalize a copy with qpdf, then export through LibreOffice or Ghostscript if needed.
