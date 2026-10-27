# Slice execution

## Establish the contract

Read the whole target issue or request, its parent spec, project instructions, and affected code. If the target is a GitHub issue, load it with `gh issue view <number-or-url> --json number,title,body,state,labels,url` using the exact repository; prefer the most efficient supported GitHub capability for issue reading. State the observable completion conditions and, for each, the independent check that will prove it; this is the proof plan `SKILL.md` asks for. If behavior is unresolved, return to `grill-with-docs`; if the request is clear but technically incomplete, investigate and make routine implementation choices.

Inspect existing patterns at the entry point, boundary, data owner, and tests. Check current repository status and preserve unrelated changes. Identify the smallest coherent diff that delivers the requested behavior through every necessary layer.

Before introducing a helper, component, service or dependency, search the affected area and likely shared modules for an existing implementation. Check suitable project utilities and installed dependencies, then standard-library or platform features, before writing new code. Choose what satisfies the full behaviour and the project's conventions with the least maintenance burden. A shorter option that loses required semantics, safety, accessibility or approved design is not equivalent. Keep the search proportional to the change; do not map the whole repository for a local edit.

## Implement in proving increments

Order work so each increment reduces uncertainty or unlocks an observable check. Update contracts and callers together. Keep domain rules in their real owner and validate untrusted data at boundaries. Treat migrations, permissions, errors, retries, and cleanup as part of the behavior when relevant.

Run the narrowest meaningful check after each risky increment. Diagnose failures rather than weakening assertions or adding guards that conceal the cause. Re-read the diff during implementation to catch scope drift and accidental edits.

Do not create broad abstractions for one local use, rewrite neighboring code for aesthetic consistency, or add compatibility paths without a real consumer.

## Prove and report

Run project-required checks, targeted tests, and the real acceptance surface. Inspect generated files, migrations, rendered UI, API responses, or CLI output rather than relying on exit codes alone. Use `verify` for the final behavioral proof.

Report the resulting behavior, consequential decisions, checks and observed results, and any limitation. Do not claim completion for a skipped or inaccessible acceptance surface.
