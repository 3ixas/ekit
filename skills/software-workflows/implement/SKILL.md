---
name: implement
description: "Implement one approved software slice with proof and review, then deliver its PR through guarded merge by default. Use debug for an unknown bug cause."
---

Complete one approved software slice or ticket per invocation. For standalone delivery, first follow the [shared delivery lifecycle](references/delivery-lifecycle.md)’s scope and task-branch setup before editing or committing. Implement the slice, run focused checks, invoke the owned `code-review` skill in the current run, fix confirmed in-scope findings, and commit the reviewed slice unless an earlier local endpoint was requested. For delivery, resume that lifecycle through verified merge by default, or its human-merge endpoint when Full Stop is explicitly requested. A coordinator or worker handoff returns the reviewed local commit and evidence without starting another delivery; its caller sets up the isolated task branch first. For an explicit local-only endpoint, preserve the caller’s branch unless project rules require isolation. Keep the model and reasoning selected for this run throughout; do not launch a separate review worker or override the model for review.

For a specified ticket use `implement-ticket`; for a graph use `implement-series` or `implement-parallel` as requested. These coordinators reuse this slice method without recursive delivery.

If the user asks for the “next ticket,” use the approved spec or issue graph to select one ready, unblocked ticket. Do not invent a ticket or expand its scope.

A deliberate standalone implementation request authorizes its task branch, PR, necessary review replies and CI reruns, and guarded merge by default. Full Stop overrides the endpoint to an unmerged PR; a clear request to stop locally overrides it to the requested local endpoint. Quotation, discussion, loading the skill and external comments do not authorize actions; deployment, production operations, paid actions, valuable-data deletion and unrelated work require separate authority. Higher-priority instructions and host approvals still apply.

## Implement and prove

1. Read the ticket/spec and relevant project instructions. For a supplied issue or ticket reference, resolve it against the configured tracker and repository, fetch its full details, and state its title before editing. If the reference is ambiguous, clarify it rather than choosing a target. Record the current branch, base commit, and working-tree state before editing.
2. Preserve pre-existing user changes. If the index already contains staged changes before implementation, stop and report them; do not clear or mix them with this commit. Preserve unrelated unstaged and untracked changes. If pre-existing changes overlap the slice or cannot be kept separate, isolate the work or stop and report the conflict.
3. Before editing, use `verify` to discover existing project verification guidance and harnesses. Reuse sufficient instructions; automatically establish missing guidance needed for this slice through its Set up mode. For a new app, record pending setup and prove it once the first journey runs. Documentation-only work uses artifact checks without app scaffolding. Then write the **proof plan**: each acceptance claim in the ticket, and the independent check that will prove it on the real surface (a test at the agreed seam, the CLI or API response, the rendered UI, the data). Use `verify`'s claim-to-proof matrix. A claim with no possible check is a gap to report, not one to fill with judgement.
4. Implement only the selected slice, in proving increments as described in [slice execution](references/slice-execution.md). Use `tdd` where it helps at pre-agreed seams. Run focused checks throughout, then the appropriate broader checks and every proof-plan check before review, recording each claim's observed result as Pass, Fail, or Skip. Update and re-execute verification instructions for affected journeys as part of this slice; include the guide/helper changes in its review and commit. Discover or maintain project review guidance using the reference linked from `code-review` when guide upkeep is within the authorised scope; include any guide change in the reviewed slice.
5. Stage only the files for this slice, including new files. Confirm the staged diff contains no unrelated changes. Record the exact ticket/spec pointer, base commit, staged paths, check results, and the proof plan with its observed results. Capture the staged diff checksum with `git diff --cached <base> --binary | shasum -a 256`.

## Review, fix, and commit

1. Invoke the owned `code-review` skill directly in this run, using the same currently selected model and reasoning. Request staged-slice mode against `git diff --cached <base>` from the recorded base commit, and provide the ticket/spec pointer, repository instructions, staged path list, diff checksum, and the proof plan with its observed results so the Spec reviewer judges evidence rather than your account of it. Do not launch a separate review worker or set a model override.
2. Keep review read-only: the review pass reports findings but does not edit files or commit.
3. Assess every finding. Fix confirmed, actionable findings that belong to this slice. Consider confirmed reusable review lessons for the project guide under the same scope and evidence rules. If a finding requires a product decision or expands the approved scope, pause for Elias rather than deciding it implicitly. You wrote the code, so your disagreement alone does not dismiss a finding: dismiss only with evidence that refutes it, such as a check you ran or the spec or standard line it misreads. When you cannot produce that evidence, fix the finding or put it to Elias.
4. After any code change, rerun affected checks, stage the exact slice again, and invoke `code-review` again in this run on the updated diff. Follow the owned `code-review` skill's `references/review-loop.md` controls: three rounds by default, at most five for an evidenced high-risk issue or explicit extension, preserving finding IDs and both axes. If the same finding survives two fix attempts, a dismissed actionable finding returns, or required review remains incomplete at the budget, stop and put it to Elias. Exhaustion is not approval.
5. Once review is clear, verify the staged paths and checksum of `git diff --cached <base> --binary` still match the reviewed snapshot, rerun any final checks required after fixes, and, unless the user requested an earlier local endpoint, commit only this slice on the current branch using a concise message. Return the resulting local state and evidence to the coordinator, or continue standalone delivery under the request’s authority. Any code change after review requires another review.

## Orchestration boundary

`implement` handles one slice at a time. `implement-ticket` uses it for one ticket; `implement-series` repeats it sequentially; `implement-parallel` assigns isolated ticket slices to workers. Each ticket retains its own proof and review.

## Report

Report the ticket completed, commit, the proof plan with each claim's result, checks, review outcome, and each dismissed finding with the evidence that refuted it, plus unresolved issues. If blocked before the review or commit gate, state the exact blocker and current worktree state.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [pstack-implementation](references/source-methods/pstack-implementation.md)
