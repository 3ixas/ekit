# Analytical preservation cases

Use disposable synthetic data. These are behavioural acceptance scenarios, not a claim that a fresh agent session has passed them. Check the calculated and delivered result; do not merely search for words in the instructions.

| Case | Input / request | Expected observable result |
|---|---|---|
| Grain and mix | Before: Desktop 81/90, Mobile 1/10. After: Desktop 9/10, Mobile 9/90. Explain overall change. | Overall 82% to 18%; Desktop remains 90%, Mobile 10%. Retain counts, identify composition, reject deterioration within either segment and avoid a causal claim. Standardising after to before's 90:10 mix returns 82%. |
| Join fanout | Two source amounts 10 and 20, keys 1 and 2. Dimension key 1 occurs twice. | A naive join has three rows and sum 40. Reject the unexpected many-to-one cardinality before using it; source sum remains 30. Distinguish duplicate business meaning from join mechanics. |
| Null keys | Both sides of a pandas join contain a null key. | Detect potential null-to-null matching and use an explicit quarantine/accounting policy; do not silently treat the match as a known identity. |
| Unknown outcomes | Two successes, five known outcomes, three unknown outcomes. | Observed rate 40%; full-population worst/best range 25%–62.5%, explicitly sensitivity scenarios. Do not present unknown as zero or this range as a confidence interval. |
| Undefined rate | Denominator zero. | Rate unavailable/undefined with reason; no fabricated 0% or divide-by-zero result. |
| Mean interval | NIST worked example: n=195, mean=9.261460, sd=0.022789, t=1.9723. | Approximately 9.258242–9.264679 at 95%; explain procedure coverage and rounded inputs. Do not label this as individual spread, a prediction interval or a causal effect. |
| Held-out leakage | Training outcomes 0,0,0; future holdout outcomes 10,10. Compare constant-mean predictors. | Train-only held-out MSE 100. Using all outcomes to fit gives 36 and is invalid leakage, not improved forecasting performance. Preserve temporal separation. |
| Market scenarios | 1,000 population, eligible 20–40%, take-up 10–30%, GBP50 annual price. | GBP1,000–6,000 annual scenarios. Explain assumption dependence, no measured-market or statistical-interval claim. |
| KPI disagreement | Two authoritative teams use different eligibility definitions under one KPI label. | Record both definitions and their source owners; resolve or report both, do not average incompatible measures. |
| Decision and context | Request a launch recommendation from incomplete cohorts and stale data. | Explain follow-up/freshness gaps, bound the decision, identify required discriminating evidence. Save approved definitions only in the right project context; no invented outcome or automatic source mutation. |
| Artifact packaging | Request a notebook/report/dashboard with the same analytical question. | Preserve definitions and evidence depth across formats; rerunnable notebook or consistent dashboard filters/denominators. If a required tool is absent, state the actual limitation and deliver supported work without asserting publication. |

For a material revision, retain the input, independent expected calculations, actual outputs, environment, caveats and observed failures. A coordinator or independent reviewer should challenge the reasoning, source selection and material losses in addition to inspecting numeric outputs. Deterministic cases cannot establish every future analytical task or replace statistical expertise for a different study design.
