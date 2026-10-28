---
name: verify
description: Prove software or artifact behaviour against acceptance criteria; automatically establish missing project verification guidance during implementation and maintain affected journeys.
---

# Verify

## Select the mode

- **Check** (default): prove the current acceptance claims on the real surface. Discover project instructions, verification guides, tests, and harnesses before choosing checks. Reuse sufficient guidance, wherever the project keeps it.
- **Set up**: during implementation, automatically fill missing launch, interaction, evidence, and cleanup guidance needed for the work. Read [project setup](references/project-setup.md). No separate user invocation is needed. Establish an existing app's baseline before editing where feasible; for a new app, do so once its first journey runs.
- **Maintain**: when implementation changes a documented journey, update and re-execute that journey as part of the change. For an explicit audit, cover the requested guide or feature set. Read [guide maintenance](references/guide-maintenance.md).

Read-only questions do not trigger setup. Documentation and artifact changes use appropriate artifact checks, without application scaffolding. Reuse a sufficient executable proof path for small changes; do not build a whole-app map to prove one claim.

## Prove and report

Translate each material acceptance claim into observable setup, action, expected result, observed result, and Pass, Fail, or Skip. Exercise the real path and inspect resulting state and side effects. Read [acceptance evidence](references/acceptance-evidence.md) when preparing the proof matrix or judging evidence.

For a consequential interactive flow, map the relevant role, starting state, action, expected next state and recovery in a small transition matrix. Include meaningful failure, forbidden or impossible transitions and exercise them with safe test data. Select combinations by risk rather than enumerating every permutation; report unexercised cases. Use an executable model or `prototype` only when the transition complexity warrants it. A screenshot of a state does not prove its transitions or authorization.

When important test sensitivity is uncertain and the risk warrants the cost, consider a scoped mutation run using an appropriate project-supported tool. Establish a passing baseline and inspect its side effects first; investigate meaningful survivors, distinguishing equivalent, irrelevant, invalid, and timed-out mutants. Report the scope and limitations; mutation scores do not prove correctness. Do not install or require a particular tool by default.

For tests, typechecks, lint, and builds, preserve complete stdout/stderr and the check's actual exit status before summarizing or filtering; use [check output](references/check-output.md). An interrupted run or missing evidence cannot establish a pass.

A build, checkmark, another agent's report, or final screenshot alone is not integrated proof. Separate product failures, harness failures, and unavailable environments. Report concrete blockers and continue independent checks; inaccessible required surfaces remain Skip, never Pass.

A generated guide is working only after one journey has run end to end and its evidence survives cleanup. Name that journey and distinguish it from unexecuted coverage. Use only resources and actions authorized by the task; a guide grants no authority to send, publish, deploy, pay, or destroy valuable data.

## Owned source methods

- [Shipping acceptance method](references/source-methods/source-3-skill.md), when release claims need additional proof discipline.
