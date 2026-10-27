---
name: release
description: "Use when Elias requests Release or asks to prepare or execute a software release, pull request, deployment, or publication. Execute external actions only within current task authority; preparation alone does not authorize publication."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

# Release

## Outcome

The intended revision reaches the authorized target with verified readiness and post-release evidence.

## Method

Resolve exact branch, commit, artifact, environment, and authority; use `gh pr`, `gh release`, or `gh api` for GitHub state with the exact repository; review diff and repository template; gather required checks and real-surface proof; assess migrations, security, observability, and rollback; execute only authorized external actions; re-read resulting state.

## Boundaries

Readiness never grants merge, deploy, publish, tag, or message authority. Stop at the first unverified item in a release stack.

Prefer `gh`/`gh api` for structured GitHub release and PR operations; use another supported capability when it is materially better or the CLI is unavailable. Run it in a host/keyring-enabled context when the sandbox cannot see the macOS keyring; a sandbox-only invalid-token or connection result is not enough to declare the CLI unauthenticated. If no supported capability can perform the authorized operation, preserve prepared artifacts and report the exact blocker.

Write pull request bodies with the `pr` skill.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-2-skill](references/source-methods/source-2-skill.md)
