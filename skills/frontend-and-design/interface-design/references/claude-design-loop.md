# Claude Design loop

Use Claude Design when the host offers the Design artifact type: a claude.ai canvas of live artboards that the agent writes directly. In Claude Code, the Artifact tool's quickstart with the `design` intent names the type. The canvas is where you and the user explore, compare, and approve screens; the project `DESIGN.md` remains the durable contract.

The Design type ships its own instructions for the canvas file format, design-system installation, and publishing. Follow them for mechanics. This reference covers only the design method around them.

## Checkpoint before external writes

Before creating or changing a canvas, confirm that `DESIGN.md` contains the product decision, journey, references, chosen direction, target devices, representative states, and acceptance criteria. Then tell the user:

- which canvas will be created or opened, and its name;
- which design system the canvas will use, or that its look comes from `DESIGN.md`;
- the proposed design-system summary: colour roles, fonts, geometry, density, and motion intent;
- what the first artboard group will demonstrate.

A new canvas is private to the user, but it is still a write to an external service. Wait for explicit confirmation unless the current request already authorizes that specific write.

## Start from the contract

1. Open the canvas recorded in the `DESIGN.md` exploration record, or create one canvas for this design effort. Record its link there immediately so a later session, in either agent, resumes the same canvas.
2. Choose the design system. Use a Claude Design design system when one fits the product or the user names one. Otherwise build the canvas look from the colour roles, typography, geometry, and density in `DESIGN.md`.
3. Keep `DESIGN.md` canonical. If the canvas or a design system Claude Design creates drifts from it, correct the canvas, or update `DESIGN.md` first when the user has approved a change of direction.

## Explore and iterate

Write every generation and edit request as [generator prompting](generator-prompting.md) describes. For a redesign of an existing screen, the first artboard or screen is a faithful reproduction of the current product, checked against its running surface, and variants derive from it.

1. Draw the primary journey first: one artboard per representative screen, with realistic content and the states from the screen matrix. Title each group of artboards on the canvas so the user can scan the flow.
2. When the journey itself is the question, link the artboards into a click-through prototype.
3. For a real unresolved choice, add a small set of labelled variant artboards side by side. Vary one or two explicit axes such as layout, density, typography, colour temperature, imagery, or signature interaction. Do not produce random alternatives or restart the direction for a local problem.
4. Compare each round against the reference set, product job, content priority, required states, responsive targets, accessibility requirements, and acceptance criteria. The Design type discourages rendering or re-reading the canvas to self-check, so compare from the artboards you wrote and from the user's review. Ask before any rendered check.
5. Invite the user to comment directly on artboards. Treat each comment as feedback: name the largest visible gap and make one material change per revision so the result stays diagnosable.
6. Repeat until the direction is coherent enough to carry into implementation. Keep the chosen artboards, rejected variants, unresolved questions, and feedback in the `DESIGN.md` exploration record.
7. Present the selected direction and remaining trade-offs. Explicit user approval is the sign-off that permits implementation; unresolved product or visual decisions stay open.

## Handoff

Artboards are visual evidence and a design reference, not production code. Carry the accepted tokens, hierarchy, states, content rules, responsive changes, and interaction rules into the project's own components and implementation contract. Then use `implement`, `ui-polish`, and `verify` on the real product surface.

Before handoff, confirm that `DESIGN.md` records the canvas link, accepted direction, rejected alternatives, open decisions, acceptance evidence, and user sign-off. If the direction changes materially during implementation, update `DESIGN.md` first and repeat the relevant part of the loop. Do not let an artboard silently become the new product decision.
