---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
---

Write a handoff document summarising the current conversation so a fresh agent can continue the work.

Save it to `~/.agents/handoffs/<project>/<YYYY-MM-DD-HHMM>-<topic>.md`, not the current workspace. `<project>` is the main checkout's directory name, which is the same from any worktree (`basename "$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")"`), or the current directory's name outside a repository. `<topic>` is a short kebab-case slug. Create the folder if needed, and never overwrite or delete an earlier handoff.

Include a "suggested skills" section naming which instructions the next agent should load through its available skill mechanism or read as files.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

End your reply with the absolute path you wrote and the exact resume command, so a fresh session after a context reset can find it: `/pickup <absolute-path>` in Claude Code, `$pickup <absolute-path>` in Codex.


## Host note

The handoff folder is shared by Codex and Claude Code, so either host can resume it. Keep the document self-contained: state the goal, settled decisions, authorized scope, current work state, observed checks, unresolved blockers, and exact next action, linking existing artifacts for detail. Do not rely on host-specific commands or hidden chat history. If writing fails because the sandbox denies the folder, say so, write to the OS temporary directory as a fallback, and report both the failure and the fallback path.
