# Word compatibility notes

- `python-docx` does not expose every Word feature. Treat tracked changes, content controls, fields, and complex drawing layers as preservation-sensitive.
- Pandoc prioritizes semantic structure over pixel-identical layout.
- LibreOffice is useful for normalization and rendering, but may alter advanced Word-only features.
- Use a reference DOCX with named styles when exact organizational formatting matters.
- Never promise preservation of macros or signatures without a format-specific test.
