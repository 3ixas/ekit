# EKit

This repository is the sole editable source for every personal skill and shared agent instruction I deliberately use. It supports Codex, Claude Code, and OpenCode through host-specific generated projections. External services and CLIs remain separate tools; their authentication and access do not transfer between agents.

I normally describe what I want in ordinary language. My active agent selects one primary owner and loads relevant supporting specialists. User-requested (`explicit`) workflows load when I name or clearly request their method in ordinary language or dictation. Multiple workflows can be requested together under one primary owner. `$skill-name` in Codex and `/skill-name` in Claude Code remain optional shortcuts. Request recognition is model-guided; loading never grants additional action authority.

This is my personal collection, tailored to my workflows rather than a general-purpose toolkit. There is no promise of support or compatibility for other setups. External contributions are considered case by case.

For browser downloads and selective use on another machine, see [download skills for work](docs/work-downloads.md). [Publication readiness](docs/publication-readiness.md) records the remaining gates before making this repository public.

## Day-to-day paths

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
| Tasks and scheduling | FlowSavvy; invoke its owned workflow when requested |
| Personal facts and notes | `obsidian` |
| Change this skill system | `skill-review` → `skill-authoring` |

Full Stop and Full Send accept natural language or dictation; slash/dollar commands are optional. Discussion and quoted mentions do not invoke them. Their delivery endpoint never expands the approved scope.

`grilling` is the general exhaustive alignment workflow. It works with codebases, product ideas, writing, documents, and personal or life decisions. `grill-with-docs` is the software wrapper that runs `grilling` with `domain-modeling` and durable project documents.

## Groups

| Group | Responsibility |
|---|---|
| [Software workflows](skills/software-workflows/README.md) | Take software from uncertainty through implementation, proof, and release. |
| [Engineering specialists](skills/engineering-specialists/README.md) | Supply language, platform, security, data, and operational judgment. |
| [Frontend and design](skills/frontend-and-design/README.md) | Create reference-led interfaces and validate their experience and craft. |
| [Research and decisions](skills/research-and-decisions/README.md) | Find evidence, understand systems, develop options, and analyze data. |
| [Writing and artifacts](skills/writing-and-artifacts/README.md) | Produce strong prose and correctly rendered files. |
| [Knowledge and productivity](skills/knowledge-and-productivity/README.md) | Use FlowSavvy for current tasks and scheduling, and Obsidian for durable notes and commitment reviews. |
| [Personal workflows](skills/personal-workflows/README.md) | Hold the few personal routines that earn dedicated instructions. |
| [Agent system](skills/agent-system/README.md) | Clarify, coordinate, teach, preserve continuity, and maintain skills. |

Approved active skills live in `skills/<group>/<id>`. Candidates under `candidates/` are never installed. Paused skills remain owned but inactive under `paused/`. Retired skills remain in Git history.

The [activation manifest](docs/activation-manifest.md) lists the active, candidate, and paused bundles with their lifecycle, group, invocation, and origin.

## Manage the repository

```sh
python3 scripts/skills.py check --list
python3 -m unittest discover -s tests -v
python3 scripts/skills.py sync
python3 scripts/skills.py updates
python3 scripts/skills.py doctor
python3 scripts/skills.py claude-doctor
python3 scripts/skills.py opencode-doctor
python3 scripts/skills.py capabilities
```

`sync` is a preview unless `--apply` is supplied. Application requires a marked runtime, creates a timestamped rollback snapshot, stages the complete runtime beside the target, swaps it atomically, installs the canonical global `AGENTS.md`, and verifies hashes. The one-time first migration uses `sync --apply --adopt-unmanaged`; it backs up the old unmarked runtime before replacement.

See [using the system across agents](docs/agent-portability.md) for first-time setup, routine sync and health checks, host-specific invocation limits, and the latest fresh-session verification record.

## Review and provenance

Every adapted or synthesized bundle records its sources in `metadata.json`. [Third-party notices](THIRD_PARTY_NOTICES.md) describe licences and copying limits. The maintained source inventory and adaptation treatment live in [provenance](docs/provenance/retained-source-treatment.md). Historical assessments and private review receipts stay outside the public collection.

`python3 scripts/skills.py updates` compares pinned source paths with their current upstream state. It never changes an owned skill. Review a useful change through `skill-review`, adapt it through `skill-authoring`, run focused behavioural checks, then sync.
