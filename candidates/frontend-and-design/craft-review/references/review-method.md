# Review lenses and findings

Use the approved direction, real content and audience as the reference. A dense operations tool, public service and expressive portfolio can all show craft with different visual languages. Premium appearance has no universal objective score.

| Dimension | Questions and evidence | Handoff when correction is authorised |
|---|---|---|
| Visual precision | Do hierarchy, baseline/optical alignment, semantic spacing, wrapping, icon weight and surfaces support the task? Capture the actual state at relevant sizes. | `ui-polish`; `interface-design` if the foundation or direction needs to change. |
| Interaction quality | Is acknowledgement immediate and completion truthful? Exercise dismissal, focus, repeat input and interruption on safe data. | `ui-polish`, with `motion` for temporal behaviour and `accessibility` for access needs. |
| Technical smoothness | Are there visible shifts, delayed input, flickering placeholders or stutter? Record the symptom; use traces or timings to investigate causes. | `performance` for causal measurement; do not infer a cause from a screenshot. |
| Behavioural completeness | Can people recover from failure without losing work? Inspect relevant empty/loading/error/success states, long content, native links and navigation. | `ui-polish` for bounded refinement; the appropriate implementation owner and `verify` for behaviour. |
| System coherence | Does the same component behave consistently across contrasting screens, themes and states? Are differences justified by their jobs? | `ui-polish` for shared-component corrections; `interface-design` for changed system rules. |
| Restraint | Does anything compete with the main task, repeat an explanation or add a needless interaction? Check what would be lost by removal. | `ui-polish` within the approved direction; escalate changed flow or information architecture. |

## Finding format

For each material finding include:

- **Location and evidence:** route/component, state, viewport/input, observation and capture or measurement reference.
- **Evidence class:** observed defect; causal hypothesis needing a named check; or preference relative to the approved direction. Do not label a hypothesis confirmed because it is plausible.
- **Consequence and reach:** who is affected, what task becomes harder and whether the fault repeats through a shared component. Use qualitative priority with a reason.
- **Correction and owner:** the smallest useful change and the existing owner that should implement or investigate it.
- **Verification:** setup, action and observable result, including a neighbouring shared-component use when relevant.

Separate observation from cause: a recorded heading jump is observed; a fallback-metric mismatch needs inspection of the loaded fonts. An error message alone does not prove that edits survived. A shorter animation is a hypothesis until the interaction is experienced. Treat familiar patterns as contextual questions rather than automatic defects.

## Finish

Lead with the most useful diagnosis and up to three priorities, then the supporting findings, what worked and evidence limits. If fewer findings are warranted, say so. If the interface is unavailable, provide a bounded provisional assessment from the supplied evidence and name the missing surface checks; do not fabricate a completed walkthrough. A screenshot-only assessment stays within visible composition even when asked whether the whole experience is polished.

This independently written method is informed by the supplied craftsmanship synthesis, [Vercel's interface guidelines](https://vercel.com/design/guidelines) and [Linear's redesign account](https://linear.app/now/how-we-redesigned-the-linear-ui). No article text, assets or private source note is included.
