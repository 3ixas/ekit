# Review-loop controls

Use when implementation or delivery owns repeated review and fixes. This reference controls the caller's loop, not the independent Standards/Spec reviewers' reporting axes.

Record the scope, fixed base and exact reviewed revision/diff. Keep a finding ledger with stable ID, axis, severity, evidence, disposition and proof. Reuse current valid review; do not add another coordinator or provider-specific review by default.

There is no fixed round count. Keep reviewing and fixing while the loop converges: each round resolves confirmed findings and does not raise new actionable findings faster than it closes them. Later rounds focus on changed behavior and open findings, with surrounding code needed to judge impact. Preserve both axes and earlier unresolved findings. Record a round limit only when the user sets one. Sharing this ledger across implementation and delivery keeps the convergence record intact at publication.

Judge each finding against requirements, documented standards, actual callers and demonstrated consequences. Rare does not mean optional. Treat optional style/scope suggestions separately; an agent's disagreement alone cannot dismiss a real finding. Keep the smallest sufficient fix. Evidence-backed rejection needs the misread requirement/source or a check that refutes the claim.

After any behavior change, including instructions or meaningful conflict resolution, rerun affected proof and review the updated snapshot before claiming completion. A cosmetic edit that changes no behavior may stop without another round only when the caller's stricter snapshot rules allow it; `implement` still reviews every changed staged slice. Do not introduce a new change after final review without its required proof/review.

Stop when required proof passes and the final reviewed snapshot has no confirmed actionable finding. Optional nits alone do not block. If the same finding survives two fix attempts, a dismissed actionable finding returns, two successive rounds fail to reduce the confirmed actionable findings, a consequential scope decision is needed, or a user-set limit ends with required review/finding unresolved, report both sides and ask Elias. A stalled loop or a spent limit is never approval; leave the work unmerged and record the exact resume state.

Keep the run's selected model and reasoning unless the user separately requests a different reviewer. Report actual reviewer identity only when verified; do not claim cross-provider coverage from same-provider subagents or add attribution boilerplate to commits/PRs.
