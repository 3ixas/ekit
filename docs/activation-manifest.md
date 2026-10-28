# Activation manifest

`explicit` means user-requested in natural language or dictation; special command syntax is optional. Model loading remains enabled, and action permissions remain separate.

This is the reviewed source-to-runtime contract after the 2026-09-15 fidelity and harness migration. Only the **active** collection is projected into `~/.agents/skills`. Candidate and paused bundles remain source-owned but unavailable to normal routing.

- Active: **88** skills
- Candidates: **1** skill
- Paused: **1** skill

## Software Workflows

| Skill | Invocation | Origin |
|---|---|---|
| `app-audit` | automatic | original |
| `security-audit` | explicit | adapted |
| `architecture` | automatic, supporting | synthesized |
| `pr` | automatic | adapted |
| `babysit-pr` | explicit | synthesized |
| `blast-radius` | supporting | imported |
| `code-review` | automatic | adapted |
| `debug` | automatic | synthesized |
| `defend` | automatic | original |
| `dogfood` | explicit | adapted |
| `domain-modeling` | supporting | synthesized |
| `grill-with-docs` | automatic | adapted |
| `implement` | automatic | adapted |
| `implement-spec` | explicit | adapted |
| `full-stop` | explicit | adapted |
| `full-send` | explicit | adapted |
| `modernize` | explicit | adapted |
| `migration` | explicit, supporting | synthesized |
| `pr-feedback` | automatic | adapted |
| `refactor` | automatic, supporting | synthesized |
| `release` | explicit | synthesized |
| `tdd` | supporting | synthesized |
| `to-spec` | automatic | adapted |
| `to-tickets` | automatic | adapted |
| `triage` | automatic | synthesized |
| `verify` | automatic, supporting | synthesized |
| `wayfinder` | explicit | adapted |

## Engineering Specialists

| Skill | Invocation | Origin |
|---|---|---|
| `api-design` | automatic, supporting | adapted |
| `ci` | automatic, supporting | synthesized |
| `ios` | supporting | adapted |
| `nextjs` | supporting | adapted |
| `observability` | automatic, supporting | synthesized |
| `openai` | supporting | synthesized |
| `payments` | supporting | adapted |
| `performance` | automatic, supporting | synthesized |
| `postgres` | supporting | synthesized |
| `python` | supporting | synthesized |
| `react` | supporting | synthesized |
| `react-native` | supporting | adapted |
| `security` | automatic, supporting | synthesized |
| `shadcn` | supporting | adapted |
| `supabase` | supporting | synthesized |
| `swift` | supporting | original |
| `typescript` | supporting | imported |
| `vercel` | supporting | synthesized |

## Frontend And Design

| Skill | Invocation | Origin |
|---|---|---|
| `accessibility` | automatic, supporting | synthesized |
| `apple-design` | supporting | adapted |
| `interface-design` | automatic | synthesized |
| `libraries-dev` | supporting | adapted |
| `motion` | automatic, supporting | synthesized |
| `prototype` | automatic | adapted |
| `ui-polish` | automatic | synthesized |
| `user-research` | automatic | imported |

## Research And Decisions

| Skill | Invocation | Origin |
|---|---|---|
| `compare` | automatic | synthesized |
| `data-analysis` | automatic | adapted |
| `data-visualization` | automatic | adapted |
| `doc-review` | automatic | synthesized |
| `how` | automatic, supporting | adapted |
| `ideate` | automatic | synthesized |
| `product-thinking` | automatic | synthesized |
| `research` | automatic | synthesized |
| `strategy` | automatic | adapted |
| `to-questionnaire` | automatic | imported |
| `why` | automatic, supporting | adapted |

## Writing And Artifacts

| Skill | Invocation | Origin |
|---|---|---|
| `documents` | automatic | adapted |
| `images` | automatic | adapted |
| `pdf` | automatic | adapted |
| `slides` | automatic | adapted |
| `spreadsheets` | automatic | adapted |
| `writing` | automatic | synthesized |
| `writing-for-agents` | supporting | synthesized |

## Knowledge And Productivity

| Skill | Invocation | Origin |
|---|---|---|
| `email-assistant` | explicit | adapted |
| `flowsavvy` | explicit | original |
| `flowsavvy-project` | explicit | original |
| `todoist-project` | explicit | original |
| `flowsavvy-feature-request` | explicit | original |
| `obsidian` | automatic | adapted |

## Personal Workflows

| Skill | Invocation | Origin |
|---|---|---|
| `dinner-decider` | automatic | original |

## Agent System

| Skill | Invocation | Origin |
|---|---|---|
| `grilling` | automatic | imported |
| `handoff` | automatic | adapted |
| `pickup` | automatic | synthesized |
| `retro` | automatic | adapted |
| `skill-authoring` | automatic | synthesized |
| `skill-review` | automatic | original |
| `learn` | explicit | original |
| `teach` | explicit | adapted |
| `wait-what` | automatic | imported |

## Paused

| Group | Skill | Origin | Reason |
|---|---|---|---|
| research-and-decisions | `defuddle` | imported | Paused: executable absent and no observed use; source retained. |
| agent-system | `parallel` | adapted | Owned source retained for future use; excluded from runtime because it is a harness concern. |

## Candidate disposition

`design-control-loop` is a software-workflows candidate: retained source for an explicit scheduled agent loop, not an installed active workflow. Promote only through `skill-review` and `skill-authoring` for an actual need. Paused and candidate owners remain outside every runtime projection. Current metadata and the maintained provenance inventory record sources and treatment; historical curation assessments remain private.
