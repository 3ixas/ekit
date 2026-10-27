# Frontend And Design

Create reference-led interfaces and validate their experience, craft, motion, accessibility, and user evidence.

| Skill | Invocation | Purpose |
|---|---|---|
| `accessibility` | automatic, supporting | Design, implement, or audit accessible interfaces across semantics, keyboard and focus, forms, errors, layout, media, motion, and assistive technology. |
| `apple-design` | supporting | Design or review Apple-platform interfaces using current Human Interface Guidelines, native interaction patterns, accessibility, and supplied references. |
| `interface-design` | automatic | Orchestrate substantial product interface design from references and product intent through `DESIGN.md`, Claude Design or Stitch exploration, user sign-off, and rendered implementation QA. |
| `libraries-dev` | supporting | Reveal, assess, or integrate the seven public Libraries.dev React effects when one fits the approved visual direction. |
| `motion` | automatic, supporting | Design and improve meaningful interface motion, gestures, transitions, timing, springs, sequencing, reduced-motion behaviour, and runtime performance, and direct animation or video rendered from code. |
| `prototype` | automatic | Build a throwaway reference-led prototype or comparable variants to answer one consequential product, interaction, visual, or technical decision. |
| `ui-polish` | automatic | Refine an existing coherent interface across hierarchy, typography, colour, layout, surfaces, states, interface copy, native feel, resilience, and light motion. |
| `user-research` | automatic | Plan and synthesize user interviews or usability studies with neutral prompts, an evidence ladder, and explicit confidence. |

## Common paths

- Whole-app final quality pass: app-audit owns the coverage matrix, relevant fixes, and recheck across web or native mobile surfaces.

- New or substantially changed flow: `interface-design` owns references → project `DESIGN.md` → Claude Design or Stitch exploration and sign-off, supported by `prototype` when one isolated experiment is needed → `to-spec` → `to-tickets` → `implement` → `ui-polish` → `verify`.
- Small settled interface change: `implement` → `ui-polish` when useful → `verify`; do not open an exploration loop for a change whose direction is already clear.
- Open direction: references → `prototype` → select → production implementation.
- Existing coherent UI: `ui-polish`, calling motion and accessibility when relevant.
- Any web app or site used on phones: `ui-polish`'s mobile-web mode before release, including the mobile Safari edge colours, verified in iOS Safari rather than desktop emulation.

The full pinned Taste toolkit lives once under `interface-design`: website/app direction generators, reference libraries, asset search and browser diagnostics. `ui-polish` uses its inspection and critique path; `motion` uses the optional scroll-stage foundation. Strong Taste defaults yield to approved project decisions in `DESIGN.md`; no separate Taste skill is installed.
