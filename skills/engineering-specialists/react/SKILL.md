---
name: react
description: Build or review React components, composition, state, effects, accessibility, and performance using the project's version and architecture.
---

# React

## Outcome

React code with clear ownership, stable component APIs, and measured rendering behaviour.

## Method

Inspect framework and versions; prefer composition over boolean-prop matrices; let live call sites, not stories, tests, or mocks, define each component's prop contract, so props every live caller supplies are required, unused props are removed, and support code adapts to the contract (Dex Horthy); keep state close to ownership; use effects only for synchronization; preserve server/client boundaries where applicable; when a task needs a library, prefer what the project already installs, otherwise start from [Emil Kowalski's curated picks](references/source-methods/emil-pick-ui-library.md) and say when you leave that list; measure performance; test user behaviour and accessibility.

## Boundaries

Do not apply framework advice without checking the repository or duplicate design decisions owned by interface-design.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [vercel-react](references/source-methods/vercel-react.md)
- [source-2-skill](references/source-methods/source-2-skill.md)
