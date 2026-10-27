---
name: writing-for-agents
description: Write or revise AGENTS.md, SKILL.md, prompts, and agent-consumed documents so routing, steps, evidence, and completion remain clear and economical.
---

# Writing For Agents

## Outcome

Agent instructions that reliably change the intended behaviour without context sprawl.

## Method

1. **Name the reader and its triggers.** Identify the agent that consumes the file and every situation that should load it, in the words the user and agent already use. Done when the description or heading routes each of those situations and no neighbouring one.
2. **Separate steps from reference.** Keep the entrypoint to what the agent does every time; move conditional detail into references linked from the step where it applies. Done when every reference link says when to read it.
3. **Keep related rules together.** Put each rule where the agent acts on it, not in a general section. Done when no rule has to be found in two places.
4. **Make each step checkable.** Give every step an observable completion criterion. Done when an agent could tell, without judgement calls, whether it has finished the step.
5. **Cut what does not change behaviour.** Remove duplication, stale facts, no-op statements, and prohibitions without a reason. Done when deleting any remaining sentence would change what the agent does.
6. **Forward-test risky behaviour.** For anything that sends, deletes, publishes, or routes, run a realistic request through a fresh agent. Done when the observed behaviour matches the intent.

## Boundaries

Do not restate discoverable environment facts or hide essential rules behind vague links.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [Technical-writing method](references/source-methods/pstack-technical-writing.md) when the task needs document modes, sentence-level clarity rules, or a worked technical edit.
- [Agent-instruction method](references/source-methods/source-1-writing-for-agents.md) when restructuring an instruction set needs its detailed progressive-disclosure and evaluation guidance.
