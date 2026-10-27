# FlowSavvy project conversion contract

## Interpret the source brief

Treat the source title and notes as a brain dump. Extract the intended outcome and classify each useful fragment:

- An action or outcome becomes an actionable task with one clear result.
- Context, constraints, links, commands, and references become notes on the relevant task; preserve exact wording where changing it could change meaning.
- A prerequisite becomes a direct dependency. Add inferred relationships only when the logic is strong and show the reason in the proposal. Build one acyclic dependency graph for the complete child-task set: every child must participate in at least one direct edge, and no child may be an orphan or belong to a disconnected component. A first/root task satisfies this rule by blocking downstream work; a final/leaf task satisfies it by being blocked by upstream work. Do not invent a fake project-start, project-end, or project-brief task to manufacture an edge. If a genuine action cannot be connected without inventing sequencing, keep it in notes or ask a clarification question rather than creating an unconnected child.
- A question or decision becomes a decision task, or a clarification question when its answer changes scope, deadline, dependency, scheduling, or deletion.
- An idea, risk, or optional improvement becomes a clearly identified suggestion rather than an assumed commitment.

Develop the notes into a coherent plan. Add high-confidence missing steps, but do not invent external facts, commitments, or dates. If a general fragment cannot safely be assigned, surface it in the proposal or place a concise developed context summary on the most relevant child task; never silently drop it. Do not create a non-actionable project-brief task merely to hold notes.

Aim for roughly 5–15 useful tasks. Use a flat list of independently completable actions; use phase labels in titles or notes only when they improve scanning, and create milestone tasks only for real outcomes.

For a recurring source, resolve one selected occurrence before planning. Use the occurrence date from the task's due date for an auto-scheduled series or from its start date for a fixed-time series. The generated project tasks are one-time tasks; do not copy the recurrence rule. Keep the parent series intact.

## Project and task fields

The proposed project list uses:

- title: `PROJECT: <source task title>`;
- colour: the live source list colour;
- scheduling hours: the live source list's scheduling-hours profile.

Child tasks use the project list's ID and, for flexible work, normally use auto-scheduling with a defensible duration estimate. Respect the inherited scheduling profile and existing splitting settings. Set a minimum chunk only when the task genuinely requires uninterrupted work. Use fixed-time fields only for an explicit fixed-time commitment.

Map a genuine source deadline to the final deliverable or final dependency gate, not every child task. Add intermediate deadlines only when explicit or necessary. Treat source priority as a signal, then assign each child `low`, `normal`, `high`, or `asap` according to consequence, deadline, and dependency importance; do not blanket-copy it.

Use `blockedByIds` or `blocksIds` for every direct edge. Use the minimum truthful edges needed to express the flow: genuinely independent branches may be scheduled in parallel, but they should converge on a real downstream synthesis or final-deliverable task when the work has one. Do not create arbitrary edges merely to produce a linear-looking chain. If IDs are not yet available, create the tasks in planned upstream-to-downstream order and then perform full-object dependency updates while preserving all unrelated fields. Before source deletion, verify that the resulting graph is acyclic, connected, and incident to every child task; a one-task decomposition cannot satisfy this invariant and is not a project conversion.

## Proposal and mutation gates

The proposal must make these visible:

1. source task or selected occurrence identity, source list, task type, important fields, recurrence date/scope when relevant, and planned source action;
2. project-list title, colour, scheduling hours, and whether the user must create it manually;
3. the developed outcome and note allocation;
4. each child title, notes, duration, scheduling mode, priority, deadline, and dependencies; show the full directed dependency graph and the rationale for each edge;
5. extracted versus inferred content, assumptions, unresolved questions, and expected schedule effects;
6. the verification condition before source deletion and the later project-list cleanup step;
7. the graph invariant: every child participates in a direct edge, the graph is acyclic and connected, and any parallel branch is justified rather than arbitrary.

After the single approval, re-read live lists before using a manually created project list. Require an exact title match plus the expected colour and scheduling-hours profile, and pause on no match or multiple matches. Create child tasks and verify their fields and dependency relationships. Do not proceed to source deletion if any child is orphaned, the graph is disconnected or cyclic, or any edge is missing. Only then delete a non-recurring, non-fixed-time source task. For a recurring source, do not call a series-scope delete or alter the recurrence. Instruct the user to delete the selected occurrence only, wait for confirmation, and verify that occurrence where the connector supports it; future occurrences must remain.

If a mutation partially succeeds, keep the source task, stop, report the affected IDs and exact gap, and resume by reconciling the existing project rather than duplicating tasks. A matching existing project list is a delta target, not a reason to create another list.

When all required tasks and the final deliverable are complete, ask before deleting the project list. If the relevant list operation is unavailable, provide the exact manual cleanup step and do not substitute browser automation. Deleting the project list must not delete or alter the recurring source series.
