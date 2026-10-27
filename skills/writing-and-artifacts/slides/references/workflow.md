# Presentation workflow

## Story and evidence

State the audience's intended activity or decision in concrete terms. Select evidence that supports it and distinguish observations, estimates and recommendations. Build an outline in which titles communicate the point and neighbouring slides advance the story. Avoid repeating the same dense list with different headings. Sources and dates should be available without overwhelming the main slide.

Choose the output and aspect ratio for the setting. Inspect brand/reference constraints, existing masters/layouts, notes, charts, media, fonts and editability requirements. Do not destroy notes, embedded data or animations incidentally when round-tripping an existing deck. Disclose unsupported elements before claiming faithful preservation.

## Compose and build

Use native text, shapes, tables and charts when they meet the requirement; retain editable objects unless a visual genuinely requires a raster asset. Set a clear title/body/evidence hierarchy, align objects on a deliberate grid and reserve comfortable margins. Tables and charts need readable labels, units, truthful scales and source context. Use accessible contrast and do not encode a critical distinction with colour alone.

Content has to fit its container at a sensible font size. Estimate bounding boxes and inspect shapes beyond the slide edges, but do not treat containment arithmetic as proof that text fits. Account for internal text margins, paragraph spacing, wraps and the actual rendered font. Split or simplify an overcrowded slide rather than shrinking it until it becomes unreadable.

## Render and check

Reopen the saved deck and verify slide count/order, intended titles, editable content and object relationships. Export/render using an available compatible office or presentation engine. Inspect every slide both as a thumbnail sequence for pacing and at ordinary presentation scale for text, chart labels, clipping and alignment. Check images at their displayed size; inspect especially long titles, dense tables and edge-aligned elements.

Re-render affected slides after fixes. If fonts are substituted, record the actual rendering environment and review the substituted result; do not claim identical behaviour in another engine. Animations, transitions, speaker notes and embedded media may need native playback or separate inspection, beyond static PDF renders.

The representative preservation case uses an editable two-slide deck: one message-led title slide and one evidence/table slide. Reopen it, verify content and shape containment, export both pages and inspect both rendered images. Its passing result establishes this static fixture, not universal compatibility or animation support.

## Tool limits and provenance

Resolve the current host's slide runtime and renderer. Python-pptx can manipulate supported PPTX objects; it does not render slides or emulate PowerPoint layout. If the chosen tool lacks a requested feature, keep the original and report that limitation rather than flattening the deck silently.

This workflow is independently authored from EKit's presentation requirements. Pinned python-pptx documentation is consulted for text-container semantics only; no prose or examples are copied. The separately recorded Felix Rieseberg source is a reference-only influence on describing the audience's activity; its text is not redistributed.
