# ekit-context

A plain Claude Code command hook, so it runs on Claude Code Desktop and in T3 Code alike. It replaces nothing in elias-mods, which stays Desktop-only.

Before each main-thread prompt, the `UserPromptSubmit` hook reads the latest main-thread `usage` in the transcript (input, cache-creation and cache-read tokens) and divides it by `context_window` (default 1,000,000, the window of Opus 5.5 and Sonnet 5.5 in Claude Code). Once fill reaches `handoff_at` (default 70), it adds one line of context asking Claude to offer a handoff and, in T3 Code, to open the pickup thread with `t3_thread_launch` after Elias approves.

- It fires once per crossing. A flag under the plugin's data folder clears when fill drops below the threshold, as after compaction.
- Subagent prompts are ignored.
- Any error leaves the prompt untouched.
- `handoff_at` mirrors the elias-mods option of the same name; change both together. A test keeps their defaults equal.
- `context_window` is not read from the session: hooks receive no window size. On a model with a smaller window, set it to that size.
- On Desktop the elias-mods barometer's **Handoff** button still appears; this hook is the reminder Claude itself acts on.

Install it from this repository's marketplace, which Claude Code already knows as `elias-agent-skills`:

```sh
claude plugin install ekit-context@elias-agent-skills
```

T3 Code runs Claude with `~/.claude`, so the installed plugin applies there too. Tests: `tests/test_context_handoff.py`.
