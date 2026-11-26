## What to build

Workflow paths become structured data, and that data generates the README's "More workflows and when I use them" table. After this, a path is changed in one place, and the README can't drift from it. This prefactor lets the Skill catalogue in a later ticket reuse the same data.

- The existing table moves into a structured file under `config/`. Each entry has a situation, ordered steps, and optional notes. A step is a skill id or free text for a non-skill step. The wording stays as it is.
- A new `skills.py catalog` subcommand previews the generated README table and writes it with `--apply`. Generation is deterministic.
- `check` fails when the README table differs from what the data generates, or when a step names an unknown, candidate or paused skill.

Spec: #78.

## Acceptance criteria

- [ ] After migration, `catalog --apply` produces a README table with the same content as today, apart from formatting.
- [ ] Hand-editing the generated README table makes `check` fail with a staleness error.
- [ ] A path step naming an unknown, candidate or paused skill makes `check` fail.
- [ ] Regenerating unchanged inputs is byte-identical.
- [ ] Unit tests cover each case; `check` and the unit tests pass.
