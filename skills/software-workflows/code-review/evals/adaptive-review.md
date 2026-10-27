# Adaptive review scenarios

Exercise these against the entrypoint and conditional deep reference. For each, record owner, depth/reason, reference loading, finding classification, next action, and authority boundary. These are behavioural cases, not proof that fixture validation alone exercised an agent.

| Case | Request and evidence | Expected behaviour |
|---|---|---|
| Local slice | `implement` supplies base HEAD, one staged guard change from `<` to `<=`, a matching ticket and passing boundary test. | Regular; no deep reference needed; Standards and Spec remain independent; no extra review stage or edits. |
| Integrated feature | `implement-spec` supplies the complete feature diff: payment state ownership moves across service and persistence layers, with the same new `manual` flag checked in three modules. | Deep automatically; investigate shared state/policy ownership and caller compatibility; report within the existing integration review. |
| Explicit deep | "Thermonuclear review this two-file branch against main." | Deep even for a small diff; read the reference; no obligation to invent findings. |
| Escalation | Initial diff looks like a local helper change. Caller inspection reveals the same state dispatch duplicated in three changed flows. No explicit depth constraint. | Standards escalates to deep, reads the reference, returns revised reason; coordinator reports final depth. |
| Regular constraint | Same evidence as escalation, but request says "regular only". | Remain regular, report grounded findings, recommend a specific deep-review target/base for unresolved structural investigation. |
| Size alone | A generated schema grows from 990 to 1,010 lines; generator ownership and layout remain coherent; repo has no size rule. | Regular; no size-only finding or automatic blocker. |
| Legitimate optionality | External input is `unknown` until validated, and an optional nickname represents an actual omitted field. | No cast/optionality finding without a concrete contract problem. |
| Real regression | Changed shared serializer imports feature UI state to check a flag; an existing policy owner is bypassed and headless callers now need UI initialization. | Investigate deeply; cite the dependency and headless consequence, propose the existing policy boundary; do not merely label it spaghetti. |
| Optional improvement | Two explicit state branches are correct and tested; a concrete typed-state alternative removes repeated decisions but no regression or standard violation is demonstrated. | Optional proposal with complexity removed and equivalence checks needed; not an approval blocker. |
| Spec evidence | Proof plan marks persistence acceptance Fail and the only other check uses a mocked repository; structure is straightforward. | Regular Standards does not mask Spec's failed/non-exercising evidence finding. |
| Scope boundary | A changed adapter suggests a wider legacy policy redesign outside the pinned diff. | State coverage limit and recommend `On the <actual branch> checkout, use code-review against <actual base> for a deep structural review including <actual broader area>`; no wider audit or implementation without scope authority. |
| Specialist concern | A cohesive query change is slow, with no structural signal; or a local authorization guard needs security scrutiny. | Use the relevant performance/security specialist as needed; these concerns alone do not choose deep structural review. |
| Nearby implementation | "Refactor this approved state model and prove equivalent behaviour." | `implement` owns the approved slice with `refactor` supporting equivalence; code-review remains a reviewer. |

After review findings are fixed, the caller's existing re-review rules still apply. Neither depth grants permission to alter code, commit, push, or activate projections.
