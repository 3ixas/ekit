---
name: skill-authoring
description: Create or update an approved owned skill with concise instructions, progressive resources, provenance, invocation policy, and meaningful evaluation.
---

# Skill Authoring

## Outcome

A valid owned bundle whose routing and observable behaviour match the approved contract.

## Method

1. Read [the owned-bundle contract](references/owned-bundle-contract.md) before repository changes. Confirm the approved admission or update decision, current owner, and sources.
2. Choose the smallest bundle that supplies the approved behaviour. Write discriminating frontmatter and an entrypoint focused on the method; link conditional detail where it is needed and retain only useful scripts/assets.
3. Record sources, licences, invocation policy, and owned adaptations so the bundle is attributable and its dependencies are explicit.
4. Run repository checks and realistic positive, nearby negative, authority/failure, and output scenarios required by the contract. Done when the bundle is valid and observed behaviour matches the approved contract; report unresolved failures rather than activating it.

## Boundaries

This skill does not admit itself, activate candidates, sync runtime, or publish without the corresponding decision and authority.


## Owned source methods

These snapshots preserve the reviewed upstream methods. Open one only for a specific method the task needs; the owned steps above govern routing, authority, and completion. Upstream plugin paths and host instructions are historical context, not additional dependencies.

- [source-2-skill](references/source-methods/source-2-skill.md)
