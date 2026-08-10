---
name: system-diagram
description: Turn a system description into a source-controlled architecture, flow, sequence, state, dependency, network, or circuit diagram with an editable source and rendered SVG or PNG. Use for Mermaid, Graphviz, PlantUML, Schemdraw, block diagrams, data flows, service maps, and documentation diagrams outside PowerPoint.
---

# System Diagram

Deliver the diagram source with the render.

## Workflow

1. List entities, boundaries, relationships, direction, cardinality, trust zones, and the one point the diagram must explain.
2. Read `references/tool-selection.md` and choose one notation.
3. Build a coarse layout before adding labels. Prefer left-to-right flow, short orthogonal edges, and visible system boundaries.
4. Use exact interface names and distinguish synchronous, asynchronous, optional, and failure paths.
5. Run `scripts/render_diagram.sh SOURCE OUTPUT`.
6. Inspect the render at normal reading size. Fix crossings, clipped labels, weak contrast, and ambiguous arrow direction.

## Quality Gate

- Keep the editable source beside the render.
- Include a legend only when conventions are not obvious.
- Do not use decorative icons in place of precise labels.
- Split diagrams that need more than one reading order.
