# Analytical methods

Independently authored guidance for the owned analytical workflow. This is an operational reference, not a copied upstream skill or a source of account permissions. Choose the methods the question warrants; a short answer still needs defensible evidence.

## Define the claim before calculating

Write the decision and the observation that would change it. Separate a description (what happened), a forecast (what may happen) and an intervention claim (what would happen if we changed something). Agree the population, observation unit, eligibility rules, measure, denominator, period, timezone and comparison. Record exclusions and whether the period is complete. A user, session, account and event are different units; do not silently substitute one for another.

For each headline measure retain its definition, owner/source, extraction time, query or transformation, units and freshness. Rates need the underlying numerator and denominator. Recalculate a combined rate from the combined counts; averaging group percentages is valid only under the corresponding weighting assumptions. Distinguish a count change, relative percent change and percentage-point change. A zero denominator is undefined, not 0%.

Use the rawest relevant authorised data that makes the decision reproducible. Start with narrow schema, definition and sample checks; query only needed fields and rows. Context can explain a result but cannot replace the controlling metric source. A source preview, an old screenshot or an anecdote is not the underlying population. Resolve conflicting definitions with their owners or present both explicitly; do not combine unlike series merely because their labels match.

## Establish data fitness

Inspect types, valid ranges, key uniqueness, time coverage, outliers, missing values, record counts and selection effects. Distinguish unavailable, not applicable, suppressed and observed zero. Measure missingness overall and by important segment; complete-case results may change the population. Preserve raw inputs and document cleaning, including any deduplication rule. Never quietly drop inconvenient outliers or fill unknown measures with zero.

Before a join, state its expected cardinality and count unmatched keys. Check row counts and additive totals before and after. In pandas, `validate` can reject a violated one-to-one or many-to-one contract and `indicator` exposes match coverage. Null keys can match other null keys in pandas; quarantine or explicitly account for them rather than assuming SQL null semantics. A valid cardinality does not establish that the keys mean the same thing.

For large sources, inspect and aggregate near the source where practical. Record sampling and access limitations. If a required source is inaccessible, state the exact missing evidence and narrow the conclusion. Do not invent a result, silently switch to weaker evidence, upload private rows to a new service, or treat demo data as observations.

## Explain differences and test alternatives

Reconcile the headline difference to its components. Inspect relevant cohorts, distributions, volumes and seasonal/calendar effects before blaming a feature, person or campaign. Consider instrumentation changes, late arrivals, denominator shifts, segment composition and selection effects. Name the prevailing explanation, a competing explanation and what observation would discriminate them. Association alone does not identify an intervention effect.

For an additive total, a bridge should reconcile exactly from start to end without double-counting overlapping drivers. For a rate, distinguish changes within segments from changes in their mix. Compare a common set of segments and standardise to an explicit weighting population when useful. Show both observed and standardised results and explain what the latter controls for. Do not present a decomposition as unique when ordering or interactions affect it.

Example: 81/90 Desktop and 1/10 Mobile observations give 82% overall. Later, 9/10 Desktop and 9/90 Mobile give 18% overall. Both segment rates are unchanged. A claim of deteriorating segment performance fails; changing composition explains this fixture. The appropriate next real-world question is why the mix changed, not a confident causal story invented from these counts.

For a launch or business recommendation, connect the effect size to the decision threshold, costs and plausible harms. Retention cohorts need comparable follow-up time; funnels need ordered events, eligibility and deduplication rules; experiments need the actual randomisation unit, exposure definition and assignment integrity. Diagnose those assumptions before interpreting a metric.

## Quantify uncertainty and robustness

State whether uncertainty comes from sampling, measurement, missingness, modelling or future scenarios. Choose a method suited to the design, dependence and sample size. For an approximately appropriate independent-sample mean model, a t interval uses the sample mean, sample standard deviation, sample size and the relevant t critical value. Confidence describes the procedure's long-run coverage, not a probability assigned to the realised fixed interval. Do not use a mean interval as a prediction interval for individual observations.

Report the estimate, meaningful bounds, method, confidence level, n and assumptions together. Retain asymmetric bounds. Small samples, clustered observations, repeated measurements and skew can invalidate a casual normal approximation. Use an appropriate method or report that supported inference is unavailable. Significance of a difference requires analysis of that difference; overlapping or separate group intervals are not a substitute.

Run sensitivity analyses for consequential assumptions. Distinguish a confidence interval from a best/worst missing-data scenario. For 2 successes among 5 observed outcomes and 3 unknown outcomes, 40% is the observed-data rate; 25%–62.5% is the full-population range under extreme unknown outcomes. Neither extreme is a probability statement. State which choices would reverse the recommendation.

Avoid selecting a favourable test after seeing results. Keep exploratory comparisons distinct from a prespecified confirmatory claim; disclose multiple comparisons and material model choices. Statistical significance alone does not establish useful size, causality or absence of risk.

## Validate predictions without leakage

Separate held-out data before any transformation that learns from the data. Fit imputation, scaling, feature selection and models only on training data. Use time-ordered or grouped splits when future observations or repeated entities would otherwise leak information. Compare with a simple relevant baseline and report the chosen error measure on untouched holdout data, sample size and any shift between training and evaluation populations.

A pipeline can keep fitted preprocessing together with the estimator. It does not repair a wrong split, leaked target feature or repeated use of the holdout set to choose a model. If data are too sparse for a credible evaluation, say so; do not relabel in-sample fit as predictive performance.

## Choose the analytical work product

| Need | Useful method and completion evidence |
|---|---|
| KPI definition | Specify purpose, formula, eligibility, grain, period, source, owner, target and intended response. Include a counter-metric where optimising the headline could create harm. |
| KPI readout | Reconcile actual versus comparable prior period and target, show volumes and relevant history, investigate material changes and state the decision or next observation. |
| Quality investigation | Quantify which rows/fields are affected, compare segments and time, identify whether the flaw can change the decision, and propose a bounded repair or qualified use. |
| Market sizing | Separate population, eligibility, adoption, frequency and price; align currency and period. Cross-check bottom-up and top-down estimates where evidence permits. Expose assumption ranges and avoid presenting a broad scenario as a measured market. |
| Product or business choice | Compare realistic alternatives against the decision's costs, benefits, evidence quality, uncertainty and reversibility. Explain the unsupported claims and the next discriminating evidence. |
| Reusable notebook | Keep inputs, definitions, transformations and environment discoverable. Restart and run in order; do not rely on hidden cell state or a manual edit to an exported result. |
| Report or dashboard | Use the requested surface and validated measures. A dashboard also needs meaningful filters, freshness, empty/error states and consistent filtered denominators. Styling does not certify the analysis. |
| Reusable context | Save approved definitions, schema, source paths and limitations in the project's authoritative location; keep credentials, personal rows and speculative conclusions out of generic context. |

Inline, report, dashboard, notebook and export are packaging choices, not different standards of evidence. Honour an explicit deliverable. Resolve consequential ambiguity with available context; do not introduce a mandatory host switch or require unavailable vendor machinery. Consult `data-visualization` for chart design and the appropriate artifact owner for spreadsheet, PDF, document or slide delivery.

## Check and deliver

Recompute a material result by an independent route where practical: a hand-worked sample, separate SQL aggregation, known control total or independently reviewed calculation. Check units, signs, rounding, totals and denominators through to the final displayed result. Reopen exported files or rendered outputs and verify that filters, labels, notes and uncertainty refer to the same evidence.

Deliver the decision-relevant finding, its evidence, limitations and an appropriate next action. Retain the reproducible query/code, bounded input identity, parameter values and outputs without exposing unnecessary private data. Distinguish actual findings, interpretations, scenarios and unresolved questions. Creating a local artifact is not permission to publish, email, schedule or change the source system.

## Primary references and provenance

The source register in [sources.json](sources.json) records the exact documentation responses reviewed. No source prose, code examples or images are redistributed. These independently written methods use public statistical and software concepts; a response digest identifies the reviewed response and does not claim that an evergreen URL is immutable.

- [pandas 2.3.3 merge API](https://pandas.pydata.org/pandas-docs/version/2.3.3/reference/api/pandas.merge.html): join validation, indicators and null-key behaviour.
- [NIST mean confidence intervals](https://www.itl.nist.gov/div898/handbook/eda/section3/eda352.htm): interval calculation and interpretation.
- [scikit-learn 1.7 common pitfalls](https://scikit-learn.org/1.7/common_pitfalls.html): evaluation isolation and preprocessing leakage.
