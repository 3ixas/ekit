---
name: grilling
description: Explore a plan, decision, or idea through exhaustive shared questioning until consequential choices are settled. Use when Elias requests Grilling or wants to stress-test their thinking; discussing the workflow or quoting its name is not an invocation.
---

Explore until you reach a shared understanding and the user is better equipped to reason about similar decisions themselves. Map this as a **design tree**: every consequential decision branches into the decisions that hang off it.

Read [collaborative exploration](references/collaborative-exploration.md) before the first round. Make the reasoning behind consequential questions accessible within the existing conversation, adapting to what the user understands. Domain skills supply their own questions, methods, artifacts, and evidence; this skill supplies the shared exploration method.

Before the first round, run the [depth pass](references/depth-pass.md) on what the user brought: the outcome one level up, what an expert would add, the rawest evidence, an expert-level target, and the independent proof of done. It deepens the tree; anything that would raise scope or ambition enters as a frontier question with your recommendation, never as a silent assumption.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

When a frontier decision is generative or a matter of taste (what something could be, how it could feel, what shape it takes), show options instead of asking: three concrete options side by side, each diverging on a named axis, one of them a stretch option, with your recommendation. The chosen option seeds the next, more concrete round. Follow [options rounds](references/options-rounds.md) for when to use them, their shape, the ladder of concreteness, rendering, and the exploration trail.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the consequential frontier is empty and the choices meet the decision-ready standard in collaborative exploration. Resolve material unknowns or explicitly defer them with an acceptable reason or a specific test; do not keep branching into implementation details or interesting questions that cannot change the decision or next step. Before calling it done, run the gap check and present the settled agreement for confirmation as described in [the question-frontier method](references/question-frontier.md). Briefly surface the most useful reusable thinking from this session. Do not act on the agreement until the user confirms you have reached a shared understanding.
