# UI Polish Modes

Start from screenshots or the running interface and its references. Preserve the established visual direction. Choose the smallest set of modes that addresses visible problems, then make changes in coherent batches.

When refinement restructures markup or controls, load `interface-design` through the current host and read that skill's `references/redesign-preservation.md` for the affected surface: record relevant links, forms, actions/effects and hooks before editing, then compare and exercise them afterward. A small settled style edit needs only the affected checks. Preserve the approved concept's material choices; explain substitutions using the visual implementation plan in that skill's `references/design-contract.md`, with `verify` proving behaviour beyond screenshots.

## Audit and prioritize

Walk the primary journey and representative states. Judge screenshots rather than the source you or another agent wrote: capture the first screen and full page at about 1440, 768, and 390 px, then ask whether one thing leads at a glance, whether the page reduces to two or three masses when squinted at, whether a competitor could use it unchanged, whether each section's layout differs from its neighbours, whether the phone layout is composed rather than squeezed, and whether anything covers a headline or control. Record findings by user impact and visual reach. Fix foundation problems before local decoration: hierarchy before colour nuance, layout before shadows, component anatomy before one-off overrides.

Ask whether the screen could have come from typing its page type into an agent with no brief. Look for the familiar AI defaults: the centred badge-headline-two-buttons hero, purple or blue gradient backgrounds and gradient text, Inter on slate as the whole palette, three equal cards as every section, emoji as icons, glass and shadow on every surface, an accent used so often it points at nothing, and the newer "editorial" default (cream with terracotta, tiny uppercase labels above every heading, a pill badge above the hero, one italic serif word, hairlines everywhere). Each is a question, not a ban: keep it when the product's direction calls for it, otherwise correct it from the missing decision rather than swapping in another default. Removing defaults without adding substance leaves a thin page, which reads worse than a rich one.

## Hierarchy and layout

Make the main action and reading order apparent. Align related elements, use a deliberate spacing scale, control line length, and remove containers that add no grouping. Balance density with the task. Test narrow, wide, short, and tall viewports rather than treating responsiveness as one mobile screenshot. When spacing looks uneven, measure it in the browser (computed margins, gaps, and padding on the rendered DOM) against the project's spacing scale instead of judging by eye, and report off-scale values with their elements.

## Typography

Give each text style a job. Reduce unnecessary sizes and weights, set readable measures and line heights, align numerals where comparison matters, and verify real font loading. Use hierarchy and spacing before relying on faint colour. Preserve semantic heading order independently from visual size.

## Colour and surfaces

Assign colours by role: canvas, surface, text, border, action, selection, status, and focus. Check contrast in actual component states. Use borders, shadows, tint, blur, and radius consistently and only to communicate elevation, grouping, focus, or material. Avoid stacking every surface treatment on the same component.

## Components and states

Normalize control height, icon scale, labels, affordances, focus, hover, pressed, disabled, loading, success, error, and empty states. Make click targets match their visual grouping. Remove one-off variants that should use an existing project component. Use one icon family across the product, preferring the one already installed; mixed stroke weights and styles read as assembled by accident.

Small interaction details compound (Emil Kowalski). Buttons respond on press, for example a slight scale on `:active`. Popovers and dropdowns grow from their trigger. Nothing appears from `scale(0)`. After the first tooltip, later ones show without delay. Prefer semi-transparent shadows and borders over solid ones where they separate surfaces. [The design-engineering snapshot](source-methods/emil-design-eng.md) has the full before-and-after catalogue and review format.

## Copy

Interface text is part of the design. Give it one voice and check every string on the journey:

- **Actions** name what happens: "Save changes", "Start my trial", "Delete project". Avoid "Submit" and "OK" where a real verb exists. A destructive action names what it destroys and sits beside an equally visible cancel.
- **Errors** say what happened, why in one clause, and how to fix it, next to the field that caused it. Never blame the reader or show a bare code.
- **Empty states** name the emptiness, say why it is empty, and offer one next action. An empty state with no next step is a dead end.
- **Loading and progress** say what is happening ("Uploading 3 of 8 files…") and completion says what changed ("8 files uploaded to Reports"). No unprovable promises such as "Almost done".
- **Headlines** carry one idea in a dozen words or fewer, without exclamation marks or claims the screen cannot support.
- **Consistency:** one label per action across the product; concrete numbers over "some"; no "just", "simply", or filler such as "seamless" and "robust"; text that survives translation (no idioms, no variables mid-sentence).

Use `writing` for longer marketing or editorial prose; this mode covers the strings inside the interface.

## Resilience

Interfaces are usually built against kind demo data. Break the component with the realistic worst case before calling it finished (Emil Kowalski's `break-ui` method):

1. **Map every rendered value**, including counts, timestamps, badge and status text, labels that come from data, avatars, and the list length itself. For each, find its real limit in the validation schema, database column, API type, or `maxLength`. No limit is a finding. A frontend limit shorter than the backend's means longer values will arrive through imports or the API.
2. **Build one worst-case dataset**, shaped exactly like the demo data, from plausible values only: real naming patterns, real email shapes, or the schema's maximum. Random strings prove nothing. Spread different failures across the first visible rows rather than stacking them in one. Also cover **empty**, **one** (every count at exactly 1), and **huge** (the realistic list maximum, which also tests performance).
3. **Swap data, not markup.** Feed the worst case through the same boundary as the demo data (fixture, mock, props, API stub). Add a dev-only **Demo / Worst case / Empty / One / Huge** toggle, for example a URL parameter or a prototype route, that never ships.
4. **Look for the breaks** at the component's real container width, at 320px, at the widest layout, at 200% zoom, and in dark mode and right-to-left when the product supports them. Typical causes: flex children without `min-width: 0` or `flex-shrink: 0`, unbreakable strings, hardcoded plurals, raw numbers instead of `Intl` formatting, placeholders left by missing optional fields, initials sliced from the first byte, and broken-image avatars with no fallback.
5. **Decide each long string per field.** Wrap what identifies something. Truncate at the end for secondary metadata, and in the middle when values differ at the end (files, paths, shared-domain emails). Clamp multi-line previews. Never truncate numbers, amounts, or dates.
6. **Report before fixing.** List each break as Broken, Ugly, or Fragile, with the value that caused it and a fix with its location. Put the genuine design decisions to Elias. Say what held up. Fix only what he picks, then flip through every state again, Demo included, and keep the worst-case fixture as the regression test.

[The break-ui snapshot](source-methods/emil-break-ui.md) has the failure-signature table and the full worst-case catalogue.

Also test validation errors, slow loading, text scaling, keyboard navigation, and reduced motion. Prefer layout rules that absorb content variation over truncation that hides meaning.

## Native and human feel

Respect the target platform’s navigation, controls, pointer or touch behavior, feedback, safe areas, and system settings. Human feel comes from clear product choices, real content, meaningful details, and consistent craft. Do not add ornamental noise, fake handwritten cues, arbitrary asymmetry, or excessive animation to simulate personality.

## Mobile web

Run this mode on every web app or site that people will use on a phone, before release, not only when a problem is reported. Remove the tells that make it feel like a website in a browser (Emil Kowalski):

- Gate hover styles behind `(hover: hover) and (pointer: fine)` so they don't stick after a tap.
- Remove the tap-highlight flash.
- Use `100dvh` for app shells and `100svh` for heroes instead of `100vh`.
- Keep input text at least 16px so iOS doesn't zoom the page.
- Give feedback on pointer-down and set `touch-action: manipulation`.
- Stop pull-to-refresh with `overscroll-behavior` where the app owns scrolling.
- Respect safe areas with `viewport-fit=cover` and `env(safe-area-inset-*)`.
- Prevent long-press text selection on controls.
- Constrain gesture surfaces with `touch-action`.
- Set `theme-color` for each colour scheme.
- Make the colours behind Safari's status bar and bottom controls match the page's top and bottom edges, including edges that change colour as the page scrolls. `theme-color` alone does not do this in the browser; follow [mobile Safari edges](mobile-safari-edges.md) for the edge-strip technique, the frosted-glass header caveat, and its limits.

Desktop device emulation reproduces none of these reliably. Verify on real hardware, or say which fixes are verified from code only. [The mobile-native snapshot](source-methods/emil-mobile-native.md) has the exact code for each fix.

## Redesign threshold

Escalate to `interface-design` when polishing requires changing the user journey, information architecture, component foundation, or visual direction. Escalate material temporal behavior to `motion`.

## Finish

Re-render the same states and sizes. Compare before and after against the references, check that behavior did not regress, and stop when remaining differences are preference-level or outside the requested scope.
