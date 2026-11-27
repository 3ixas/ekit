# which-skill behavioural eval

`scripts/verification/which_skill_eval.py` checks that `which-skill` recommends the right owner. It gives every case in `evals/routing.json` to a fresh, non-interactive Claude session and a fresh Codex session. The request comes from the case. The runner is local and opt-in, makes real model calls, and is never part of CI.

## Isolation

Each isolated temp workspace holds this checkout's active bundles, as a host synced from it would list them, so the eval tests the branch and not the last sync. Installed copies are hidden: an installed personal skill shadows a workspace skill of the same name.

- **Claude** runs with `--setting-sources project` and `--no-session-persistence`, which also leaves out user settings, plugins and `~/.claude/CLAUDE.md`, so it uses the CLI's default model unless `--claude-model` is set.
- **Codex** runs with an empty `HOME` and the real `CODEX_HOME`, which keeps its sign-in, model config, global `AGENTS.md` and any skills under `CODEX_HOME`.
- One read-only isolated workspace is prepared per run and shared across cases, while each case runs in its own fresh non-interactive CLI session and scratch directory.

```sh
python3 scripts/verification/which_skill_eval.py --subset sample --claude-model sonnet --codex-model gpt-6-luna --output-dir /tmp/which-skill-eval
python3 scripts/verification/which_skill_eval.py --resume --subset sample --claude-model sonnet --codex-model gpt-6-luna --output-dir /tmp/which-skill-eval
python3 scripts/verification/which_skill_eval.py --host codex --codex-model gpt-6-luna --only 0 65 debug
python3 scripts/verification/which_skill_eval.py --claude-model sonnet --codex-model gpt-6-luna --output-dir /tmp/which-skill-full
```

- `--only` takes one or more case indexes (position in `routing.json`) or owner skill ids.
- `--subset` selects a deterministic smaller slice of `evals/routing.json` (mutually exclusive with `--only`):
  - `sample`: one representative case per explicit-only primary, one per automatic owner with a declared `authority_stop`, and every `no_fit` case.
  - `explicit`: every case marked `explicit` in `evals/routing.json`.
  - `boundary`: every case whose owner declares `authority_stop`, plus every `no_fit` case.
- `--resume` (requires `--output-dir`) checks the SHA-256 input fingerprint recorded in `results.json` (projected `which-skill` bundles, `evals/routing.json`, and declared `authority_stop` metadata) and per-host model consistency. When both match, already-passed `(host, case)` pairs are skipped and only missing, failed, or errored cases run; when inputs or a host's model changed, `--resume` refuses with an error instead of mixing stale results.
- **Canary-first guard:** whenever a host has more than 5 pending cases, the runner runs 1 canary case for that host before fanning out the rest across `--jobs` workers. If the canary hits a quota/rate limit or CLI error, remaining cases for that host are skipped immediately without launching parallel sessions. Pass `--no-canary` to bypass the guard.
- `--jobs` sets concurrent sessions per host (default 2); `--claude-model` and `--codex-model` pin a model.

## What passes

- **Owner:** the first `Owner` line names the case's `owner` exactly. A second block in an ambiguous answer does not count. A case marked `no_fit` instead passes when the answer is a plain "no skill applies" with no `Owner` line.
- **Boundary:** when the owner declares `authority_stop` in its `metadata.json`, the `Stops at` line must name the labelled boundary. Either of two readings is enough: it shares at least three keywords with the case's own `authority_stop` label (all of them when the label is shorter), or it carries at least a quarter of the keywords (and two or more) of the owner's declared stop. The second reading exists because many older case labels describe request-specific behaviour, such as reusing a verification guide, rather than the authority boundary, so no faithful answer could match them. Owners without a declared stop are not boundary-checked.

A failed case never edits a label. Fix the cause in `which-skill` (its `SKILL.md`, or the generated catalogue's source metadata) and rerun.

## Output and exit status

The runner prints pass, fail and error counts per host, a case-by-host grid, and each failure with its request, labelled boundary, `Stops at` text, shared keywords and transcript path. Raw answers and `results.json` (`{"fingerprint": ..., "outcomes": [...]}`) go to `--output-dir`, or to a temp folder it names; `results.json` is updated atomically as cases complete so interrupted runs can be resumed with `--resume`. A session that errors or hits a provider usage limit is reported as `error`, not `fail`; on a quota or rate limit the runner stops spawning remaining queued sessions for that host.

Running all 75 cases launches 75 fresh sessions per host (each loading the ~9.4k-token Skill catalogue). For routine iteration, prefer `--only` or `--subset sample` with `--resume` and lighter models — for example `--claude-model sonnet` (or `haiku` for fast checks) and `--codex-model gpt-6-luna` — reserving flagship models (`--claude-model opus` / `--codex-model gpt-6.2-sol`) for targeted `--subset sample` or `--only` confirmation runs.

Exit 0 when every case passes, and also when a CLI is missing: each missing `claude` or `codex` prints a skip message, and with neither present the run skips entirely. Exit 1 when any case fails or errors, and exit 2 on invalid arguments or a `--resume` fingerprint or model mismatch.
