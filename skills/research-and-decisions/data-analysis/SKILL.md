---
name: data-analysis
description: Analyze quantitative, product, or business data with explicit grain, quality, assumptions, reproducible methods, validation, and decision relevance.
---

# Data Analysis

## Outcome

A reproducible analysis whose claims follow from validated data and whose uncertainty is visible.

## Method

Before analysing, deepen the brief: name what an expert analyst would do that was not asked for, the rawest data available, the methods and tools they would use (a database and a statistical model, not a summary table), and the independent evidence that would confirm the answer. Put any change of scope to Elias rather than adopting it.

1. Establish the decision, population, grain, time window, and metric definitions so the result can be reproduced.
2. Inspect freshness, missingness, joins, duplicates, and bias. Record limitations that could change the conclusion before interpreting the results.
3. Analyse reproducibly in Python or SQL. Test the prevailing explanation adversarially against the raw data, not only alternatives to it.
4. Validate calculations independently. For a predictive claim, hold data out before fitting and report performance on that held-out data.
5. Connect findings to the decision and preserve the reproducible artifacts. Done when the conclusion is supported by the validated results and its material uncertainty is explicit.

## Boundaries

Do not hide data limitations or let a polished chart substitute for a valid method.


## Method detail and preservation

Read [analytical methods](references/analytical-methods.md) for the specific analytical methods, failure cases and verification needed by the task. These are independently authored methods; [source treatment](references/NOTICE.md) and the reviewed source register travel with the bundle. Use the [preservation cases](evals/preservation-cases.md) when evaluating a material method change. No proprietary runtime, publication service or historical plugin path is required.
