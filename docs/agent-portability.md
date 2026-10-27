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
```

The three sync commands above are previews. Read the additions, changes, removals, target paths, and backup plan before applying a projection:

```sh
python3 scripts/skills.py sync --apply
python3 scripts/skills.py claude-sync --apply
python3 scripts/skills.py opencode-sync --apply
```

Use `sync --apply --adopt-unmanaged` only for the one-time migration when the Codex/shared skill directory already exists without this repository's ownership marker. The command backs up that directory before replacing it. Do not hand-edit installed skill copies.

## Routine updates and checks

After changing the canonical repository, run the unit tests and `check`, preview every host projection, then apply only the projections you use. Start a new agent session after syncing so the host discovers the current instructions and skill descriptions.

```sh
python3 scripts/skills.py check
python3 -m unittest discover -s tests -v
python3 scripts/skills.py sync
python3 scripts/skills.py claude-sync
python3 scripts/skills.py opencode-sync
python3 scripts/skills.py doctor
python3 scripts/skills.py claude-doctor
python3 scripts/skills.py opencode-doctor
```

Use `python3 scripts/skills.py updates` to check pinned upstream sources without changing owned skill content. Use `python3 scripts/skills.py capabilities` for per-host tool, orchestration, routing, and catalog evidence. Add `--skill <id>` to focus the report on one skill's tool and routing dependencies. `--catalog-warning-tokens N` sets a local early-warning threshold; it is an estimate, not a published Codex limit. The report checks local executable prerequisites, but cannot see every app's live session permissions or connected-tool catalogue.

## What each host receives

| Host | Shared instructions | Owned skills | Invocation and limits |
|---|---|---|---|
| Codex | `~/.codex/AGENTS.md` | `~/.agents/skills` | User-requested skills permit model loading through `allow_implicit_invocation: true`. `$skill-name` is optional. |
| Claude Code | `~/.claude/CLAUDE.md` links to shared instructions; generated routing in `~/.claude/rules/elias-agent-skills.md` | `~/.claude/skills` links to the managed runtime | Owned skills remain model-loadable; `/skill-name` is optional. The plugin checks supporting ownership without redirecting requested workflows to slash commands. |
| OpenCode | `~/.config/opencode/AGENTS.md` | Native discovery from `~/.agents/skills` | User-requested skills remain model-loadable; V2 metadata explicitly enables autoinvocation. Stable V1 follows descriptions and instructions. |

`explicit` means **user-requested**, not manual-command-only. Natural language and dictation count when they name or clearly request the workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Multiple requested methods and supporting handoffs may compose under one primary owner without another invocation. Request recognition is model-guided on every host, not a deterministic permission boundary. Supporting-only routing is guidance; the Claude plugin can warn or refuse missing ownership. Loading a skill grants no additional action authority.

The [OpenAI skills guide](https://developers.openai.com/plugins/concepts/skills) describes metadata-based discovery and direct invocation. The [Claude Code skills guide](https://code.claude.com/docs/en/skills) documents description-based selection, `/skill-name`, and `disable-model-invocation`. [OpenCode's skills guide](https://opencode.ai/docs/skills) documents shared Agent Skills paths and on-demand loading; V2 routing details are in the [V2 guide](https://opencode.ai/v2/docs/skills).

Skills describe workflows. The host, MCP server, or executable provides access and performs actions. For example, a local `gh auth status` result does not prove that a Claude or OpenCode session can read this repository's issues. The [capability report](../scripts/capabilities.py) preserves that distinction. Configure integrations at the layer they require, then verify each one from the host session that will use it.

For the approved free Motion documentation and shadcn integrations, see [component MCP setup](component-mcp.md). MCP configuration, backups and project registries are separate from skill projection.

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
