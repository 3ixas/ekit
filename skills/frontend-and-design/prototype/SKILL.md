---
name: prototype
description: Build a throwaway prototype to answer a design question. Use when the user wants to sanity-check whether a state model or logic feels right, or explore what a UI should look like.
---

# Prototype

A prototype is **throwaway code that answers a question**. The question decides the shape.

## Pick a branch

Before building, name the decision and the uncertainty the prototype must retire, and pick the cheapest form that can answer it; see [prototype experiments](references/prototype-experiments.md), which also covers comparing variants fairly.


Identify which question is being answered, using the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"** → [LOGIC.md](references/source-companions/LOGIC.md). Build a single shareable HTML file (free-play buttons plus tabbed guided walkthroughs) that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"** → [UI.md](references/source-companions/UI.md). Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar. Each variant diverges on an axis you can name in a phrase (layout, density, personality, motion, or interaction model), fully works with realistic content, and never touches production code until one is chosen (Emil Kowalski).

The two branches produce very different artifacts, so getting this wrong wastes the whole prototype. If the question is genuinely ambiguous and the user isn't reachable, default to whichever branch better matches the surrounding code (a backend module → logic; a page or component → UI) and state the assumption at the top of the prototype.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.** Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious, but name it so a casual reader can see it's a prototype, not production. For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.** A UI prototype starts from one command in the project's task runner: `pnpm <name>`, `python <path>`, `bun <path>`, etc. A logic demo is a single HTML file the user double-clicks. Either way, no thinking required to start it.
3. **No persistence by default.** State lives in memory. Persistence is the thing the prototype is _checking_, not something it should depend on. If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE, wipe me" name.
4. **Skip the polish.** No tests, no error handling beyond what makes the prototype _runnable_, no abstractions. The point is to learn something fast.
5. **Surface the state.** After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Capture it when done.** Record the verdict, evidence and remaining uncertainty. Carry the validated decision into production through the owning implementation workflow and current task scope. Preserve the prototype as a **primary source** on a throwaway branch, out of main, when a local commit is authorized; leave an implementation-issue pointer only when that external write is authorized. Otherwise include the local path and handoff text in the response. The main branch keeps only the validated decision.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [source-2-skill](references/source-methods/source-2-skill.md)
- [emil-prototype](references/source-methods/emil-prototype.md): a fixed picker harness for flipping between live UI variants and promoting the winner.
- [source-4-arena](references/source-methods/source-4-arena.md)
