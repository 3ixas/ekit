---
name: flowsavvy-project
description: "Use when Elias asks to develop a FlowSavvy task into a project list with structured child tasks and dependencies. Do not select for a routine task update."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

# FlowSavvy Project

## Outcome

Turn a genuine multi-step task into a colour-matched FlowSavvy project list with useful, schedulable child tasks joined by a truthful, dependency-connected flow while preserving the user's control over external changes and destructive cleanup.

## Route

Use when the user invokes `flowsavvy-project` (`$flowsavvy-project` in Codex, `/flowsavvy-project` in Claude Code) or naturally asks to turn a FlowSavvy task into a project or break it down into a project list.

- Work only with tasks whose live source list title is `WORK` or `CURRENT FOCUS`; resolve list IDs, colours, and scheduling-hours profiles live rather than relying on saved values.
- If the task is not uniquely identified, inspect incomplete tasks in those two lists and ask the user to choose. Do not guess.
- Use explicit intent as the primary signal. Heuristics may identify a likely multi-step project, but never convert a task silently.
- A selected occurrence of a recurring task may seed a one-time project. Resolve its occurrence date before proposing changes; never treat the whole series as the source to delete.
- Keep fixed-time tasks, including fixed-time recurring occurrences, behind explicit opt-in because they represent calendar commitments.
- Use `flowsavvy` for ordinary FlowSavvy reads, reviews, task edits, rescheduling, completion, and other work that is not project conversion.

## Method

1. Read the complete source task and current FlowSavvy configuration. For a recurring task, resolve the selected occurrence and its date before planning; do not conflate the occurrence with the parent series. Treat the title and notes as a rough brief, not as a ready-made task list.
2. Develop the brief into an outcome, actionable tasks, relevant context, constraints, a complete dependency graph, estimates, priorities, and a final deliverable. Classify and preserve useful note content according to [the conversion contract](references/conversion-contract.md). Every proposed child must participate in at least one direct dependency edge; do not leave an orphan task or disconnected dependency component.
3. Build a complete proposal before writing anything. Show the source task or selected occurrence and its planned source action, `PROJECT: <source title>` list metadata, note allocation, every child-task field, every dependency edge with its direction and rationale, inferred items, assumptions, unresolved questions, and any manual list step.
4. Require one explicit approval for the complete conversion. Planning or review alone never authorizes FlowSavvy mutation.
5. Create or obtain the project list through MCP when the required list operation is exposed. If list creation is unavailable, give the user the exact title, source colour, and scheduling-hours profile to create manually; never use UI automation. Re-read and require one unique match before creating child tasks.
6. Create the child tasks in dependency order in the matched project list, establish the complete direct dependency graph once IDs are known, and re-read all affected tasks and relationships. Confirm that the graph is acyclic, connected, and that every child participates in at least one edge before continuing. Preserve fields during replacement-style updates.
7. For a non-recurring, non-fixed-time source, delete the original task only after every child task and dependency has been verified. Preserve a fixed-time source for the explicitly approved manual source action; conversion opt-in alone does not authorise deleting a fixed commitment. For a recurring source, never delete or alter the series automatically: after verification, instruct the user to delete only the selected occurrence manually, wait for confirmation, and re-read it where possible. If any step fails, preserve the source or series, report partial progress and returned IDs, and support a delta-based retry without duplication.
8. When the final deliverable and all required tasks are complete, propose deleting the project list. Require a final confirmation; if list deletion is unavailable, ask the user to delete it manually. This cleanup must not affect a recurring series or its future occurrences. If the user has already deleted the list, do not recreate it unless explicitly asked.

## Boundaries

Do not create project lists for other source lists, invent deadlines or fixed times, copy one priority to every child, create arbitrary dependencies just to satisfy the graph, leave a child task orphaned or in a disconnected component, create a fake project-start or project-end task, create a non-actionable project-brief task, silently discard unassigned brain-dump material, delete or modify a recurring series during conversion, or claim completion from scheduled blocks alone. Preserve genuine parallel work when its dependency logic supports it; do not force an arbitrary linear chain.

Follow the existing `flowsavvy` live-operation contract for pagination, full-object replacement updates, recurrence scope, re-reads, and reporting schedule consequences. Report assumptions, limitations, created IDs, and any manual checkpoint plainly.
