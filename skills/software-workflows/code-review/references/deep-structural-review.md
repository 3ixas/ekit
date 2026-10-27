# Deep structural review

Read only for a selected deep review or an evidence-based escalation. This is a method within the Standards axis, not another reviewer or implementation stage.

## Investigate the simpler shape

1. Trace the changed flow through its real owners, callers, state transitions, and contracts. Read enough surrounding code to understand constraints; leave unrelated legacy cleanup outside the review.
2. Identify the source of reader load: duplicated decisions, competing state representations, responsibility split across layers, unnecessary delegation, or orchestration that obscures invariants.
3. Develop a concrete alternative using the repository's existing concepts and utilities. Describe the proposed ownership and flow, and which branches, flags, wrappers, or concepts disappear. Relocating the same complexity without reducing it is not sufficient.
4. Check the alternative against requirements and callers. Account for errors, lifecycle, ordering, partial updates, compatibility, and observability where affected. Parallel execution needs evidence of independence; a boundary validation may legitimately require optional values or unknown input. Simpler-looking code that changes these semantics is not an equivalent remedy.
5. Classify the result. A demonstrated regression has an identifiable consequence in this change. A beneficial alternative without such a regression is an optional improvement, even if substantial. Omit proposals that cannot be grounded beyond personal preference.

## Report and stop

For each material structural finding or optional proposal, give the file/hunk, current cost, concrete alternative, complexity removed, and the behaviour-preservation evidence needed (for example, caller compatibility checks or state-transition tests). Distinguish evidence already observed from checks still needed; do not claim equivalence from a sketch alone.

Keep findings concise and within Standards; the Spec reviewer retains requirements and acceptance-proof ownership. Respect documented repository conventions. File size is a clue to cohesion, never an independent approval threshold unless the repository explicitly makes it one.

Do not edit code or broaden the approved implementation scope. When the useful next step requires a wider review, name the unreviewed area and provide a specific `code-review` invocation with its target checkout, fixed base, and broader area. A redesign proposal is not permission to implement it.

## Source

Independently written adaptation of Cursor's [thermo-nuclear-code-quality-review](https://github.com/cursor/plugins/blob/190d28736eff128ec94f502a22c7fe0c4b56cd37/cursor-team-kit/skills/thermo-nuclear-code-quality-review/SKILL.md), MIT, Copyright (c) 2026 Cursor. The owned version replaces automatic size/simplification blockers with evidence-based findings and preserves read-only review authority. See repository `licenses/mit-cursor-team-kit.txt`.
