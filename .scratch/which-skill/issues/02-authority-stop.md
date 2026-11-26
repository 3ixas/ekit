## What to build

Skills that can change external state declare where their authority stops, so the Skill catalogue can carry it from the source.

- Add an optional `authority_stop` string to the skill metadata schema. `check` rejects an empty or non-string value.
- Fill it for every skill whose workflow can merge, publish, deploy, send, delete or change external state (about 20, including `implement`, `implement-ticket`, `implement-series`, `implement-parallel`, `full-send`, `full-stop`, `release`, `babysit-pr`, `modernize`, `email-assistant`, `planning`, `todoist-project`, `flowsavvy`, `flowsavvy-project` and `pr-feedback`). Take the wording from each skill's SKILL.md; don't invent new limits.

Spec: #78.

## Acceptance criteria

- [ ] The schema documents the optional field, and `check` fails on an empty or non-string value.
- [ ] Every side-effecting skill has an `authority_stop` that matches its SKILL.md. The PR lists which skills were judged side-effecting and why borderline ones were left out.
- [ ] `check` and the unit tests pass.
