---
name: architecture
description: Design or review software architecture when responsibilities, boundaries, interfaces, data flow, dependencies, or structural tradeoffs materially affect the result.
---

# Architecture

## Outcome

A grounded target structure or a prioritized structural review with rationale.

## Method

1. Map affected entrypoints, owners, data flow, contracts, and constraints. Separate observed structure from assumptions; identify the decisions on which correctness depends.
2. Sketch responsibilities, types, signatures, modules, and flows. Compare materially different options only where a real tradeoff remains; assess coupling, state, lifecycle, operability, and migration.
3. For a consequential new requirement, compare a focused patch with a coherent target shape as if the requirement had been known earlier; weigh migration and scope, then deliver the chosen shape in verifiable stages. When concurrent writes matter, first consider partitioning ownership; if state must be shared, specify coordination and recovery from partial failure.
4. Record the chosen shape and rationale, the strongest rejected alternative, and any staged migration. For a review, return prioritized structural risks with the concrete failure or change pressure that exposes each one.

Read [references/architecture-method.md](references/architecture-method.md) for substantial design or structural review.

## Boundaries

Do not impose architecture ceremony on local changes. Existing patterns are evidence, not proof of quality.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [matt-codebase-design](references/source-methods/matt-codebase-design.md)
- [pstack-architect](references/source-methods/pstack-architect.md)
- [compound-plan](references/source-methods/compound-plan.md)
