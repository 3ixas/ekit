# Owned-bundle contract

## Source layout

An active, candidate, or paused bundle lives at `<lifecycle>/<group>/<id>/`. `SKILL.md` and `metadata.json` are required. For user-requested (`explicit`) skills, add `agents/openai.yaml` with `allow_implicit_invocation: true`; do not disable model invocation. Write descriptions as discriminating natural-language triggers, with adjacent non-triggers. Commands are optional, and supporting handoffs within an authorized workflow need no second invocation. Request recognition is model-guided, not an action permission boundary. Add references, scripts, assets, or evaluations only when they change real behaviour.

## Instructions

- Make the frontmatter description discriminating enough for routing.
- Keep the entrypoint focused on outcome, decisions, method, and boundaries.
- Link conditional detail at the point it becomes relevant.
- Preserve authority boundaries. A skill never grants permission to send, publish, deploy, delete, pay, or expose private material.
- Do not encode project facts, personal knowledge, generic tutorials, or provider documentation that should be queried live.

## Provenance

For each meaningful source, record its repository or package identity, immutable revision, exact path, digest, licence treatment, use, and owned changes. Imported text retains required notices. Independently written synthesis must say so. Do not list a source that did not affect the bundle.

## Evaluation

Run the repository check and unit tests. For substantial changes, exercise:

- a request that should select the skill;
- a nearby request that should select another owner;
- an authority or failure boundary;
- the main observable output or mutation path.

Candidates stay outside the installed projection until those checks justify an explicit promotion decision.
