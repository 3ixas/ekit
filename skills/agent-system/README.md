# Agent System

`explicit` means user-requested in natural language or dictation; special command syntax is optional. Model loading remains enabled, and action permissions remain separate.


Clarify, coordinate learning journeys, teach, preserve continuity, review the workflow, and maintain the skill collection.
| Skill | Invocation | Purpose |
|---|---|---|
| `grilling` | automatic | Resolve a codebase, product, writing, personal, or life decision through exhaustive rounds until user and agent share a complete understanding. |
| `handoff` | automatic | Write a concise HANDOFF.md that lets another session continue work without relying on hidden chat history. |
| `pickup` | automatic | Resume work from HANDOFF.md by checking its claims against current repository and issue state before continuing. |
| `retro` | automatic | Conduct a retrospective on a coding session and suggest improvements to the agent's environment. |
| `skill-authoring` | automatic | Create or update an approved owned skill with concise instructions, progressive resources, provenance, invocation policy, and meaningful evaluation. |
| `skill-review` | automatic | Assess a proposed skill, repository, upstream update, or retirement against Elias's needs, existing owners, routing, dependencies, provenance, maintenance cost, and behaviour. |
| `teach` | explicit | Teach one coherent mission using the source-faithful guided workspace method. |
| `learn` | explicit | Coordinate a multi-capability learning journey through bounded Teach tracks, evidence, and route reviews. |
| `wait-what` | automatic | Recover immediately when Elias says he is lost by restating the current point in plain language and rebuilding only the missing context. |
## Common paths

- Exhaustive shared understanding: `grilling`. Focused learning: `teach`. Multi-capability learning: `learn` → `teach` → evidence and route review.
- Cross-session work: `handoff` → `pickup`. Taking over an inherited PR/branch also loads Pickup’s conditional intent, credit and continuation guidance; publishing and merge endpoints need their own authority.
- Collection change: `skill-review` → `skill-authoring` → repository checks and sync.

`parallel` is retained under `paused/` as an owned harness reference and is not installed.
