# Architecture method

## Map the system

Start from runtime entry points and trace control, data, and ownership across the affected path. Record modules, stores, external systems, contracts, lifecycles, deployment boundaries, and operational constraints. Distinguish present facts from assumptions and accidental legacy structure.

Identify load-bearing decisions: where state lives, who owns each invariant, which direction dependencies flow, how components communicate, and how failure is contained. Use domain terms consistently and sketch concrete types, interfaces, or sequences when prose leaves room for incompatible implementations.

## Compare viable shapes

Generate alternatives only for decisions with material tradeoffs. Compare them using the constraints that matter here:

- correctness and invariant ownership;
- coupling, cohesion, and reader load;
- change frequency and likely extension points;
- data consistency and concurrency;
- failure isolation, retries, idempotency, and recovery;
- security and trust boundaries;
- testability, observability, deployment, and rollback;
- migration cost and compatibility.

Prefer a cohesive local design over speculative generality. Treat abstraction as justified when it centralizes a real invariant or removes repeated coordination, not merely repeated syntax.

## Record the decision

State the chosen structure, responsibilities, dependencies, data flow, and public contracts. Explain the strongest rejected alternative and why the current constraints favor the choice. Include a migration path when the target cannot be reached atomically and identify how each stage remains valid.

For a review, report structural risks in impact order with the concrete change pressure or failure that exposes them. Avoid recommending a rewrite when a boundary, owner, or contract can be repaired directly.
