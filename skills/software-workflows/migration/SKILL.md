---
name: migration
description: "Use as supporting expertise when Elias requests Migration or a substantial staged data, API, or cross-system migration within the owning workflow. Do not initiate a migration from a compatibility question."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

# Migration

## Outcome

A safe transition with inventory, reconciliation, cutover evidence, and a clear legacy-removal condition.

## Method

1. Inventory producers, consumers, data, and constraints. Record the compatibility window and the invariant each migration stage must preserve.
2. Sequence expand, backfill, reconcile, cutover, and cleanup. Define idempotent retries, roll-forward and rollback conditions, and an observable check for each stage before executing it.
3. Verify each authorized stage against those checks. Record reconciliation and cutover evidence; remove legacy paths only when their consumers and removal-readiness condition have been checked.

## Boundaries

Ordinary SQL syntax belongs to postgres. Release owns production go/no-go and external action authority.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-1-skill](references/source-methods/source-1-skill.md)
