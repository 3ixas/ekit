# Establish reusable project verification

Use during implementation when existing instructions and harnesses do not provide a reproducible proof path for the current work, or when setup is requested directly. Setup is part of the implementation scope; keep it limited to the journeys needed for that scope.

## Discover before writing

Read project instructions and inspect existing documentation, package/build commands, tests, fixtures, and automation. Identify the user surface (browser, CLI, API, desktop, mobile, or library), exact startup command, available driving tools, observable results, and instance/data ownership. Reuse sufficient guidance and link existing tests and helpers instead of duplicating them. A functioning test harness with clear setup and evidence can already be sufficient.

For an existing app, execute the relevant baseline before editing where feasible. For a new app without a runnable journey, record setup as pending in the proof plan and complete it once the first journey runs, before final proof and review. Startup failure is a concrete blocker: diagnose within the task's scope or report it; do not invent working commands or expand into unrelated repairs.

## Write for the next agent

Use the project's established verification documentation location. Otherwise create `docs/verification/README.md`; add feature recipes under `docs/verification/features/` only as needed. Put new executable helpers under `scripts/verification/` unless the project has an established harness location. Do not install a project-specific skill globally or create a vendor-specific skill directory.

The guide must make these instructions discoverable from the project's existing agent/developer entrypoint: add one short link there, or in the root README if no such entrypoint exists. Preserve its structure and unrelated instructions.

Record only observed commands and prerequisites; mark unexecuted instructions as draft. Cover:

- **Launch:** exact commands, working directory, required configuration names (never secret values), disposable fixtures/storage, migrations, and seeds. Readiness means a usable journey from fresh disposable storage, not just a listening port or a database health response. Stateless apps and libraries document the equivalent clean invocation.
- **Doctor:** read-only checks of app/build identity, readiness, authentication prerequisites, and ownership of the instance and test data. Check before driving and after surprising behaviour; reset a wedged UI or relaunch an owned instance if health checks cannot see the failure.
- **Drive:** real commands, routes, accessible names, or stable selectors from this app, using its existing harness and available host tools first. Document state and tool prerequisites, including whether sessions can coexist.
- **Evidence:** capture the action and resulting state, plus persistence and other side effects through a second observable view where relevant. Record the working-tree revision, command, result, and artifact locations. Exercise actual user entrypoints rather than internal setters. Use external substitutes only at existing production boundaries; document what a dry-run actually skips by observing its effects.
- **Cleanup:** stop only processes or sessions this run created; remove only owned disposable state. Never kill by process name or take over the user's running app. Preserve proof artifacts outside disposable storage. Clean failed attempts too.
- **Helpers:** include executable scripts only when they remove repeated work; document exact invocation and observed outputs. Prefer existing project tooling and dependencies.

Use the [adapted feature-map example](feature-map-example/README.md) when feature recipes will help. Each recipe names the user behaviour, entrypoints, preconditions, exact actions and expected results, and gotchas. Seed only the current work's journeys; a broader setup request starts with three to five features, or all if fewer exist. Never present an invented example selector or command as a verified app fact.

## Prove before delivery

Follow the guide cold: launch, doctor, drive one mapped journey, capture action/result and relevant side effects, then clean up. Verify artifacts still exist after cleanup. Fix and re-execute failed guide steps within scope, cleaning up every failed iteration. The normal proof plan still covers every material acceptance claim; this one-journey setup proof is not whole-app coverage.

Missing credentials, tools, services, or fixture preconditions remain concrete gaps. Record the attempted path and unmet prerequisite; never weaken a journey to make it pass. Continue independent implementation/proof where possible. Unexecuted guidance is draft; a failing observed claim is Fail and an inaccessible required check is Skip.

When a substitute environment is used, list setup supplied by that environment that the actual target will not supply. Those target steps remain unverified. Report the guide location, proven journey, coverage gaps, evidence, and cleanup outcome.

## Shared work

The `implement-spec` coordinator owns shared guide setup and integration. Give workers its location, fixture/instance ownership rules, and their journey scope. Workers may propose affected recipe updates with their slice, but must not independently scaffold competing guides. Use isolated instances/storage; serialize driving when isolation is unavailable. Re-prove affected instructions on the integrated revision.
