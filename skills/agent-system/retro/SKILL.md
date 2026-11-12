---
name: retro
description: "Review a session for environment and workflow improvements and reusable user preferences; learn from corrections or prune existing preference guidance. Use the relevant design, writing or engineering skill to change the work itself."
---

Suggest evidence-backed improvements to future runs: the agent's environment and workflow, and reusable preferences expressed by the user. A focused request to learn from corrections or prune preference guidance runs that branch without requiring a full environment review.

## Steps

1. Load `writing-for-agents` through the host's available skill mechanism, or read its installed `SKILL.md`, for the instruction-writing method.

2. Read the primary sources for the specified session, defaulting to the current one. Use the host's available conversation history or local transcripts; include earlier sessions when requested and accessible. State missing or partial coverage rather than claiming every turn was reviewed.

3. Look for candidates for improvement in these categories.

- **Navigation**: how easy was it for the agent to find the right files? Are there hidden dependencies between files? Would a **navigation pointer** make it easier? _Use when_ the session took a long time to find a piece of information.
- **Automated checks**: are there automated checks that could catch errors the agent made? Linting, typing, tests, filesystem linters? Read the repo's own check command first (its `package.json`/build-tool `lint`/`check` scripts, its CI workflow), so a check that already exists but sits unwired or silently broken is the finding, not a reinvention. A repo with no **guardrail** (no pre-commit hook and no CI job running its lint/typecheck/test command) is itself a finding: an un-linted repo is a standing missed opportunity, not a neutral default. _Use when_ the agent made a mistake an automated check could have caught, or the repo has no guardrail at all.
- **Coding standards**: should the **reviewer agent** be given a new rule to enforce? Should an existing rule be removed or clarified? Classify the violation first: a **mechanical** one (a fixed syntactic pattern, a banned API, an import shape, a file-location rule) gets a deterministic check, full stop: a custom rule in the repo's own linter, a new pre-commit hook, or a new CI job, whichever the repo's language and existing guardrail make cheapest. Default to building the check over writing the rule. Reserve `CODING_STANDARDS.md` for genuine **judgement calls** (cross-file consistency, "matches the surrounding style," anything no guardrail could ever substitute for). _Use when_ the reviewer agent failed to catch a mistake.
- **Global AGENTS.md**: are there any steering instructions that should be moved to coding standards (or automated checks) instead? _Use when_ the AGENTS.md file is particularly large - in the repo OR the user's global scope.
- **Tool economy**: did the agent make expensive tool calls that could be streamlined? Is there any custom tooling (CLI's, MCP's) that is particularly token-inefficient? _Use when_ the agent made an expensive tool call.
- **No-ops**: look for instructions in steering files that don't modify the agent's behavior. _Use when_ the steering files are large and unwieldy.
- **Information access**: look for opportunities to increase the agent's access to information. Teeing dev server logs, readonly access to third-party services. _Use when_ a crucial piece of information was not available to the agent.
- **Altitude**: when this task is an instance of recurring work, name the recurring outcome an agent could own, the missing evidence or tools, the bounded authority needed, and the specific setup change that would reduce repeated human intervention. For example, keeping an app crash-free needs accessible crash reports, versions mapped to commits, and a reproducible environment; distinguish authorised local diagnosis and fixes from release authority. Recommend a concrete setup change using the session's evidence. A recommendation does not create monitoring, change permissions, or authorise external actions. _Use when_ the user handed the agent one instance of a recurring kind of work.

4. When corrections or confirmed reusable choices appear, read [learning from corrections](references/learning-from-corrections.md). Include evidence-backed preference candidates alongside environment findings. For a focused pruning request, use that reference's pruning method instead. If there is no reusable preference evidence, say so briefly; do not manufacture rules.

5. Present numbered candidates in order of consequence, with the evidence, proposed change, reason, scope and destination. Include unresolved questions, conflicts and useful skipped corrections without empty sections. Before persistence, resolve inferred reasons and scope conflicts and confirm which concrete proposals are approved; reuse existing approval without asking again. A Retro request alone authorizes recommendations, not durable preference writes.

6. Apply only approved items through their existing owners. Route shared-skill changes through `skill-review` and `skill-authoring`; use `writing` for personal writing context and `obsidian` for personal knowledge. Show the resulting diff and check added guardrails against the codebase. Report existing violations; do not fix application code or silently weaken enforcement as part of preference capture. External actions still need their own authority.

## Reference

### Implementation vs Review

Remember that all work goes through two stages: implementation and review. The implementation agent has the most **context pressure**. They are responsible for exploration, writing code, and debugging failures.

The review agent receives a focused diff and usually has less implementation context to hold. It must still inspect the source and evidence needed to verify its findings; it often does not need to write code or debug.

This means that the review agent should be responsible for imposing coding standards, not the implementation agent.

### Files

You have access to several files in the repo:

- `CLAUDE.md`/`AGENTS.md`: these files are pushed to the context window of any agent working in this repo. They should be used incredibly sparingly, usually only for **navigation pointers** to other files.
- `CODING_STANDARDS.md`: this file is read during review, not implementation. Add **navigation pointers** to docs folders if the standards file gets more than 1,000 lines long.
- Docs: use docs as references files, pointed to by other files. Look for existing docs before writing new ones.
- Skills: use skills for docs (since their description goes into the agent's context window), or for user-invoked commands. Follow the advice in the `writing-for-agents` skill.
