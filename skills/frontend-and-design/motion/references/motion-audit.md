# Motion audit and diagnostics

Use this sequence for an app-wide motion review; for a focused request, use only the relevant steps. Scope the surfaces and platform first, inspect the actual interactions, and preserve documented product decisions. Findings from code alone are candidates, not proof of feel or performance.

## 1. Assess and remove

Map motion by surface, trigger, purpose and likely frequency. Sweep existing transitions, keyframes, animation utilities, motion-library props, scroll reveals, loops, route changes, loading indicators and animated data. Check keyboard and frequently repeated actions especially; also look for decorative reveals that delay content and repeated chart entrances. Frequency and input method are prompts for judgment, not automatic deletion rules. Keep feedback or continuity that earns its place; record the reason for both kept and proposed removals.

Before removing or reducing motion, trace hidden initial states, completion callbacks and timers, exit/unmount sequencing, focus movement, layout shifts previously masked by motion, and tests or selectors that wait on it. Preserve final visibility, state, focus, accessibility and interaction timing. Remove orphaned animation code only after checking its references; do not remove a dependency without task authority. Verify the actual interaction, including repeated and interrupted use and reduced motion. Report changed and deliberately retained motion and any unverified surfaces.

## 2. Improve what remains

Use motion-design and, for a whole-codebase audit, the historical improve-animations snapshot for its recon, categories and plan format. Vet findings against observed behaviour, the product and current owned guidance. Prioritise specific, evidence-backed improvements; state when feel requires a real interaction or device check. A request for assessment alone does not authorize edits. Implement selected changes when the task authorizes them.

## 3. Diagnose performance

Map the affected interaction, driver, animated properties and concurrent work. With the performance skill, capture a comparable baseline and profile frames, long tasks, layout, paint and input responsiveness on representative devices where available. Investigate measured suspects: per-frame React renders, inherited custom-property updates across large subtrees, expensive blur or shadows, unintended `transition: all`, layout work, and main-thread contention during navigation or loading. These are hypotheses, not automatic defects.

Prefer compositor-friendly visual movement where it preserves the interaction; genuine content reflow may require layout. CSS or WAAPI may allow off-main-thread animation, but acceleration is conditional on the browser, property and implementation. Check the installed Motion version and current documentation: upstream reports HTML transform shorthands can accelerate from Motion 14.2, while older versions and dynamic or layout-driven paths differ. Never infer acceleration or a speedup from syntax alone. Avoid blanket `will-change` or dependency upgrades; compare the actual trace before and after, including interruption, visual correctness and reduced motion. Report device and measurement limits; desktop throttling is not proof of real phone GPU behaviour.
