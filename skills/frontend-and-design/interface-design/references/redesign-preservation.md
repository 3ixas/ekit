# Preserve behaviour through a redesign

Use when restructuring an existing interface or substantially changing its visual system. Independently written, informed by Hallmark's redesign inventory, with behaviour verified through the project's own checks. `interface-design` owns scope and handoff, `ui-polish` applies this during scoped refinement, and `verify` proves the resulting interactions.

## Before editing

Inspect the affected routes, source and representative rendered states. In the project's `DESIGN.md` handoff, or a linked project verification record, capture the relevant items:

- Facts and copy that must remain, including prices, dates, names, claims, consent and legal text.
- Navigation destinations and route parameters; forms, field names, validation, submission destinations and expected effects.
- Controls and handlers, including success, failure, retry, cancellation and persistence behaviour where reachable.
- IDs, test hooks and analytics events used by tests or other code; shared components or data boundaries the view relies on.
- What the task authorizes changing and what stays fixed. Reference existing tests and baseline evidence rather than duplicating them.

Keep this proportional to the affected surface. A small settled spacing or colour edit needs only its relevant behaviour check, not a full inventory or new design ceremony. Reuse existing project records, preserve unrelated working changes, and never require a clean tree merely to begin. Do not capture credentials or personal form contents in evidence.

## After editing

Compare the same routes and states with the baseline. Account for removed or changed inventory items; restore accidental losses and explain intentional changes within the authorized scope. Update the record when an approved product change alters the expected behaviour.

Use the project's existing interaction tests and permitted browser tools to exercise affected actions. Check the actual effect: submission reaches the intended boundary, saved state persists, navigation reaches the right destination, and failure or cancellation behaves as specified. Use test data and mocks where appropriate; a visual task does not authorize real messages, charges or other external commitments.

A text or DOM inventory is a clue, not proof of equivalence. An unchanged handler name can hide a removed request; an equivalent rename can look like a loss. Judge intentional refactors by behaviour, not exact identifier matching. Screenshots establish appearance, not successful submission or persistence. Report unavailable checks and unresolved behaviour instead of claiming preservation from a clean diff.
