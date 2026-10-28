---
name: app-audit
description: "Use for a whole-app readiness pass with local fixes, rechecking and lasting CI gates across web or mobile surfaces: when Elias asks, and at the checkpoints in his instructions (before a first release or deploy, before calling an app-launch task done, before the PR for an initial build). Do not select for a focused bug fix or design question."
---

# App Audit

## Outcome

A remediated app with evidence across its relevant routes, states, and device sizes, the checks that proved it kept as CI gates, and a concise account of remaining risks.

## When to use

Use when asked, and at the checkpoints in Elias's instructions, for a whole-app final pass, launch-readiness sweep, or a search for the small defects that make a product feel unfinished or template-generated. Use verify for a bounded change and ui-polish for a focused visual refinement.

## Method

1. **Establish the target.** Read project instructions, inspect the current worktree and existing design references, identify the app type and stack, and find its available running preview, production URL, browser, device, or simulator. Preserve unrelated user changes. If the project uses Vercel, compare the intended production host with the actual production domain: a vercel.app URL is normal for a preview, but is a finding when the public production site is still using the default host. If the target cannot be inspected, mark that part unverified rather than guessing.

2. **Map coverage.** Enumerate all canonical public routes, dynamic route families, and native screens from the router, content sources, links, and sitemap. Create a small matrix of route families, user journeys, meaningful states, and device sizes. Check metadata across every public route; use representative routes and state combinations for rendered checks, and exercise every distinct visible control. For repeated shared controls, verify the implementation and each route-specific variation. Do not imply exhaustive coverage when the app is too large or a surface is unavailable.

3. **Check web delivery and discoverability.** For every public, indexable page, inspect the rendered head and verify a useful page-specific title and description, the intended absolute canonical URL, working favicon/icon references, and appropriate Open Graph and social-card metadata with a reachable, suitable image. A shared social image is acceptable only when it represents those pages well. Check the actual card rendering with available tooling; otherwise verify the tags and image directly and state that platform rendering or cache behaviour was not observed. Check that robots rules and the sitemap match the intended public route set and canonical host. Check meaningful server-delivered content, HTTP status codes, discoverable navigation, named controls, and recoverable errors using [agent-readiness guidance](references/agent-readiness.md). For an appropriate public URL, retrieve its existing Is Agentic report; starting or refreshing a public scan requires publication authority. Private apps and pages that should not be indexed are not failures for lacking public SEO assets. Use current official guidance when framework or platform conventions matter.

4. **Exercise product behaviour.** When first-use conversion or onboarding is relevant, use dogfood’s first-use pass for contrasting journeys to first success. Follow the important user journeys and inspect every visible link, button, menu, form, and other control on each distinct route. Confirm that links have the right destinations and controls produce the expected visible result; find placeholders, dead clicks, misleading disabled states, and unfinished interactions. Exercise relevant loading, empty, success, validation, error, recovery, and not-found states using safe test data. Do not trigger real payments, messages, deletions, or other consequential actions just to test them.

5. **Inspect accessibility and responsive craft.** Use the project’s actual breakpoints and test at narrow mobile, common mobile, tablet, desktop, and at least one awkward intermediate width; include long text, large data, empty data, and relevant error content. Suggested widths include 320, 390, 768, 1024, and 1280 pixels, adjusted to the app. Check overflow, clipping, wrapping, touch and keyboard use, focus visibility, logical headings and landmarks, control names, contrast, reduced motion, and image alternatives that match the image’s purpose. For native apps, test target devices or simulators for safe areas, dynamic text sizing, keyboard behaviour, orientation, navigation, permissions, and offline or error recovery where relevant. A browser rendering does not prove native behaviour.

6. **Look for consistency and runtime defects.** Compare rendered screens with the project’s design file and supplied references. Look for drift in spacing, typography, colours, buttons, radii, icons, and shared components without imposing a new visual direction. Inspect browser console and network failures, leftover debug output, accidental development routes or files, unsafe build artifacts, and exposed secrets without printing secret values. Measure route-level JavaScript or native performance against the project’s own budget or a before/after baseline; do not invent a universal bundle-size threshold. Use [the AI-slop patterns](references/ai-slop-patterns.md) as prompts, not as automatic design rules.

7. **Fix and recheck.** Fix clear, local defects in the app, not just report them. Prefer the smallest coherent correction that preserves the product’s identity and intended behaviour. Use the relevant owned accessibility, dogfood, ui-polish, performance, security, ios, react-native, or vercel specialist when a finding needs deeper work; this skill still owns the coverage matrix and final result. Re-run the affected checks and verify the finished interface. If a larger design decision, unavailable environment, or external setting blocks a safe fix, describe the evidence and the smallest next action.

8. **Keep what you proved.** The repository should already have the `ci` baseline from when it was created; if it does not, hand that to `ci` first. Then pick, from what this pass passed, the checks that are cheap, deterministic and need no live service, and give them to `ci` to add to the repository's single check command (for a web app: route and metadata checks, accessibility and copy checks, and the guard that fails when a verify script is not run by CI). Checks that are slow, subjective or need a live site stay as work done in a pass; a recurring live one can be a scheduled workflow. Write `docs/review/APP-AUDIT.md`: the date, the commit, and each area's Pass, Fixed, Blocked or Not applicable, so the next pass and any freshness check can read it.

## Boundaries

This is an audit and local remediation workflow. Running at a checkpoint is not authority to deploy or publish: proposing CI changes is local, but pushing them is not. It does not authorize deployment, publication, DNS or domain changes, external account changes, or destructive actions. Never expose secret values. Do not treat a source scan or successful build as proof of the rendered product, or treat a screenshot at one size as responsive verification.

Report what was checked, the routes/devices/states exercised, fixes made and rechecked, commands or tools used, and remaining failures or skips. Mark each material area Pass, Fixed, Blocked, or Not applicable, with brief evidence.
