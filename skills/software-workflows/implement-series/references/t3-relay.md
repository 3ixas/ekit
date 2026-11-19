# T3 relay

In T3 Code, each ticket runs in its own thread. After a ticket's merge is verified, the thread that delivered it writes a relay handoff, launches a fresh thread to pick it up, and stops. The new thread continues the same run from step 2. This keeps every ticket in a clean context and makes the thread list a record of the run.

## When it applies

Relay is the default when all of these hold:

- The host provides `t3_thread_launch` (T3 Code). Other hosts keep the in-thread loop unchanged.
- Elias has not asked to keep the run in one thread ("stay in this thread", "no relay"). That choice carries forward in the relay handoff.
- The current ticket's merge is verified, its post-merge activation is complete, its tracker state is reconciled, and the graph and target branch are refreshed.
- At least one ticket is now ready. When the graph is complete, give the final run report here instead. When the remaining tickets are all blocked, report the blocker and resume state as step 5 describes; do not launch a thread just to wait.

With Full Stop, nothing merges, so no relay fires; the run stays in its thread.

A deliberate Implement Series request in T3 authorizes every relay in that run: writing each relay handoff, launching each successor thread and settling the predecessor. It does not need a separate approval per relay, and it grants the successor no authority beyond the original request.

## Relay steps

1. Detach this thread's watchers on the merged PR (`unwatch_pull_request` when it was watched). Leave no armed auto-merge or queue entry on graph PRs other than one recorded in the handoff.
2. Write the relay handoff with the `handoff` method to its usual folder, named `<YYYY-MM-DD-HHMM>-series-<graph-slug>-<next-ticket>.md`. Mark it `Relay: implement-series` in its first lines and include:
   - the spec, graph and tracker pointers, the target branch and the endpoint;
   - the original request's authority, quoted briefly, and any user choices that change the run (stated order, deadlines, waiting budget, relay opt-out);
   - the run ledger: one row per completed ticket with its PR, verified merge commit and thread link, carried forward from the previous relay handoff plus this ticket;
   - the ready ticket to start next, and any blocked tickets with their exact resume points;
   - this thread's `threadId` and link as the predecessor;
   - "Learned this run": repository facts the next thread would otherwise rediscover, such as a known flaky check, a slow test command or a sync quirk. Keep it short; link artifacts rather than copying them.
3. Launch the successor with `t3_thread_launch` in the same project and environment:
   - `title`: `Series: <graph> · <next-ticket>`;
   - `message`: ask it to use the `pickup` skill on the relay handoff's absolute path and continue Implement Series;
   - `workspaceStrategy`: `worktree` from the freshly fetched target (`origin/<target>` with `startFromOrigin: true`), on a new branch named for the ticket;
   - `clientRequestId`: `series-<graph-slug>-<next-ticket>`, reused unchanged on any retry so a lost reply never creates a second thread;
   - inherit model and modes.
4. Verify the launch returned a thread. Then end with one short line linking the successor thread and the handoff path, and settle this thread (`t3_thread_organize`, `action: "settle"`, no `threadId`). After a confirmed launch this thread takes no further action on the run, even if woken later; a later wake only points to the successor.
5. If the launch fails after one retry with the same `clientRequestId`, keep ownership here: report the failure, keep the handoff for reference, and continue the run in this thread from step 2.

## Successor start

The successor's `pickup` reads the handoff, then confirms with `t3_thread_read` that the predecessor has finished its turn and that no other thread with the same series title is working the next ticket. If another owner is active, it stops and reports both threads rather than racing. Otherwise it re-reads live tracker, PR and branch state and continues at step 2 of Implement Series without asking for confirmation. Stale handoff details never override live state.

## Final report

The thread that finds the graph complete reports the whole run from the ledger plus its own ticket: each ticket's PR, merge commit and thread, any ticket left blocked, and whether any auto-merge or continuation remains armed.
