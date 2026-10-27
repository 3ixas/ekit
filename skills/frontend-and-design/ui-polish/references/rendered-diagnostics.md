# Rendered diagnostics

For a broader tool-backed pass, use interface-design's shared Taste inspector through that skill's `references/taste-toolkit.md`; apply the project's recorded policy and retain the finding categories and unexecuted checks. Do not copy the toolkit into ui-polish.

Use when the render suggests clipping, overlapping text, unintended scrolling, unreadable text or a broken asset. These targeted measurements complement the screenshot audit; they do not score taste or prove accessibility. Independently written, informed by the reviewed Designer Stack v6 browser and visual-QA methods.

## Measure the reported defect

Use the host's existing browser and record route, state, theme, viewport and affected selector. Wait for the page's actual fonts, images and loading state before judging it. Prefer a local reproduction with representative content; do not upload private screenshots to another service without authority.

| Symptom | Evidence to collect | Boundary |
|---|---|---|
| Sideways page movement | Document `scrollWidth` versus viewport width; find the element extending the page. | An intentional gallery whose own `overflow-x:auto` contains its content is different from document overflow. Test reaching its final item. |
| Cut-off meaningful text | The element's `scrollWidth`/`scrollHeight` versus client dimensions, computed overflow and a close screenshot. | Ellipsis, scrolling text areas and collapsed disclosures can be intentional; compare with the product contract. |
| Text collision | Screen coordinates of the actual text runs, their clipping/stacking context and a screenshot of the intersection. | Parent boxes intersect normally. Decorative overlaps can be intentional. Confirm that readable content or a control is obscured. |
| Broken image | `complete`, `naturalWidth`, selected source and the rendered fallback. | Not-yet-loaded and lazy off-screen images need their real loading state tested first. |
| Low contrast | Computed foreground, effective background and text size/weight; inspect every supported theme. | Transparency, gradients, images, canvas and video can make ancestor background colours misleading. Mark unmeasured contrast unresolved and inspect the rendered region; use accessibility guidance for the applicable requirement. |

Preserve valid project choices such as system/Inter headings, gradients, punctuation, card counts and intentional motion. Generic aesthetic patterns are critique questions, not mechanical failures. Chromium findings do not establish Safari, keyboard or assistive-technology behaviour; retain the existing mobile-web and accessibility checks.

Report the observation, interpretation, fix and recapture for the affected state. A limited DOM API, unavailable browser or missing measurement is a verification limit, never a clean result. Use the available host API for the specific measurement and do not install another browser merely to force the toolkit to run.

## Text baked into pixels

For suspected overprinted text in a screenshot, PDF, slide or canvas, inspect a close crop first. DOM measurements cannot inspect text baked into an image. The reviewed upstream OCR scanner is not installed or required by this workflow: OCR confidence and intersecting word boxes are only clues and can miss short labels or flag unfamiliar scripts and illustrations. If a project's existing OCR tool is useful, check its language models and compare flagged crops with the actual image. Missing OCR or too little readable text means it could not judge. Artifact-specific skills still own rendering and final inspection.
