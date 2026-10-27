---
name: data-visualization
description: Design, generate, and verify truthful accessible charts, figures, or analytical dashboards for a defined question and audience.
---

# Data Visualization

## Outcome

A rendered visual whose encoding, labels, scale, uncertainty, and emphasis support correct interpretation.

## Method

1. Choose the chart from the comparison task and data shape. Preserve truthful baselines and scales; label units, definitions, sources, and uncertainty.
2. Use accessible colour and direct annotation, then render at the target size.
3. Inspect the rendered image for clipping, density, legibility, and misleading emphasis; fix observed failures and render again. Done when the actual output supports the intended comparison and unavailable checks are disclosed.

For a React/shadcn product dashboard that needs a chart implementation, read [Bklit](references/bklit.md) as an optional source after choosing the encoding.

## Boundaries

Product dashboard interaction also needs interface-design. Never invent data to improve composition.


## Method detail and preservation

Read [chart methods](references/chart-methods.md) for the specific analytical methods, failure cases and verification needed by the task. These are independently authored methods; [source treatment](references/NOTICE.md) and the reviewed source register travel with the bundle. Use the [preservation cases](evals/preservation-cases.md) when evaluating a material method change. No proprietary runtime, publication service or historical plugin path is required.
