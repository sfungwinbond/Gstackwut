# Excel compatibility notes

- `openpyxl` reads and writes formulas but does not calculate them. Use LibreOffice or Excel to refresh cached values.
- Preserve VBA with `keep_vba=True`; do not rename `.xlsm` to `.xlsx`.
- Prefer built-in chart types and fonts available on Windows.
- Avoid manually splicing OOXML unless a library cannot express the change.
- After a manual OOXML change, validate ZIP members and relationship targets, then normalize with LibreOffice.
- Store percentages as numeric fractions with percentage number formats. Store dates as dates, not localized strings.
- Use absolute references intentionally and check that inserted rows or columns did not shift model ranges.
