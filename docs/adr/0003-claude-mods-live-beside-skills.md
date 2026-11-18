# Claude Code plugins live beside skills

Claude Code mods are JavaScript plugins that run inside Claude Code and can
draw in its interface. They exist only for Claude Code, while this repository
is the canonical source for instructions shared by Codex, Claude Code, and
OpenCode. Mods still live here, as the one mods plugin at `plugins/elias-mods/`,
because they enforce and extend the same personal system the skills define,
such as supporting-only routing, and should change under the same review and
history.

The plugin sits outside the `skills/`, `candidates/`, and `paused/`
lifecycles and is not part of `sync`, `claude-sync`, or `opencode-sync`
projections. During development it loads through `CLAUDE_CODE_PLUGIN_DIRS`,
since the Desktop app cannot take `--plugin-dir`; installing it for daily use
is a separate, previewed step with a rollback path. The repository's unit
tests run `claude plugin validate --strict` and `claude plugin test` on it
through `tests/test_elias_mods.py`, which skips when the `claude` CLI is
missing.

Elias-mods stays a Desktop-only plugin. A plain Claude Code hook that must
also run where mods do not, such as T3 Code, lives in its own plugin beside
it (`plugins/ekit-context/`) under the same rules: outside the projections,
installed in a separate step, and validated by the unit tests when the
`claude` CLI is present.

Mods may observe, hold, or refuse a tool call, but never approve one: auto
mode already owns approvals, and an unseen second approver would be hard to
reason about.
