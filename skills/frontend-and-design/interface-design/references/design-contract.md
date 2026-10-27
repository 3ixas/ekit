# Design contract

Create this file in the project that is being designed. It is the durable record of the approved design direction and is the input to the screen exploration loop in Claude Design or Stitch. Keep product decisions here; keep personal skill instructions in the agent-skills repository.

```md
# DESIGN.md

## Product and decision

- Product or feature:
- Problem and user:
- Design decision this work must settle:
- Primary job and audience:
- Primary journey:
- Success looks like:

## Scope

- Surfaces and screens:
- Target devices and responsive range:
- Included states:
- Explicitly excluded:
- Technical or product constraints:
- Real content or asset requirements:
- Brand assets (logo, marks, fonts) and where each must render:

## References

For every selected reference, record the URL or local path, what it contributes, and what must not be copied.

| Reference | Role and useful evidence | Carry over | Do not carry over |
|---|---|---|---|
|  |  |  |  |

## Design DNA

- Content priority and reading path:
- Layout, grid, rhythm, and density:
- Typography roles:
- Colour roles:
- Surfaces, borders, shadows, and radii:
- Components and interaction feedback:
- Icon family (one, already installed where possible):
- Motion purpose and pacing:
- Platform and accessibility assumptions:

## Interface copy

- Voice, in one line, and words to avoid:
- Actions: buttons name the action ("Save changes", "Delete project"), never "Submit" or "OK" where a verb exists:
- Errors: what happened, why in one clause, and the fix, next to the field that caused it:
- Empty states: name the emptiness, say why it is empty, offer one next action:
- Loading and progress: say what is happening ("Uploading 3 of 8 files"), never an unprovable promise:

## Direction

- Chosen direction:
- Product-specific signature:
- Anti-goals and generic defaults to avoid:
- Why this direction fits the product and references:
- Alternatives considered and rejected:

## Screens and states

For each screen, state the user decision it supports and the states it must show.

| Screen | User decision | Empty | Loading | Error | Success | Other states |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |

## Exploration record

- Service (Claude Design or Stitch):
- Canvas or project link:
- Design system:
- Screens, artboards, or variants:
- Chosen direction:
- Rejected directions and why:
- Exploration trail (one line per options round: options and axes, choice, why the others lost):
- Remaining open decisions:
- Last reviewed:

## Acceptance and sign-off

- Acceptance criteria:
- Evidence reviewed:
- User feedback and required changes:
- User sign-off:
- Signed off on:

## Implementation handoff

- Approved tokens and component rules:
- Responsive changes:
- Accessibility requirements:
- Motion and reduced-motion requirements:
- Acceptance evidence:
- Links to the approved screens or screenshots:

### Redesign preservation (when changing an existing surface)

- Affected routes and representative states:
- Inventory or linked baseline: facts/copy, links, forms/fields, actions/effects, test and analytics hooks:
- Authorized changes and what must stay:
- Interaction checks and expected outcomes:
- Before/after comparison, intentional differences and unverified behaviour:

### Visual implementation plan (when a concept depends on specific materials)

| Region or signature detail | Medium and reason | Actual asset source or missing asset | Responsive/accessibility treatment | Change from approved concept and why |
|---|---|---|---|---|
|  |  |  |  |  |
```

Record real values (sizes, weights, colours, spacing, radii). A value taken from a screenshot or reference rather than from source or a design file is marked as an estimate; never invent one to complete the table. Keep the file short enough to read in one sitting.

For redesigns, follow [redesign preservation](redesign-preservation.md). For a visual concept whose character depends on imagery, texture or a distinctive interaction, plan only those important regions before implementation. Choose semantic code for essential text, controls, live data and reflowing layout; choose CSS, SVG, canvas, raster or other assets by purpose, accessibility, responsiveness and measured cost. Record a supplied asset, licensed source, authorized generation plan, or an honest gap. Do not quietly replace an approved photograph, illustration, texture or interaction with a simpler substitute; explain the trade-off and update the contract, returning a material change in direction to the user. This plan is independently written, informed by Hallmark's medium inventory; it imports no blanket ban on illustrations or CSS textures and requires no new generator or paid service. Small settled edits omit these optional sections.

The file can be shorter for a small surface. Substantial work should not proceed to implementation until the reference set, primary journey, required states, chosen direction, acceptance criteria, and user sign-off are recorded. If exploration is skipped, record the reason and the evidence supporting that decision. Projects created before this template may still have a `Stitch exploration record` heading; treat it as the exploration record.

## Taste decisions when used

Record page versus app branch; subject inventory and section claims/evidence for websites; main question, finding and next action for each app screen; data reconciliation assumptions; actual asset availability; selected direction/style and seed; product-specific signature; and intentional exceptions with reasons. Link the supporting `.taste-skill/` sheet and policy. Approved tokens and behaviour here govern those generated records, not the reverse. In mixed website/app projects keep shared identity but separate composition and work-screen requirements.
