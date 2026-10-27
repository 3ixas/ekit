# Accessibility Review

Use the current standard required by the project. For web work, consult the current [WCAG recommendation](https://www.w3.org/WAI/standards-guidelines/wcag/) and platform accessibility guidance rather than relying on remembered thresholds.

## Design and implement by journey

Identify the critical user journeys and the access needs relevant to the product. For each journey, inspect:

- semantic structure, landmarks, headings, names, roles, values, and relationships;
- keyboard and switch reachability, logical order, visible focus, traps, shortcuts, and focus restoration;
- forms, instructions, labels, autocomplete, validation, error association, and recovery;
- status announcements, loading, live changes, dialogs, menus, and route changes;
- contrast, non-colour cues, text scaling, zoom, reflow, orientation, and spacing overrides;
- touch target size, pointer alternatives, gesture alternatives, and timing;
- image alternatives, captions, transcripts, and meaningful data visualization descriptions;
- animation, flashing, autoplay, vestibular impact, and reduced-motion settings;
- authentication, session expiry, destructive actions, and help.

Prefer native semantics and controls. Add ARIA only when the native platform cannot express the behavior; custom widgets inherit full keyboard, focus, state, and announcement responsibilities.

## Verify with layered evidence

Automated tools find a subset of detectable failures. Combine them with keyboard-only use, zoom and text scaling, forced or high-contrast settings where relevant, reduced motion, and a screen reader pass through critical journeys. Test real error and empty states rather than only the ideal path.

Report the tested standards, platforms, browsers, assistive technologies, journeys, and limitations. Describe findings by user effect, location, reproduction, relevant requirement, and remediation direction. Do not claim compliance from a clean automated scan or a partial audit.
