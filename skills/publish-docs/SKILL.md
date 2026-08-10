---
name: publish-docs
description: Turn Markdown, notebooks, code, API docstrings, and analysis into maintainable HTML, PDF, Word, slide, site, or book output. Use for Quarto and Pandoc publishing, code-to-HTML documentation, MkDocs or Sphinx sites, notebook reports, tutorials, reference docs, and reproducible technical publications.
---

# Publish Docs

Keep the source maintainable and treat rendered files as build products.

## Workflow

1. Identify the reader and choose the output before choosing the engine.
2. Read `references/backend-selection.md` and use the smallest backend that supports the required citations, code execution, navigation, and formats.
3. Put narrative, code, figures, and citations under source control. Use relative links and stable asset paths.
4. Make code execution deterministic. Pin environments, seed randomness, and separate expensive data preparation from rendering.
5. Build every requested format. Inspect HTML links, PDF pagination, Word styles, and code-cell output.
6. Add one discoverable entry point and commands that reproduce the build.

## Quality Gate

- Reach a visible result within three tutorial steps.
- Keep tutorial, how-to, reference, and explanation content distinct.
- Test every copy-paste command.
- Check local links and missing assets.
- State which artifacts are source and which are generated.
