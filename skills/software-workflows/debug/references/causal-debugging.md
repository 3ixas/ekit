# Causal debugging

## Make the symptom precise

Record the observed result, expected result, environment, inputs, timing, frequency, and last known good state. Reproduce with the smallest faithful path. If reproduction is unsafe or unavailable, gather existing telemetry and state what cannot be established.

Separate facts from hypotheses. Build a short causal timeline across boundaries: input, validation, state read, decision, write, side effect, response. Compare a failing case with a working case and change one meaningful variable at a time.

## Test hypotheses

Write each hypothesis as a falsifiable statement with the observation that would support or reject it. Prioritize by explanatory power and cost to test, not by ease of patching. Add narrow temporary instrumentation where the causal chain is invisible, then remove or intentionally retain it as useful observability.

Inspect recent changes and dependencies, but do not equate correlation with cause. After two failed fixes or contradictory observations, reset the premise: reproduce again, check that the inspected process and data are current, and reconsider environment, concurrency, caching, and test assumptions.

## Correct and prove

Fix the earliest responsible cause at its owning boundary. Do not mask a bad state with default values, broad exception handling, retries, or timing delays unless those are part of the intended contract. Search for sibling paths sharing the same faulty assumption.

Prove the original reproduction now passes, the targeted regression test fails without the fix when practical, and nearby success and failure cases remain correct. Use `verify` for the real-surface proof and report any production-only evidence that remains unavailable.
