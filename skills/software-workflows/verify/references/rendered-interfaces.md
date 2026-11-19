# Rendered interfaces

Use when a claim depends on what a browser or simulator shows.

- **Your own server.** Start the dev server from the checkout under review. Worktrees share ports and databases unless the project isolates them, so pick a free port (the project's setup script may assign one) and confirm the page you load comes from your checkout, for example by a change only it contains.
- **Widths.** Check at least one desktop width (1280–1440) and one mobile width (375–390), plus any breakpoint the change touches. Include the interaction states the claim depends on: hover, focus, open menus, error and empty states. A simulator check uses device sizes in place of widths.
- **Driver.** Prefer the project's browser tests or its Playwright setup, otherwise an available headless browser tool. These checks run in the verifying thread; they are not the interactive browser work the shared instructions send to Codex. If no headless driver is available, mark the rendered claim Skip with the reason; do not substitute the shared preview.
- **Evidence.** Name each screenshot by claim, width and state, such as `nav-open-mobile-390.png`, and attach it to the report. A screenshot supports a claim only with its origin, revision and state, and never replaces checking behaviour and resulting state.
- **Showing Elias.** The host's shared preview is Elias's screen, and parallel threads would take it over, so open it only when Elias asks to see the change or the change is mainly visual (layout, styling, motion). Which tool that is depends on the host; see EKit's `docs/agent-portability.md`.
