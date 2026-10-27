---
name: flowsavvy
description: "Use when Elias asks to read, review, plan, create, update, reschedule, or complete FlowSavvy tasks. Do not select for general productivity advice or historical Todoist context."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

# Flowsavvy

## Outcome

FlowSavvy reflects the requested current tasks and schedule without losing existing properties.

## Method

1. Resolve the requested scope against live lists, calendars, scheduling hours, and connector capabilities. Follow [the live-operation contract](references/live-operation-contract.md) before an audit or mutation.
2. Retrieve the relevant objects, paginating complete reviews. Distinguish tasks, events, scheduled blocks, and completion records; report incomplete coverage rather than inferring completion.
3. Before an authorised write, read the full object, resolve recurring-series scope, and preserve omitted fields in replacement-style updates.
4. Re-read each affected object. Report verified changes, returned IDs, scheduling consequences, and any failed or uncertain result.

## Boundaries

FlowSavvy owns task execution and schedule truth; Obsidian owns goals and personal knowledge; Calendar owns fixed commitments. A direct instruction to create, update, complete, or reschedule authorizes that narrow write. Review or planning alone does not authorize mutation.
