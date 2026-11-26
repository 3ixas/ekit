# Scope: which-skill

Status: approved by Elias, 2026-11-26. Terms are defined in [GLOSSARY.md](../../GLOSSARY.md): Skill recommendation, Workflow path, Skill catalogue. Decision record: [ADR 0004](../../docs/adr/0004-which-skill-uses-a-generated-catalogue.md).

## Problem and outcome

EKit has 92 active skills. Agents already select owners from descriptions, so routing is not the gap: Elias's awareness is. He refers to the repository to find the right skill, and the 22 explicit-only skills (`hill-climb`, `wayfinder`, `full-send`, `craft-review`, …) never run unless he names them. Outcome: Elias can ask, in any host, which skill fits what he is about to do or is doing, get an answer grounded in the routing contract, and stay fluent in the collection as it grows.

## Decisions (agreed)

1. **Advise, then offer.** It gives a Skill recommendation and offers to start the owner; it starts it only on Elias's yes. Explicit-only workflows and anything with side effects (publishing, merging, sending) always wait for his words; a recommendation grants no authority.
2. **Questions it answers.**
   - Upfront: "I'm about to do X, what should I use?"
   - Mid-task: "Is this thread using the right skill; did I miss one?", judged from the current conversation.
   - "What changed since `<date>`": skills added or reviewed since then.
   General browsing stays with the activation manifest.
3. **Knowledge source: a generated Skill catalogue** in the skill's references, produced by `scripts/skills.py` from bundle metadata and Workflow path data; `check` fails when it is stale. The host's loaded skill listing is a cross-check, and a mismatch is reported rather than guessed around. Only active skills are recommended. See ADR 0004.
4. **Invocation: explicit only, role `either`.** Automatic invocation would compete with every owner skill.
5. **Name: `which-skill`**, in the `agent-system` group.
6. **Recommendation shape.** One owner, with:
   - `Owner`: skill, and why it fits
   - `Brings in`: supporting skills
   - `Say`: the exact phrase to invoke it, so Elias learns trigger wording
   - `Stops at`: the authority stop
   - `Also worth naming`: only when an explicit-only skill really applies
7. **Ambiguity.** Show at most two branches, each with the fact that decides between them (cause unknown → `debug`; known line → `implement`). Ask only when neither branch is safe to start without the answer.
8. **No fit.** Say plainly that no skill applies and to ask normally. If the request looks recurring, suggest `skill-review` for a possible new skill. Never stretch the nearest skill.
9. **Workflow paths become structured data** (e.g. `config/paths.json`) generating both the README "More workflows" table and the catalogue, replacing the hand-maintained table.
10. **Change dates travel with the catalogue.** It records each skill's `added` date (tracked in metadata, backfilled from git) and `reviewed` date, so "what changed" works without the repository; answers say they are as fresh as the last sync.

11. **Authority stops come from metadata.** An optional `authority_stop` metadata field, filled for skills with side effects, feeds the catalogue's `Stops at` (agreed during to-spec, 2026-11-26).

## Definition of done

- On every case in [evals/routing.json](../../evals/routing.json) (63 today, 28 owners), the recommended owner matches the labelled `owner` and the `authority_stop` is surfaced.
- 11 new routing cases cover the explicit primary skills that have none yet.
- A structural test in CI checks catalogue freshness, the README table's generation, and the eval cases.
- One sampled fresh-session run each in Claude and Codex confirms the shape and explicit-only invocation.
- All five host projections previewed, applied and doctored after merge, per AGENTS.md.

## Exclusions

- No automatic invocation and no change to how other skills are selected.
- No general catalogue browser; the activation manifest keeps that job.
- Candidate and paused skills are not recommended.

## Assumptions and open items

- Assumes the catalogue fits comfortably in context when loaded explicitly; measure its token size during implementation (`capabilities --catalog-warning-tokens` exists for this).
- The exact `config/paths.json` schema and generator design are implementation decisions.
- The added date is tracked in metadata rather than read from git, so a later-day commit or squash merge cannot make the catalogue stale (ADR 0004).

## Evidence

- `evals/routing.json`: request → owner, supports, authority_stop; consumed by `tests/test_skills.py`.
- README "More workflows and when I use them" table: current Workflow paths, prose only.
- `docs/activation-manifest.md`: 92 active, 1 candidate, 2 paused.
- `scripts/skills.py capabilities`: existing catalogue status reporting.
