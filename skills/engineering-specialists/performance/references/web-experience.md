# Web experience diagnostics

Use for a web interface with visible instability, slow feedback or stutter. Start with the user's action and actual symptom; confirm the mechanism with measurements before changing it. Reuse the project's browser, profiling and field telemetry tools. This reference requires no new service or dependency.

| Symptom | Baseline evidence | Candidate mechanism to test |
|---|---|---|
| Headings jump on first load | Cold-load recording, layout-shift entries, font requests and fallback/final geometry. | Font metric mismatch; inspect existing font optimisation before trying measured fallback overrides. |
| Images or panels move surrounding content | Layout-shift sources and actual placeholder/final dimensions. | Missing reserved dimensions or skeleton geometry unlike the delivered content. |
| Typing or clicking responds late | Record action-to-paint, long tasks and relevant component updates with representative data. | Main-thread work, expensive rendering or synchronous event work; profile before memoising or caching. |
| Expansions or transitions stutter | Trace layout, paint, frames and input during normal and interrupted use. | Repeated layout or expensive paint; compare a simpler implementation without changing the interaction's meaning. |
| Loading feedback flashes or seems stuck | Timestamp input, feedback, request completion and displayed outcome for fast, slow and failed requests. | Unstable indicator policy, unnecessary waiting or missing reconciliation; faster spinner motion is not lower latency. |

Keep viewport, device, cache state, data volume, network and measurement method comparable before and after. Inspect one hypothesised mechanism at a time and recheck correctness, recovery and a neighbouring use of any shared component. Report uncertainty or noisy results rather than retain an unproven optimisation.

For load, interaction and stability budgets, consult the current [Web Vitals definitions](https://web.dev/articles/vitals). Distinguish field percentiles from local lab observations; one fast run cannot establish real-user performance. Performance metrics do not score visual taste.

[Improved font fallbacks](https://developer.chrome.com/blog/font-fallbacks) explains font metric overrides. [High-performance CSS animations](https://web.dev/articles/animations-guide) explains layout, paint and compositor trade-offs. Consult installed-version documentation for implementation details. Independently written diagnostic guidance; no source code or article text retained.
