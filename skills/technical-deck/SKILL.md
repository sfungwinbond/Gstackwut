---
name: technical-deck
description: Create or edit technically rigorous PowerPoint diagrams using editable native PPTX shapes, connectors, charts, tables, and labels. Use for architecture and block diagrams, chip or die-stack diagrams, interfaces and buses, timing diagrams, memory maps, data flows, sequence diagrams, comparison slides, technical roadmaps, and engineering presentations that must open cleanly in Windows PowerPoint.
---

# Technical Deck

Produce a `.pptx` whose technical meaning is clear and whose primary elements remain editable.

## Workflow

1. Inspect the source deck, template, figures, tables, or datasheets. Preserve the theme when editing an existing deck.
2. Write the diagram model first: entities, boundaries, ports, relationships, direction, units, states, and the one conclusion the slide must communicate.
3. Use PptxGenJS for new shape-heavy decks and `python-pptx` for targeted edits. Start new work from `scripts/new_technical_deck.mjs`.
4. Read `references/patterns.md`, choose one diagram pattern, and place objects on a numeric grid. Put containers behind components, connectors behind labels, and route lines orthogonally.
5. Label measured, datasheet, calculated, and estimated values distinctly. Show assumptions and min/typ/max qualifiers.
6. Run `scripts/validate_pptx.py OUTPUT.pptx`.
7. Render through LibreOffice and inspect every slide. Fix clipping, overlap, tiny text, ambiguous arrows, and low contrast.

## Drawing Rules

- Default to widescreen 13.333 by 7.5 inches with a 0.35-inch safe margin.
- Use Windows-safe fonts. Keep body text at 14 pt or larger and labels at 11 pt or larger when practical.
- Use one semantic meaning per color and never rely on color alone.
- For die stacks, separate physical containment from logical connectivity and state whether work is per-die, broadcast, serialized, or parallel.
- For timing, share one time axis and align every transition.
- Keep diagrams editable. Do not flatten the entire slide into an image.
