# Bounded measurement

Choose the smallest improvement worth acting on before comparing candidates. Verify that the workload performs the intended work and includes correctness checks for affected callers. Prefer an operation count when it faithfully explains the bottleneck; report it as a proxy until a representative runtime measurement confirms a latency claim.

For variable timing or model output, inspect no-change variation first. Pair baseline and candidate under comparable load, alternating execution order when order effects matter; fix workload, configuration and aggregation. Repeat only enough to resolve the decision. A median of three measurements is not automatically reliable, and a small difference inside observed variation is inconclusive.

Spend each experiment on one causal hypothesis with enough potential headroom to matter. Reuse valid profiles and results rather than rerunning them to recreate an explanation. Record the hypothesis, exact change, comparable measurements, preservation checks and retain/discard decision. Review implausible gains for reduced work, omitted failures or measurement changes before accepting them.

Begin with one targeted experiment. Continue only when evidence identifies another worthwhile in-scope hypothesis; default to at most three candidate attempts, including failed ones. An explicit task budget overrides this default. Stop sooner when the target is met, two successive attempts fail to produce a useful gain, measurement cannot resolve the gain, a guard fails, or the next step needs a scope decision. Never extend a limit silently. Reserve time and any paid-call allowance for final confirmation and required review before beginning another attempt.

On the selected candidate, run broader representative workloads and affected correctness checks. A changed environment or a fixed benchmark needs a fresh baseline. Keep the last demonstrated good state if confirmation fails; report the attempted change and remaining uncertainty. Ordinary profiling or a single fix does not require a new coordinator, panel or numerical quality rubric.
