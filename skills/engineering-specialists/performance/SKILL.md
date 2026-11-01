---
name: performance
description: Measure, profile, trace, and improve software performance through causal experiments and paired evidence.
---

# Performance

## Outcome

A demonstrated improvement in a load-bearing metric without correctness regression.

## Method

Choose the user-perceived metric and target, proposing the target an expert would set as a stretch alongside the stated one as the floor (200 ms where 5 s was asked, when the baseline and platform make it plausible); name the decision the measurement supports and check that the workload measures the intended work; capture a baseline; profile CPU, memory, I/O, database, bundle, or trace evidence; form a causal hypothesis; change one mechanism; measure again under comparable conditions; explain consequential results against the observed or plausible limiting factor, without inventing a precise model; retain wins and revert noise.

For visible web instability, input delay, loading flicker or stutter, read [web experience diagnostics](references/web-experience.md) to connect the symptom to a measurable mechanism.

## Boundaries

Do not optimize from intuition, accept shared-runner noise as proof, or trade correctness for an unmeasured gain.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [pstack-performance](references/source-methods/pstack-performance.md)
- [compound-optimize](references/source-methods/compound-optimize.md)
- [addy-observability](references/source-methods/addy-observability.md)
