# Learning journey templates

Use these as small starting points. Keep only sections that carry decisions or evidence.

## `MISSION.md`

```md
# Mission: {journey}

## Why
{The real-world reason this journey matters.}

## Constraints
- {time, access, preferences, or other boundaries}
```

## `DESTINATION.md`

```md
# Destination: {outcome}

## Independent outcome
{What Elias can do without the teaching workflow's help.}

## Evidence of completion
- {observable performance}

## Out of scope
- {explicit boundary}
```

## `ROADMAP.md`

```md
# Roadmap

## Capability areas
| Area | Status | Evidence or next decision |
|---|---|---|
| {area} | proposed / active / blocked / complete | {short note} |

## Horizon
- Active track: {track and bounded outcome}
- Next proposal: {track and rationale}
- Later hypotheses: {areas not yet planned}
```

## `STATE.md`

```md
# Journey state

- Lifecycle: planning / active / paused / completed / superseded
- Active track: {track-id or none}
- Last boundary: {date and short result}
- Next action: {one bounded action}
- Open decision: {none or link to OPEN-QUESTIONS.md}
```

## `LEARNER.md`

```md
# Learner context

## Known baseline
- {capability or prior knowledge — demonstrated with evidence link, or self-reported and unverified}

## Preferences and constraints
- {how to teach, available practice, support limits}

## Current support needs and misconceptions
- {only those relevant to the active or next track; link evidence when observed}
```

## `SOURCES.md`

```md
# Sources

- [{source}]({url}) — {what it covers and when to use it}

## Gaps
- {missing or disputed source area}
```

## `REVIEWS.md`

```md
# Route reviews

## {date} — {track or route}
- Evidence: {independent performance and assistance used}
- Decision: continue / split / contract / promote / pause / change destination
- Rationale: {why}
- Next: {bounded next action}
```

## `REVIEW-QUEUE.md`

```md
# Review queue

Warm-up retrieval at the start of each session. Pick the due items, ask without notes, then reschedule: after a clean unaided recall, roughly double the interval (1 → 3 → 7 → 14 → 30 → 60 days); after a miss, reset it to 1 day.

| Item | Source | Last result | Interval | Next due |
|---|---|---|---|---|
| {prompt or exercise to recall} | {lesson, reference, or track link} | new / clean / assisted / missed | {days} | {YYYY-MM-DD} |
```

## `tracks/{track-id}/BRIEF.md`

```md
# Track: {bounded capability}

- Destination: {link or short statement}
- Outcome: {one observable capability}
- Baseline: {what is already demonstrated}
- Prerequisites: {known gaps}
- Sources: {links or link to SOURCES.md}
- Practice context: {where the capability will be used}
- Evidence target: {what independent performance looks like}
- Allowed support: {what may be consulted during practice}
- Status: proposed / active / blocked / complete / paused
```

## `EVIDENCE/{date}-{track-id}.md`

```md
# Evidence: {track} — {date}

- Outcome tested: {track outcome}
- Attempt or artifact: {link to the actual work or feedback, or a concise observation when no artifact exists}
- Conditions: {task and context, date, novelty where relevant, and allowed support}
- Independent result: {what Elias did without teaching assistance, or none yet}
- Assisted practice: {what was done and the highest assistance rung used, per the handoff contract}
- Feedback: {who or what assessed the result, with a link if external; or none}
- Remaining gap: {unknown, misconception, or prerequisite}
- Claim and decision: {what this evidence supports, what remains uncertain, and continue / promote / contract / pause}
- Next step: {one bounded action}
```
