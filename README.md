# EKit

EKit is Elias’ kit: the skills and shared instructions I use with Codex, Claude Code and OpenCode.

I keep them here so I can change a workflow in one place and use it across my personal setup. It also gives me a public reference I can download from another machine without signing into GitHub.

The collection covers software development, research, writing, documents and a few personal routines. Some skills are adapted from other people’s work; others are specific to how I use agents.

[Browse the skills](skills/) · [Download complete bundles](docs/work-downloads.md) · [Set up the personal system](docs/agent-portability.md)

## How I use it

I normally describe what I want in ordinary language. The agent selects a workflow and brings in the relevant specialists. When I want a particular method, I name it:

```text
Use Grill With Docs to help me work through this feature before we build it.
```

```text
Implement the next ready ticket, check it against the requirements and review the change.
```

```text
Review this explanation and make it clearer, keeping my voice.
```

For software work, I want the agent to understand the task, make a focused change and show evidence that it works. The usual path for a larger change is:

**Work through the problem → write the spec → break it into tickets → implement each slice → verify → review the session.**

That maps to [`grill-with-docs`](skills/software-workflows/grill-with-docs/SKILL.md) → [`to-spec`](skills/software-workflows/to-spec/SKILL.md) → [`to-tickets`](skills/software-workflows/to-tickets/SKILL.md) → [`implement`](skills/software-workflows/implement/SKILL.md) → [`verify`](skills/software-workflows/verify/SKILL.md) → [`retro`](skills/agent-system/retro/SKILL.md). Smaller, settled changes can go straight to `implement`. `implement-spec` handles an approved set of tickets with parallel agents.

Naming a workflow counts as requesting it; `$skill-name` in Codex and `/skill-name` in Claude Code are optional shortcuts. The agent can combine requested workflows and supporting skills, but loading a skill does not grant permission to publish, send messages or take other actions outside the task. See the [portability guide](docs/agent-portability.md) for each host’s behaviour and limits.

<details>
<summary>More workflows and when I use them</summary>

| Situation | Usual path |
|---|---|
| Deliberate repository security audit | Explicit `security-audit` (coverage, independent verification, reports) → separately scoped remediation |
| App nearing release | app-audit (whole-app checks, fixes, and evidence) → release when authorized |
| Small clear software change | `implement` (one slice, same-model review, fixes, and commit) → `verify` |
| New product idea | `product-thinking` (verdict, riskiest assumption, cheapest test) → `grill-with-docs` when it earns a build |
| Nontrivial or unclear product work | `grill-with-docs` → `to-spec` → `to-tickets` → one-ticket `implement` per invocation → final `verify` → `retro` |
| Approved multi-slice specification | `implement-spec` (parallel implementer subagents → one code review of the integration branch) → `retro` |
| Approved work through PR readiness | Explicit “Full stop” → `implement` for one slice or `implement-spec` for an approved graph → proof/review → publish and monitor → human merge handoff |
| Approved work through merge | Explicit “Full send” → the same delivery lifecycle → guarded merge once all gates pass |
| Aging PR | Explicit `modernize` → reassess current intent → authorized rebase/update, or REWORK/CLOSE recommendation |
| Destination known, route uncertain | `wayfinder` → research/prototypes → `grill-with-docs` |
| New or substantially changed interface | `interface-design` (references → `DESIGN.md` → Claude Design or Stitch exploration and sign-off) → `to-spec` → `to-tickets` → one-ticket `implement` per invocation → `ui-polish` → `verify` → `retro` |
| Existing interface needs craft | `ui-polish`, with `motion` and `accessibility` when relevant |
| Writing | `writing`; the file-format skill owns DOCX, PDF, spreadsheet, slide, or image output |
| Quick understanding | ask normally; Codex may use `how` or `why` |
| Focused learning | `teach` |
| Multi-capability learning journey | `learn` → `teach` → evidence and route review |
| Understand completed work | `defend` |
| Resume later | `handoff` → `pickup` |
| Tasks and scheduling | Todoist for current tasks; FlowSavvy remains available when requested |
| Personal facts and notes | `obsidian` |
| Change this skill system | `skill-review` → `skill-authoring` |

Full Stop and Full Send accept natural language or dictation; slash/dollar commands are optional. Discussion and quoted mentions do not invoke them. Their delivery endpoint never expands the approved scope.

`grilling` is the general exhaustive alignment workflow. It works with codebases, product ideas, writing, documents, and personal or life decisions. `grill-with-docs` is the software wrapper that runs `grilling` with `domain-modeling` and durable project documents.

</details>

## Use a few skills elsewhere

Start with [the active skills](skills/) and choose the parts that fit your setup. Each skill is a directory: its references, scripts, assets, metadata and notices can matter just as much as `SKILL.md`.

The [download guide](docs/work-downloads.md) covers browser downloads at a recorded commit, dependencies and comparison with an existing installation. Public downloads do not need a GitHub login. The work network’s download route and receiving agent still need checking on that machine.

If you use this at work, keep the work machine’s instructions, accounts and installation process in charge. Review the selected bundles there before changing anything. The full personal sync commands below also manage global instructions; use the download guide for selective adoption.

## What’s here

| Group | Responsibility |
|---|---|
| [Software workflows](skills/software-workflows/README.md) | Take software from uncertainty through implementation, proof, and release. |
| [Engineering specialists](skills/engineering-specialists/README.md) | Supply language, platform, security, data, and operational judgment. |
| [Frontend and design](skills/frontend-and-design/README.md) | Create reference-led interfaces and validate their experience and craft. |
| [Research and decisions](skills/research-and-decisions/README.md) | Find evidence, understand systems, develop options, and analyze data. |
| [Writing and artifacts](skills/writing-and-artifacts/README.md) | Produce strong prose and correctly rendered files. |
| [Knowledge and productivity](skills/knowledge-and-productivity/README.md) | Use Todoist for current tasks, and Obsidian for durable notes and commitment reviews. |
| [Personal workflows](skills/personal-workflows/README.md) | Hold the few personal routines that earn dedicated instructions. |
| [Agent system](skills/agent-system/README.md) | Clarify, coordinate, teach, preserve continuity, and maintain skills. |

Approved active skills live in `skills/<group>/<id>`. Candidates under `candidates/` are never installed. Paused skills remain owned but inactive under `paused/`. Retired skills remain in Git history.

The [activation manifest](docs/activation-manifest.md) lists the active, candidate, and paused bundles with their lifecycle, group, invocation, and origin.

## Maintain the personal setup

I edit the source in this repository, then generate the installed copies for each agent. Installed files are generated output; changes belong here.

After a source change, run the checks:

```sh
python3 scripts/skills.py check --list
python3 -m unittest discover -s tests -v
```

Then preview the host projections:

```sh
python3 scripts/skills.py sync
python3 scripts/skills.py claude-sync
python3 scripts/skills.py opencode-sync
```

These commands show the proposed changes without applying them. Review additions, changes, removals, global instructions and the rollback path before using `--apply`. Application requires a marked runtime and creates a timestamped backup. The one-time `sync --apply --adopt-unmanaged` migration also backs up an existing unmarked runtime.

See the [portability guide](docs/agent-portability.md) for setup, rollback and fresh-session checks. The [Claude plugin](plugins/elias-mods/README.md) is installed and updated separately.

<details>
<summary>Health checks and upstream updates</summary>

```sh
python3 scripts/skills.py doctor
python3 scripts/skills.py claude-doctor
python3 scripts/skills.py opencode-doctor
python3 scripts/skills.py capabilities
python3 scripts/skills.py updates
```

`updates` compares the recorded source paths with upstream. It never overwrites an owned skill. I review a useful change through `skill-review`, adapt it through `skill-authoring`, then validate and preview the projections before syncing.

</details>

## Sources and licences

This collection includes adaptations from [Matt Pocock’s skills](https://github.com/mattpocock/skills), [Poteto’s PStack](https://github.com/cursor/plugins/tree/main/pstack) and other sources. Each adapted skill records its source, revision and changes in `metadata.json`.

The [root MIT licence](LICENSE) covers my eligible original contributions. Upstream material keeps its own terms; see [licence scope](LICENSE_SCOPE.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the [source inventory](docs/provenance/retained-source-treatment.md). Keep the relevant notices and licence files with any bundles you use.

I maintain EKit for my own use and consider contributions case by case. There is no support or compatibility promise for other setups.
