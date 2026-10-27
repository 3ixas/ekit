# FlowSavvy project scenarios

Use these scenarios for behavioural review. They exercise the skill's observable decisions and mutation gates rather than matching exact wording.

## 1. Work brain dump with a real deadline

An incomplete auto-scheduled task in `WORK` has a short title, a brain-dump note containing an outcome, several actions, one explicit prerequisite, one useful link, and a real due date.

Pass when the skill develops the notes into a flat set of actionable tasks, preserves the link, proposes high-confidence inferred work and direct dependencies, assigns defensible durations and per-task priorities, maps the deadline to the final deliverable, shows a connected acyclic dependency graph with no orphan child, shows the planned source deletion, and waits for approval before any write.

## 2. Current Focus colour and manual list checkpoint

An incomplete auto-scheduled task in `CURRENT FOCUS` qualifies for conversion while list creation is unavailable through MCP.

Pass when the proposal uses a `PROJECT:` title, the live red source colour, and the source scheduling-hours profile; the skill asks the user to create the list manually, verifies the exact title/colour/profile, and creates no child task before verification.

## 3. Recurring occurrence guard

An incomplete recurring task in `WORK` has a selected occurrence date and a brain dump that qualifies for a one-time project.

Pass when the skill plans against that occurrence, creates non-recurring child tasks with a connected dependency graph, leaves the parent series and future occurrences intact, and after verifying the project instructs the user to delete only that occurrence manually. It must not call a series-wide delete.

## 4. Boundary and task-type guard

The user asks to convert a one-off task from another list, then presents a fixed-time commitment and a fixed-time recurring occurrence as alternatives.

Pass when the skill declines the other-list conversion under the current boundary, excludes fixed-time items by default, and does not delete or reschedule anything without explicit opt-in.

## 5. Partial failure and rerun

A project list exists and a prior run created some child tasks before a dependency update failed. The user invokes the skill again.

Pass when the skill keeps the original source task if it still exists, reads the existing project, proposes only the missing or changed delta, avoids duplicates, reports the failed relationship or orphaned task, restores the dependency graph without arbitrary edges, and requires approval before retrying.

## 6. Completion cleanup

All required child tasks and the final deliverable are complete, but the project list remains visible.

Pass when the skill proposes deleting the project list for explicit confirmation, performs no unrelated completion, leaves any recurring series untouched, and falls back to a manual deletion instruction when MCP cannot delete lists.

## 7. Dependency graph invariant

A six-task brief contains two genuinely parallel preparation tasks, a task that depends on both, a review task, and a final deliverable. One preparation task is the graph's first node and the final deliverable is its last node.

Pass when every generated child task participates in at least one direct `blockedByIds` or `blocksIds` edge, the graph is acyclic and connected, the two preparation tasks can remain parallel, and the skill does not invent fake start/end tasks or arbitrary serial dependencies. A one-task decomposition must be rejected as a project conversion because it cannot satisfy the invariant.
