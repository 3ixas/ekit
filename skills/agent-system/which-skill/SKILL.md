---
name: which-skill
description: "Use only when Elias explicitly asks which EKit skill to use for a task, whether this thread is using the right skill, what skills changed since a date, or invokes which-skill directly. Do not select for ordinary task requests that belong to an owning skill."
argument-hint: "What task, current thread, or date are you asking about?"
---

Explicit means user-requested. Ordinary language and dictation count; slash/dollar syntax is optional. Load only when Elias asks which EKit skill fits a task, whether this thread is using the right skill or missed one, what skills changed since a date, or invokes `which-skill` directly. Discussion, quoted mentions, negation, and ordinary task requests do not invoke it. Loading this skill grants no action authority.

## Grounding

Read [the Skill catalogue](references/skill-catalogue.md) before answering. Do not inspect the EKit repository live at answer time, and do not answer from memory alone.

- Recommend **active skills only** (everything listed in the catalogue is active; never recommend candidate or paused skills).
- Cross-check the host's loaded skill listing against the catalogue. If the skill you would recommend is missing from the host's loaded skills, or the loaded listing disagrees with the catalogue, report that mismatch plainly (noting a likely sync gap) instead of recommending a missing skill as ready to run.
- Keep general browsing with the activation manifest; answer only the three questions below.

## 1. Upfront recommendation ("which skill should I use for X?")

Select one owning skill from the catalogue and answer in this exact shape:

```text
Owner: <skill>, <why it fits>
Brings in: <supporting skills, or none>
Say: "<exact invocation phrase>"
Stops at: <authority stop, or "works locally">
Also worth naming: <explicit-only skill and condition>
```

Rules for each line (keep labels plain, without bold formatting):

- `Owner`: the exact active skill id from the catalogue, followed by a comma and a concise explanation of why it fits so Elias learns the distinction. A skill the request asks to use by name (such as "Use Grilling to…") is the owner even when a sibling's description also fits; say in the explanation when the sibling would suit better. A quoted or negated name is not a request. An explicit-only skill is the owner only when the request itself asks for what it does: it names the workflow, or states the situation its catalogue description opens with (for example one identified ticket, an approved graph, a named PR to babysit). Changing a file in a repository, including a prose fix in its docs, is a software slice for `implement`; `writing` owns prose work that is not a repository change, such as emails, essays, posts and drafts. Otherwise the owner is the automatic skill that handles the work, and the explicit-only skill goes on `Also worth naming` (for example `debug` for a bug that keeps failing, with `hill-climb` named).
- `Brings in`: the supporting skills the owner will bring in for this request, chosen from the owner's catalogue `Brings in` column plus any specialist the request clearly needs, or `none`.
- `Say`: a concise natural-language phrase Elias can say to invoke that owner (teaching the trigger wording, especially for explicit-only workflows).
- `Stops at`: when the catalogue declares an `authority_stop` for the owner, restate it close to verbatim, in the catalogue's own words: what the owner may do without asking and what still needs separate authority. When the request sets a narrower endpoint (for example a local commit only), state that endpoint first and then still give the catalogue's limits. Trim clauses that plainly do not apply to the request, but never reduce it to the owner's outcome (such as "an open PR ready to merge") or paraphrase it into a few words. When the catalogue says `No external side effects`, write `works locally`.
- `Also worth naming`: include this line **only** when an explicit-only workflow genuinely applies to the request, naming the skill and the condition under which to use it. Omit the line completely when no explicit-only skill applies.

End every upfront recommendation with a short offer to start the owner (for example, `Want me to start <skill>?`) without starting it.

### Ambiguity

When the request leaves a deciding fact unstated and could reasonably go two ways, do not guess one branch — show both branches (at most two blocks in the shape above), each led by the concrete fact that decides between them (for example: `If the cause is unknown:` → `debug`; `If the exact change is already known:` → `implement`). Ask a clarifying question **only** when neither branch is safe to start without Elias's answer.

### No fit

When no active skill genuinely owns the request, say plainly in one line that no skill applies and to ask normally. Never stretch the nearest skill over an unmatched request. If the request looks recurring, suggest `skill-review` to assess whether it earns a new skill.

## 2. Mid-task check ("is this thread using the right skill?")

Judge from the current conversation:

1. Name the thread's **current owner** first (or state plainly that no skill currently owns the thread).
2. If the current owner still fits, say so briefly and note any missed supporting skill or applicable explicit-only workflow.
3. If another active skill fits the remaining work better, give a recommendation block in the shape above for that owner.

## 3. What changed since `<date>`?

Filter active skills in the catalogue whose `Added` or `Reviewed` date is on or after `<date>` (ISO `YYYY-MM-DD`):

- **Added:** active skills with `Added >= <date>`.
- **Revised:** active skills with `Added < <date>` and `Reviewed >= <date>`.
- If nothing matches, say so plainly.
- Always include a freshness note naming the catalogue's `Generated` date and stating that the answer is as fresh as the last EKit sync (it does not require a local checkout).

## Starting the owner

Advise first, then offer to start the recommended owner. Never start the owner or execute work automatically — start it **only** on Elias's yes. A recommendation grants no authority: explicit-only workflows and any skill with external side effects (merging, publishing, deploying, sending, deleting, or changing external state) still wait for Elias's own explicit words authorizing that workflow.
