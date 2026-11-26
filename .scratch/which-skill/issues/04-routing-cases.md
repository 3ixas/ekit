## What to build

Every explicit primary skill is exercised by the routing eval set, because explicit-only skills are where `which-skill` adds the most value.

- Add one routing case each for `full-send`, `full-stop`, `babysit-pr`, `modernize`, `security-audit`, `dogfood`, `planning`, `email-assistant`, `todoist-project`, `flowsavvy-project` and `flowsavvy-feature-request`, using the existing fields with `explicit: true`. Each case is a realistic request with a truthful `authority_stop`.
- The routing-scenario test fails when any explicit, non-supporting active skill has no case.

Spec: #78.

## Acceptance criteria

- [ ] 11 new cases exist, each one's `authority_stop` agreeing with its skill's SKILL.md.
- [ ] Removing any explicit primary's only case makes the unit tests fail.
- [ ] `check` and the unit tests pass.
