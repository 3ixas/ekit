# which-skill behavioural eval

`scripts/verification/which_skill_eval.py` checks that `which-skill` recommends the right owner. It gives every case in `evals/routing.json` to a fresh, non-interactive Claude session and a fresh Codex session. The request comes from the case; the only EKit skill in the isolated temp workspace is the `which-skill` bundle. The runner is local and opt-in, makes real model calls, and is never part of CI.

```sh
python3 scripts/verification/which_skill_eval.py                    # all cases, both hosts
python3 scripts/verification/which_skill_eval.py --host codex --only 0 65 debug
python3 scripts/verification/which_skill_eval.py --output-dir /path/to/keep/answers
```

`--only` takes case indexes (position in `routing.json`) or owner skill ids. `--jobs` sets concurrent sessions per host; `--claude-model` and `--codex-model` pin a model.

## What passes

- **Owner:** the first `Owner` line names the case's `owner` exactly. A second block in an ambiguous answer does not count. A case marked `no_fit` instead passes when the answer is a plain "no skill applies" with no `Owner` line.
- **Boundary:** when the owner declares `authority_stop` in its `metadata.json`, the `Stops at` line must name the labelled boundary. Either of two readings is enough: it shares at least three keywords with the case's own `authority_stop` label (all of them when the label is shorter), or it carries at least a quarter of the keywords (and two or more) of the owner's declared stop. The second reading exists because many older case labels describe request-specific behaviour, such as reusing a verification guide, rather than the authority boundary, so no faithful answer could match them. Owners without a declared stop are not boundary-checked.

A failed case never edits a label. Fix the cause in `which-skill` (its `SKILL.md`, or the generated catalogue's source metadata) and rerun.

## Output and exit status

The runner prints pass, fail and error counts per host, a case-by-host grid, and each failure with its request, labelled boundary, `Stops at` text, shared keywords and transcript path. Raw answers and `results.json` go to `--output-dir`, or to a temp folder it names. A session that errors or hits a provider usage limit is reported as `error`, not `fail`.

Exit 0 when every case passes, and also when a CLI is missing: each missing `claude` or `codex` prints a skip message, and with neither present the run skips entirely. Exit 1 when any case fails or errors.
