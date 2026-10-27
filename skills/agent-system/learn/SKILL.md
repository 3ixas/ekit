---
name: learn
description: "Use when Elias requests Learn or a sustained multi-capability learning journey with tracks, learner records, and route reviews. Do not select for a brief explanation or a standalone lesson."
argument-hint: "What larger learning destination are you working toward?"
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only for a clear request for this workflow or a supporting handoff within an authorized workflow. Discussion, quoted mentions, negation, and adjacent questions do not request execution. Loading this skill grants no additional action authority.

The user has invoked `learn` for a destination that needs several connected capabilities. Coordinate the journey; do not become a second teaching engine. Use `teach` for each bounded track.

## Choose the right owner

- One coherent capability with one observable outcome: use `teach` directly. Do not create a roadmap just because the topic may take several sessions.
- Several capabilities, topics, or phases must combine to reach the destination: continue with `learn`.
- If the scale or destination is unclear, use `grilling` to establish it before creating durable state.

A broad destination is complete when Elias can independently perform the agreed outcome. Lessons, elapsed time, coverage, and scores are evidence of activity or practice, not proof of capability.

## Start or resume a journey

Use a separate private journey workspace. It is not this skills repository, a product repository, an employer repository, GitHub issues, a calendar, or the retired Adaptive Learning repository. If no journey workspace is known, ask Elias to choose or approve one before the first durable write.

Read the existing journey files in this order, when present:

1. `STATE.md`, `DESTINATION.md`, and `ROADMAP.md`.
2. `MISSION.md`, `LEARNER.md`, and `SOURCES.md`.
3. `REVIEWS.md`, `REVIEW-QUEUE.md`, `OPEN-QUESTIONS.md`, the active track brief, and the track's Teach workspace.

Use [the journey templates](references/templates.md) for missing files. Keep the files short and update them in place. Remove or close temporary `OPEN-QUESTIONS.md` items when they are settled.

## Establish the destination

Before planning lessons, agree on a destination contract:

- the real-world outcome and why it matters;
- the observable actions that count as independent capability;
- the starting baseline, constraints, and available practice contexts;
- the capability areas that may be needed;
- what is explicitly out of scope for this journey.

Use `research` to ground unfamiliar domains and high-trust sources. Record the useful sources in `SOURCES.md`, with what each source is for and any gaps. Do not fill uncertainty with model memory.

Create a provisional, receding-horizon roadmap. Show the destination and capability areas. Detail only the active track, keep the next track as a strong proposal, and leave later tracks as hypotheses. Do not pretend to know the whole curriculum in advance.

## Run one track at a time

Keep exactly one primary track active. Other tracks may receive brief retrieval or maintenance work, but do not run parallel curricula.

For the active track:

1. Create or update `tracks/<track-id>/BRIEF.md` with its bounded outcome, baseline, prerequisites, constraints, sources, practice context, and evidence target.
2. Create `tracks/<track-id>/teach/` as the Teach workspace. From the agreed brief, populate its `MISSION.md` in Teach's mission format before the first lesson. Keep the journey mission at the root and the bounded track mission here. Preserve and reconcile an existing Teach mission rather than overwriting it.
3. Read `references/teach-learn-integration.md`.
4. Before the track's first lesson, run a short unaided diagnostic against its evidence target. Record anything Elias passes as evidence and skip it; what he cannot yet do becomes the starting point.
5. Read the installed Teach skill's `SKILL.md` and its `references/` as files and follow that method with the Teach workspace as its working directory. Teach is model-loadable; load it directly or read its instructions as files. The active Learn request authorizes this supporting handoff; a second user invocation or subagent is not required. Give it the brief and handoff context. Teach owns the lesson loop, resources, references, exercises, feedback, and learning records. For a separate session, pass the absolute track workspace and brief path so Teach resumes the same track.
6. At a meaningful boundary, collect Teach's return summary and write an evidence record under `EVIDENCE/`. Link the attempt or artifact and record its conditions, support used, observed result, feedback source, and remaining gap. Separate independent performance from assisted practice.
7. Update `LEARNER.md` with relevant demonstrated capabilities, support needs, and misconceptions, linking the evidence. Keep self-reported prior knowledge labelled as a claim until demonstrated. Then update `STATE.md`, the active track, and `REVIEWS.md` before deciding what comes next.

Do not redesign the wider journey inside a Teach session. If the track is too large, split or contract it at the route review. If the destination changes materially, confirm the new contract before rewriting the roadmap.

## Open and close every session

A journey runs across many short sessions, so each one starts and ends the same way.

- **Open:** read `STATE.md` and the active track, give Elias a recap of at most three lines, run a short retrieval warm-up from the items due in `REVIEW-QUEUE.md`, and propose one bounded plan sized to the session time recorded in `LEARNER.md`.
- **Close:** write a learning record or evidence only when earned, add newly learned items to `REVIEW-QUEUE.md`, reschedule warm-up items by result (widen the interval after a clean unaided recall, shorten it after a miss), set `STATE.md`'s next action, and commit the journey files when the workspace is a Git repository.

`REVIEW-QUEUE.md` is the spacing mechanism for taught and maintenance material. It is a Markdown list, not a scheduler.

## Review and route

At each route review, decide from evidence whether to:

- continue the track with a smaller next step;
- revisit a prerequisite or misconception;
- promote the track because the agreed independent evidence exists;
- contract, replace, or pause the track;
- propose the next track and its rationale;
- revise the destination, constraints, or source plan.

A user-assisted success is valuable practice, but it is not independent proof. Do not mark a capability complete until Elias performs the agreed outcome with the allowed level of support. Preserve uncertainty and unresolved questions instead of smoothing them over.

Elias approves the destination contract, the initial broad route, material route changes, and major capability claims. The coordinator may choose routine lessons, exercises, source reading, and the next small practice step within that boundary.

## Boundaries

- `teach` owns bounded teaching. `learn` owns destination, tracks, evidence, and route decisions.
- `grilling`, `research`, normal engineering or product skills, and `verify` remain the owners of their own methods. Invoke them when the track needs them; do not reproduce their instructions here.
- Keep learner state in the private journey workspace. Do not write personal learning records into this skills repository.
- Use Markdown as the canonical record. Do not introduce a database, scheduler, issue system, or hidden state for the first implementation.
- If the Teach handoff contract or required workspace is missing, stop at that boundary and report the missing dependency. Do not silently invent a competing teaching process.

A journey may be `planning`, `active`, `paused`, `completed`, or `superseded`. On resume, read current state and evidence first. Completion requires the destination contract to be met, the evidence recorded, and no material open question that would change the claim.
