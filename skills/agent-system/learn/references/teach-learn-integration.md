# Teach and Learn integration

`learn` is the journey coordinator. `teach` is the bounded teaching method. This is the single handoff contract between them.

## Learn → Teach

Every handoff supplies:

- the journey and track IDs;
- the destination and the track's bounded outcome;
- the learner's current baseline, known misconceptions, constraints, and allowed support;
- the relevant high-trust sources and unresolved source gaps;
- the absolute or clearly resolved Teach workspace path;
- the evidence that would demonstrate independent capability;
- the specific next request for this teaching boundary.

Before the first lesson, Learn creates the track Teach workspace and writes its `MISSION.md` from the agreed brief using Teach's mission format: why this bounded track matters, observable success, constraints, and out-of-scope edges. The journey root's `MISSION.md` remains the broader why. If an existing track mission differs materially from the brief, reconcile it with Elias before changing either contract.

Within an active Learn session, read the installed Teach skill and follow its method with all relative teaching paths resolved from the supplied track workspace, regardless of the agent's initial current directory. The explicit Learn request authorizes this supporting handoff; do not wait for another `$teach` command. No subagent is required. If teaching continues in another session, give that session the absolute Teach workspace path and `BRIEF.md` path; start by reading both and the existing Teach records. A standalone Teach request continues to use its own current teaching workspace.

Teach may refine the next lesson, exercise, source reading, or feedback loop. It must keep the track outcome and workspace boundary visible and must not redesign the wider roadmap.

## Attempts and assistance

Evidence has to link to real attempts, so inside a Learn track Teach keeps every practice attempt as an artifact:

- **Exercises** live in `exercises/NNNN-<dash-case-name>/` inside the Teach workspace. Each has a short spec, a check Elias runs himself when the skill allows it (for code, a test file run from the terminal), and his attempt exactly as he wrote it. Lessons link to their exercises. Keep corrected versions beside the original attempt rather than overwriting it.
- **Assistance ladder.** When Elias is stuck, escalate one rung at a time and only when he asks or has clearly stalled: 0 unaided, 1 nudge (a question that points at the stuck spot), 2 targeted hint (names the concept or line to look at), 3 partial worked example, 4 full solution. Never write the practice solution before he has attempted it. Record the highest rung used for each attempt in the exercise folder.
- An attempt counts towards independent evidence only at rung 0 under the conditions in the track brief. Rungs 1–4 are assisted practice.

## Teach → Learn

At a meaningful boundary, Teach returns:

- what Elias can now do independently, with the concrete evidence;
- what was practised with assistance and the highest assistance rung used per attempt;
- links to the actual attempts or artifacts, their conditions, and the source of any external feedback;
- misconceptions, uncertainty, and blocked prerequisites;
- lesson, reference, asset, and learning-record paths created;
- a bounded next-step recommendation and any request to change the track brief.

Do not return a lesson count, time total, or score as a capability claim. If no independent evidence exists, say so.

## Promotion and route changes

`learn` records the return in `EVIDENCE/`, updates `LEARNER.md` from supported claims, and decides whether the track continues, splits, contracts, pauses, or is promoted. Link each demonstrated learner claim to evidence; keep self-reported knowledge and uncertain inferences labelled. Promotion requires the independent evidence named in the track brief. A proposed destination or route change that affects other tracks returns to the user for approval before the roadmap changes.

If the learner is stuck, prefer a smaller prerequisite, a different explanation, or a new practice context. Do not create a second active track to hide the gap.

## Boundaries

Teach owns the lesson method and the track's learning artifacts. Learn owns the destination, roadmap, active-track state, evidence, and route reviews. The journey workspace is the only durable learner state. Missing handoff context is an explicit stop condition, not permission to invent a parallel contract.
