## What to build

Independent proof that `which-skill` recommends the right owner: a local, opt-in runner gives every routing eval case to `which-skill` in fresh, non-interactive Claude and Codex sessions.

- A case passes on an exact match of the `Owner` line with the case's owner.
- When the owner declares an `authority_stop`, the `Stops at` line must also name the labelled boundary (keyword overlap with the case's `authority_stop`). Failures are listed for human review.
- The runner reports pass/fail per case and per host, and exits 0 with a skip message when a CLI is missing, following the opt-in real-browser tests.
- Run it on the full eval set and record the results in the PR's verification notes.

Spec: #78.

## Acceptance criteria

- [ ] Every routing case passes in both Claude and Codex, or each failure is fixed in `which-skill` (not by editing labels) and the rerun passes.
- [ ] Every side-effecting owner passes the boundary check.
- [ ] The runner skips cleanly without the CLIs; CI is unaffected.
- [ ] Results are recorded in the PR.
