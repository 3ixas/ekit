---
name: modernize
description: "Use when Elias explicitly asks to modernize or rebase an aging PR: reassess its intent against the current base, then update only a still-useful branch within authority."
---

# Modernize

Decide whether the original goal still belongs before updating the branch. A request to assess an old PR is read-only; a deliberate request to modernize/rebase it authorizes that task's branch update, not merge, closure, changed base or a product rewrite.

## Establish intent and changed context

1. Read repository instructions and resolve the exact PR URL, head repository/branch/SHA, target base/SHA, author, complete diff, linked issue, commits, checks and review threads. Fetch the actual base and PR head; record the merge base and original commit series.
2. Preserve dirty/index changes. Use a suitable existing isolated worktree or create one at the recorded head when needed; do not overwrite another active checkout.
3. Inspect base changes since divergence, related open/merged PRs, current callers, contracts and invariants. Determine whether the problem is already solved, the code was moved/deleted, responsibility changed or the original approach would reintroduce obsolete behavior. Do not equate a conflict-free rebase with conceptual correctness.

## Choose before mutating

- **MODERNIZE:** goal and implementation still fit. Under update authority, rebase and resolve conflicts against the current intent and invariants.
- **REWORK:** goal is useful but needs a meaningfully different implementation. Show the smallest credible change and pause for its scope decision before rewriting or pushing it.
- **CLOSE:** current evidence shows the work is superseded or no longer useful. Cite that evidence and stop; recommend closure without closing unless separately authorized.

For MODERNIZE, compare the pre/post commit series with `git range-diff` and inspect the complete final diff. Use `verify` for affected acceptance claims, and `code-review` for behavior or meaningful conflict-resolution changes under the owned `code-review` skill's `references/review-loop.md` controls. Preserve intended supported behavior and genuine human authorship.

Immediately before pushing, reread the remote head and target. If either moved, reassess; do not overwrite intervening work. When pushing the authorized task branch after a rebase, use the explicit observed lease: `git push --force-with-lease=<branch>:<original-remote-head> <remote> HEAD:<branch>`. A failed lease requires fetching and reassessment, never an unqualified force push.

If the PR has auto-merge enabled or is queued, a branch update could merge it. Stop before that update unless the user authorized disabling those settings or selected Full Stop/Full Send for this PR. Do not silently inherit merge authority. Use `pr-feedback` for any necessary review replies, and post only within authority.

## Report

Lead with MODERNIZE, REWORK or CLOSE and the evidence. Give the PR URL, meaningful base changes, pre/post head, range-diff interpretation, proof/review results, push result if authorized, and the remaining decision. Assessment alone makes no external change. Modernize alone never merges, closes or changes the PR's base.
