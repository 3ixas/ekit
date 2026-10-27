# Apple Platform Design

Consult the current [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) and platform documentation because controls and conventions change. Use Apple’s guidance as the authority for current platform behavior; use this reference to structure the design decision.

## Start with the platform

- **iPhone:** touch-first, compact, often one-handed, interruption-prone, with navigation and primary actions placed for reach and clarity.
- **iPad:** resizable scenes, multitasking, keyboard, pointer, Pencil, drag and drop, and layouts that use width without becoming an enlarged phone.
- **Mac:** precise pointer, keyboard, menu commands, multiple windows, denser information, resizable content, and established toolbar and sidebar conventions.
- **Watch, TV, and spatial platforms:** distinct glance, focus, distance, input, comfort, and session-length constraints. Do not project phone patterns onto them.

Design shared concepts across devices while adapting navigation, density, presentation, and input to each platform.

## Prefer system behavior

Use native controls, text styles, symbols, materials, navigation, selection, sheets, alerts, menus, keyboard commands, focus, drag and drop, and system services when they fit. Custom treatment should solve a product need and retain expected semantics, access, and feedback.

Support Dynamic Type or the platform equivalent, VoiceOver, sufficient contrast, Reduce Motion, Reduce Transparency, increased contrast, localization, dark appearance, and content size extremes. Respect safe areas and system gestures.

## Integrate with the system

Consider deep links, search, sharing, notifications, widgets, App Intents, continuity, undo, document handling, privacy permission timing, and platform-specific input only when they advance the product journey. Ask for permissions in context and explain the benefit before the system prompt.

## Review native feel

Inspect the running app with target devices and settings. Check navigation and dismissal, back behavior, toolbar placement, control state, selection, keyboard and pointer use, scrolling, sheets, alerts, text scaling, safe areas, rotation or resizing, motion, haptics, and interruption recovery. A visual resemblance to Apple’s marketing does not establish platform fit.
