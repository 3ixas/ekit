# Bootstrap: the baseline workflow for a new repository

Use when creating a repository, or when first working in one with no `.github/workflows`. Propose the files and show the diff; pushing the workflow or enabling branch protection needs Elias's say-so.

## Principle

CI starts on day one and only ever gains gates. It does not wait for an audit. The baseline holds what the repository has when it is created; each later check joins the same single command.

## The baseline

- **One entry point.** A single `check` command in the repository's own tooling (`package.json` script, `make check`, `just check`) runs lint, typecheck and tests. CI runs that command and nothing else for checks, so local and CI never differ.
- **Every branch push, plus forks.** Trigger on `push` for all branches so a branch gets feedback when pushed. Run `pull_request` jobs only for fork PRs, because a same-repository PR would repeat the push run.
- **Least privilege.** `permissions: contents: read`; no secrets in checks; no deploy step.
- **Reproducible.** Pin the toolchain version and use a frozen-lockfile install. Cache the package manager's store.
- **Cheap guards.** Lint the workflow files (actionlint), run `git diff --check`, set `timeout-minutes`, and cancel superseded runs with a `concurrency` group.
- **A coverage guard.** Once the repository has more than one verify script, add a check that fails when a script named `verify*` is not run by CI. This stops CI quietly rotting as the repository grows.

## By stack

Detect the stack from the repository; do not copy another repository's file.

| Stack | Setup | Check command runs |
| --- | --- | --- |
| Node, web app | Node + pnpm/npm/yarn from the lockfile | lint, typecheck, build, unit tests |
| Python | Python version from `pyproject.toml`; `uv` or pip from the lockfile | ruff/lint, type check, pytest |
| Swift / iOS | macOS runner, Xcode version pinned | build, unit tests on a simulator |
| Library / CLI | the language's toolchain | lint, tests, a build of the published artifact |

## Added later, not in the baseline

- **Browser end-to-end tests**, once they exist. When the suite grows slow, shard it across parallel jobs, and run it in a pinned browser image rather than installing browsers per run.
- **Build-reading checks** (routes, sitemap, metadata), once a build exists and `app-audit` or the owner has proved them worth keeping.
- **A scheduled live-site check** (links, headers) for anything recurring that needs the deployed site; run it on a cron, not on pull requests.
- **Audit freshness, opt-in.** A check that warns or fails if `docs/review/APP-AUDIT.md` is missing or older than a chosen number of days or commits. Offer it for apps with a release; skip it for throwaway repositories.
- **The Codex review gate.** Opt-in per repository and tied to that repository's merge rules. Never part of the baseline.

## Receiving checks from app-audit

`app-audit` hands over checks it proved. Keep only those that are cheap, deterministic and need no live service; add each to the single `check` command (or the build-reading step), then run the whole gate against a passing case and a deliberately failing one before it is relied on.
