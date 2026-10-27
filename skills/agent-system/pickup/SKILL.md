---
name: pickup
description: Resume or take over handed-off work, a PR, branch or agent chat by checking intent, current source state, contributor credit and authorized continuation.
---

# Pickup

## Outcome

A validated resume plan followed by authorized continuation.

## Find the handoff

When given a PR, branch or chat instead of a handoff file, start with that source and read the [inherited-work guidance](references/inherited-pr.md); do not search for an unrelated local handoff. For a handoff file, look in this order and use the first match:

1. A path given with the request.
2. The newest file in `~/.agents/handoffs/<project>/`, where `<project>` is the main checkout's directory name, which is the same from any worktree (`basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"`), or the current directory's name outside a repository.
3. Legacy locations: files matching `*handoff*.md` (any case) in the OS temporary directory (`$TMPDIR`), newest first, whose file name contains the project name (with dots and spaces read as hyphens). A file that only mentions the project in its content is a candidate to show and confirm, never one to pick automatically.

Say which file you picked and its timestamp. If more than one recent candidate fits, list them and confirm which to use. If nothing is found, say so plainly and list every place you looked. Never start from scratch silently.

## Method

1. Read the selected source and its pointed evidence, then inspect current Git/worktree, issue, and test state relevant to the continuation.
2. Classify the inherited state as clean, diverged, incomplete, or stale. Preserve settled decisions and identify changed assumptions against the live evidence.
3. State the exact next action and continue within the existing authority when the direction remains valid. Done with reconciliation when each material discrepancy is resolved or raised as a concrete decision; continuation then follows the owning workflow.

## Boundaries

Do not repeat all discovery or trust stale checkmarks. Ask only when divergence materially changes direction or risk. Never delete or edit a handoff file.
