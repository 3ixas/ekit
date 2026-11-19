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

End your reply with the absolute path you wrote and the exact resume command in its own fenced code block, so it can be copied in one go from this thread later: `/pickup <absolute-path>` in Claude Code, `$pickup <absolute-path>` in Codex.


## Host note

The handoff folder is shared by Codex and Claude Code, so either host can resume it. Keep the document self-contained: state the goal, settled decisions, authorized scope, current work state, observed checks, unresolved blockers, and exact next action, linking existing artifacts for detail. Do not rely on host-specific commands or hidden chat history. If writing fails because the sandbox denies the folder, say so, write to the OS temporary directory as a fallback (`$TMPDIR` when set, otherwise `/tmp` on Unix; `%TEMP%` on Windows), and report both the failure and the fallback path.

In T3 Code, when Elias approves a handoff and the file is written, open the pickup thread: call `t3_thread_launch` in the same project with a prompt that asks the new thread to use the pickup skill on the absolute path, then give Elias the thread. Do not launch it before the approval or when Elias asks to resume elsewhere. When an owning workflow that Elias deliberately requested already authorizes the handoff and launch, such as an Implement Series relay, that request is the approval; follow the workflow's title, workspace and retry rules for the launch.

In T3 Code, once the file is written, also settle this thread with `t3_thread_organize` (`action: "settle"`, no `threadId`) so the handoff stays its last message; T3 applies it at the end of the turn. Skip settling when Elias wants to keep working in this thread, or when writing failed and no handoff exists.
