# T3 relay

In T3 Code, each ticket runs in its own thread. After a ticket's merge is verified, the thread that delivered it writes a relay handoff, launches a fresh thread to pick it up, and stops. The new thread continues the same run from step 2. This keeps every ticket in a clean context and makes the thread list a record of the run.

## When it applies

Relay is the default when all of these hold:

- The host provides `t3_thread_launch` (T3 Code). Other hosts keep the in-thread loop unchanged.
- Elias has not asked to keep the run in one thread ("stay in this thread", "no relay").
- The current ticket's merge is verified, its post-merge activation is complete, its tracker state is reconciled, and the graph and target branch are refreshed.
- At least one ticket is now ready. When the graph is complete, give the final run report here instead. When the remaining tickets are all blocked, report the blocker and resume state as step 5 describes; do not launch a thread just to wait.

With Full Stop, nothing merges, so no relay fires; the run stays in its thread.

A deliberate Implement Series request in T3 is Elias's request for these new threads. It authorizes every relay in that run, including writing each relay handoff, launching each successor thread and settling the predecessor, without separate approval per relay. It grants the successor no authority beyond the original request.

## Relay handoff contract

A relay handoff is an ordinary `handoff` document whose first line is exactly `Relay: implement-series`. Name it `<YYYY-MM-DD-HHMM>-series-<graph-slug>-<ticket>.md` and include:

- the spec, graph and tracker pointers, the target branch and the endpoint;
- the original request's authority, quoted briefly, and any user choices that shape the run (stated order, deadlines, waiting budget);
- the run id: the first thread's start time as `YYYYMMDDHHMM`, set once and carried unchanged by every relay;
- the run ledger: one row per completed ticket with its PR, verified merge commit and thread link, carried forward from the previous relay handoff plus this ticket;
- the run's role (the Engineer by default, or the Lead when Elias asked for it) and any fallback in use;
- the proposed next ticket, and any blocked tickets with their exact resume points;
- this thread's `threadId` and link as the predecessor;
- "Learned this run": repository facts the next thread would otherwise rediscover, such as a known flaky check, a slow test command or a sync quirk. Keep it short; link artifacts rather than copying them.

## Relay steps

1. Release this thread's hold on the run: detach its watchers on the merged PR (`unwatch_pull_request` when watched), and remove any step 6 scheduled continuation or wake for this run, verifying the removal. Record in the handoff any graph PR still armed for auto-merge or queued.
2. Write the relay handoff.
3. Launch the successor with `t3_thread_launch` in the same project and environment:
   - `title`: `Series: <graph> · <ticket>`;
   - `message`: ask it to use the `pickup` skill on the relay handoff's absolute path and continue Implement Series;
   - `workspaceStrategy`: `worktree` from the freshly fetched target (`origin/<target>` with `startFromOrigin: true`), on a new branch named for the ticket;
   - `clientRequestId`: `series-<graph-slug>-<run-id>-r<n>`, where `n` is the number of tickets in the ledger after this one. It identifies this relay transition, not a ticket, so a successor that switches tickets never blocks a later relay; reuse it unchanged on any retry so a lost reply never creates a second thread;
   - `modelSelection` and `runtimeMode`: the run's role, chosen as the Roles section of the shared instructions sets out: the Engineer at `high` unless Elias asked for the Lead for this run. When the Engineer's launch fails or its provider reports exhausted quota, use the table's Engineer fallback and record it in the handoff. Inherit the interaction mode.
4. On a confirmed launch, this thread takes no further action on the run. End with the successor's link, then the handoff path and resume command as the `handoff` skill requires, and settle this thread (`t3_thread_organize`, `action: "settle"`, no `threadId`).
5. If the launch errors or its reply is lost, retry once with the same `clientRequestId`. If that also fails, search for a thread with the successor's title created after the handoff (`t3_thread_search` or `t3_thread_list`):
   - Found: treat it as the successor and finish step 4.
   - None found: keep ownership here. Report the failed launch, do not settle this thread, and continue at step 2 of Implement Series here; the unused handoff stays as a record.
   - Unknown, because the search failed: stop with the exact resume state rather than risk two owners.

## Escalation

An Engineer that escalates its ticket (as the `implement` skill describes) hands run ownership to the Lead thread it launches. That Lead thread delivers the ticket, then relays as above, carrying the run's role unchanged, so the next ticket starts on the Engineer again. Record the escalation in the ledger row's thread column.

## Successor start

The successor's `pickup` reads the handoff from the path in its launch message. A relay handoff found only by searching the handoffs folder may be stale, so confirm it with Elias before acting on it.

1. Wait for the predecessor to finish its turn (`t3_thread_wait` on its `threadId`, bounded to a few minutes). The predecessor normally ends its turn just after launching, so a running predecessor at first read is expected, not a conflict.
2. Treat the run as owned elsewhere, stop and report both threads only when the predecessor is still working after the wait without having settled, or another thread is already working the same ticket for this run.
3. Re-read live tracker, PR and branch state and continue at step 2 of Implement Series without asking for confirmation. Prefer the proposed ticket when it is still ready. If live state selects a different ticket, rename the thread (`t3_thread_update`) and the still-unpushed branch to match before starting work. Stale handoff details never override live state.

## Final report

The thread that finds the graph complete reports the whole run from the ledger plus its own ticket: each ticket's PR, merge commit and thread, any ticket left blocked, and whether any auto-merge or continuation remains armed.
