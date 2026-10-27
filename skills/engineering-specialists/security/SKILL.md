---
name: security
description: Threat-model, harden, or review software involving trust boundaries, credentials, permissions, input, sensitive data, dependencies, or public attack surface.
---

# Security

## Outcome

Prioritized exploitable findings and verified protections at the relevant boundaries.

## Method

Map assets, actors, data flow, entry points, and trust boundaries; test likely abuse paths; inspect authn/authz, validation, injection, secrets, SSRF, deserialization, uploads, dependencies, CI permissions, and insecure defaults; use static tools as evidence; triage variants; verify scanners ran and suppressions are justified.

Read [references/security-review.md](references/security-review.md) for threat modeling, audit coverage, and finding standards. For Python-specific work, also read [references/python-security.md](references/python-security.md).

Keep ordinary questions and focused reviews here. A deliberate repository audit with persistent coverage records, isolated hunters, and independently verified reports belongs to the explicit `security-audit` workflow; do not start that workflow merely because security is relevant.

## Boundaries

Do not claim security from a clean scanner or run invasive testing outside authorized scope.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [addy-security](references/source-methods/addy-security.md)
- [trailofbits-differential-review](references/source-methods/trailofbits-differential-review.md)
