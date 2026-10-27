# Motion implementation sources

Read this when implementing nontrivial Motion code, choosing an SVG/timeline engine, or considering an interactive Rive asset. The owned motion-design rules still decide whether and how much to animate.

## Match the installed platform and version

Inspect the package manifest, lockfile, existing imports and UI primitives first. Search current official docs for that version and platform before changing APIs. For a new modern React integration, use `motion/react` in client components; `motion/react-client` provides motion elements to server components, while hooks, presence and configuration belong in a client component. Preserve working older `framer-motion` code unless migration is required by the task; a library recommendation does not authorize a project-wide migration.

For nontrivial APIs, use the free Motion documentation MCP when connected: search the actual API or interaction (for example `AnimatePresence`, `drag` or `shared layout`) with platform `react`, `js` or `vue`, then read the returned documentation resource. Tool names and access come from the live server. Without it, read the official version-appropriate docs through the available research tools and say the MCP is unavailable; do not stop ordinary work or invent a successful search.

## React implementation checks

- Keep `AnimatePresence` mounted, put conditional children inside it, and use stable unique keys. Choose sequential exits only when the swap should wait. For `popLayout`, verify positioning and ref forwarding against the installed version.
- Use `layout` for a justified layout transition and `layoutId` for a shared element. Scope IDs per component instance to prevent unrelated indicators or cards joining the same transition.
- Use MotionValues for continuous input. Read them in callbacks/effects or derived values, not during React render. Animate the source value and let derived values follow it; check the installed version's supported `useTransform` signatures. Avoid React state updates on every frame and clean up subscriptions.
- Respect reduced motion through the existing app policy; for a new Motion integration consider app-level `MotionConfig reducedMotion="user"`. Preserve feedback and test keyboard alternatives for pointer reordering.
- For Base UI, use the documented `render` element composition, preserving refs and event handling. If Base UI owns unmounting, control open state and coordinate its portal/keep-mounted lifecycle with presence using the installed component's API.
- For Radix, use supported `asChild` composition and controlled state when needed for exit motion. Apply `forceMount` only to the Radix primitive that supports it, never to a DOM element. Verify focus return, Escape, outside click and rapid close/reopen; animation must not break the primitive's behaviour.
- Prefer transform and opacity. A small measured height-to-auto transition may be justified; do not assume layout, filter, clipping, SVG or WebGL work is compositor-only. Measure the real browser and device rather than adopting acceleration claims as guarantees.

## Access boundaries

Only the free documentation server is part of this workflow. Public example metadata or a demo link is not premium source. Inspect connected capabilities and entitlement before offering Motion+ source, audits or visual editing. Do not import or install `motion-plus` from a free example description, reconstruct unavailable premium source, or introduce a paid dependency. Free docs support an independently built alternative. Upstream docs and skill snapshots disagree about some free easing capabilities; verify returned tool access before promising them.

## Conditional engines

**Anime.js:** use the official documentation when the approved interaction needs SVG morphing, motion paths or coordinated timelines, particularly outside React. Prefer the existing engine and CSS for simpler work; do not add a second runtime to duplicate it. Inspect the installed major version, scope imperative work to its component, revert/clean up on unmount, and test reduced motion, interruption, native scrolling and browser cost. Installing `animejs` installs a library, not agent instructions.

**Rive:** consider it for an approved stateful illustration, character or interactive explanatory diagram. It is a separate authoring/runtime trade-off, not a routine button-animation dependency. The CLI can create text-based scenes, preview, inspect, verify and capture frames; confirm current commands in official docs. Work in a dedicated project folder and review generated AGENTS.md/CLAUDE.md before integrating so existing project instructions are preserved. Build structure first, then detail; verify state/data bindings and input, inspect rendered frames and test the exported asset in the target runtime. Keep meaningful controls and accessible alternatives in host UI. Check the current CLI/editor export, signing, account and pricing requirements before promising delivery. No Rive installation, export purchase or prototype follows from merely selecting this reference.

Sources: [official Motion AI Kit](https://github.com/motiondivision/ai-kit/tree/78a83b1485fa70dab9037c480de0c7cf53930df7/plugins/motion/skills/motion), [Motion docs](https://motion.dev/docs), [Anime.js](https://animejs.com/documentation), [Rive agent workflow](https://rive.app/docs/cli/agents). Independently written method synthesis; exact provenance is in metadata.json.
