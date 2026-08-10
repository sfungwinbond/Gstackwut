# Technical Diagram Patterns

## Answer-First Executive Slide

- State the decision or implication in the title, not merely the topic.
- Put the primary evidence in one visual and reserve a side panel for the action.
- Keep model basis, source status, and scenario qualifiers visible.
- Use a table for exact values and a native chart for relative magnitude.

## Market Map or Two-by-Two

- Name both axes and show which direction is favorable.
- Explain bubble size, color, and score; avoid implied precision without a basis.
- Put candidates into decision-oriented quadrants such as prioritize, test, build,
  or deprioritize.
- Pair the matrix with a ranked recommendation and explicit gating criteria.

## Transformation Roadmap

- Use columns for time horizons or phases and rows for accountable workstreams.
- Put an owner and an observable deliverable on every initiative.
- Show funding or scale gates as milestones with named evidence requirements.
- Separate mobilize, prove, and scale so activity is not mistaken for realized value.

## System or SoC Architecture

- Put the system boundary in a pale container.
- Arrange sources/controllers left, processing center, and storage/sinks right.
- Expose named ports on component edges; label buses once near the line.
- Use lane headers for clock, power, security, software, or physical domains.
- Add one callout stating the design consequence or bottleneck.

## Chip, Package, and Multi-Die Stack

- Nest package → dies → banks/planes using progressively lighter containers.
- Draw physical stacking vertically and logical command/data paths separately.
- Label die count, density per die, aggregate density, and shared resources.
- Mark operations as per-die, broadcast, serialized, interleaved, or parallel.
- Show uncertainty or die-to-die variance beside modeled aggregate timing.

## Interface or Data Flow

- Lay out the happy path left-to-right; put retries/errors below it.
- Label arrow payloads and protocols, not just endpoints.
- Put trust, process, or network boundaries behind the nodes they contain.
- Use numbered steps only when order is essential.

## Sequence Diagram

- Use equal-width actor columns and vertical lifelines.
- Keep time downward. Draw calls solid and returns dashed.
- Use activation bars only where execution ownership matters.
- Put alternate/error paths in labeled frames.

## Timing or Waveform

- Share one horizontal time grid across every signal.
- Draw digital transitions as separate editable line segments.
- Use overbars or `#` suffixes consistently for active-low signals.
- Shade setup/hold or busy intervals lightly and label their limits.
- State voltage, temperature, clock mode, and min/typ/max basis in the note.

## Memory or Register Map

- Use a vertical address axis with hexadecimal boundaries.
- Make region height proportional only when scale aids understanding; otherwise
  mark the map as not to scale.
- Show reserved gaps and access type (`RO`, `RW`, `W1C`) explicitly.
- For bitfields, align bit numbers and group related flags with a light band.

## Comparison or Trade Study

- Use a table for exact values and a chart for magnitude.
- Keep scales identical across products and densities.
- Separate datasheet values from modeled or margin-adjusted values.
- Include assumptions, units, and the decision implication in a callout.

## Review Checklist

- Can a reader state the main conclusion in five seconds?
- Are every arrow's direction and meaning unambiguous?
- Are units, conditions, sources, and uncertainty visible?
- Are all primary elements editable native PowerPoint objects?
- Does the slide remain legible when printed or viewed at 100%?
