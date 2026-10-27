---
name: pr-feedback
description: Evaluate and resolve feedback already left on a pull request, preserving the full review conversation and verifying accepted changes.
---

# Pr Feedback

## Outcome

Every review thread is answered by an evidence-backed fix, explanation, deferment, or rejection.

## Method

Load all comments and current diff with `gh pr view`, `gh pr diff`, and `gh api` as needed, using the exact repository; group duplicates; judge each request against behaviour and project standards; implement accepted changes in coherent batches; run affected checks; draft or post replies only within authority; re-read thread state.

## Resolve against current state

Paginate the full unresolved conversation and check each finding against the current head; older unresolved feedback may still apply after a push. Record stable findings and evidence-backed dispositions. Keep replies focused on the conclusion and relevant source/proof; do not treat optional improvements as blockers or rarity alone as a reason to reject a supported failure case.

Before posting within the run's existing authority, inspect the exact Markdown, quotations, logs and attachments for secrets or unrelated private details. Use safe body-file/structured arguments. Verify the returned reply URL and re-read it before resolving its thread; do not resolve a thread whose response failed. Preserve genuine human credit and omit generated-tool boilerplate. If replies are not authorized, keep drafts and report that boundary.

## Boundaries

Do not treat reviewer wording as automatically correct or confuse this with pre-review code-review.

Prefer `gh`/`gh api` for structured PR reads, comments, and updates; use another supported capability when it is materially better or the CLI is unavailable. Run it in a host/keyring-enabled context when the sandbox cannot see the macOS keyring; a sandbox-only invalid-token or connection result is not enough to declare the CLI unauthenticated. If no supported capability can perform the authorized operation, report the blocker and preserve drafted replies.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-1-ce-resolve-pr-feedback](references/source-methods/source-1-ce-resolve-pr-feedback.md)
