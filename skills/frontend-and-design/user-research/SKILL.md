---
name: user-research
description: "Plan UX research, discovery interviews, usability tests, or synthesis of user evidence for a product decision. Use for evidence-backed recommendations; visual direction belongs to interface-design and settled production coding to implement."
license: MIT
metadata:
  author: hueyexe
---

# User Research

## Outcome

A decision-ready research plan or recommendation traceable to user evidence, with assumptions, confidence and the next useful test stated.

## Method

1. **Frame the decision.** Inspect supplied artifacts and existing evidence. Name the product decision, user task/context, desired behaviour and business outcome, constraints, and evidence gaps. Ask only when missing information materially changes the work; use [decision prompts](references/decision-prompts.md) for such questions, adapting their illustrative shapes to the host’s actual input tool. Done when facts and assumptions are distinguishable and one primary research question is answerable.
2. **Choose the smallest credible mode.** Use discovery for unclear needs, descriptive research for workflows/context, evaluative testing for an existing concept or UI, and quantitative evidence for measurable effects. Read the matching workflow and defaults in [research method](references/research-method.md#workflow); do not use small qualitative samples to estimate prevalence or establish causality. Done when the method and proposed evidence can inform the named decision.
3. **Prepare or conduct the work.** For interviews, create neutral prompts anchored in recent experiences; for usability tests, write realistic goal-based tasks and success criteria rather than click instructions. Read the relevant planning, moderation and testing sections in [research method](references/research-method.md#workflow). Include behaviour-based participant criteria, consent/recording/privacy, roles, logistics, accessibility accommodations and synthesis. Do not pitch, lead, teach or rescue during observation. Done when the plan can be run or the observed session record is captured with its limitations.
4. **Synthesize with traceability.** Separate observations and quotes from interpretations and recommendations. Compare patterns, outliers, opportunities and risky assumptions; retain source/session pointers. Use the [evidence ladder and prioritization rules](references/research-method.md#decision-framework), with [principle cards](references/principle-cards.md) when interpreting a difficult trade-off. Done when each finding has an identifiable source and confidence appropriate to the method.
5. **Recommend the next action.** State the recommendation, user/business value, evidence, confidence, alternatives or trade-offs, accessibility and frontend implications, and smallest next test or metric. Use the relevant [critique or implementation guidance](references/research-method.md#frontend-implementation-guidance) when recommendations change a UI. Done when the recommendation answers the original decision without treating preferences or stakeholder assumptions as observed behaviour.
6. **Check the deliverable.** Use only the applicable sections of [checklists](references/checklists.md). When a plan risks leading questions, invented personas, frozen maps, research theater or overclaiming, consult [anti-patterns](references/anti-patterns.md). Report missing participant access or accessibility coverage explicitly. Done when the selected checklist passes or each unresolved limitation is stated beside the affected conclusion.

## Boundaries

Research planning does not authorize participant contact, recording, incentives, scheduling or publishing. Use the authority supplied by the current task for those actions. Do not invent sessions, quotes, personas or user evidence.

Pure visual styling belongs to `ui-polish` or `interface-design`; settled production coding belongs to `implement`. Rigorous statistical analysis needs `data-analysis`; regulated human-subjects research requires qualified review beyond general UX planning.
