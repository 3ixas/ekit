## What to build

Elias can say "which skill should I use for X?", "is this thread using the right skill?" or "what changed since `<date>`?" in any host and get a Skill recommendation grounded in a generated Skill catalogue (ADR 0004).

- New `which-skill` bundle in `agent-system`: origin original, explicit invocation, role `either`. It gives one owner per recommendation, in this shape:
  ```
  Owner: <skill>, <why it fits>
  Brings in: <supporting skills, or none>
  Say: "<exact invocation phrase>"
  Stops at: <authority stop, or "works locally">
  Also worth naming: <explicit-only skill and condition>   (only when it applies)
  ```
  - **Ambiguous request:** at most two blocks, each led by the fact that decides between them; a question only when neither branch is safe to start.
  - **No fit:** says so plainly, and suggests `skill-review` when the request looks recurring.
  - **Mid-task:** judges from the current conversation and names the current owner first.
  - **"What changed":** lists added and revised active skills since the date, with a freshness note.
  - **Starting the owner:** it advises, then offers to start the owner, and starts it only on Elias's yes. Explicit-only and side-effecting workflows still need his explicit words.
  - **Scope of advice:** recommends active skills only, and reports a mismatch between the host's loaded skills and the catalogue instead of recommending a missing skill.
- The generator renders the Skill catalogue into the bundle's references. It lists every active skill (id, group, one-line purpose, invocation, role, `authority_stop`, added date from git, reviewed date) and every Workflow path, with a generation date taken from its inputs' latest commit. It's produced by `catalog`, and `check` fails when it's stale.
- `capabilities` reports the catalogue's estimated token count against the existing warning threshold.
- Rows go into the agent-system README and the activation manifest (93 active).
- After merge, preview and apply all five host projections and run all five doctors.

Spec: #78.

## Acceptance criteria

- [ ] Editing the catalogue, or changing metadata without regenerating, makes `check` fail. Regenerating unchanged inputs is byte-identical.
- [ ] The catalogue contains every active skill and no candidate or paused skill, with `authority_stop` where declared.
- [ ] `capabilities` reports the catalogue token estimate.
- [ ] A fresh Claude session and a fresh Codex session each show that `which-skill` does not trigger on an ordinary request and that, when invoked, it returns the shape above for one clear request, one ambiguous request and one no-fit request.
- [ ] `check`, the unit tests, all five syncs (applied after merge) and all five doctors pass.
