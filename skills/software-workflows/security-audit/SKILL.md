---
name: security-audit
description: "Use when Elias requests Security Audit or a deliberate repository security audit with coverage records, isolated hunters, independent verification, and reports. Focused security questions and reviews use security."
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

# Security Audit

## Outcome

A source-pinned security audit with explicit coverage, independently verified findings, exact unresolved blockers, and machine-checked report records.

## Invocation

Run only when Elias requests this workflow or clearly accepts a deliberate repository audit. Use `security` for questions, threat modelling, implementation guidance, or a focused review; use `code-review` for a general diff review and `app-audit` for product readiness. Loading this skill as context does not start an audit.

## Method

1. **Establish scope and capabilities.** Identify the target, source revision and dirty files, relevant paths, prior runs, output location, profile, and any user-set budget. Default to standard; use quick or scoped only when it matches the request, and report partial coverage. Choose a fresh output directory outside the target within an authorized writable workspace. Check Node.js and the host's delegation capability before launching work. Fresh agents must remain independent; serialize waves when concurrency is limited. If independent agents or validators are unavailable, report the exact blocker and an incomplete run rather than substituting self-review.
2. **Read the audit contract.** Follow the [six-phase method](references/cloudflare/audit-method.md), including its budget gate, execution controls, parent-owned shared records, and isolated agent writes. Its skill directory means this owned bundle root; validators and schema live under `scripts/`. Read reconnaissance, hunting, and reporting references when entering those phases. Load only domain companions selected from source-visible boundaries.
3. **Map, hunt, and challenge.** Build architecture and deterministic coverage records; assign bounded units to isolated hunters; use fresh coverage critics to expose missing paths. Give every candidate to a fresh verifier that tries to refute it. Preserve prior-run fingerprints only after checking current source and conditions. Record unassigned or blocked work explicitly.
4. **Validate and report.** Run `node <skill-dir>/scripts/validate-findings.cjs <output-dir>/findings.json` and `node <skill-dir>/scripts/validate-coverage-ledger.cjs <output-dir>/coverage-ledger.json` at the method's prescribed gates. Independently verify final records before deriving reports. Close with either complete artifacts and passing validators, or explicit incomplete status and disclosed gaps; never claim complete coverage from a partial run. Validator success proves record structure, not exploitability or host isolation.

## Execution and authority

Audit source is read-only. Target-controlled execution requires the method's OS-enforced network, environment, filesystem, resource, and time restrictions plus safe evidence promotion. A prompt, generic tool sandbox, or available browser does not prove those controls. The bundle includes validators, not a sandbox launcher or artifact-promotion implementation. If controls cannot be demonstrated, continue source review and retain runtime-dependent candidates as `needs_validation`; do not run target code to force confirmation.

Use dummy data and the smallest local observation that establishes the boundary result. Do not probe live services, install dependencies, spend API quota, publish, or change target source. The audit recommends narrow fixes; accepted remediation returns to `implement` or `debug` under its own scope. Do not transmit private code to additional services. Keep retained outputs within the authorized location and omit secrets.
