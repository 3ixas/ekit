# Software Workflows

`explicit` means user-requested in natural language or dictation; special command syntax is optional. Model loading remains enabled, and action permissions remain separate.


Take software from uncertainty through implementation, review, proof, and release.

GitHub issue and pull-request state is handled through the local `gh` CLI or its `gh api` wrapper. Run GitHub CLI/API commands in a host/keyring-enabled context when the sandbox cannot see the macOS keyring. A sandbox-only invalid-token or connection result is not enough to declare the session unauthenticated; verify in the host context first. Use the most efficient supported GitHub capability for the task. Prefer `gh`/`gh api` for structured issue state; use another supported capability when it is materially better or the CLI is unavailable. If no capability is available, preserve drafts and report the blocker. Never use `--insecure-storage` or put a token in plaintext.
| Skill | Invocation | Purpose |
|---|---|---|
| `security-audit` | explicit | Audit repository security with deterministic coverage, isolated hunters, independent verification, validated findings, and explicit execution blockers. |
| `app-audit` | automatic | Run a whole-app web or mobile readiness pass at Elias's checkpoints or on request, fix material defects, recheck routes, metadata, agent readiness, interactions, accessibility, craft and runtime hygiene, and keep what it proved as CI gates. |
| `architecture` | automatic, supporting | Design or review software architecture when responsibilities, boundaries, interfaces, data flow, dependencies, or structural tradeoffs materially affect the result. |
| `code-review` | automatic | Review a diff or PR along Standards and Spec axes; automatically choose regular or deep structural review, honour explicit depth requests, and separate regressions from optional improvements. |
| `debug` | automatic | Diagnose and fix unexpected software behaviour through reproduction, causal evidence, root-cause correction, and regression proof. |
| `defend` | automatic | Help Elias understand and defend a completed or proposed software change through code-grounded explanation, challenge, teaching, and a final reviewer-facing defence. |
| `dogfood` | explicit | Exercise a running product change as a real user to find experience, coherence, and quality problems beyond functional correctness. |
| `domain-modeling` | supporting | Model domain concepts, states, invariants, transitions, and language when software behaviour depends on a clear conceptual structure. |
| `blast-radius` | supporting | Find what a proposed or implemented change could break beyond direct symbol callers and rank safety claims by evidence. |
| `implement` | automatic | Complete one approved software slice per invocation: implement, prove, review in the current run, fix in-scope findings, re-review, and commit locally. |
| `implement-spec` | explicit | Implement an approved spec and its tickets with parallel implementer subagents on one integration branch, then one code review. |
| `full-stop` | explicit | Carry approved work through proof, publication, CI and review to an open PR ready for human merging. |
| `full-send` | explicit | Carry approved work through the same lifecycle and merge only after the complete current-head gate. |
| `modernize` | explicit | Reassess an aging PR against current intent and architecture before an authorized branch update. |
| `migration` | explicit, supporting | Plan and execute substantial data, API, or cross-system migrations through compatible, verifiable stages. |
| `pr-feedback` | automatic | Evaluate and resolve feedback already left on a pull request, preserving the full review conversation and verifying accepted changes. |
| `pr` | automatic | Write a pull request body with a visual summary, before-and-after evidence, and merge danger. |
| `babysit-pr` | explicit | Monitor an open pull request through checks and review activity, taking only the follow-up actions authorized for the run. |
| `refactor` | automatic, supporting | Improve code structure or simplify settled code while preserving intended behaviour and proving equivalence. |
| `release` | explicit | Prepare and execute an authorized software release, pull request, deployment, or publication with exact-target evidence and rollback thinking. |
| `grill-with-docs` | automatic | Define nontrivial software work through exhaustive clarification and repository evidence, then write durable agreed scope. Use when the problem or product behaviour is not yet clear enough to implement. |
| `to-spec` | automatic | Convert confirmed scope into one implementation contract with behaviour, interfaces, constraints, acceptance evidence, and explicit exclusions. |
| `tdd` | supporting | Use a meaningful red-green-refactor loop when test-first evidence will clarify behaviour or prevent regression. |
| `to-tickets` | automatic | Split an approved specification into dependency-aware vertical slices and prepare GitHub Issues with observable acceptance evidence. |
| `triage` | automatic | Triage GitHub issues or pull requests by validating evidence, finding duplicates, reproducing when needed, and recommending the accountable next action. |
| `verify` | automatic, supporting | Prove acceptance claims; automatically establish missing project verification guidance during implementation and maintain affected journeys. |
| `wayfinder` | explicit | Navigate large work whose destination is known but whose route requires research, prototypes, or dependent decisions before a specification can exist. |
## Common paths

- User-requested delivery modes: “Implement ticket #42. Full stop” → the one-slice method → PR readiness without merge; “Full send” adds a guarded merge. An approved whole spec uses `implement-spec` inside the same delivery mode. Natural language/dictation counts; ordinary implementation still ends at a local commit.
- Aging PR: `modernize` → MODERNIZE, REWORK or CLOSE recommendation, with only authorized branch updates.

- Deliberate repository security audit: explicit `security-audit` → verified report and unresolved blockers → separately scoped remediation. Ordinary security work stays with `security`.

- App nearing release: app-audit → local fixes and recheck → release when separately authorized.

- Small clear feature or settled change: `implement` (one slice, including review, fixes, and commit) → `verify`.
- Unexpected or broken behaviour: `debug` → supporting specialists → `verify`.
- Nontrivial product work: `grill-with-docs` → `to-spec` → `to-tickets` → one-ticket `implement` per invocation → final `verify` → `retro`.
- Nontrivial interface work: `grill-with-docs` → `interface-design` with project `DESIGN.md` and a Claude Design or Stitch exploration loop → `to-spec` → `to-tickets` → one-ticket `implement` per invocation → `ui-polish` → `verify` → `retro`.
- Approved multi-slice specification: explicit `implement-spec` → parallel implementer subagents with `tdd` → one `code-review` of the integration branch → `retro`.
- Unclear route: `wayfinder` → research or prototypes → `grill-with-docs`.
- Completed change: `code-review` when review is needed; `defend` when understanding is needed; then `release` when authorized.

`merge-conflicts` was retired on 2026-10-05 after Matt Pocock removed its upstream source as no longer needed; Git history retains it.
