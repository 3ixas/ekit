# Chart methods

Independently authored design and verification guidance. Start with the reader's comparison, not a preferred library. An installed renderer supplies capabilities, not analytical justification or permission to publish.

## Prepare the chart's evidence

Record the question, audience, source, extraction time, population, grain, units, denominator and period. Determine whether values are observations, estimates, forecasts or scenarios. Preserve unknown values explicitly. Validate the measure before drawing conclusions; use `data-analysis` when the task needs analytical inference or a data-quality investigation. A synthetic design fixture must be labelled and kept separate from real evidence.

Retain only the bounded reviewed data needed for the requested output. Do not embed credentials, personal identifiers, private reasoning or an entire source table in a downloadable HTML page. A summary visual can still expose sensitive small groups; review the authorised disclosure boundary before export or sharing.

## Match encoding to the task

| Reader's task | Candidate forms | Check before choosing |
|---|---|---|
| Compare categories or rank | Aligned bars or dots; a table for exact lookup | Preserve a meaningful order; use horizontal labels for long names. Bars showing absolute magnitude need a zero baseline. |
| Follow measured change over time | Line or points with dates; bars/dots for a few discrete periods | Respect actual spacing and gaps. Do not imply observations between isolated points or invent history to fill a design. |
| Compare distributions | Histogram, box plot, empirical distribution or individual observations | State binning and sample sizes. Summaries can hide tails, clusters and outliers. |
| Examine association | Scatter plot; density or aggregation when points overlap | Both axes must describe comparable units/populations; correlation is not an intervention effect. |
| Show a partition | Stacked bars or small multiples; a pie only when angle/part-whole reading is useful | Categories must form a meaningful whole. Overlapping audiences do not sum to 100%. |
| Explain an additive change | Waterfall/bridge | Contributions and endpoints must reconcile; label interactions and residuals honestly. |
| Show estimates and uncertainty | Point with bounds or a supported band; bounds table if rendering is inadequate | Define interval type and level. Preserve asymmetric limits and distinguish forecast/scenario ranges. |
| Examine a matrix | Heatmap plus useful labels/table | Define a continuous sequential or diverging scale. Differentiate missing combinations from observed zero. |
| Compare many series | Small multiples, highlighting or a focused selection | Shared scales and units support magnitude comparisons; independent scales require explicit explanation. |

Keep chart variety subordinate to the question. A simple repeated form is useful for comparable measures. Top-N displays need a stated selection rule and a route to the remaining values when needed. An Other group is valid only when mutually exclusive additive categories can be combined without changing the measure's meaning. Recompute rates from their counts instead of summing percentages or averages.

## Scales, units and absence

Label units and any transforms visibly. A log axis cannot show zero or negative observations; choose another encoding or explain a defensible treatment. Never drop those values without disclosure. Dual axes can manufacture a visual relationship; use a common scale, normalisation with an explicit base, or separate aligned panels when that makes the comparison clearer.

Use the same scale, ordering and time window across related panels unless the intended comparison requires otherwise. Absolute bars should extend from zero. A focused line or change scale may be useful, but show its bounds and context rather than hiding a truncation. For values crossing zero, keep the zero reference visible and sign unmistakable.

Missing time points create gaps, explicit missing markers or notes. Do not turn them into zeros or join a line across them as if measured. Date labels should locate the first and latest observations and remain readable. Format rates as percentages consistently in axes, labels and tooltips; do not mix fractions and percent units.

## Uncertainty and interpretation

Keep the estimate and its uncertainty together. Record the method, confidence/coverage level, sample and population in the accompanying evidence. Do not manufacture symmetric bounds, average interval endpoints across groups, or reuse aggregate intervals after filtering. Scenario limits, individual spread and sampling confidence describe different things.

A chart must not imply that the overlap of two intervals establishes significance or that an event annotation proves causality. Add an annotation only when it helps the specific reading task and is supported by the shown data or a source actually checked. Keep limitations adjacent to the relevant claim rather than hidden in a distant appendix.

## Accessible presentation

Make the essential comparison available without seeing the image. Supply a short identification/summary and a longer description or data table with the important values, pattern and qualifications. Associate them with the figure. Table headers and reading order should be meaningful independently of the picture. An image-only PDF export may need an accompanying accessible document; do not claim that visual rendering proves PDF accessibility.

Use more than hue for series and states: direct names, position, line patterns, point shapes, fill treatment or explicit labels. Retain meaningful identity across views. Check grayscale and, when tools permit, common colour-vision deficiencies. If simulation is unavailable, disclose that and assess the redundant encoding rather than asserting simulated results.

Choose readable text sizes at the intended display/export dimensions. Allocate space for long labels, negative signs, endpoints, notes and uncertainty bars. Prefer wrapping, more space or a simpler view to tiny fonts. Avoid decorative marks, 3D perspective and area/volume encodings that distort precise comparisons. A restrained palette and hierarchy should help identify the evidence, not supply an unsupported narrative.

## Delivery and implementation

Honour the requested surface: inline view, document figure, static image, notebook, report or interactive dashboard. Use available installed tools and a renderer whose documented features support the intended encoding. A renderer limitation is a reason to change the implementation or disclose a limitation, not to omit uncertainty silently. Do not assume a proprietary shared runtime, plugin path, remote script or package install exists.

For product dashboards, preserve the established application stack and consult `interface-design` when interaction or layout needs work. [Bklit](bklit.md) is optional for an appropriate React/shadcn application. A connected account, new renderer, hosted site or distribution action still needs its own authority. Keep local previews and exports separate from publication.

For interactive views, test that the principal filter changes the chart, bounds, denominator, annotations, exact-value view and export together. Verify empty, loading, failure, one-point, all-zero, negative and missing-value states where they are possible. Keyboard/touch access and focus need real testing in the chosen UI; a static chart cannot prove those behaviours.

## Inspect the actual result

1. Compare plotted values and labels to the reviewed table, including units, periods, signs, totals, missingness and denominator. Check that a percentage point change was not labelled as percent growth.
2. Render at intended normal and narrow dimensions and in each requested export. Inspect every chart for clipping, collisions, illegible text, misleading spacing and lost uncertainty.
3. Check the text/table alternative and the claimed non-colour distinctions. Inspect grayscale; record any unperformed screen-reader, browser, contrast or colour-vision checks precisely.
4. Exercise the main interaction if one exists. Keep the evidence and annotations aligned after filtering or refresh; do not leave obsolete claims attached to a new population.
5. Correct observed faults and render again. Record the final file/revision, the scope of the checks, known limitations and the source data identity. A valid SVG, successful build or screenshot alone is not analytical or accessibility clearance.

## Primary references and provenance

[sources.json](sources.json) identifies the reviewed public documentation responses. This guidance contains no copied upstream prose, code samples, images or runtime. The fingerprints identify retrieved responses; evergreen pages are not claimed to be immutable revisions.

- [Government Analysis Function chart guidance](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-charts/): chart selection and scale/readability practice.
- [W3C complex images tutorial](https://www.w3.org/WAI/tutorials/images/complex/): meaningful text alternatives for charts.
- [W3C WCAG 2.2 use of colour explanation](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html): information must not depend only on colour.
