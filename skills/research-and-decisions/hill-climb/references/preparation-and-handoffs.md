# Preparation and handoffs

## Refine a rough request

Start with the user's desired result and why it matters. Inspect the actual implementation and evidence before asking for facts. Use `grilling` to work through choices that change the outcome: intended users/journey, expected and unwanted behaviour, important edge cases, constraints, acceptable trade-offs and what would count as convincing proof. Propose a strong target grounded in evidence alongside the minimum acceptable outcome; settle scope increases with Elias. Do not turn a simple known fix into a compulsory interview.

Reuse existing Grilling agreements, Wayfinder destinations/decisions and specs. Put new consequential choices into the current frontier rather than opening another questionnaire. Confirm the shared outcome through Grilling's existing closing agreement; no second sign-off when the outcome and execution authority are already settled. Once preparation is complete, carry the agreed brief directly into the climb if already requested, rather than asking for a special command.

Build the smallest acceptance checks needed for the work. A feature's tests can initially fail for missing behaviour; record those expected gaps separately from preservation guards for working behaviour. A bug needs a reproducer or explicit evidence gap, an expected result and sibling/regression cases. Passing more tests is progress, but every required behaviour and preservation check must pass before completion. Reduce performance/cost only while preserving the agreed functional outcome. Human judgment can settle product/taste choices; do not replace it with an invented scalar rating.

## Recommend a climb where it earns its cost

During ordinary work, Grilling or Wayfinder, identify a bounded piece when several plausible approaches need real testing, repeated fixes have failed, interactions make correctness difficult, or an ambitious target needs iterative evidence. Explain the concrete uncertainty, why an ordinary pass is insufficient, likely proof and a finite budget. Offer the specific piece, not the entire project by default. Generic polish, simple chores and rhetorical requests for 'the best' do not earn a climb by themselves.

A suggestion is not execution. If Elias already requested a climb, refine and proceed under that authority once ready. Otherwise seek acceptance of the recommendation before starting the loop; do not add repeated approvals for in-scope steps. If the workflow is unavailable or still a candidate, say so and preserve the proposed brief; do not promote/install it implicitly.

## Work through existing owners

- `grilling` resolves the outcome; `grill-with-docs` preserves substantial software scope. Their decisions remain authoritative.
- `wayfinder` identifies a destination and uncertain route. Recommend a climb for a specific mapped investigation or delivery slice. Its planning-only default remains: accepting the recommendation does not silently convert the map into implementation. Obtain execution authority or leave a precise handoff.
- `debug` reproduces and localises the fault; it does not run a separate unbounded fix loop alongside this one. If the diagnosis changes a requirement or reveals a scope decision, return that choice to Elias before further fixes.
- `implement` owns feature/fix slices, proof and the existing review/delivery lifecycle. Supply the climb's local evaluation endpoint so an experimental attempt does not publish or merge before selection and confirmation. Reuse valid final proof/review, and deliver only to the already-authorised endpoint.
- `compare` develops competing approaches when that comparison is needed; Hill Climb owns the subsequent attempt/decision record. Verification, performance and skill-authoring keep their specialist methods. Share evidence and budgets, avoiding duplicate coordinators, checks and review panels.
