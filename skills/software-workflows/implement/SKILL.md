---
name: implement
description: "Implement one approved software slice end to end: focused checks, code review, in-scope fixes, and a local commit. For a bug, use it when the cause and fix are already known; otherwise use debug."
---

Complete one approved software slice or ticket per invocation. A normal invocation implements the slice, runs focused checks, invokes the owned `code-review` skill in the current run, fixes confirmed in-scope findings, and commits the reviewed slice. Then stop; another invocation handles the next ticket. Keep the model and reasoning selected for this run throughout; do not launch a separate review worker or override the model for review.

If the user asks for the “next ticket,” use the approved spec or issue graph to select one ready, unblocked ticket. Do not invent a ticket or expand its scope.

An explicit Full Stop or Full Send request selects a separate delivery coordinator around this one-slice method. Return the reviewed local commit and evidence to that coordinator; its accepted task-specific authority owns publishing and the final endpoint. Without that request, this skill still stops at the local commit.

## Implement and prove

1. Read the ticket/spec and relevant project instructions. Record the current branch, base commit, and working-tree state before editing.
2. Preserve pre-existing user changes. If the index already contains staged changes before implementation, stop and report them; do not clear or mix them with this commit. Preserve unrelated unstaged and untracked changes. If pre-existing changes overlap the slice or cannot be kept separate, isolate the work or stop and report the conflict.
3. Before editing, use `verify` to discover existing project verification guidance and harnesses. Reuse sufficient instructions; automatically establish missing guidance needed for this slice through its Set up mode. For a new app, record pending setup and prove it once the first journey runs. Documentation-only work uses artifact checks without app scaffolding. Then write the **proof plan**: each acceptance claim in the ticket, and the independent check that will prove it on the real surface (a test at the agreed seam, the CLI or API response, the rendered UI, the data). Use `verify`'s claim-to-proof matrix. A claim with no possible check is a gap to report, not one to fill with judgement.
4. For a material visual change, capture a rendered baseline before editing where feasible; after the change capture the same route, state, viewport and representative data. Record unavailable baselines instead of implying a comparison. Images supplement interaction and accessibility proof, not replace it. A small nonvisual change needs no screenshot or whole-app audit.
5. Implement only the selected slice, in proving increments as described in [slice execution](references/slice-execution.md). Use `tdd` where it helps at pre-agreed seams. For an affected UI, stress the changed component or journey with relevant realistic extremes and failure states, using `ui-polish` resilience guidance when useful; reproduce and fix clear in-scope defects, then recheck. Run focused checks throughout, then the appropriate broader checks and every proof-plan check before review, recording each claim's observed result as Pass, Fail, or Skip. Update and re-execute verification instructions for affected journeys as part of this slice; include the guide/helper changes in its review and commit.
6. Stage only the files for this slice, including new files. Confirm the staged diff contains no unrelated changes. Record the exact ticket/spec pointer, base commit, staged paths, check results, and the proof plan with its observed results. Capture the staged diff checksum with `git diff --cached <base> --binary | shasum -a 256`.

## Review, fix, and commit

1. Invoke the owned `code-review` skill directly in this run, using the same currently selected model and reasoning. Request staged-slice mode against `git diff --cached <base>` from the recorded base commit, and provide the ticket/spec pointer, repository instructions, staged path list, diff checksum, and the proof plan with its observed results so the Spec reviewer judges evidence rather than your account of it. Do not launch a separate review worker or set a model override.
2. Keep review read-only: the review pass reports findings but does not edit files or commit.
3. Assess every finding. Fix confirmed, actionable findings that belong to this slice. If a finding requires a product decision or expands the approved scope, pause for Elias rather than deciding it implicitly. You wrote the code, so your disagreement alone does not dismiss a finding: dismiss only with evidence that refutes it, such as a check you ran or the spec or standard line it misreads. When you cannot produce that evidence, fix the finding or put it to Elias.
4. After any code change, rerun affected checks, stage the exact slice again, and invoke `code-review` again in this run on the updated diff. Follow the owned `code-review` skill's `references/review-loop.md` controls: three rounds by default, at most five for an evidenced high-risk issue or explicit extension, preserving finding IDs and both axes. If the same finding survives two fix attempts, a dismissed actionable finding returns, or required review remains incomplete at the budget, stop and put it to Elias. Exhaustion is not approval.
5. Once review is clear, verify the staged paths and checksum of `git diff --cached <base> --binary` still match the reviewed snapshot, rerun any final checks required after fixes, and commit only this slice on the current branch using a concise message. Do not push unless separately requested. Any code change after review requires another review.

## Orchestration boundary

`implement` handles one ticket per invocation. `implement-spec` is the parallel alternative for a whole spec: its own implementer subagents build tickets with `tdd`, and it runs one `code-review` over the integration branch at the end, so it does not call this skill.

## Report

Report the ticket completed, commit, the proof plan with each claim's result, checks, review outcome, and each dismissed finding with the evidence that refuted it, plus unresolved issues. If blocked before the review or commit gate, state the exact blocker and current worktree state.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [pstack-implementation](references/source-methods/pstack-implementation.md)
