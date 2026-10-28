---
name: interface-design
description: Design a substantial new product interface or visual direction, or redesign an existing one, from product intent and references through user-approved direction and rendered verification. For focused craft in an established interface, use ui-polish.
---

# Interface Design

## Outcome

A user-approved direction grounded in the product and references, recorded in `DESIGN.md`, and verified on the implemented surface.

## Choose the path

Use this workflow for a new product surface, a new visual direction or a substantial redesign. For a small settled change, use the existing design system; focused craft in a coherent interface belongs to `ui-polish`. Use `grill-with-docs` for unsettled product behaviour or information architecture, `wayfinder` for an uncertain route to a known destination, and `prototype` for a focused experiment.

## Method

1. **Frame.** Establish the audience, job, journey, platform, constraints and success. For an existing surface inspect the running interface and its source; for a redesign follow [redesign preservation](references/redesign-preservation.md) and carry its baseline into verification.
2. **Find direction.** Discuss open decisions with the user; use `grilling` when exhaustive exploration is warranted or requested. Build a small reference set with distinct jobs and record what each contributes and what must not be copied; use [reference-led design](references/reference-led-design.md) and, when examples or components are missing, [reference sources](references/reference-sources.md). A connected library is optional: use focused searches when they help, record source and query, and protect private details. For web motion, consult `motion` when useful. When it helps an unresolved website or web-app design decision, consult the relevant [Taste toolkit](references/taste-toolkit.md) branch; use its draw only when it helps broaden that decision. Ground the direction in real content, product needs and reachable states.
3. **Explore the decision.** For an unresolved consequential visual decision, use an options round: show three concrete visual directions side by side on named axes, with their references and a recommendation; include a stretch where appropriate. The user can choose, combine or reject them; develop the selection. Reuse this round when it answers the screen decision too. Run another only for a distinct unresolved decision. Explain consequential trade-offs and compare against the product job, references, states, responsive targets and accessibility; distinguish user feedback from usability evidence.
4. **Record the direction.** Create or update `DESIGN.md` using the minimum in [design contract](references/design-contract.md); add conditional details as needed. Record the selected direction and exploration trail, and obtain the user's approval of new or materially changed consequential visual decisions before implementation; retain an existing approval when the direction is unchanged. Do not invent content, proof or brand assets.
5. **Make the direction inspectable.** Select the cheapest surface that can answer the remaining question: sketches, a local prototype, or an existing or user-named exploration service. When Claude Design or Stitch is useful and available, use its [Claude Design loop](references/claude-design-loop.md) or [Stitch loop](references/stitch-loop.md); follow [generator prompting](references/generator-prompting.md) when generating screens. Before an external write, identify what will be sent or changed and obtain confirmation unless the request already authorizes that specific write. If a service is unavailable or skipped, use a local alternative and record the reason and any unverified states. Do not claim sketches or user-reviewed artboards are a rendered check.
6. **Critique and approve.** Inspect the rendered direction at representative sizes and states where possible using [screenshot critique](references/screenshot-critique.md); use its shared checks and the appropriate website or app lens. Check [AI-default patterns](references/ai-default-patterns.md) against the product and approved direction, not as a ban list. Fix material problems before presenting a new or materially changed direction, record remaining gaps and obtain sign-off; retain existing approval when the direction is unchanged. If rendering is unavailable, disclose the gap and use the best available evidence; do not claim it passed.
7. **Hand off and verify.** Carry the approved direction, states, accessibility and motion requirements into project-owned components. Add a short project-instruction pointer to `DESIGN.md` after approval. Use `implement`, relevant specialists and `verify` to check the real interface and interactions at representative sizes and states. For web surfaces used on phones, include `ui-polish`'s mobile-web mode and actual iOS Safari evidence. If the direction changes materially, update the contract and repeat the affected decision and approval.

## Boundaries

`DESIGN.md` is the durable project contract; service design systems and generated screens follow it. Exploration is evidence, not production code by default. Preserve approved design decisions and existing behaviour unless the task authorizes changing them. A skill or reference does not authorize external writes, paid actions or disclosure of private data.

## Owned source methods

Open these snapshots only for their specific method; the owned steps above govern.

- [source-3-skill](references/source-methods/source-3-skill.md): source design workflow.
- [source-4-web-design-guidelines](references/source-methods/source-4-web-design-guidelines.md): source web interface guidance.
