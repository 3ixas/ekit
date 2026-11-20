# T3 relay

In T3 Code, when `implement-ticket` starts in a Lead thread, the Lead confirms the ticket is ready, writes a relay handoff, launches a fresh Engineer worktree thread to deliver it, and settles. The Lead thread does not implement the ticket.

## When it applies

Relay to an Engineer thread is the default when all of these hold:

- The host provides `t3_thread_launch` (T3 Code) and the current thread is running as the **Lead**.
- Elias has not explicitly asked for the Lead (per the Roles section of the shared instructions) and has not asked to keep the work in this thread ("stay in this thread", "no relay").
- The ticket is resolved from live tracker state, its scope and endpoint are established, and its readiness is verified: every blocker has a verified merge satisfying it (an open or queued PR, armed auto-merge or closed issue alone is not proof), no open product ambiguity blocks it, and existing PRs and branches have been checked to avoid duplicate work. If blocked, ambiguous or already delivered, report that here and do not launch a thread.

When the current thread is already running as the **Engineer** (including the launched successor) or another non-Lead role and Elias did not ask for the Lead, when a Lead thread was explicitly asked for the Lead or to stay in-thread, or on hosts without `t3_thread_launch`, deliver the ticket directly in this thread. If Elias explicitly asked for the **Lead** while in a non-Lead thread, do not silently implement on the Engineer: launch a fresh **Lead** worktree thread using the same relay contract when `t3_thread_launch` is available, or report the role mismatch and ask before continuing.

A deliberate `implement-ticket` request in T3 is Elias's request for this Engineer thread. It authorizes writing the relay handoff, launching the Engineer worktree thread and settling the Lead thread without separate approval. It grants the Engineer no authority beyond the original request.

## Relay handoff contract

A relay handoff is an ordinary `handoff` document saved to `~/.agents/handoffs/<project>/<YYYY-MM-DD-HHMM>-ticket-<ticket-slug>.md` whose first line is exactly `Relay: implement-ticket`. Include:

- the ticket reference/URL, title, spec/context pointers, target branch and selected endpoint (verified merge by default, Full Stop, or explicit local-only);
- the original request's authority, quoted briefly, and any user choices that shape delivery (deadlines, waiting budget, existing PR or branch when resuming);
- verified readiness evidence (blockers confirmed merged, existing PR check);
- the delivery role (`Engineer`, or `Lead` when redirecting an explicit Lead request from a non-Lead thread);
- this thread's `threadId` and link as the predecessor;
- short repository notes the successor would otherwise rediscover (link artifacts rather than copying them);
- "Suggested skills": `pickup`, `implement-ticket`, `implement`, `code-review`, `pr`, `verify`.

## Relay steps

1. Write the relay handoff.
2. Launch the successor thread with `t3_thread_launch` in the same project and environment:
   - `title`: `Ticket: <ticket>` (ticket identifier and short title);
   - `message`: ask it to use the `pickup` skill on the relay handoff's absolute path and deliver the ticket with `implement-ticket`;
   - `workspaceStrategy`: for a fresh ticket, `worktree` from the freshly fetched target (`origin/<target>` with `startFromOrigin: true`) on a new branch named for the ticket. When resuming an existing unmerged ticket branch, pass that branch ref (`startFromOrigin: false`, or its pushed remote ref) only if no other checkout holds unpushed local work on it; if unpushed local edits exist elsewhere, stay in that checkout or report it instead of stranding them;
   - `clientRequestId`: `ticket-<ticket-slug>-<YYYYMMDDHHMM>`, set once for this handoff and reused unchanged on any retry of the same launch so a lost reply never creates a second thread;
   - `modelSelection` and `runtimeMode`: the **Engineer** at `high` (or the **Lead** when redirecting an explicit Lead request from a non-Lead thread), chosen as the Roles section of the shared instructions sets out (setting `runtimeMode` by provider, never above the launching thread's own mode). Inherit the interaction mode.
3. On a confirmed launch, this thread takes no further implementation action on the ticket. End with the successor thread's link, then the handoff path and resume command as the `handoff` skill requires, and settle this thread (`t3_thread_organize`, `action: "settle"`, no `threadId`).
4. On launch failure or lost reply:
   - For a transient error or lost reply (not exhausted quota), retry once with the **same** `clientRequestId`.
   - If that retry still fails, or the Engineer provider reports exhausted quota, search for a thread with the successor's title created after the handoff (`t3_thread_search` or `t3_thread_list`):
     - **Found:** treat it as the successor and finish step 3.
     - **Unknown** (the search failed): stop with the exact resume state rather than launching a fallback or risking two owners.
     - **None found:** when launching the Engineer, try the role table's Engineer fallback once—appending `-fallback` to `clientRequestId` and noting the fallback in the launch message and report (never modifying the written handoff). If that fallback launch errors or its reply is lost, apply one same-key retry and the same title search above.
   - Only when launching (including fallback when applicable) still fails and the title search confirms **None found**: keep ownership here, report the failed launch, do not settle this thread, and deliver the ticket directly in this thread (leaving the unused handoff as a record). If the request was an explicit Lead override from a non-Lead thread, report the failed launch and ask rather than implementing on the Engineer.

## Successor start

The successor's `pickup` reads the handoff from the path in its launch message. A relay handoff found only by searching the handoffs folder may be stale, so confirm it with Elias before acting on it.

1. Wait for the predecessor thread to finish its turn (`t3_thread_wait` on its `threadId`, bounded to a few minutes). The predecessor normally ends its turn just after launching, so a running predecessor at first read is expected, not a conflict.
2. Treat the ticket as owned elsewhere, stop and report both threads only when the predecessor is still working after the wait without having settled, or another thread is already working this ticket.
3. Re-read live tracker, PR and branch state. If the ticket is still ready, deliver it directly with `implement-ticket` (without launching another thread) under the recorded endpoint and authority. If live state shows the ticket is now blocked, ambiguous or already delivered, report that instead of implementing. Stale handoff details never override live state.
