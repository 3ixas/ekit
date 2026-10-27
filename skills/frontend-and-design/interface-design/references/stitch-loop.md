# Stitch loop

Follow this loop when the exploration-surface step selects Stitch. Confirm the current host exposes each named capability; use its documented equivalent when tool names differ, and report missing capabilities rather than guessing a call.

Use Google Stitch as the visual design workspace for substantial new interface direction, multi-screen flows, or redesigns where layout, hierarchy, or the design system still needs evidence. The project `DESIGN.md` remains the durable contract; Stitch is where the team explores, compares, and records visual decisions.

## Checkpoint before external writes

Before creating or changing a Stitch project, confirm that `DESIGN.md` contains the product decision, journey, references, chosen direction, target devices, representative states, and acceptance criteria. Then tell the user:

- which Stitch project will be created or opened;
- which `DESIGN.md` and any other assets will be uploaded;
- the proposed design-system summary: colour roles, fonts, geometry, density, and motion intent;
- what the first screen group will demonstrate.

Wait for explicit confirmation before the external upload or project/design-system mutation unless the current request already authorizes that specific write. If the user chooses to skip Stitch, record the reason and the written direction in `DESIGN.md` before implementation.

## Start from the contract

1. Create or open the Stitch project for the product. Prefer the project identifier in `.stitch/metadata.json`; after a new project or screen, persist the project, design-system, and screen identifiers there so a later session can resume.
2. Upload the approved `DESIGN.md`.
3. Create or update the Stitch design system from the uploaded document, then inspect the generated tokens and correct any mismatch with the written direction.

Use the Stitch MCP in this order: `upload_design_md`, then `create_design_system_from_design_md`. The design system must exist before generating screens so that screens are evaluated against one coherent foundation. When extending an existing interface, inspect representative existing screens first and preserve useful incumbent decisions deliberately.

## Explore and iterate

Write every generation and edit request as [generator prompting](generator-prompting.md) describes. For a redesign of an existing screen, the first artboard or screen is a faithful reproduction of the current product, checked against its running surface, and variants derive from it.

1. Generate a representative first screen or screen group from the primary journey, using realistic content and the approved design system. Describe the structure and interaction; let the design system supply the tokens.
2. If a meaningful design question remains, generate a small set of labelled variants. Vary one or two explicit axes such as layout, density, typography, colour temperature, imagery, or signature interaction. Do not request random alternatives or restart the whole direction for a local problem.
3. Compare screens against the reference set, the product job, content priority, required states, responsive targets, accessibility requirements, and the acceptance criteria in `DESIGN.md`.
4. Make focused edits that name the largest visible gap and the intended correction. Prefer one material change per iteration so the result remains diagnosable.
5. Repeat the compare-and-edit loop until the direction is coherent enough to carry into implementation. Keep the chosen direction, rejected alternatives, unresolved questions, feedback, and Stitch links or screenshots in `DESIGN.md`.
6. Present the selected direction and remaining trade-offs to the user. Treat explicit user approval as the sign-off that permits implementation; unresolved product or visual decisions stay open.

Use `generate_screen_from_text` for the first screen, `generate_variants` for bounded alternatives, `edit_screens` for focused corrections, and `get_project` or `get_screen` to inspect the result. Use `apply_design_system` when an existing group of screens needs to be brought back to the accepted foundation. Use `extract-design-md` or the equivalent source inspection path when an existing codebase needs its current visual language documented before redesign.

## Handoff

Stitch output is visual evidence and a design reference. Do not treat generated HTML as production code by default. Carry the accepted tokens, hierarchy, states, content rules, responsive changes, and interaction rules into the project's components and implementation contract. Then use `implement`, `ui-polish`, and `verify` on the real product surface.

Before handoff, confirm that `DESIGN.md` records the accepted direction, rejected alternatives, open decisions, acceptance evidence, and user sign-off. If the direction changes materially during implementation, update `DESIGN.md` first and repeat the relevant part of the loop. Do not allow a Stitch screen to silently become the new product decision.
