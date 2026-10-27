---
name: implement-spec
description: "Use when Elias requests Implement Spec or asks to implement an approved specification and ticket graph through coordinated parallel implementers. A settled single slice uses implement."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

Read the repository's issue-tracker configuration (`docs/agents/issue-tracker.md` when present). If no tracker is configured, work from the local `.scratch/<feature>/issues/` tickets that `to-tickets` writes.

The goal is the entire spec implemented on a single **integration branch**, with verified ticket outcomes and the tracker updates prepared. Current-task authority is required before pushing, creating or updating PRs, posting comments, or changing tracker state. Tracker configuration describes how work closes; it does not authorise those writes. Continue local implementation and proof while any publication decision is pending.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Implementer subagents** should be run in the background where possible for maximum concurrency.

An explicitly requested Full Stop or Full Send coordinator carries this approved spec's integrated result through delivery. Return its final revision, proof matrix and review ledger to that coordinator. Ordinary `implement-spec` retains its existing endpoint; the mode does not authorize extra tickets or bypass review.

## Steps

1. Read the spec and tickets to understand the task graph. Use `verify` to discover reusable project guidance and harnesses and plan acceptance proof. The coordinator owns missing guide setup and its integration: establish the needed baseline before implementation where feasible, or once a new app's first journey runs. Keep setup proportional to the spec and use artifact checks for documentation-only work.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create the integration branch. If the tracker closes work through PRs, prepare a draft PR body with the `pr` skill, including the intended closing references. Open it after the first merge in step 5 only when the current task authorises the required push and PR creation; a branch with no commits ahead of main cannot open one. Without that authority, retain the prepared body locally and continue implementation. Do not ask again for authority already supplied.

4. Use **implementer subagents** to implement each ticket, each in its own worktree on its own branch. Each implementer subagent:
   - confirms its worktree is based on the integration branch before starting, and resets onto it if not;
   - receives the verification guide location (or pending setup milestone), journey scope, and instance/data ownership rules from the coordinator; reuses that guidance and proposes affected recipe updates with its slice rather than creating a competing guide;
   - loads the owned `tdd` skill to build the ticket and uses `verify` to prove its acceptance claims;
   - merges the integration branch tip into its own branch before reporting done

5. Once an **implementer subagent** completes, merge its work to the integration branch with a **merger subagent**. The coordinator reconciles guide changes and runs proof on the integrated revision; use isolated instances/storage or serialize all driving when isolation is unavailable.

6. If this changes the **frontier** of available tickets, kick off more **implementer subagents** to work on the new tickets. This allows for maximum concurrency.

7. Once all tickets are complete, prove and review the integrated result:
   - Use `verify` to prove the combined acceptance claims and re-execute affected guide instructions. Record the claim-to-proof matrix, observed Pass, Fail, or Skip results, and concrete blockers; incomplete required proof prevents a completion claim.
   - Record the integration commit and working-tree state; if uncommitted changes are included, record the exact diff and checksum. Call `code-review` with the fixed base, spec pointer, integrated proof matrix and observed results, and exact revision or diff checksum so the Spec reviewer judges evidence for that snapshot.
   - Fix confirmed in-scope findings in a single **implementer subagent**. Dismiss findings only with refuting evidence and put scope decisions to Elias. After fixes, rerun affected acceptance and guide checks, update the matrix, and re-review the changed integrated result. Use the owned `code-review` skill's `references/review-loop.md` controls, sharing the three-round default budget and finding ledger with any delivery coordinator. At most five rounds need an evidenced high-risk issue or explicit extension. If the same finding survives two fix attempts, a dismissed actionable finding returns, or required review is incomplete at the budget, put it to Elias; exhaustion is not approval.
   - Complete only when required proof passes, no confirmed actionable finding remains, and the final state matches the reviewed snapshot. Any later code change needs affected proof and review again.

8. Report the verified integration branch and ticket outcomes. Mark an existing draft PR ready or apply tracker updates only within current-task authority. Otherwise, preserve the proposed PR/tracker changes locally and report them as pending publication, not completed tracker state. Ask for any missing authority only after the exact changes are reviewable; its absence does not block completed local implementation or proof.

9. Clean up all **implementer subagent** worktrees.
