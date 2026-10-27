# Scope contract

## Gather evidence first

Read the request, project instructions, relevant product documents, current behavior, nearby code, and recent decisions. Treat existing implementation as evidence of the current state, not as a requirement. Record contradictions instead of silently choosing a side.

Use `grilling` to pursue the next decision that could change behavior, constraints, cost, risk, or acceptance. Ask each round's frontier questions together, as `grilling` describes, and continue independent investigation while waiting. A scope is settled only when the remaining unknowns can safely be decided during implementation.

## Cover the decision surface

Capture:

- problem, trigger, and intended outcome;
- users or actors and their permissions;
- current behavior and desired behavior;
- happy path, meaningful variants, failures, and recovery;
- data created, read, changed, retained, or exposed;
- interfaces and systems affected;
- constraints, compatibility, rollout, and migration expectations;
- explicit exclusions;
- observable success, the target an expert would set for it, and the independent evidence that will prove it (from `grilling`'s depth pass);
- material risks;
- evidence, assumptions, and still-open questions.

Use domain modeling when unclear nouns, states, ownership, or transitions are causing ambiguity. Prefer concrete examples where abstract wording could hide different interpretations.

## Produce a durable scope

Write the scope in the project's canonical location. Link the evidence that explains current behavior. Preserve decisions and rationale; omit speculative implementation detail. Mark assumptions clearly and do not call the scope approved until Elias has explicitly confirmed the complete result.

The scope is ready for `to-spec` when an implementer would not need to make a new product decision. It is not ready while any unresolved question could produce meaningfully different user behavior.
