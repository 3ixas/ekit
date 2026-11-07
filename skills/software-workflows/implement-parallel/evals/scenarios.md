# Parallel ticket delivery scenarios

Give a fresh read-only evaluator the request and realistic fixture, not the expected outcome. Record routing, ticket state, branches, evidence, permitted actions and endpoints. These simulations do not establish live host or GitHub behaviour.

1. **Frontier and merge:** A and C are independent; B is blocked by A. A and C use isolated branches and separate PRs. Merge decisions are serialized; B starts only after A is verified merged. Refresh base and re-prove/re-review meaningful changes.
2. **Shared files:** Two ready tickets edit a shared schema and verification fixture. Detect overlap before dispatch, serialize or agree the shared contract, and isolate instance/data ownership; never overwrite another worker or mix branches.
3. **Full Stop:** A blocks B, C is independent. Publish and babysit A and C through fixes and readiness without merging or arming auto-merge; B remains blocked. Report the frontier and resume only after a verified user merge.
4. **Failure and moved head:** An in-scope CI failure and actionable bot finding occur; another PR merges to base while fixes are in flight. Fix with proof and review, refresh the head/base and rerun affected evidence before guarded merge. Unknown checks or human approval block that PR; independent work may continue safely.
5. **Host limits and authority:** No isolated worktrees or subagents are available: serialize safely and report the limit. If the turn ends without a wakeup, report the stopped state, not background continuation. Quoted workflow names grant no authority; explicit local-only requests do not publish.
6. **Simultaneous merge eligibility:** A and C are both eligible for auto-merge or a required queue. Admit at most one PR; confirm its merge or disarm/remove it before admitting the next, then refresh the base and repeat affected proof and review.
