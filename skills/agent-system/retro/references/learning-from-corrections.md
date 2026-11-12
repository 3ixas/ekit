# Learn from corrections

Use when a retrospective includes user corrections or confirmed reusable choices, or the user asks to learn from corrections or prune existing preference guidance. This method applies to design, writing and working preferences; keep project and personal facts with their authoritative owners.

## Collect and qualify

Read the available session evidence before proposing rules. For each candidate, retain a source quote or attributable diff, what the agent did, the desired result and any reason the user supplied. Look for:

- Explicit corrections and confirmed non-obvious choices a fresh agent might otherwise miss.
- Edits the user made to the agent's output. A changed file alone does not establish authorship or preference; qualify uncertainty and ask only when it affects a proposal.
- Repeated nudges: capture the final accepted result and its scope rather than each intermediate step.
- Reverts, rejected variants and deletions: establish what was rejected without inventing the reason.

Skip one-off content, functional bugs and corrections to task understanding as preference rules; they can still support environment findings. A useful rule should prevent the same mistake on a different instance of the same kind of work. No evidence is a valid outcome.

## Generalise and reconcile

Choose the narrowest reusable scope the evidence supports. One card's treatment does not establish a universal surface rule. Preserve exceptions, exact values and the strength of the user's wording; a single change from 400ms to 200ms does not establish a 150–200ms range.

Inspect existing design contracts, project instructions, standards, project skills and the relevant personal guidance before adding a duplicate. If an equivalent rule already exists, diagnose whether it was discoverable, loaded, clear and applicable. Propose the smallest evidenced repair; stronger wording alone does not fix an unread rule. Show both sides of a contradiction and obtain a choice before replacing it. Recency alone does not settle scope or authority.

Use the user's reason when available. Otherwise propose a reason labelled **inferred** and obtain confirmation before persisting it. Resolve consequential ambiguity in generalisation the same way. Do not present the agent's own best practice as the user's preference.

Self-test the proposed rule and reason against the original mistake: could a fresh agent still produce the rejected result, or would the rule forbid an accepted exception? Clarify only what the evidence supports.

## Choose a destination

- **Project design:** use the existing `DESIGN.md` section; propose creating the file or section only when needed. Check project instructions for a pointer and propose one if the contract is otherwise undiscoverable. Keep design direction consistent with `interface-design`'s existing contract.
- **Project working or coding preferences:** use the existing project guidance or review standards. Follow Retro's distinction between deterministic checks and judgement; do not put all lessons into global instructions.
- **Personal writing:** use `writing` to locate and maintain the authoritative writing context. A session-specific wording choice does not automatically become a personal rule.
- **Personal knowledge:** use `obsidian`. Do not store personal facts in generic skills or update host memory implicitly.
- **Shared instructions or skills:** establish evidence that the preference applies across projects, locate the owned source, then route through `skill-review` and `skill-authoring`. Never edit generated runtime copies.

Prefer an existing lint rule, token restriction or meaningful test for mechanically detectable violations. Propose its concrete enforcement and retain a concise rule with its reason in the appropriate guidance. Inspect existing configuration and code to state what the check would flag; label unexecuted estimates. Loading a skill grants no action authority.

Keep conditional detail in an existing reference or project skill when justified by its audience and size, leaving a short pointer. Do not create skills or reorganise documents merely because a section crosses an arbitrary length.

## Propose, then persist approved items

Use numbered candidates with **evidence → rule or repair → reason → scope → destination**, plus a concrete check where appropriate. Identify questions, conflicts and useful exclusions compactly. Keep a proposed reason marked inferred until confirmed. Offer selective approval in ordinary language; do not require a special command.

Write only items covered by concrete approval and whose material questions are resolved. Broader implementation authority elsewhere does not approve newly inferred preferences. Preserve accepted wording, exceptions and existing unrelated rules. Store the rule and reason with a date and source pointer or short quote where appropriate; avoid copying private transcript excerpts into public guidance. Use a private evidence pointer or an approved sanitised summary instead.

Show the resulting diff. Implement approved checks and run them across the codebase; report existing violations and their count. If enforcement would break existing checks, present the result for a decision about remediation or warning severity. Do not change component code, fix unrelated violations or downgrade enforcement without authority.

## Prune existing guidance

Read the named guidance and its loading pointers; use requested session evidence when available. Propose merges for duplicates, expose contradictions and identify vague or undiscoverable rules. Preserve supported reasons and exceptions. Missing historical evidence limits the claim: do not invent an original rationale, delete rules as obsolete without support, or strengthen preferences into bans. Apply the same selective-approval and diff requirements.
