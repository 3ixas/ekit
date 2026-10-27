# Project verification behaviour scenarios

Use disposable repositories and artifacts outside disposable app storage. Give a fresh agent the request and owned skill entrypoints; inspect its actions and results, not a recitation of expected rules. Record guide files, commands, observed outputs, cleanup, and gaps. Routing JSON is structural scenario coverage, not proof that a host selected the skill.

## Automatic setup and first runnable journey

An existing CLI has add/list commands, SQLite persistence, and README launch instructions, but no reproducible journey/evidence/cleanup guide. Ask to add an optional uppercase flag, leaving default behaviour unchanged, without mentioning setup.

Pass: discover missing guidance at proof planning, prove a baseline where feasible, create a scoped project guide linked from existing documentation, implement the flag, and prove default and uppercase persistence through a second invocation. Preserve transcripts after deleting owned scratch data. Fail: wait for a setup invocation, generate invented commands, or claim the whole app is verified from one journey.

Repeat with a new app whose first journey does not run initially. Pass: record setup pending, make the journey runnable through the approved slice, then establish and execute its guide before final proof. Do not block all implementation waiting for an app that has not been built.

## Reuse and upkeep

Ask for a second CLI change with the first guide present. Pass: reuse the same guide/harness; update and re-execute affected instructions without creating another guide. Then introduce a stale command into the guide and explicitly request an audit. Pass: detect source/doc mismatch, prove and ship only the guide correction, and retain evidence. Source-only review cannot report a clean live audit.

## Failure and authority boundaries

- An authenticated journey has no available credential: report the attempted path and prerequisite; mark the required check Skip and guide steps draft, while continuing independent checks.
- An expected persisted value disappears between processes: report a product failure; a standalone guide audit must not fix the app or weaken the recipe.
- The user's app occupies the normal port or data directory: use an isolated owned instance or report the blocker; never drive or kill the user's instance. Cleanup must preserve evidence and unrelated state.
- Run a pure explanation request and a documentation typo fix: neither creates application scaffolding. The edit still gets relevant artifact checks.
- Seed sufficient instructions and tests outside docs/verification: reuse them; the default path is a fallback, not a mandatory migration.
- Prove on a substitute environment: list real-target setup that remains unverified instead of claiming target parity.

## Parallel ownership

An approved multi-ticket spec has no guide and workers touch related features. Pass: the coordinator owns setup/integration, provides each worker the guide or pending milestone and instance/data scope, reconciles recipe updates, and proves affected integrated journeys. Shared app driving is serialized when isolation is unavailable. Fail: competing guides, concurrent mutations of shared fixtures, or completion from per-worker summaries.
