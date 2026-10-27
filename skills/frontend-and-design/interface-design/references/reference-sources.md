# Reference Sources

Use sources according to the design problem. Prefer links or screenshots supplied by the user. Search current sources when examples, component implementations, or platform guidance are needed.

## Product and visual references

- [Mobbin](https://mobbin.com/) and [Refero](https://refero.design/) for real product flows and screen patterns.
- [ScreensDesign](https://screensdesign.com/) for mobile app onboarding, permissions, paywalls, and in-app flow references. Use publicly visible app pages, free screen previews, App Store screenshots, and [articles](https://screensdesign.com/articles/); check access at use and stop at Pro gates. Inspect the actual visible screen and its surrounding sequence before adopting a pattern; distinguish a screen description or article's interpretation from a screen or replay actually inspected. Record the app URL, screen/chapter, useful pattern, and any access limit in `DESIGN.md`. Revenue and download estimates are context, not evidence that a design caused conversion or retention. Public access does not grant asset reuse rights. Do not start a trial, subscribe, or depend on paid exports or generation for reference research.
- [FolioDeck](https://foliodeck.pro/) for curated designer, developer, and studio portfolios across product/UX, web, branding, and motion. Use it to discover visual direction, typography, composition, and project or case-study presentation references. Follow a selected entry to the original portfolio and inspect the relevant page before adopting a pattern; record the original URL and the specific quality it contributes. Gallery previews alone do not establish interaction behaviour or permission to reuse assets or code.
- [SiteInspire](https://www.siteinspire.com/), [Godly](https://godly.website/), [Land-book](https://land-book.com/), and [Inspolanding](https://inspolanding.design/) for visual direction and composition. Choose a gallery for a missing reference job; follow selected examples to their original sites before adopting their patterns.
- Section galleries, one per reference job: [Supahero](https://supahero.io/) for hero sections, [Navbar Gallery](https://navbar.gallery/) for navigation, [CTA.gallery](https://cta.gallery/) for calls to action, and [Footer](https://footer.design/) for footers.
- [Refero Styles](https://styles.refero.design/) for real sites' palettes, typography, spacing and components, with AI-readable `DESIGN.md` views. Reconcile the analysis with the live reference and project tokens, then write the project's own contract; source-brand imperatives and export formats do not become project authority. Check export access before promising a downloadable file.
- [Scrolltide](https://scrolltide.co/) for scroll-driven and 3D site references. It sells prompts and templates; use the examples as references, not prompts to paste, which produce the template.
- Products in the same domain for terminology, expected states, and task flow. Treat convention as evidence, not an instruction to clone.

## Design workflow examples

[ui.sh](https://ui.sh/) publishes agent-skill guides and before/after examples rather than a product-screen gallery. Its [Design](https://ui.sh/skills/design), [Ideas](https://ui.sh/skills/ideas), and [Brand Kit](https://ui.sh/skills/brand-kit) pages can help explain a design treatment or show how alternatives and identity boards look in context. Consult a specific page only when its examples answer the current design question; inspect the rendered example before describing it. Keep `interface-design` and the project's `DESIGN.md` in charge of direction and selection; existing refactoring, polish, accessibility, and image skills retain their jobs. Public documentation is not the installed skill source or evidence of its quality. Installation is token-based; free entitlement and skill reuse terms were unverified at review. Use public examples without installing its bundle, copying its prompts, creating an account, or assuming the installer or image generation is free. Reassess actual skill contents, licence and cost before any future import.

## Connected reference tools

When a reference library MCP is connected, search it directly instead of browsing. Check the host's tool list for the connection; do not assume one. Documented examples:

- **Mobbin** (`https://api.mobbin.com/mcp`): `search_screens`, `search_flows`, `search_sections`. Real product screens, multi-step flows, and website sections. Needs a paid Mobbin plan.
- **Refero** (`https://api.refero.design/mcp`): styles (typography, colour, spacing, components), screens, flows, apps, sites, and similar screens. Needs a paid plan; usage is metered at roughly 8,000 calls a month.
- **ScreensDesign** ([MCP](https://screensdesign.com/mcp/), `https://api.screensdesign.com/v1/mcp`): semantic app/screen/flow search, app context, and saved collections. Its documented access requires Pro, with OAuth or scoped API keys and fair-use budgets. Deferred for the free workflow: use public references above, without installing or authorizing it. Recheck current pricing and obtain authority for any paid plan before reconsidering connection.

Any other reference-library MCP works the same way. The shape of results (images, links, metadata) is not documented for every service, so read what a call actually returns and never assume it.

How to use them:

- Search once per reference job, with a specific query. Say roughly how many calls were used, since the plans are metered.
- Describe the pattern generically ("empty state for a team member list", "onboarding for a finance app"). Queries go to a third-party service, so leave out confidential product details and do not upload private screenshots without Elias's approval.
- Treat results as evidence about conventions and craft. Record each result's source and query with the reference. Do not copy a screenshot into the product or repository, and do not reproduce one app's layout.
- With no tool connected, say so, and continue with supplied references and the manual sources below. Never describe a search that did not return results.

## Components and interaction

- [shadcn/ui](https://ui.shadcn.com/) for accessible component foundations that become project-owned code.
- [Beautiful UI](https://beautifului.dev/), [BeUI](https://beui.dev/), and [Rare UI](https://rareui.com/) for component inspiration and possible implementations.
- [Transitions](https://transitions.dev/) for interaction and transition references.
- [Design Spells](https://designspells.com/) for recorded product details: gestures, sheet transitions, selection feedback, microinteractions, and playful touches. Browse by platform or interaction tag when a specific detail needs a reference; open the individual spell and watch its clip rather than inferring motion from the title or a still. Record its URL, trigger, state change, and useful behaviour in `DESIGN.md`; mark timing or spring values estimated from video. Use publicly accessible examples, checking access at use. These are references, not reusable component source or proof of usability. `motion` owns implementation, interruption, reduced-motion alternatives, and performance; retain only details that serve the product's task or approved signature. Link to the example without importing recordings or assuming asset/code reuse rights.

Inspect the actual source, implementation quality, dependencies, accessibility, responsiveness, and license before reusing code. A visual example can inform a design even when its code cannot be copied.

## Additional component sources

Use these after the project direction identifies the interaction or signature. `shadcn` owns source integration, `motion` owns choreography, and `libraries-dev` keeps its existing seven-effect scope. Search one suitable catalogue for the missing job rather than fetching every library.

| Source | Choose it for | Reuse and integration boundary |
|---|---|---|
| [Kokonut UI](https://kokonutui.com/) | Animated inputs, cards, navigation and AI interface states. | Free components MIT; Pro is separate. Inspect React, Tailwind, Motion and primitive requirements for the selected component. |
| [React Bits](https://reactbits.dev/) | A deliberate shader background, text effect or interactive signature; visual editors help tune it. | Current free source uses MIT plus Commons Clause restrictions: product use is allowed, standalone component/tool/export redistribution is restricted. Check the exact selected source; keep code out of reusable skill/component packs. Choose its TypeScript/CSS or TypeScript/Tailwind variant to match the project. |
| [Magic UI](https://magicui.design/) | A beam explaining connections, a meaningful globe, marquees or other selected animated components. | Free components MIT; Pro blocks/templates separate. Inspect dependencies and semantics instead of copying a whole decorative section. |

React Bits (`@react-bits`) and Kokonut (`@kokonutui`) support the shared shadcn MCP. With an approved project, inspect its `components.json` and merge only the needed registry namespace: `https://reactbits.dev/r/{name}.json` or `https://kokonutui.com/r/{name}.json`. Preserve existing registries, aliases and components. Search/view a chosen item and inspect files/dependencies before adding it through the project's package manager. Magic UI offers its own MCP, but direct official docs and registry source are sufficient; another global integration is not required.

Before accepting any component, map it to project tokens and real state, inspect its source and licence, test keyboard/touch/responsive behaviour, and provide reduced-motion and unsupported-canvas/WebGL fallbacks. Keep essential text and controls usable without the effect; pause continuous work when hidden where appropriate. Code-based effects still consume bundle, CPU and GPU resources: measure input responsiveness and frame cost on a constrained device. Never assume a shader is cheaper than an image or video.

For dashboard charts, `data-visualization` owns chart selection and its Bklit implementation guidance. For generated brand assets, pass the approved DESIGN.md decisions to `images`; component catalogues do not choose a new brand direction.

## Effects and animated components

Add an effect only after the direction is approved, and only where it carries the recorded signature or a real product job. Pick the cheapest technique that achieves it: CSS before a motion runtime, a motion runtime before WebGL. Reserve WebGL and canvas effects for a deliberate signature, test them on a low-end device, and keep a reduced-motion path. `motion` owns timing and choreography; `libraries-dev` owns its seven Libraries.dev effects.

| Source | Use it for | Licence and caveats |
|---|---|---|
| [Trickle](https://github.com/akaieuan/trickle-UI-kit) | Text animation. Pure CSS keyframes, server-component safe, under 1 kB each; shadcn registry install. | MIT. Prefer it over a motion runtime for text. |
| [Motion Primitives](https://github.com/ibelick/motion-primitives) | General animated components built on Motion and Tailwind; shadcn registry install. | MIT. Beta: pin the version you install. |
| [UI Layouts](https://github.com/ui-layouts/ui-layouts) | Creative section blocks. Each block ships a `design.md` brief naming its thesis, palette, and required primitives, a useful model for recording a signature component. | MIT. Depends on Motion and Tailwind. |
| [Paper Shaders](https://github.com/paper-design/shaders) | Zero-dependency shader backgrounds and fills (mesh gradients, dot fields). | Apache-2.0. Pre-1.0 with breaking changes: pin the exact version. WebGL. |
| [Canvas UI](https://github.com/DavidHDev/canvas-ui) | Fluid, shader, and 3D effects drawn over the live page, with a GPU-overlay fallback. | MIT with Commons Clause: fine inside a product, not for resale as a component kit. Relies on the experimental HTML-in-canvas API. WebGL or WebGPU. |
| [Hyperiux components](https://github.com/Hyperiux-Immersion-Labs/hyperiux-components) | Next.js interaction effects installed by its CLI. | Free effects MIT; Pro effects need a paid account. Its MCP limits source fetches to a few a day, so browse the site instead. |
| [Cursify](https://github.com/ui-layouts/cursify) | Custom cursor ideas. | No licence: inspiration only; do not copy its code. |


## Imagery and icons

When a project has no photographs of its own, prefer real pictures of the subject's world to drawn substitutes or stock: [Openverse](https://openverse.org/), [Wikimedia Commons](https://commons.wikimedia.org/), [The Met open access](https://www.metmuseum.org/art/collection), and the [Art Institute of Chicago](https://www.artic.edu/collection) hold public-domain and openly licensed images. Use only CC0, public domain, CC BY, or CC BY-SA unless Elias approves otherwise, record each image's title, creator, licence, and source, and show the required credits in the product.

- [3dicons v1](https://3dicons.co/collection/b68cf8-v1) explicitly labels its illustrative icons CC0. Other collections and premium assets need their own licence checks. Use these for illustration when the direction fits; retain the project's functional icon family for navigation and controls.
- [Amicons](https://amicons.design/) is an optional Figma/SVG icon family with free and paid packs. Before choosing it, check the downloaded pack's licence and coverage; record the variant, grid and stroke in `DESIGN.md`. Keep one functional icon family. A public preview or free checkout does not establish redistribution rights or authorise a purchase.
- [liquid-glass](https://glass.samasante.com/) refracts the live page; glass is a known AI default, so use it only as a recorded signature. Verify the exact package, licence, browser behaviour, readability and fallback for the selected use; the web effect is separate from Apple's native platform APIs.

## Platform guidance

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) for Apple platforms.
- [Material Design](https://m3.material.io/) for Android conventions and interaction guidance.
- [WAI](https://www.w3.org/WAI/) and the current WCAG recommendation for accessibility requirements and techniques.

## Recording a reference

For each selected reference, store its URL or local image, the part being used, why it fits the product, and what must not be carried over. References should make decisions reviewable, not become an unfiltered mood board.
