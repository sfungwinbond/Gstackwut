---
name: technical-deck
description: Create or edit rigorous executive and technical PowerPoint diagrams using editable native PPTX shapes, connectors, charts, tables, and labels. Use for answer-first consulting decks, market maps, value cases, operating models, roadmaps, architecture and block diagrams, interfaces, timing or sequence diagrams, comparison slides, and presentations that must open cleanly in Windows PowerPoint.
---

# Technical Deck

Produce a `.pptx` whose decision or technical meaning is clear and whose primary elements remain editable.

## Workflow

1. Inspect the source deck, template, research, workbook, figures, and tables. Preserve the theme when editing an existing deck.
2. Write the diagram model first: decision question, takeaway, entities, boundaries, relationships, direction, units, states, and the one conclusion the slide must communicate.
3. Use PptxGenJS for new shape-heavy decks and `python-pptx` for targeted edits. Start new work from `scripts/new_technical_deck.mjs`.
4. Read `references/patterns.md`, choose one diagram pattern, and place objects on a numeric grid. Put containers behind components, connectors behind labels, and route lines orthogonally.
5. Label sourced, measured, calculated, estimated, and illustrative values distinctly. Show assumptions, units, scenario, and confidence qualifiers.
6. Run `scripts/validate_pptx.py OUTPUT.pptx`.
7. Render through LibreOffice and inspect every slide. Fix clipping, overlap, tiny text, ambiguous arrows, and low contrast.

## Drawing Rules

- Default to widescreen 13.333 by 7.5 inches with a 0.35-inch safe margin.
- Use Windows-safe fonts. Keep body text at 14 pt or larger and labels at 11 pt or larger when practical.
- Use answer-first slide titles; put exact values in tables and magnitude in native charts.
- Use one semantic meaning per color and never rely on color alone.
- For timing, share one time axis and align every transition.
- Keep diagrams editable. Do not flatten the entire slide into an image.

The bundled starter is a fully fictional three-slide market-entry, roadmap, and
value-case deck. Replace its illustrative entities and numbers with evidence from
the current task.
