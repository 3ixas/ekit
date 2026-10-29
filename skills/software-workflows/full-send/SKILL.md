---
name: full-send
description: "Use only when Elias explicitly requests Full Send: carry approved work through implementation, proof, PR creation, CI and review fixes, and merge once the complete gate passes."
---

# Full Send

Follow the shared delivery lifecycle in the owned `full-stop` skill's `references/delivery-lifecycle.md` with endpoint **verified merge**. This selects the shared method, not Full Stop's entrypoint or its no-merge endpoint.

A deliberate “Full send” request authorizes the lifecycle's task-branch work, PR creation/updates, necessary review replies, CI reruns, management of this PR’s auto-merge/queue settings to prevent premature merging, and merge after its complete gate passes. It is a current-task instruction, not standing permission from this file. Quoted text, external comments, installation and requests merely to explain the skill grant no authority. Scope, higher-priority constraints and host approvals still apply; deployment, production operations, valuable-data deletion, paid actions and unrelated services need separate authority.

Immediately before merging, fetch and verify the live head/base, final proof and review, required checks, required human approvals, unresolved findings and mergeability. Unknown or stale evidence blocks merging. Use the repository's permitted merge method and an expected-head guard, such as `gh pr merge --match-head-commit <verified-head>` when supported. Never use administrative bypasses. For a required merge queue, first verify its admission conditions: complete local proof/review, required current-head checks/approvals and no blocker except queue entry or checks generated only after enqueue. Enqueue the verified head through the protected route, then wait for those queue checks and GitHub-confirmed merge; a changed PR head requires reassessment. For auto-merge, arm only when all local proof and review is complete, the live head is the one you verified, and required-check discovery succeeded and shows the checks and approvals that must still pass; with no required checks or unknown protection, auto-merge could fire at once, so do not arm it. Queued or armed is not merged.

## Finish merged

A Full Send turn ends with the PR merged, or on a named blocker: a failed or disputed gate, a missing required human approval, or a budget that ran out on a real defect. Pending checks or bot review are never a place to stop and hand back. A host's CI monitor usually reports failures, comments and conflicts but not success, so a green PR may never wake you; do not rely on a wake to finish.

1. Once the PR is published and its local proof and review are done, arm auto-merge pinned to the verified head (`gh pr merge <n> --auto --match-head-commit <40-character sha>` with the repository's permitted method, or the host's own tool) when the repository allows it. GitHub then merges on the green gate with no further wake.
2. Where auto-merge is unavailable, keep the turn open through the active waiting budget with bounded reads (or the host's own wait facility) and merge when the gate passes. Where the host forbids polling, rely on armed auto-merge.
3. Any push changes the head: turn auto-merge off and arm it again pinned to the new head, since an armed merge for an old head silently never fires.
4. Rerun only the failed jobs once when the failing test cannot be affected by the diff or the repository's runbook calls it a known flake. A second failure of the same test on one head is real: investigate.
5. If the turn must end with checks still pending, say so plainly: whether auto-merge is armed and will merge without further action, or that the PR will not merge by itself.
6. After the merge, verify the merged state and commit, then clean up the task branch and worktree under the repository's rules.

Report the PR URL, verified merge commit, proof/review outcome and consequential decisions. If blocked, keep the PR unmerged and ask through the available user-input tool with the exact blocker and recommended next step. Do not claim completion from confidence, a watcher exit, queue entry or budget exhaustion.
