---
name: doc-review
description: Review requirements, plans, or specs with role-specific lenses. Use when the user wants to improve an existing planning document.
---

# Document Review

## Outcome

A planning document improved by independent, evidenced findings: safe fixes applied, real decisions put to Elias, and everything else noted.

## Method

1. **Read the document whole**, plus the evidence it rests on: linked specs, the code or product it describes, `GLOSSARY.md`, and decisions it cites. Name the document type (requirements, plan, spec, decision record, design).
2. **Choose the lenses.** Always run **coherence** and **feasibility**. Add each conditional lens whose signals the document shows, using [the lenses](references/lenses.md). Tell Elias which lenses will run and why each conditional one applies.
3. **Review each lens independently.** Use one read-only subagent per lens when the host supports them, otherwise separate passes. A lens sees the document and evidence, not the other lenses' findings. Each finding states what is wrong, where (section or line), the evidence, why it matters, and a concrete fix.
4. **Synthesize.** Merge duplicates and drop findings that do not survive a check against the document and evidence. Rank by consequence, then sort each into one tier:
   - **Apply**: unambiguous, mechanical fixes that change no decision (broken references, contradictions with one obvious resolution, missing cross-links, terminology that conflicts with `GLOSSARY.md`).
   - **Decide**: anything that changes scope, behaviour, priority, or a trade-off. These are Elias's calls.
   - **FYI**: valid but low-value observations.
5. **Apply and walk through.** Apply the **Apply** tier and list each change. Put the **Decide** tier to Elias as a `grilling` round: one numbered question per decision, each with your recommendation. Use an options round when a decision has several genuinely different resolutions. Apply the answers, then list the **FYI** tier briefly.

When run with no one to answer, as part of a pipeline, apply only the **Apply** tier and return **Decide** and **FYI** as structured text for the caller.

## Boundaries

Review the document's content, not its prose style; `writing` owns style. Do not expand scope by adding requirements a lens wishes existed; raise them as **Decide** findings. Preserve resolved decisions unless new evidence contradicts their factual basis, then raise a **Decide** finding rather than silently replacing them. Do not edit a document Elias does not own; report findings instead.
