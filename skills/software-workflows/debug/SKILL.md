---
name: debug
description: Diagnose and fix unexpected software behaviour through reproduction, causal evidence, root-cause correction, and regression proof. Use when the cause of a bug is not yet known.
---

# Debug

## Outcome

A reproduced failure, supported causal chain, focused correction, and evidence that the failure is gone.

## Method

1. Establish the environment, expected behaviour, and observed symptom. Capture a reproducer and its result; if reproduction is blocked, name the missing evidence rather than asserting a cause.
2. Localize with logs, data, history, and instrumentation. Write falsifiable hypotheses and test the riskiest fact; after repeated failed fixes, revisit the premise before trying another patch.
3. Correct the supported cause within scope. Re-run the reproducer, check relevant sibling cases, and report before/after evidence and remaining uncertainty.

Read [references/causal-debugging.md](references/causal-debugging.md) for intermittent, multi-layer, production-only, or repeatedly misdiagnosed failures.

## Boundaries

Do not replace diagnosis with defensive guards or unrelated cleanup. State inaccessible evidence precisely.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [matt-diagnosing-bugs](references/source-methods/matt-diagnosing-bugs.md)
- [pstack-poteto-mode](references/source-methods/pstack-poteto-mode.md)
- [compound-debug](references/source-methods/compound-debug.md)
- [source-4-skill](references/source-methods/source-4-skill.md)
