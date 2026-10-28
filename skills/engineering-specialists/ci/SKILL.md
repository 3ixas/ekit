---
name: ci
description: Build, debug, or review continuous-integration workflows for fast deterministic feedback, least privilege, safe artifacts, and local parity.
---

# CI

## Outcome

A pipeline whose gates are relevant, reproducible, and safe to operate.

## Method

Inspect current workflow and repository commands; reproduce failures locally where possible; minimize permissions; pin third-party actions appropriately; separate read-only checks from mutations; validate cache keys and artifacts; protect secrets and untrusted PR contexts; make failures actionable.

For a new repository, or one with no workflow, start from the [bootstrap baseline](references/bootstrap.md): propose it on day one and add gates as they are proved; `app-audit` hands over its lasting checks to add. Proposing is not pushing.

Done when the changed gate runs against representative success and failure cases, its permissions and artifact paths are inspected, and any check not reproduced is named.

## Boundaries

Release owns deployment decisions. Do not replace a working pipeline merely to standardize tools.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-1-skill](references/source-methods/source-1-skill.md)
