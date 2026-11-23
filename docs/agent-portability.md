# Use the owned skills across agents

This repository is the only editable source for the approved skills and shared personal instructions. Generated runtime copies are projections for each agent. Edit the source here, then sync the hosts you use.

Credentials are not part of the intended repository or sync contract. Sync projects only skills and instructions; publication scanning and its limits are recorded in [publication readiness](publication-readiness.md). An agent may use local CLI credentials or its own connected accounts, but availability in one app is not guaranteed in another. Verify that the receiving agent can perform an integration or action before a skill reports success.

## First setup

For browser downloads and selective adoption at work, follow [download skills for work](work-downloads.md). Full sync below is for a machine where you intend to install the personal system, including global instructions.

After the repository is public, HTTPS cloning requires no GitHub login:

```sh
git clone https://github.com/3ixas/ekit.git
cd ekit
```

The address is intended for the later authorised public repository. It may not exist or permit anonymous access during preparation; no public access or workstation result is claimed here.

```sh
git pull
```

Then run its checks and review each projection before applying it:

```sh
python3 scripts/skills.py check
python3 -m unittest discover -s tests -v
python3 scripts/skills.py sync
python3 scripts/skills.py claude-sync
python3 scripts/skills.py opencode-sync
python3 scripts/skills.py t3-sync
python3 scripts/skills.py antigravity-sync
```

The five sync commands above are previews. Read the additions, changes, removals, target paths, and backup plan before applying a projection:

```sh
python3 scripts/skills.py sync --apply
python3 scripts/skills.py claude-sync --apply
python3 scripts/skills.py opencode-sync --apply
python3 scripts/skills.py t3-sync --apply
python3 scripts/skills.py antigravity-sync --apply
```

### Externally managed skills

List external skill directory names in `config/runtime.json` under `external_skills` before syncing (for example `yab-browser`). EKit carries those directories through its shared-runtime sync but does not own, update, or include them in its file manifest. The external provider remains responsible for installing and updating them. An absent external directory is left absent; symlinked external directories and collisions with EKit-owned skill IDs stop the sync. Unregistered extras are still proposed for removal, so inspect every preview. A concurrent external change detected during staging aborts the sync; avoid running vendor setup at the same time.

Use `sync --apply --adopt-unmanaged` only for the one-time migration when the Codex/shared skill directory already exists without this repository's ownership marker. The command backs up that directory before replacing it. Do not hand-edit installed skill copies.

## Routine updates and checks

After changing the canonical repository, run the unit tests and `check`, preview every host projection, then apply only the projections you use. Start a new agent session after syncing so the host discovers the current instructions and skill descriptions.

```sh
python3 scripts/skills.py check
python3 -m unittest discover -s tests -v
python3 scripts/skills.py sync
python3 scripts/skills.py claude-sync
python3 scripts/skills.py opencode-sync
python3 scripts/skills.py t3-sync
python3 scripts/skills.py antigravity-sync
python3 scripts/skills.py doctor
python3 scripts/skills.py claude-doctor
python3 scripts/skills.py opencode-doctor
python3 scripts/skills.py t3-doctor
python3 scripts/skills.py antigravity-doctor
```

Use `python3 scripts/skills.py updates` to check pinned upstream sources without changing owned skill content. Use `python3 scripts/skills.py capabilities` for per-host tool, orchestration, routing, and catalog evidence. Add `--skill <id>` to focus the report on one skill's tool and routing dependencies. `--catalog-warning-tokens N` sets a local early-warning threshold; it is an estimate, not a published Codex limit. The report checks local executable prerequisites, but cannot see every app's live session permissions or connected-tool catalogue.

## What each host receives

| Host | Shared instructions | Owned skills | Invocation and limits |
|---|---|---|---|
| Codex | `~/.codex/AGENTS.md` | `~/.agents/skills` | User-requested skills permit model loading through `allow_implicit_invocation: true`. `$skill-name` is optional. |
| Claude Code | `~/.claude/CLAUDE.md` links to shared instructions; generated routing in `~/.claude/rules/elias-agent-skills.md` | `~/.claude/skills` links to the managed runtime | Owned skills remain model-loadable; `/skill-name` is optional. The plugin checks supporting ownership without redirecting requested workflows to slash commands. |
| Antigravity | Managed `~/.gemini/GEMINI.md` (T3 Code 0.1.11+ links it into each Antigravity profile) | `~/.gemini/config/skills` links to `~/.agents/skills` | Skills load by name and description. User-requested and supporting-only routing are guidance in the managed rules, not enforced. |
| OpenCode | `~/.config/opencode/AGENTS.md` | Native discovery from `~/.agents/skills` | User-requested skills remain model-loadable; V2 metadata explicitly enables autoinvocation. Stable V1 follows descriptions and instructions. |

`explicit` means **user-requested**, not manual-command-only. Natural language and dictation count when they name or clearly request the workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Multiple requested methods and supporting handoffs may compose under one primary owner without another invocation. Request recognition is model-guided on every host, not a deterministic permission boundary. Supporting-only routing is guidance; the Claude plugin can warn or refuse missing ownership. Loading a skill grants no additional action authority.

The [OpenAI skills guide](https://developers.openai.com/plugins/concepts/skills) describes metadata-based discovery and direct invocation. The [Claude Code skills guide](https://code.claude.com/docs/en/skills) documents description-based selection, `/skill-name`, and `disable-model-invocation`. [OpenCode's skills guide](https://opencode.ai/docs/skills) documents shared Agent Skills paths and on-demand loading; V2 routing details are in the [V2 guide](https://opencode.ai/v2/docs/skills).

Skills describe workflows. The host, MCP server, or executable provides access and performs actions. For example, a local `gh auth status` result does not prove that a Claude or OpenCode session can read this repository's issues. The [capability report](../scripts/capabilities.py) preserves that distinction. Configure integrations at the layer they require, then verify each one from the host session that will use it.

For the approved free Motion documentation and shadcn integrations, see [component MCP setup](component-mcp.md). MCP configuration, backups and project registries are separate from skill projection.

## T3 Code

T3 Code is Elias's primary development host. It is not a separate skill host: it runs Claude through the Claude Agent SDK with `~/.claude`, and Codex through its app server with `~/.codex`, including `~/.codex/AGENTS.md`. Its threads therefore receive the Claude Code and Codex projections above. T3 adds its own `t3-code` tools to every thread, including `delegate_task`, `t3_thread_launch`, `watch_pull_request`, `preview_*` and scheduled tasks, plus orchestration instructions of its own.

| Behavior in T3 | Consequence |
|---|---|
| Background work goes through `delegate_task`, never a background native agent | Foreground native subagents still work; background and cross-provider children use `delegate_task`. |
| `preview_*` is not used unasked to verify or show the agent's own edit | Verification works off-screen; agents open the live preview when Elias asks or the change is mainly visual. |
| `html_preview` and `html_render` reach every provider's thread; Claude artifacts reach only Claude threads | Visual options and design directions render inline through `html_render` whatever the model; an artifact is the choice for phone review, element comments or sharing. Screenshots stay as the agent's own check evidence. |
| Worktrees do not isolate ports or databases | Each worktree's dev server needs its own port. |
| Claude task-list tools are off unless the Claude instance sets `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` | Set it in T3's Claude provider environment. |
| Desktop mods, such as the elias-mods band, do not draw | Plain Claude Code hooks still run. |
| No context barometer | The `ekit-context` plugin's hook asks Claude to offer a handoff at the threshold and, after approval, open the pickup thread. |

`t3-sync` keeps the T3 settings EKit manages, listed in `config/t3-settings.json`: provider environment variables such as `CLAUDE_CODE_ENABLE_TODO_TOOLS=1`, default and fallback models, favorites, the default permission mode, worktree cleanup and per-project default models. T3 rewrites its settings file whenever Elias changes something in the app, so `t3-sync` merges only those keys and leaves every other key as it is. It resolves projects by folder through a read-only, consistent snapshot of T3's state database and skips a project T3 has not added yet. T3 watches the file and keeps an external edit, so applying while the app runs is supported; each apply saves the previous file under `~/.t3/ekit-backups`. `t3-doctor` fails when a managed key has drifted and warns about skipped projects and about worktrees under `~/.t3/worktrees` whose branch was deleted upstream, as GitHub does after a merged PR. Squash merges leave no local trace, so a branch still on GitHub is not reported.

Load inventory, 2026-11-18, T3 Code desktop 0.1.10 with Claude Opus 5.5 in auto mode, read-only: the thread loaded the shared instructions, generated routing rules, the project `AGENTS.md` through `CLAUDE.md`, about 175 skills including plugin skills, the Concise output style, a SessionStart hook, auto memory and the native Agent tool. Task-list tools and the elias-mods band were absent. This proves what loaded, not how the agent acts on it; the behavioral checks below remain to be run in T3.

## Antigravity

Antigravity runs Gemini 4 Neon. In T3 Code it is a provider like Claude and Codex, started with a private `--gemini-dir`: `~/.t3/userdata/providers/antigravity/<sha256 of the instance id>`. That profile isolates credentials, hooks and MCP. Since T3 Code 0.1.11 (pingdotgg/t3code#39531), T3 links `~/.gemini/GEMINI.md` and `~/.gemini/AGENTS.md` into the profile root at session launch alongside the skill folders `~/.gemini/config/skills` and `~/.gemini/antigravity-cli/skills`; T3 never replaces an existing real file in a profile and removes a link whose target is gone. Antigravity never reads `~/.agents/skills` directly.

`antigravity-sync` writes one managed `GEMINI.md` (the shared instructions plus generated routing) to `~/.gemini/GEMINI.md` and makes `~/.gemini/config/skills` a link to the shared `~/.agents/skills` runtime, replacing only an empty folder the harness left behind. A `skills.json` registration would not work in T3, because T3 reads only that linked skills folder from `~/.gemini`. To migrate an earlier install without double-loading rules, `antigravity-sync --apply` backs up and removes stale managed `GEMINI.md` copies under `~/.gemini/config` and any existing T3 profiles under `~/.t3/userdata/providers/antigravity`. `antigravity-doctor` does not fail before T3 creates a profile; for every existing profile it verifies that `<profile>/GEMINI.md` links to `~/.gemini/GEMINI.md` and that no stale managed `GEMINI.md` copy remains in the profile or in `~/.gemini/config`. Because T3 creates `<profile>/GEMINI.md` when a session launches, migrating an existing profile requires starting a fresh Antigravity thread in T3 Code 0.1.11+ after `antigravity-sync --apply` before `antigravity-doctor` passes. Unmarked files at `~/.gemini/GEMINI.md`, edited managed files, and a real skills folder stop the sync; every apply saves a snapshot under `~/.gemini/ekit-backups` that can be restored with `python3 scripts/skills.py antigravity-sync --rollback <snapshot>` (which refuses to overwrite post-sync edits). Antigravity truncates a rule file over 24,000 bytes, so the sync refuses a larger projection.

| Behavior | Consequence |
|---|---|
| T3 Code's Antigravity sessions have no `watch_pull_request` | Delivery polls PR state at bounded intervals while the turn is active. |
| Some T3 Code Antigravity sessions expose neither `t3_thread_launch` nor `delegate_task` (series threads for #55 and #56, 2026-11-20) | An Engineer that escalates without `t3_thread_launch` writes the escalation handoff, stops and gives Elias the resume command for a Lead thread; Engineer→Lead cross-role review falls back to same-role review. |
| Antigravity creates empty `.gemini/skills` and `.agents/skills` folders in a workspace | Git ignores them. |
| T3 picks its own default `thought_level` for Neon (`medium` in early probes, `low` in the 2026-11-19 catalog) | Every workflow that starts an Engineer sets the level from the role table in `config/AGENTS.md`. |
| A session without `t3_thread_configure` cannot switch its own model | The role nudge for a `lead` or `engineer` skill still names the role and level; on Elias's yes, the agent says the switch is unavailable here and offers a fresh thread on that role instead. |
| In T3's `auto` runtime mode, Antigravity still waits for Elias's approval on anything outside its sandbox. On 2026-11-20 every tool call waited (Neon review children started in `auto` from an `auto` Lead thread). By 2026-11-23, workspace file reads, writes and edits and local shell commands, including `git commit`, ran unattended in Standard Sandbox mode. Network calls failed inside the sandbox (`gh` could not read its config; `git ls-remote` could not resolve `github.com`). Retrying them with the sandbox bypassed, and writing a file outside the workspace, both waited for approval (two Neon `low` probe children started in `auto` from a `full-access` Lead thread). | The shared instructions run threads and children in `full-access` (`t3-sync` sets T3's `defaultRuntimeMode`), which includes Antigravity until its `auto` runs `git push` and `gh` unattended, because every Engineer ticket ends with both. T3 refuses a child mode broader than its parent's (`runtime_mode_escalation_denied`, 2026-11-20), so a launching thread still in `auto` or narrower (such as one created before the default changed) can start Antigravity only in an approval-asking mode, and Elias is told first. A `full-access` Neon thread can start further `full-access` Neon threads. |

Verification, 2026-11-19, T3 Code with Antigravity CLI 1.5.13 and Gemini 4 Neon: before the projection, a fresh Neon child loaded only the project `AGENTS.md` and four built-in skills. Probe rules in `~/.gemini/config` did not load; the same rules in the T3 profile's `config/` did, as `GEMINI.md`, `AGENTS.md` and `rules/*.md`. With `~/.gemini/config/skills` linked to the shared runtime, the child listed 93 owned skills and could activate `implement`. After `antigravity-sync --apply`, a fresh Neon child reported the managed global rule (headings `# Personal agent preferences` and `## Managed Antigravity skill routing`), quoted the shared instruction that durable notes go to the Obsidian vault, and activated `implement` and `code-review`. `antigravity-doctor` passed.

Rule-link probes, 2026-11-20, T3 Code 0.1.11 with Antigravity 1.5.13 and Gemini 4 Neon:

- **T3 link probe (passed):** With a marker rule (`EKIT-PROBE-67-GEMINI-ROOT`) written to `~/.gemini/GEMINI.md` and `<profile>/config/GEMINI.md` moved aside, launching a fresh Neon child in T3 created `<profile>/GEMINI.md -> ~/.gemini/GEMINI.md`; the child reported `EKIT-PROBE-67-GEMINI-ROOT` as `<RULE[user_global]>` and `0` copies of `# Personal agent preferences`. With `<profile>/config/GEMINI.md` restored alongside `~/.gemini/GEMINI.md`, a second fresh Neon child loaded both files cumulatively as separate `<RULE[user_global]>` blocks, confirming that stale managed `config/GEMINI.md` copies must be removed to avoid duplicate loading.
- **Standalone CLI probe (inferred from binary identity and docs; live login absent):** Running `~/.local/bin/agy -p` stopped at the Google OAuth login prompt because standalone `~/.gemini` is not signed in on this Mac, so live standalone prompt execution remains unverified without authenticating. Because `~/.local/bin/agy` (1.5.13) is byte-for-byte identical (SHA-256 `3f669d53...`) to T3's `antigravity` binary (`antigravity acp --gemini-dir <profile>`), which read `<gemini-dir>/GEMINI.md` and `<gemini-dir>/config/GEMINI.md` cumulatively above, and Google's Antigravity rules documentation lists both `~/.gemini/GEMINI.md` and `~/.gemini/config/GEMINI.md` as standalone global rule paths, writing only `~/.gemini/GEMINI.md` is inferred to serve both T3 Code and standalone `agy` without duplicate loading.

## Fresh-session smoke check

After applying a projection, start a genuinely new session in that host and check three things:

1. Ask a small question whose answer is in the shared instructions, without asking the agent to open the instruction file. Confirm the host follows that instruction.
2. Ask for an ordinary task that clearly matches an automatic skill. Confirm the session loads the owned skill rather than relying on an external copy.
3. Request a known user-requested workflow in ordinary language, such as “Use Teach to help me learn this.” Confirm its distinctive instructions load without another command. Also test two requested workflows, a supporting handoff, discussion (“Explain what Teach does”), negation (“Don’t use Teach”), and an adjacent ordinary request. Optional command syntax should still work.

Use the structural doctors as well as behavioral checks. A doctor proves that files, links, and routing projections agree with the canonical source; only a fresh session proves that a host loaded and acted on them. Never treat a host's unrelated MCP or account status as proof that the shared skill system failed or succeeded.

## Verification record — 2026-09-26

No `SKILL.md` or skill `metadata.json` was changed for this portability ticket. This ticket documents the existing host projections and their verified behavior and limitations.

| Host | Structural checks | Fresh-session result |
|---|---|---|
| Codex CLI 0.158.0-alpha.2 | `sync` showed zero additions, changes, removals, or drift; `doctor` passed. | Passed a fresh, ephemeral, read-only session. It returned the configured Python/TypeScript personal-product defaults; `$wait-what` returned its body-specific `ASD-STE100 Simplified Technical English` instruction. A separate ordinary rewrite automatically selected and read the owned `writing` skill and its edit guidance. The CLI also logged an unrelated FlowSavvy MCP 401; that integration was not part of this test. |
| Claude Code 2.1.283 | `claude-doctor` passed and confirmed the generated routing and links. Its managed `wait-what` copy has `disable-model-invocation: true`. | Passed a fresh authenticated interactive session. Startup exposed `/wait-what`; direct invocation explained idempotency in plain language with an example, why it matters, and a non-idempotent counterexample. Asked about the loaded root `AGENTS.md`, Claude correctly identified this repository as the editable source of truth and the host runtime copies as generated files that must not be hand-edited. |
| OpenCode | `opencode-doctor` passed structural checks and reported the expected routing categories. | Pending: the `opencode` executable is not installed on this Mac, so no fresh runtime session could be tested. Install it, apply `opencode-sync`, then run `opencode-doctor` and the smoke checks above. |

The Codex and Claude smoke tests made no repository edits. OpenCode's fresh runtime test remains pending because the executable is not installed on this Mac. Credentials and integrations are not included in the repository and were not transferred.
