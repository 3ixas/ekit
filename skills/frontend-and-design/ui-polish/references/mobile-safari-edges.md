# Mobile Safari edges

Independently written for this repository from Josh Puckett's "Seamless mobile Safari" (joshpuckett.me, reviewed 2026-10-16), checked against WebKit's edge-sampling code (`Source/WebCore/page/LocalFrameView.cpp` at WebKit `77f8a2b`). Use it when a web app or site is viewed in Safari on iPhone and the page's top or bottom edge is not the browser's default colour: a coloured hero, a dark app shell, a fixed background, or a page whose edge colour changes as it scrolls.

## How Safari colours its bars

Safari tints the area behind the status bar and its bottom controls by sampling the page at each edge:

- It looks for a **fixed or sticky element touching that edge** and uses its background colour. A colour under about 75% opacity is blended against the page background.
- An edge element with **`backdrop-filter`** (a frosted-glass header or tab bar) gives Safari no single colour, so that edge gets no tint. An edge with several competing background colours behaves the same way.
- With no qualifying fixed element, the tint comes from the page background.
- `theme-color` is still worth setting per colour scheme, but in-browser Safari honours it inconsistently; it is reliable mainly for Home Screen apps. Do not rely on it alone, and it cannot give the top and bottom different colours.

## The edge-strip technique

Give each edge a thin fixed strip whose colour matches the content next to it:

1. Add two empty, `aria-hidden` elements, `.edge-top` and `.edge-bottom`, **outside any transformed ancestor** (a `transform`, `filter`, or `perspective` ancestor turns `position: fixed` into positioning relative to that ancestor).
2. Paint each with a fixed, full-width, `pointer-events: none` pseudo-element at its edge, `max(12px, env(safe-area-inset-top))` or `max(12px, env(safe-area-inset-bottom))` tall. Safari needs roughly 5px or more of the strip visible to pick up its colour.
3. Drive every colour from two custom properties, `--edge-top-background` and `--edge-bottom-background`. Set the `html` background to the top colour and the `body` background to the bottom colour so overscroll matches, and update `theme-color` with the top colour.
4. Use `viewport-fit=cover`, and keep text and controls inside `env(safe-area-inset-*)`. The strips paint behind the bars; content must not.
5. To avoid a hard line, keep a solid strip of about 5px at the very edge for Safari to sample, then add a short gradient from that colour to transparent inward (about 48px).

When the app already has a **solid** fixed header or bottom bar at an edge, Safari samples that instead and the strip is unnecessary there. When that bar uses `backdrop-filter`, decide deliberately: keep the glass and accept the untinted edge, or give the bar a solid edge strip and confirm on a device which one Safari samples.

## Colours that change

When the edge colour changes with scroll (a fixed background, sections of different colours):

- Compute the palette once per change and apply the same values to the visible background, both strips, both document backgrounds, and the `theme-color` tag, so nothing disagrees for a frame.
- Update on scroll, on a restored scroll position (back navigation, reload), on viewport resize and orientation change, and when Safari's toolbar expands or collapses.
- In a single-page app, remove the listeners and restore any shared document styles (`html` and `body` backgrounds, `theme-color`) when the route unmounts, so the next page does not inherit them.

## Limits

Each edge takes one solid colour. Images do not extend behind the bars, and a gradient that changes colour across the width cannot be matched; choose the colour at the edge's dominant point or redesign the edge.

## Verify

Desktop device emulation and desktop Safari do not show this. Check in Safari on an iPhone, or at least the iOS Simulator, at the top of the page, mid-scroll, after the toolbar collapses, in landscape, in light and dark mode, and after back navigation. Report any state checked from code only.
