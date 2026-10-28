---
name: motion
description: Design and improve meaningful interface motion, gestures, transitions, timing, springs, sequencing, reduced-motion behaviour, and runtime performance, and direct animation or video rendered from code (launch videos, loops, Remotion, Three.js).
---

# Motion

## Outcome

Motion that clarifies cause, continuity, hierarchy, or feedback without harming control or performance.

## Method

Decide in order: whether it should animate at all given how often it is seen, what job it does, the cheapest tool, transform and opacity properties, curve and duration or spring, interruption and asymmetric exit, then reduced-motion and hover gating. Prototype when uncertain, measure jank and input responsiveness, and inspect the real interaction.

Read [motion design](references/motion-design.md) for the concrete rules, physical correctness, choreography, and review. When the deliverable is an animation or video drawn by code and recorded frame by frame, read [rendered motion](references/rendered-motion.md) for directed prompts, numbers, the render contract, and the frame-by-frame review loop. It links the source snapshots holding exact curves, durations, spring configurations, and recipes.

For web interaction references or a suitable React starting point, consult [Subframe Motion](references/subframe-motion.md) when it fits the task.

For Motion APIs, presence/layout behaviour, MotionValues, Base UI/Radix integration, or a conditional Anime.js/Rive engine, read [implementation sources](references/motion-implementation.md). Match installed versions, preserve the owned design rules, and verify free versus premium access.

For final video files, hero posters or reported video stutter, use [video diagnostics](references/video-diagnostics.md) for bounded file measurements and separate evidence from actual page playback.

## Boundaries

Avoid decorative motion without a product job and never hide state or delay essential control.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [emil-animate](references/source-methods/emil-animate.md): building a new animation with exact values.
- [emil-review-animations](references/source-methods/emil-review-animations.md): reviewing motion code.
- [emil-improve-animations](references/source-methods/emil-improve-animations.md): auditing a codebase's motion.
- [emil-find-animation-opportunities](references/source-methods/emil-find-animation-opportunities.md): finding where motion would help.
- [emil-animation-vocabulary](references/source-methods/emil-animation-vocabulary.md): naming motion precisely.
- [vercel-view-transitions](references/source-methods/vercel-view-transitions.md): React view transitions.

## Taste website scenes

For an approved website signature using scroll scenes, use interface-design's shared Taste toolkit and that skill's `references/taste-toolkit.md`. It contains the stage foundation and capture tool, not a scene catalogue. Keep the project dependency method, native scroll and no-script/reduced-motion rest composition. App feedback still follows the owned motion contract; upstream image or moving-element quotas do not override it.
