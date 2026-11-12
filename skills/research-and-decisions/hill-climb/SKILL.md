---
name: hill-climb
description: "Refine and thoroughly work through a difficult feature, bug fix or improvement using bounded, evidence-led attempts. Use when Elias requests Hill Climb or accepts a specific recommendation for it. A rough goal or missing evaluation starts preparation, not rejection or immediate looping. Recommend it when uncertainty, repeated failures or consequential trade-offs justify experiments; routine settled work stays with its existing owner."
---

# Hill Climb

## Outcome

An agreed outcome worked through to demonstrated completion and a defensible improvement, or an explicit incomplete/inconclusive result within budget.

## Prepare before climbing

Read [preparation and handoffs](references/preparation-and-handoffs.md). Accept a rough feature request, bug report or difficult destination. Investigate discoverable facts; use `grilling` to settle consequential unknowns about the outcome, success conditions, constraints and trade-offs. For software, use `grill-with-docs` when durable project scope is needed. Reuse agreement from an existing Grilling or Wayfinder session instead of asking again.

Establish observable acceptance checks and what must keep working. Reuse a credible evaluation or develop the smallest sufficient proof with `verify`; use `debug` to reproduce an unknown bug and investigate causes. An executable check may report required behaviours passing/failing rather than a numerical quality score. If evidence or a user decision is unavailable, report the precise gap and next step; do not start speculative fixes. Exploration may begin before the outcome is clear; the experiment loop begins only after the outcome, scope, proof and budget are ready and any consequential agreement is confirmed.

## Run the climb

1. **Choose the bounded work.** Record the confirmed outcome, editable scope, complete acceptance conditions, useful improvement target and preservation checks. Select the difficult slice worth experimenting on; leave ordinary work with its owner. Name relevant alternative approaches and trade-offs without requiring a panel. Load `verify` and its evaluation-validity reference. For features, distinguish missing required behaviour from existing behaviour that must not regress.
2. **Bound the spend.** Read [budget and evidence](references/budget-and-evidence.md) to include preparation, diagnosis, implementation, checks, retries and final confirmation/review. Begin with one targeted attempt; continue only when evidence warrants another, with at most three candidate attempts by default. A thorough request warrants deeper investigation and proof, not an unlimited loop. Set a different finite allowance when the agreed task warrants it; obtain an extension before exceeding a recorded limit. Keep the current model and reasoning, without a standing council.
3. **Preserve the starting state.** Use an isolated checkout or owned artifact copy. Save baseline artifact/diff, harness/environment identity, raw results and preservation checks. Confirm that checks can detect the relevant failure or improvement. If the baseline meets all agreed goals, report or confirm it without a token-filling edit. Preserve unrelated work. Keep held-out answers/traces outside the proposer's accessible context where possible and report isolation limits.
4. **Test one hypothesis.** State the evidence, proposed mechanism and expected effect. Use `debug` for causal diagnosis, `implement` for an authorised feature/fix slice, `performance` for efficiency and `skill-authoring` for skill changes. These supply the work within this one experiment record and budget; do not start nested climbs or duplicate their review. Run the fixed acceptance and preservation checks on the resulting change. Retain only demonstrated useful progress with preservation checks passing; record any unmet requirements as incomplete. Undo only owned failed/inconclusive attempt edits, checking for intervening work. Stop on rollback conflict. Record patch, result and spend immediately. A changed harness, case set or metric needs review and a comparable baseline within the same remaining budget.
5. **Confirm and finish honestly.** Stop at the agreed outcome, after two successive attempts without useful progress, on unresolved noise, a failed preservation check, exhausted allowance or a consequential scope decision. Use the reserved broader/independent confirmation through `verify`, with affected proof and `code-review` owned by the implementation caller. Keep the original baseline until confirmation passes. All required acceptance conditions must pass to call a feature/fix complete; a better score or fewer failures is not enough. Failed/unavailable proof leaves the result incomplete. Do not tune from held-out results and still call them held-out. Describe the strongest demonstrated result within the tested scope; do not claim a global optimum.

## State, report and authority

Keep one concise local record of the agreed goal, scope, proof, budget, baseline, hypotheses/patches, results, remaining requirements, spend and resume state; link raw evidence. Resume only after verifying saved identities, actual completion of interrupted checks and remaining budget. Never repeat a discarded idea without new evidence.

Report baseline versus selected result, completed and unmet requirements, alternatives tried, preservation/confirmation, attempts, available cost evidence and stop reason. Distinguish injected, source-based and live proof. Budget exhaustion is not success.

A recommendation does not start a climb. An explicit request or accepted recommendation authorises preparation; existing task authority governs execution and delivery. This skill adds no authority to publish, merge, activate candidates, buy compute, expose private data or delete valuable data. Use scoped patches and existing checks; no upstream runner, runner-controlled commits, broad resets or untracked-file cleanup. Pure taste critique stays with its existing owner unless a credible check can evaluate the agreed outcome.
