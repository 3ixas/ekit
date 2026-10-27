# Motion Design

Describe motion as a state transition with a product job. Useful jobs include preserving spatial continuity, connecting cause and effect, indicating state, confirming input, explaining a gesture, and preventing a jarring change. The concrete rules below follow Emil Kowalski's animation practice; his snapshots in `source-methods/` hold the exact curves, duration tables, spring configurations, and recipes.

## Decide in order

Each step gates the next. Do not pick a curve before deciding whether anything animates at all.

1. **Should it animate?** Weigh how often it is seen. Keyboard-driven and very frequent actions (many times a day) get no animation. Frequent ones get minimal motion. Occasional ones get standard motion. Rare or first-time moments can carry delight. Deleting an animation is often the strongest improvement.
2. **What is its job?** Name the job from the list above. "It looks nice" on a frequently seen element fails.
3. **Which tool?** Use the cheapest that works: a CSS transition before keyframes, keyframes before a library. Don't install a motion library for a fade. Extend the codebase's existing easing and duration tokens rather than adding a parallel set.
4. **Which properties?** Animate `transform` and `opacity`. Animating layout properties (`width`, `height`, `top`, `left`, `margin`, `padding`) is a performance defect unless nothing else expresses the change.
5. **Curve and duration, or a spring?**
   - Entering and exiting UI uses ease-out or a stronger custom curve, never ease-in, which delays the part the user is watching.
   - Built-in CSS easings are usually too weak; use the snapshot tables rather than inventing a familiar-looking bezier.
   - Keep UI animations under about 300ms.
   - Springs suit direct manipulation, gestures, and anything that may be interrupted. Timed curves suit transitions with a known duration.
   - Compare springs across libraries by damping ratio: 1.0 never overshoots, about 0.7–0.85 settles with a hint of life, 0.4–0.6 is playful. Position and size may overshoot; opacity and colour never do.
6. **Interruption and exit.** Rapid or gesture-driven motion (toasts, toggles, drags, sheets) must retarget from its current state: use transitions or springs, not keyframes that restart from zero. Make timing asymmetric: deliberate actions (press, hold, destructive confirm) can be slower, and system responses snap.
7. **Reduced motion and pointer gating.** These ship with the animation, not after it. Under `prefers-reduced-motion`, keep opacity and colour changes and drop movement; never remove the feedback. Gate hover animations behind `(hover: hover) and (pointer: fine)`.

## Physical correctness

- Popovers, dropdowns, and tooltips scale from their trigger (`transform-origin`), not their centre. Modals stay centred.
- Never animate from `scale(0)`. Start from roughly 0.9–0.97 scale with opacity.
- After the first tooltip, show subsequent ones without delay.
- A subtle blur can bridge two states where a crossfade would jar.
- Match motion to the component's personality: a playful surface can bounce, a dashboard stays crisp.

## Choreograph sparingly

Animate the relationship the user needs to understand. Give each moment one hero move; secondary moves travel less (about 50–70%) and start shortly after it, and everything else holds. Use small staggers only when the sequence communicates structure; start the next element when the previous one is about a third done rather than strictly in sequence. Keep related elements moving as a unit. Avoid animating every child, delaying the primary task, or combining effects because each is attractive on its own.

## Inspect and measure

Write review notes as specific changes, not feelings: "it feels sluggish" becomes a shorter duration or a stronger ease-out on a named element. Never flash content more than three times a second. Review at normal speed on the target device. Use slow playback only to diagnose. Test first run, repeated use, rapid input, interrupted navigation, slow data, and reduced-motion settings. When performance is in doubt, measure dropped frames, long tasks, layout work, and input latency. In React, write per-frame values to a ref's style rather than to state. A smooth but confusing animation still fails.

## Source snapshots

Open a snapshot only when the task needs its specific material:

- [Building an animation](source-methods/emil-animate.md): the full build sequence with easing, duration, and spring tables, recipes, a never-ship list, and the performance cheatsheet.
- [Reviewing animation code](source-methods/emil-review-animations.md): the ten standards, escalation triggers, and a tiered review format, with a standards catalogue for exact values.
- [Auditing a whole codebase's motion](source-methods/emil-improve-animations.md): the audit procedure and plan template.
- [Finding where motion would help](source-methods/emil-find-animation-opportunities.md): opportunity and restraint checks.
- [Naming motion precisely](source-methods/emil-animation-vocabulary.md): shared vocabulary for describing and requesting motion.
- [React view transitions](source-methods/vercel-view-transitions.md): React's `<ViewTransition>` API.
