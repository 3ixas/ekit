# Security review

## Establish the threat model

Identify protected assets, actors, privileges, entry points, data stores, external systems, and trust boundaries. Trace sensitive data and authority through the actual flow. State realistic attacker capabilities and the consequences that matter for this product rather than applying a generic checklist at equal weight.

Prioritize abuse paths around authorization, tenant or account isolation, input reaching interpreters, credential handling, server-side requests, file handling, unsafe deserialization, dependency execution, and privileged CI or deployment workflows.

## Review controls at their owner

Check authentication and authorization separately. Enforce authorization at the resource-owning boundary and verify object-level access, role changes, and indirect references. Validate structure and allowed values before data reaches SQL, shells, templates, URLs, filesystems, or parsers. Use parameterized or structured APIs rather than escaping user strings manually.

Check secret provenance, storage, logging, rotation, and least privilege. Review redirects, webhook verification, replay protection, CSRF/CORS/cookie settings, rate limits, upload content and paths, outbound-network allowlists, and dependency lifecycle where relevant. Inspect default and failure behavior because insecure fallback often bypasses otherwise sound controls.

Use scanners, dependency audit tools, and static analysis to broaden coverage, then inspect the command result and triage findings against reachable code. A clean tool run does not prove the design is secure.

## Report and verify

For each actionable finding, include the affected asset, attack prerequisites, vulnerable path, impact, exact location, and smallest useful remediation. Distinguish confirmed exploitability from a plausible risk requiring further evidence. Group shared root causes and note representative variants.

Verify the protection with an abuse case that fails for the intended reason and a legitimate case that still works. Do not run destructive, invasive, or production testing outside explicit authorization.

## Finding discipline

For a vulnerability claim, name the lower-trust principal, its starting authority, accepted input or action, intended control, crossed boundary, affected resource, and concrete result. Reconstruct the strongest preventing control before deciding the claim. A missing best practice, same-principal self-impact, or absent second layer behind an effective first layer is not enough to establish a vulnerability.

Keep four outcomes distinct:

- **Confirmed:** current source supports the complete path and a bounded observation establishes the claimed boundary failure. State conditions and demonstrated impact; assign severity only here, and never above that impact.
- **Needs validation:** current source supports a specific boundary hypothesis, but an exact runtime, deployment, identity, or other decisive fact is missing. Name that blocker and the smallest safe check that would settle it. Do not assign severity or describe it as an established vulnerability.
- **Rejected:** source or observed behaviour refutes the claim. Record the preventing control or failed prerequisite when it explains the decision.
- **Hardening:** a useful improvement without a demonstrated boundary failure. Keep it separate from vulnerabilities.

Do not infer provider policy, proxy behaviour, browser protections, packaging, or deployed reachability from missing configuration. Do not strengthen a crash into code execution or a one-user effect into a shared outage. Use the smallest effective fix at the trusted decision point, with an abuse regression and a legitimate case.

For consequential findings, use an independent reviewer to challenge the trace and strongest control when the workflow permits it; disclose when that check was unavailable. Revalidate cited paths and conditions against current source before reusing prior findings. An unresolved lead or an unchanged rejection never establishes coverage of the surrounding area.
