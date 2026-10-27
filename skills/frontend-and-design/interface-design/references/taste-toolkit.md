# Taste toolkit

Use for substantial website or web-app design in `interface-design`, and for inspection and refinement in `ui-polish`. The full MIT toolkit is pinned to Taste 2.1.4, `6010f91a9935f1c167dfc500fb1a475681892e6b`; it is supporting material, not another skill. Read only the branch and references needed. Existing product decisions, approved `DESIGN.md`, accessibility and host authority govern. Taste defaults are strong starting choices, not evidence that a particular aesthetic is universally better.

## Website direction

1. Inventory eight to twelve real, distinctive things about the subject: materials, name, constraints, place, output, rituals and available imagery. Do not invent personal or business facts.
2. Write one claim and its evidence per section, then a complete copy deck. Remove sections with no job; identify missing content separately from invented proof.
3. Use `draw --options 3` to broaden the existing options round, alongside actual references. Judge the proposed compositions against the subject and assets. The draw supplies candidates; Elias's selected direction governs. Choose, combine or reject candidates rather than accepting randomness as authority.
4. Write the idea sentence: something particular to this subject becomes a compositional device. Substitute its nearest competitor; if it still fits unchanged, sharpen it. Carry the idea beyond the hero into useful content and the close.
5. Choose imagery from available project assets, generated assets when authorised, or honest contextual imagery found by the asset tool. Record sources and credits. Consider one useful live demonstration when it proves a claim; do not add interaction solely to satisfy a quota.
6. Build still composition and phone composition first. Give motion a purpose with `motion`; record intentional exceptions to the upstream picture and movement floors. Continue the existing exploration, approval and delivery workflow.

## App direction

Start from the [app-screen method](../assets/taste-toolkit/references/app-screens.md), not the marketing-page recipe. Record the screen's main question, the finding that matters and its next action. Inventory people, domain objects, units and realistic magnitudes. Render totals, changes, repeated facts and charts from shared data; state comparison baselines and distinguish zero, missing and unavailable values. Reconcile displayed figures without introducing a rounding policy that contradicts the product's domain model.

Use `draw --app --options 3` for style/shell candidates. Choose density and priorities from the work: glance versus long session, first action, frequently compared values and available width. Give the product a face through its terminology, actual people/objects and one useful signature. Compose phone and tablet layouts from task priority; test empty, zero, loading, error, selected, disabled and long-content states. A small settled change follows the existing direction and skips the draw.

The app study covers 23 owner-selected desktop screens from 17 unnamed products, not a representative usability study. It includes no mobile, loading/error, inbox or dense operations-table evidence. Upstream extrapolations are house rules, not measured findings. Product function and accessibility override fashionable density, colour and type restrictions.

## Commands and resources

Resolve the installed `interface-design` folder through the current host, then run commands from the target project's root. In the examples `<owner>` is that folder, not this repository or a hard-coded host path.

```sh
node <owner>/scripts/taste.mjs draw --sector personal-portfolio --brief "Public portfolio" --sections work,about,contact --seed 42 --options 3
node <owner>/scripts/taste.mjs draw --sector personal-portfolio --brief "Public portfolio" --sections work,about,contact --seed 42 --direction name-as-monument
node <owner>/scripts/taste.mjs draw --app --kind finance --brief "Shared budget" --screens overview,settings --seed 42 --options 3
node <owner>/scripts/taste.mjs draw --show
node <owner>/scripts/taste.mjs assets "Porto ceramic workshop" --json
node <owner>/scripts/taste.mjs assets --get <returned-ref> --to assets
node <owner>/scripts/taste.mjs assets --credits --to assets
node <owner>/scripts/taste.mjs lint src --json
node <owner>/scripts/taste.mjs inspect http://localhost:3000 --out .taste-skill/before --json
node <owner>/scripts/taste.mjs inspect http://localhost:3000 --out .taste-skill/after --json
node <owner>/scripts/taste.mjs scenes http://localhost:3000
```

The launcher reuses Node 22+ from the current executable, installed nvm versions or the Codex bundled runtime. `TASTE_NODE` explicitly selects an executable. It changes no shell defaults and installs nothing. Browser tools reuse an existing Chrome/Edge/Chromium or cached macOS Playwright Chromium; set `CHROME_PATH` for another compatible executable. Each run uses its own temporary browser profile. Host tool restrictions still apply: use permitted host measurements when direct browser launch is unavailable, and mark the toolkit capture unexecuted. Chromium does not prove mobile Safari, keyboard or assistive-technology behaviour.

Original command names and options remain available directly beneath `assets/taste-toolkit/scripts`. Direction sheets and default history stay in the target project's `.taste-skill/`; `TASTE_SKILL_HISTORY` remains an explicit override. Use separate `--out` folders for page and app directions in a mixed project. Preserve palette/type with `--keep palette,type` when fixed. Saved sheets are supporting records: reconcile selected tokens, signature, references and exceptions into `DESIGN.md`; a later draw never supersedes approval. Never read all library JSON into context; query `--list`, `--site`, `--photos` or a draw.

## Policy and findings

Create `.taste-skill/policy.json` from intentional decisions already recorded in the approved project contract. The `designContract` path is relative to the policy file. Example:

```json
{
  "version": 1,
  "designContract": "../DESIGN.md",
  "exceptions": {
    "palette-purple": "Approved brand violet in DESIGN.md Colour roles",
    "hairline": "Approved editorial separators in DESIGN.md Surfaces",
    "still-page": "Quiet portfolio; motion limited to useful control feedback",
    "few-pictures": "Typography-led direction approved with two actual work images"
  }
}
```

Both `lint` and `inspect` auto-load that file; `--policy path` selects another. Existing `--allow` inspector/direction allowances remain visible with a reason and must be reconciled with the contract. Policy validates rule IDs and reasons and requires the contract file; its existence does not prove user approval. Never generate exceptions merely to make a command green.

Findings retain upstream IDs, measurements and severity in `upstreamLevel`; the owned report adds `category`, `requiresConfirmation` and an exception reason where applicable:

- **functional:** broken images, document overflow, clipped/covered text, font fallback, hidden reduced-motion content and an unstarted scene. Aesthetic policy cannot waive these. Geometry detections still require checking the actual crop and intentional scroll/overlay behaviour before changing code.
- **aesthetic:** strong Taste defaults. Approved exceptions become visible `INFO` entries instead of repeated restyling demands.
- **heuristic:** inferred composition/contrast/space/scene judgements become `WARN` pending rendered confirmation. A computed ancestor colour does not prove contrast over imagery or gradients.

Exit 0 means no remaining `FAIL` findings, not approved design or release readiness. Exit 1 means findings remain; exit 2 means unavailable/invalid execution. Inspector JSON includes `status: measured` or `unavailable`; failed required probes cannot silently become clean measurements. Source lint alone cannot prove a visual defect. Inspect screenshots at each width, fix the three material problems, and repeat at most three rounds. Retain before/after evidence and unresolved limits.

## Assets, code and motion

The asset finder searches Openverse, Commons, AIC and Met; footage adds Internet Archive and NASA. Queries leave the machine: use relevant public descriptors, not private product details. Search/download only when the task needs imagery; review the source item's actual licence and restrictions, inspect the media, keep the project asset credit ledger and required credits. Do not present contextual images as the client's own product or team. Source labels are evidence to verify, not a guarantee of all rights. Asset failure is an unavailable source, not permission to invent a photograph. Clip defaults are bounded; do not raise them without a concrete need.

The optional [base CSS](../assets/taste-toolkit/assets/base.css), [base JS](../assets/taste-toolkit/assets/base.js), [app CSS](../assets/taste-toolkit/assets/app.css) and [chart helpers](../assets/taste-toolkit/assets/charts.js) are starting material. Adapt only selected pieces into project-owned tokens and components; preserve an existing component/chart system. Check semantics, keyboard use, data accuracy, empty states and accessible chart alternatives before production use. Do not ship a parallel global CSS system.

`motion` owns selected scroll scenes and timing. The pinned toolkit includes the [stage runtime](../assets/taste-toolkit/assets/scenes/stage.js), [stage CSS](../assets/taste-toolkit/assets/scenes/stage.css) and capture tool, but no scene catalogue, individual scene engines or demos. Do not call missing examples or describe them as installed. The stage references pinned GSAP/ScrollTrigger and optional SplitText/Lenis; verify current package/licence compatibility at use and follow the project's dependency method. No automatic CDN injection or dependency install. Preserve native scroll, content without scripts and reduced-motion rest compositions. Run scene capture only on a page that actually uses scenes.

## Detailed source references

- [Workflow reference](../assets/taste-toolkit/workflow.md): complete upstream website run, interpreted through this guide.
- [Copy](../assets/taste-toolkit/references/copy.md), [type](../assets/taste-toolkit/references/type.md), [colour](../assets/taste-toolkit/references/colour.md), [layout](../assets/taste-toolkit/references/layout.md): use for the relevant design decision.
- [Imagery](../assets/taste-toolkit/references/imagery.md): selection, placements, crops, footage and attribution.
- [Motion](../assets/taste-toolkit/references/motion.md) and [scenes](../assets/taste-toolkit/references/scenes.md): optional website choreography under the owned motion contract.
- [Critique](../assets/taste-toolkit/references/critique.md) and [tells](../assets/taste-toolkit/references/tells.md): apply with the owned screenshot critique; numerical scores and caps do not decide acceptance.
- [Research](../assets/taste-toolkit/references/research.md): original studies and their limitations. The recorded model-judged comparisons do not establish consistent superiority.
- [Provenance](../assets/taste-toolkit/provenance.json) and [MIT licence](../assets/taste-toolkit/LICENSE.txt): exact imported file identities; owned adaptations are recorded in metadata and the assessment.
