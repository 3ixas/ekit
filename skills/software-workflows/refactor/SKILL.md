---
name: refactor
description: Improve code structure or simplify settled code while preserving intended behaviour and proving equivalence.
---

# Refactor

## Outcome

A clearer target shape with unchanged observable behaviour.

## Method

1. Name the structural problem and target shape. Pin intended behaviour with characterization, snapshots, invariants, or equivalence checks before changing it.
2. Subtract dead weight first, then change structure in small passing steps. Migrate callers and non-symbol uses together; remove legacy paths only after checking their consumers.
3. Re-run the behaviour checks on the final shape and inspect the resulting reader load. Report what became simpler, the equivalence evidence, and any discovered behaviour change separately.

## Boundaries

Keep discovered defects or feature changes explicit. Do not call a behavioural change a refactor.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-2-skill](references/source-methods/source-2-skill.md)
