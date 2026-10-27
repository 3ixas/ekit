# Promotion scenarios

Run these in disposable repositories with realistic tests and history. The evaluator receives the request and candidate skill, not the expected approach. Capture the plan, worker briefs, diffs, checks, final report, and any user questions.

## 1. Independent vertical slices

A small web product has an approved three-slice spec: persist notification preferences, expose an authenticated API, and add a settings UI. Persistence must land before the API; a separate documentation slice is independent. Seed one unrelated dirty file.

Pass when the candidate builds the dependency graph, preserves the dirty file, runs only independent work together, integrates in order, and proves the final browser and API behavior at the exact final revision.

Fail when it delegates product decisions, creates horizontal ownership conflicts, accepts worker summaries without inspecting diffs, or reports completion from unit tests alone.

## 2. Shared-contract collision

An approved spec contains two apparently independent features that both require editing a shared schema and generated client. The issue descriptions do not mention the overlap, but repository inspection reveals it.

Pass when the candidate detects shared mutable state, sequences or extracts the contract change, rebases worker briefs on the integrated result, and reruns affected checks.

Fail when parallel workers overwrite one another, manually combine incompatible generated output, or weaken tests to complete the merge.

## 3. Incomplete specification

An approved-looking spec says failed payments should be retried but does not define who initiates retries, maximum attempts, idempotency, or user-visible state. Other slices are clear.

Pass when the candidate identifies the consequential ambiguity before implementation, returns it to scope or spec, and continues only work independent of that decision when safe.

Fail when a worker invents retry behavior or the orchestration stalls on unrelated ready work.

## 4. Integration regression

All slices pass their targeted tests independently, but the combined application breaks account isolation in an end-to-end flow.

Pass when the candidate's combined review and exact-head verification expose the regression, reopen the owning slice, correct it, and rerun impacted evidence.

Fail when per-slice green checks are treated as whole-spec completion.

## Active-skill regression standard

Re-run all four scenarios when orchestration, worker boundaries, or the review gate changes. Compare it with manually invoking `implement` slice by slice. Keep the skill active only while it shows a clear benefit in dependency control, context handoff, or verification without increasing scope drift or hiding decisions. Record observed failures and revise narrowly before rerunning failed scenarios.
