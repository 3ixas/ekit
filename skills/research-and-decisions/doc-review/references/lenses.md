# Review lenses

Independently written for this repository, informed by Compound Engineering's `ce-doc-review` personas. Each lens has a question it owns and the signals that activate it.

## Always on

**Coherence**: does the document agree with itself? Look for contradictions between sections, terms used two ways, goals that no requirement serves, requirements that serve no goal, broken references, and an order that hides dependencies.

**Feasibility**: can this be built as written? Look for steps that depend on something unspecified, assumptions about existing code or services that the evidence contradicts, missing failure and recovery paths, migration or rollout ordering risks, and estimates or sequencing that cannot hold.

For consequential recommendations, name the implicit assumptions about current behaviour, edge cases, and interactions. Check the implementation and its dependencies for evidence, distinguishing verified, contradicted, and unresolved assumptions. Verify each recommended existing pattern in its actual context: does it still exist, is its example complete, and do its constraints fit this use? If multiple viable patterns exist, present the supported options and trade-offs as **Decide**; do not silently select one or call an existing pattern good merely because it exists. Preserve settled scope and resolved decisions; contradictory new evidence warrants review of the affected decision, not unrelated redesign. Ordinary reviews do not require a new research document.

## Conditional

**Product**: is this the right thing to build? Activate when the document stakes a product position a knowledgeable stakeholder could challenge (a problem framing, a predicted user outcome, a prioritization), or when the work carries strategic weight: what the product becomes known for, a complexity bet, a path dependency, or a large opportunity cost. A choice among mechanisms for an agreed outcome is not a product position.

**Design**: will people be able to use it? Activate on user interfaces, flows, screens, interaction descriptions, responsive behaviour, or accessibility. Check states (empty, loading, error, success), journeys end to end, and consistency with any `DESIGN.md`.

**Security**: who can read or change what? Activate on authentication, authorization, sessions, externally exposed endpoints, sensitive data (personal data, payments, tokens, credentials), or third-party trust boundaries. Ordinary data handling and internal schema changes alone do not activate it.

**Scope guardian**: is the scope disciplined? Activate on priority tiers, more than about eight requirements or units, stretch or future-work sections, or scope language that drifts from the stated goals. Look for requirements that could be cut without losing the goal, and work that belongs in a later slice.

**Adversarial**: what if the premise is wrong? Activate on a requirements document with two or more challengeable claims, a high-stakes domain (auth, payments, data migration, privacy, cryptography, external integrations), a new abstraction or architectural pattern, a plan whose premise was never validated upstream, scope that extends beyond its origin, or an explicit alternatives section. Do not activate it on a routine plan that follows a validated upstream decision and introduces nothing high-stakes; that re-litigates settled questions.
