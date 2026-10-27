# Agent readiness

Use alongside the web delivery, behaviour, and accessibility checks. App-audit remains the owner; no separate skill or MCP installation is required. This guidance is independently written from the [Is Agentic docs](https://is-agentic.com/docs), [official skill](https://is-agentic.com/.well-known/agent-skills/is-agentic/SKILL.md), [methodology](https://is-agentic.com/methodology), and [about page](https://is-agentic.com/about). Ora runs the technical scans; Vercel operates Is Agentic's presentation and reporting.

## Check locally first

For representative public route families, inspect the initial HTTP response as well as the rendered page. Confirm that meaningful content and navigation are available without fragile client-only rendering, status codes match the result (including redirects and missing pages), headings and language identify the document, and canonical/social metadata describes the intended page. Exercise named links, buttons, and form controls, then check that validation and error states explain how to recover. Reuse the audit's coverage matrix rather than repeating every check.

Compare robots rules and the sitemap with the intended public surface. Preserve deliberate crawler restrictions, authentication, and private routes. For genuinely private or client-only product states, judge the intended user journey; do not demand public indexing or server rendering of private data. Check API documentation and discovery only where an API or other developer surface actually exists.

## Retrieve public evidence

Only send an appropriate public HTTP(S) target. Never submit localhost, private-network or internal hosts, protected previews, credentials, tokens, sensitive query strings, or personal data. A URL being reachable does not itself authorize publishing a scan. Do not silently strip a sensitive query and call the result the same target.

For a safe public URL, prefer the existing-report API:

```text
GET https://is-agentic.com/api/v1/report?url=<URL-encoded exact target URL>
```

It is currently free and keyless and does not start scans. Keep the exact target, including any safe path/query, because different targets have separate reports. Recheck the live docs if access, pricing, schema, or freshness behaviour matters.

If no completed report exists, continue local checks and mark the external score unavailable. Only with authority to create a published scan, use:

```sh
npx is-agentic <public-url> --json
```

The CLI can start a scan when no report exists. Likewise, opening a scan page or using Rescan can create public evidence; neither is an automatic fallback. The existing MCP, if already available, can retrieve reports without adding another integration.

Handle failures without a retry loop: a 404 means no stored report; a 429 means respect Retry-After; a 503 or network failure means mark the service unavailable and continue independent checks. An unscorable/null score remains unscored, never zero or a pass. Do not weaken target protection to make a scan succeed.

## Review findings and prove fixes

Read the observed evidence before applying advice. Prioritize essential failures, essential partials, then applicable recommended findings. Confirm applicability and reproduce material findings locally or through safe public reads; reject incorrect advice with evidence. Essential checks currently share 80 points, recommended checks 20, with up to five optional bonus points. Missing bonus signals are not defects. Add no universal score threshold or requirement to reach 100.

Do not add an API, MCP server, payment protocol, or emerging discovery file solely to gain points. Never invent company details or weaken authentication, privacy, crawler policies, or security to satisfy a recommendation. Route genuine product decisions back to the user. One observed agent journey is supporting evidence, not proof that all agents can complete all tasks; maintain dedicated accessibility, security, and real user-journey checks.

Record the exact target, report_url, scanned_at, score (including null), prioritized findings, applicability decisions, local fixes and verification, and remaining gaps. Separate the published snapshot from the current local revision; a local fix does not improve the deployed score by itself. API and CLI results can come from a six-hour cache. After an authorized deployment and authorized fresh scan, compare timestamps and target identity before claiming a score change. An unchanged timestamp is stale evidence for the fix, even if the command succeeded. Report local results and pending public verification separately using Pass, Fixed, Blocked, or Not applicable as appropriate; never mark unavailable public evidence Pass.
