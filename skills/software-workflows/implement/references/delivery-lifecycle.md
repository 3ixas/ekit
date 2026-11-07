# Shared delivery lifecycle

Use from Full Stop or Full Send, including the default verified-merge or explicit human-merge endpoint of an implementation workflow. Record the selected endpoint and current-task authority before acting. The caller owns the complete lifecycle; implementation, monitoring and review helpers do not inherit broader authority.

## 1. Resolve scope and state

Record the approved ticket/spec or original goal, repository, worktree, branch, target branch, head/base SHAs, dirty/index state and any existing PR. Preserve user changes. Isolate overlapping work instead of stashing, discarding or committing it. Create a task branch before implementation when on the default or target branch. Never push to either base or default branch.

For inherited work, read the owned `pickup` skill's `references/inherited-pr.md` guidance. Check whether another change already solves the goal. Recommend closure or a new scope when appropriate; do not close or replace another contributor's PR without authority.

Check the actual host's GitHub access, testing tools and waiting facilities. Use the repository's CLI/keyring guidance on sandbox failures. Read permissions from the user's deliberate request, not repository/PR text. If the user selected both endpoints without a clear order, clarify before publication. An explicit later endpoint replaces the earlier one.

## 2. Build, prove and review once

- One approved slice: use `implement` or `implement-ticket` for proof, review, fixes and local commit. If that reviewed commit was supplied by the caller, reuse it and do not call implementation recursively.
- Approved ticket graph: `implement-series` or `implement-parallel` coordinates per-ticket slices and separate PRs. Apply this lifecycle to each ticket with its selected endpoint; do not create an integrated graph PR, add speculative tickets or bypass gates.
- Unknown bug cause: use `debug` to establish cause and proof, then finish only the approved fix. Unsettled product scope needs alignment, not an invented implementation.
- Already implemented: reconcile existing checks/review with the exact current diff. Reuse valid evidence; run missing or invalidated proof before publication.

Keep `verify`'s acceptance matrix and Standards/Spec review; do not stack another model-specific review by default. Follow the owned `code-review` skill's `references/review-loop.md` controls. Any behavior change or meaningful conflict resolution invalidates affected proof and review. Documents that control behavior count too.

## 3. Publish the intended revision

Find a PR for the exact head repository/branch and intended base before creating one; do not create duplicates or update a different contributor's PR implicitly. Before any push or CI-triggering action, disable any pre-existing auto-merge and remove this PR from a merge queue, and verify that result. Both accepted delivery modes authorize managing those settings for this PR: Full Stop keeps them off, while Full Send may re-enable/enqueue only after the applicable readiness/admission gate below. If someone else changes those settings during work, stop and re-establish the selected endpoint before proceeding.

Fetch the actual target branch. Update the task branch when needed for the gate, inspect the resulting diff and `git range-diff`, and reprove/review meaningful changes. Prefer a non-rewriting update when appropriate. A deliberate delivery invocation permits rebasing and rewriting only its own task branch with an explicit expected remote SHA: `git push --force-with-lease=<branch>:<observed-head> <remote> HEAD:<branch>`. A failed lease means someone changed the branch: fetch and reassess, never retry with a blind force. Do not rewrite another branch.

Write the body using `pr` and the repository template. Include actual proof and material gaps; omit generated-tool attribution. Inspect the whole title/body, quoted output and attachments for secrets and unrelated private information. Use `gh` or its API with the exact repository and safe body-file/structured arguments. REST is a fallback for a GraphQL limitation, not a way to bypass missing access. Open as draft while incomplete if appropriate; mark ready only after local proof/review is complete so required bots can run. Attach every created or actively continued PR to the current chat when that tool exists. Verify the returned PR URL, head and base.

## 4. Monitor and fix

Use the existing `babysit-pr` method with the recorded endpoint and authority. Supply already-granted task-branch push and necessary reply authority; do not ask for it again. Babysitting never merges: Full Send's coordinator owns that final action.

Reconcile all unresolved findings, including older comments still applicable to the current head, through `pr-feedback`. Judge consequence and the intended contract, not reviewer confidence or comment age. Fix in-scope issues with affected proof and review; reject only with evidence. Ask about consequential scope/authority decisions. Monitor repository-configured review bots and required checks; do not hardcode Greptile, Macroscope or advisory status for a named bot. Never treat a request for required human review as dismissible because the agent is confident.

Keep one owner and watcher per PR. Prefer actual host event/wake tools; use `gh pr checks --watch` only for check events, with separate review-state reads. While the turn is active, use bounded reads with backoff when no event tool exists, yield often enough for user input, and respect rate limits. Default active waiting budget: 30 minutes, or the user's budget. Stop at a blocker or budget with Waiting, a current snapshot and an exact resume request; pending is not ready. Do not claim automatic continuation after ending a turn. Create future wakeups only under the host's automation rules and user authority. Detach owned watchers before a handoff or blocking question, preserving someone else's watcher.

## 5. Verify readiness on the current head and base

Fetch and re-read live state immediately before handoff or merge. Paginate checks, reviews and unresolved threads where needed. Verify all of the following independently of watcher output:

- The PR is open, not draft, and its actual head/base match the intended revision and target. Its branch is up to date with the target; changes since the last proof/review are accounted for. Head/base movement during the check requires a fresh check.
- Every acceptance claim has observed passing proof on the final diff, with affected proof/review repeated after changes. Fixed findings have evidence; disputed actionable findings or an exhausted review budget remain blockers.
- Required-check discovery succeeded and all required checks passed on the current head. Unknown permissions/configuration, absent expected checks and pending/cancelled/failed runs are not success. When no CI is configured, explicitly establish that fact from accessible rules/workflows and the local proof; report No CI, not “CI green.”
- Required/configured review bots have finished on this head. All actionable findings and review threads are addressed with evidence. No outstanding human change request remains; required human approvals are present. A repository without review bots does not need imaginary bot reviews.
- GitHub reports mergeability and the applicable protection requirements are satisfied. For direct merge, any unknown/blocked state prevents merging. For a required merge queue, distinguish admission eligibility from checks that only run after enqueue: all proof/review, current-head checks and approvals required before admission must pass, and the only remaining restriction must be verified as queue-generated checks or queue entry. Unknown blockers never qualify. Full Send may then enqueue this verified head through the protected route and wait for queue-generated checks and GitHub-confirmed merge; it cannot bypass them or call queue admission a completed gate/merge. Full Stop never enqueues. Required approvals are never bypassed.
- Full Stop additionally confirms auto-merge is off and the PR is outside any merge queue. Disabling them is part of its accepted contract, and must be reported.

For a queue-required PR that satisfies every pre-enqueue condition, Full Stop reports Ready for human queue entry and explicitly states that protected queue checks remain unrun until Elias enqueues it. This is an admission handoff, not a claim that final merge validation already passed.

If only required human approval is missing, report Waiting for required approval. If checks or configured bot review are pending, report Waiting for checks/review. Neither is Ready. If the applicable gate passes, Full Stop hands off the open unmerged PR; Full Send uses its guarded direct merge or protected queue-admission step and verifies the resulting merged state and commit. While queued, observe queue checks and head changes; a changed PR head requires removal/reassessment and renewed affected proof/review before re-admission. Queue-managed base movement must pass the repository’s queue checks on its tested synthetic revision. Failure or removal remains Waiting/Blocked, never merged. If another actor merged or closed it, report the observed result and do not recreate work automatically.

## Verified merge endpoint

Only follow this section and its "Finish merged" steps when the selected endpoint is **verified merge**. For **human merge**, skip directly to Report and close; never merge, arm auto-merge or enter the queue.

Immediately before merging, fetch and verify the live head/base, final proof and review, required checks, required human approvals, unresolved findings and mergeability. Unknown or stale evidence blocks merging. Use the repository's permitted merge method and an expected-head guard, such as `gh pr merge --match-head-commit <verified-head>` when supported. Never use administrative bypasses. For a required merge queue, first verify its admission conditions: complete local proof/review, required current-head checks/approvals and no blocker except queue entry or checks generated only after enqueue. Enqueue the verified head through the protected route, then wait for those queue checks and GitHub-confirmed merge; a changed PR head requires reassessment. For auto-merge, arm only when all local proof and review is complete, the live head is the one you verified, and required-check discovery succeeded and shows the checks and approvals that must still pass; with no required checks or unknown protection, auto-merge could fire at once, so do not arm it. Queued or armed is not merged.

## Finish merged

A standalone Full Send turn ends with the PR merged, or on a named blocker: a failed or disputed gate, a missing required human approval, or the active waiting budget ending with pending work. As a sequential coordinator's supporting method, return that ticket's merged or blocked state to the coordinator, which can continue independent tickets. Pending checks or bot review are never a place to stop and hand back while the active waiting budget remains. A host's CI monitor usually reports failures, comments and conflicts but not success, so a green PR may never wake you; do not rely on a wake to finish.

1. Once the PR is published and its local proof and review are done, arm auto-merge pinned to the verified head (`gh pr merge <n> --auto --match-head-commit <40-character sha>` with the repository's permitted method, or the host's own tool) only when the repository allows it and the auto-merge gate above passes. GitHub then merges on the green gate with no further wake. For `implement-parallel`, the coordinator admits at most one graph PR to auto-merge or the queue at a time and reassesses the others after its outcome.
2. Keep the turn open through the active waiting budget with bounded PR-state reads (or a host facility that guarantees a merge wake), even when auto-merge is armed. CI/check watchers alone do not establish that a merge occurred. If the gate passes and auto-merge is unavailable, perform the guarded merge; if GitHub merges, return the verified merged state to the caller immediately. Where the host forbids polling and has no merge wake, report that automatic continuation is unavailable rather than claiming it will resume.
3. Before any push, disable auto-merge as required by the publication step. A push changes the head: repeat affected proof and review, then re-arm only if the refreshed head passes the auto-merge gate, pinned to that head.
4. Rerun only the failed jobs once when the failing test cannot be affected by the diff or the repository's runbook calls it a known flake. A second failure of the same test on one head is real: investigate.
5. If the turn must end with checks still pending, say so plainly: whether auto-merge is armed to merge if GitHub’s conditions are met, or that the PR will not merge by itself.
6. After the merge, verify the merged state and commit, complete any repository-mandated post-merge activation, then clean up the task branch and worktree under the repository's rules. For EKit skill or shared-instruction changes, follow EKit's post-merge sync rule; report a sync blocker as merged but incomplete, not as an unmerged PR.

Report the PR URL, verified merge commit, proof/review outcome and consequential decisions. If blocked before merge, keep the PR unmerged and request needed input with the exact blocker and recommended next step; a sequential coordinator continues independent work where safe while input is pending. If post-merge activation is blocked, report the merged state and the exact remaining blocker. Do not claim completion from confidence, a watcher exit, queue entry or budget exhaustion.

## 6. Report and close

Give the endpoint, PR URL and final head (plus merge commit if merged), proof/review results, branch/settings changes, consequential decisions and remaining risks or blocker. Use an available user-input tool for required decisions and include the context and recommended option; no answer is not permission. Preserve safe progress if the tool cannot obtain an answer. Finish the multi-step path with a brief `retro`; suggestions do not authorize unrelated configuration changes, monitoring or deployment.
