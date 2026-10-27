# Prompting a design generator

Independently written for this repository, informed by the failure lessons Superdesign records in its skill (`superdesigndev/superdesign-skill`, pinned in `metadata.json`). They apply to any screen generator: Claude Design artboards, Stitch, or a model writing HTML directly.

## Redesigning an existing screen: reproduce, then vary

1. **Read the branch that renders.** Open the page source and find the branch the target route actually renders at the target size (desktop split view, not the mobile fallback; the feature flag that is on). Do not infer layout from component or import names; a wrong branch is the most common fidelity failure.
2. **Reproduce the baseline first.** Generate one screen that faithfully matches the current product, with its real layout, content, and components. Check it against a screenshot of the running product before going further.
3. **Vary from the baseline.** Only then explore alternatives, each derived from the reproduction. Variants generated without a baseline drift toward a generic page that no longer resembles the product.

## Describe structure, not adjectives

A reproduction or first-screen prompt describes what is on the screen and where: "two panes; left: search, three tabs, a list of slim rows; right: preview with a device frame and one primary action". Leave aesthetic adjectives ("premium", "elegant", "sleek") out of it. When the generator lacks context, adjectives become a generic marketing page. Let the design system supply tokens, and put aesthetic direction into the variant prompts, where it is the point.

When the prompt would exceed what the generator accepts, trim to the rendering branch and the token summary rather than letting the request fail and silently retrying with less context. A generator that never received the real page invents one.

## After selection, refine; do not branch

- **Branch** only when Elias asks for alternatives or an options round calls for them.
- **Selection ends branching.** Once a direction is chosen ("use this one", "continue with B"), later feedback refines that direction, however substantial, rather than spawning new alternatives.
- **Fix defects directly.** Exact corrections (wrong copy, a broken link, overflow, a specific spacing value, malformed markup) are edits to the current screen, not regenerations. Regenerate only when the fix needs design judgement. When a request mixes both, put the exact constraints into the one refinement prompt.

## Real brand assets render

When the product has a logo or other identity asset and the screen has a place for it, the real asset appears there, including inside reusable components. Never substitute initials, an emoji, a generic mark, an invented SVG, or the product name as text. Supply the asset to the generator, then check each screen for it before review. Ask which asset to use only when several genuinely compete.
