# Escalation

An **Engineer** hands a ticket back to the **Lead** instead of settling an open decision itself. Escalation is not fallback: fallback replaces an unavailable provider for one launch; escalation moves the ticket to the Lead role because the work needs judgement. A Lead thread never escalates; it settles the point or asks Elias as `implement` describes. An Engineer thread escalates even when Elias started or steered it, unless he asked it to settle the point itself or to ask him.

## Triggers

Escalate when either holds during an Engineer run of `implement`, alone or under a coordinator:

- **Unsettled decision:** the next step needs a choice the approved brief, spec, ticket and repository instructions do not settle, such as a product behaviour, a scope boundary, a contract with no stated owner or two credible designs with different consequences. A routine, reversible implementation choice is not a trigger; make it and record it.
- **Review stall:** the same finding survives two fix attempts, a dismissed actionable finding returns, two successive review rounds fail to reduce confirmed findings, or required review remains incomplete at a user-set limit (the `code-review` review-loop stop conditions).

Do not guess past a trigger, and do not ask Elias directly or start `grill-with-docs` from the Engineer: the Lead decides whether the question is his.

## Escalate

1. Stop editing. Leave the task branch or worktree intact, with staged and unstaged work as it is.
2. Release this thread's hold on the ticket: push nothing new; detach its PR watcher (`unwatch_pull_request`); remove any scheduled continuation or wake it created for the run and verify the removal; and if the PR has auto-merge armed or sits in a merge queue, disarm or dequeue it under the existing delivery authority and verify, so nothing merges while the decision is open. Record any of these that could not be released.
3. Write an ordinary `handoff` document whose first line is exactly `Escalation: <workflow>` (the workflow running the ticket: `implement`, `implement-ticket`, `implement-series` or `implement-parallel`). Name it `<YYYY-MM-DD-HHMM>-escalation-<ticket-slug>.md` and include:
   - the trigger, and the decision stated as one question with the options considered and their consequences;
   - what was tried: attempts, review finding IDs and rounds, failing checks, with links to evidence rather than copies;
   - the ticket, spec and tracker pointers, target branch, endpoint and the original request's authority, quoted briefly;
   - for a coordinated run, the incoming relay handoff path, which carries the run id, ledger, run role, user choices and blocked tickets, plus any ledger rows, blocked tickets or user choices added in this thread since; when this thread started the run without one, record those directly;
   - the worktree path, branch, base commit, last commit, `git status --short`, the staged, unstaged and untracked slice paths, and the staged and working-tree diff checksums, and the PR with its head, checks and the auto-merge, queue and wake state from step 2;
   - a standalone `Routing:` line recording the escalation cause and the role and model that escalated, e.g. `Routing: escalation=<unsettled-decision|review-stall> role=<role>/<model> cause=<brief cause>`;
   - this thread's `threadId` and link as the predecessor.
4. Then take exactly one of these branches:
   - **Parallel worker** (a child of an `implement-parallel` coordinator): return the handoff path and the decision to the coordinator, which owns the ticket and acts as the Lead side below. Launch no thread.
   - **T3 Code with `t3_thread_launch`:** launch one **Lead** thread in the same project and environment with `title` `Escalation: <ticket>`; a `message` asking it to use `pickup` on the handoff's absolute path; `workspaceStrategy` `existing_worktree` with this worktree's path, or `root` when the task branch is in the main checkout; `clientRequestId` `escalation-<ticket-slug>-<YYYYMMDDHHMM>`, set once and reused on retry; and `modelSelection` and `runtimeMode` for the Lead from the Roles section of the shared instructions, never above this thread's own mode (when that forces an approval-asking mode, tell Elias the Lead's tool calls will wait for approval). Continue at step 5.
   - **No `t3_thread_launch`** (for example an Antigravity thread that does not expose it): stop and report to Elias the decision, the handoff path and the resume command to run in a Lead thread. Do not settle this thread; it stays visible until a Lead takes the ticket, and does no further work on it.
5. On a confirmed launch, stop working the ticket: end with the Lead thread's link, the handoff path and resume command, and settle this thread. On an error or lost reply, retry once with the same `clientRequestId`, then search for an active thread with that title created after the handoff (`t3_thread_search` or `t3_thread_list`):
   - **Found:** adopt it as the Lead and finish as on a confirmed launch.
   - **None found:** report the failed escalation to Elias with the handoff path and resume command, and do not settle this thread.
   - **Unknown** (the search failed): report that a Lead thread may already exist, ask Elias to check active threads for the title before running the resume command, and do not settle this thread.

   In every branch, the Engineer does not continue the ticket.

## Lead side

`pickup` reads an `Escalation:` handoff given by path and continues without asking for confirmation. If the receiving thread is not running as the Lead, it does not take the Lead side: it launches a Lead thread as in step 4, bound to the worktree the handoff records (`existing_worktree` with that path, or `root` when it records the main checkout), when `t3_thread_launch` is available, or reports the role mismatch and asks Elias.

1. Wait for the predecessor's turn to end (`t3_thread_wait`, bounded to a few minutes). If it is still working without having stopped, or another thread is working the ticket, stop and report both threads rather than becoming a second owner.
2. Re-read the worktree, branch, PR and tracker state against the handoff; live state wins. Staged, unstaged and untracked work matching the handoff's recorded paths and checksums is the inherited slice, not pre-existing user changes; continue it.
3. Settle the decision when the brief, spec, repository or code evidence supports one answer, and record the reasoning. When the decision is genuinely Elias's (product behaviour, scope, an external commitment or cost), ask him the one question with a recommendation and wait; never guess it.
4. Resume delivery in this Lead thread under the original workflow, endpoint and authority, re-arming any watcher or auto-merge step 2 released as that workflow allows. An escalated ticket is delivered here, not relayed back to an Engineer thread. Work the Lead continues itself is Lead-implemented, so `code-review` runs on the Engineer. A series run keeps its run role: once this ticket merges, the next relay launches the Engineer as before.
