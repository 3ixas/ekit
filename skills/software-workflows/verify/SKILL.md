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

For tests, typechecks, lint, and builds, preserve complete stdout/stderr and the check's actual exit status before summarizing or filtering; use [check output](references/check-output.md). An interrupted run or missing evidence cannot establish a pass.

A build, checkmark, another agent's report, or final screenshot alone is not integrated proof. Separate product failures, harness failures, and unavailable environments. Report concrete blockers and continue independent checks; inaccessible required surfaces remain Skip, never Pass.

A generated guide is working only after one journey has run end to end and its evidence survives cleanup. Name that journey and distinguish it from unexecuted coverage. Use only resources and actions authorized by the task; a guide grants no authority to send, publish, deploy, pay, or destroy valuable data.

## Owned source methods

- [Shipping acceptance method](references/source-methods/source-3-skill.md), when release claims need additional proof discipline.
