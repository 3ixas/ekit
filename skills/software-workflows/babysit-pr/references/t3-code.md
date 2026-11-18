# T3 Code PR watching

As of T3 Code 0.1.10 (server watch added in pingdotgg/t3code#15057, bot edits in #15415).

- **Owner.** Subagents cannot see `watch_pull_request`. When running under a coordinator, return the watch request to the thread that owns the PR.
- **What wakes the thread.** T3 reads each watched PR about once a minute and wakes the thread when a check fails, when required checks pass, when someone else comments or reviews (including a bot editing its comment), or when the branch conflicts with its base. A wake is a prompt to run one pass, not a readiness verdict.
- **When it stops.** On merge or close, after ten wakes caused only by comments, or after fifteen minutes of failing to read the PR. T3 posts a note when it stops for a read failure. Do not count on a wake for a merge: a coordinator waiting to verify a merge keeps its bounded checks.
- **Re-arming.** Re-arm once after a stop that leaves work open. A second stop from comment-only wakes means the conversation needs Elias: report it instead of re-arming.
- **Budget.** The active waiting budget covers time this turn spends checking; an armed watch may outlive the turn because T3 wakes the thread. End such a turn with **Waiting, watch armed**, the snapshot and the resume request.
