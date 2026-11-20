---
name: research
description: Investigate a question against high-trust primary sources and answer it, saving the cited findings as a Markdown note when working in a repository. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Route the research by what it reads, as the Roles section of the shared instructions sets out: research into a repository or its own documentation runs as a fresh Engineer child at `medium` (in an Engineer thread, in-thread); research that needs the web goes to Codex. Run the agent in the **background** when the host supports it, so independent work can continue while it reads. If the chosen agent is unavailable, perform the same investigation directly and disclose that limitation.

Pick the method for the kind of question from [research modes](references/research-modes.md): a current fact, a recommendation, repository or skill discovery, or recent practitioner evidence.

Its job:

1. Investigate the question against **primary sources** (official docs, source code, specs, first-party APIs), not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single Markdown file, citing each claim's source.
3. Inside a repository, save it where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible. Outside a repository, return the findings instead of saving them.

When the agent finishes, read its findings and check the sources behind the main claims. Then reply with the answer in a few sentences, the confidence it deserves, and the note's path when one was saved. Outside a repository, offer to save the note.

## Owned source methods

These snapshots preserve the reviewed upstream methods. Open one only for a specific method the task needs; the owned steps above govern routing, authority, and completion. Upstream plugin paths and host instructions are historical context, not additional dependencies.

- [pstack-figure-it-out](references/source-methods/source-2-figure-it-out.md)
