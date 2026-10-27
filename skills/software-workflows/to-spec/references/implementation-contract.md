# Implementation contract

## Ground the design

Read the settled scope in full and trace every affected path in the repository. Identify the current entry points, owners, contracts, persistence, side effects, observability, and tests. Resolve any conflict with the approved scope before designing the solution.

Use architecture or domain modeling only where responsibilities, boundaries, or states materially affect the change. Prefer the smallest design that fully expresses the approved behavior and fits sound project conventions.

## Specify what an implementer needs

A complete specification describes:

- the trigger and before/after behavior;
- affected user, API, CLI, job, or data flows;
- component responsibilities and interactions;
- types, schemas, endpoints, events, or commands that form contracts;
- state transitions, invariants, validation, errors, retries, and idempotency;
- authorization and trust boundaries;
- compatibility, migration, rollout, rollback, and observability where relevant;
- acceptance claims and the surface that proves each one;
- exclusions and deferred work.

Use concrete signatures, schemas, sequence diagrams, or examples when they remove ambiguity. Do not prescribe line-by-line code or freeze incidental file names unless they are contractually important.

## Readiness check

Trace every scope outcome to a design decision and every design decision to acceptance evidence. Each acceptance claim must be judged by something other than the implementer's say-so: a runnable check, the real surface, or data the implementation was not tuned on. Check that failure behavior is as explicit as the happy path. Confirm that proposed interfaces can represent every required state without sentinel values or hidden coupling.

The spec is ready for `to-tickets` when independent implementers would make compatible decisions and can verify completion without inventing requirements. Draft locally first. Creating or editing GitHub issues requires authorization in the current task. When an issue is the project record, use the CLI/API procedure in [github-cli.md](github-cli.md); use another supported GitHub capability when it is materially better or the CLI is unavailable.
