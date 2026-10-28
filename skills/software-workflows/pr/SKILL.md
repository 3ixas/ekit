---
name: pr
description: "Use when writing a PR body."
metadata:
  credits:
    skill: show-me
    author: Dex Horthy
    organisation: Humanlayer
    url: "https://github.com/humanlayer/skills/blob/main/plugins/show-me/skills/show-me/SKILL.md"
---

Use this template for writing the PR body:

```markdown
## Summary

<one sentence: the problem this solves and what it makes possible>

<diagram, diff-sketch, or tree>

## Evidence

- **Before:** <screenshot/output/failing test run>
  **After:** <screenshot/output/passing test run>

## Merge Danger

**Door:** <one-way or two-way>

<optional: description>

**Blast Radius:** <one-word description>

<optional: potential ramifications of merge>
```

## Sections

Skip all preambles and keep prose brief. Use the user's domain language from `GLOSSARY.md` (or an older `CONTEXT.md`).

### Summary

Open with exactly one sentence on why the change exists: the problem it solves and what becomes possible once it ships.

Then pick the smallest view that makes the key point clear.

- Show logic or an algorithm as pseudocode:

```text
on(save)
  if content is unchanged
    return cached result
  write new content
  return fresh result
```

- Show runtime control flow as a call tree:

```text
submitForm
  createSession
    persistPrompt
    launchAgent
  navigateToSession
```

- Show UI structure as a component tree, including state and module boundaries that matter:

```text
<SessionPage> (apps/example/src/routes/session.tsx)
  useSessionEvents()
  <SessionToolbar>
    <RunSkillButton> (packages/ui)
```

- Show file responsibility or a broad refactor as a shallow file tree:

```text
src/
├── commands/       # parses user actions
├── sessions/       # owns session state
└── transport/      # sends API requests
```

- Show a changed data contract (SQL tables and key columns, endpoint request and response shapes, or a core data structure) trimmed to the fields that matter, as a `diff` when it changes an existing shape:

```diff
 POST /sessions
   request:  { prompt: string }
+  request:  { prompt: string, skill?: string }
   response: { id: string, status: "queued" }
```

- Show component interaction, control flow, or data flow with Mermaid:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant Daemon
    User->>UI: choose command
    UI->>Daemon: send expanded prompt
    Daemon-->>UI: stream result
```

- Use `diff` when the point is what changes and the surrounding shape already exists. Match the diff shape to the topic.

For a component change:

```diff
 <SessionPage>
   useSessionEvents()
   <SessionToolbar>
+    <RunSkillButton />
   <SessionTimeline>
+    <SkillResultCard />
```

For a file-layout change:

```diff
 src/
 ├── commands/
+│   └── show-me.ts       # expands the slash command
 ├── sessions/
-└── transport.ts
+└── transport/
+    ├── client.ts
+    └── stream.ts
```

For a call-tree or call-stack change:

```diff
 submitForm
   createSession
     persistPrompt
+    expandSkillMention
     launchAgent
-  navigateToSession
+  navigateToSession
+    subscribeToEvents
```

For a state or control-flow change:

```diff
 on(save)
-  write content
+  if content is unchanged
+    return cached result
+  write new content
+  invalidate cache
```

- Show the whole block when most of it is new, when omitted context would hide ownership or order, or when the user needs a copyable target shape:

```ts
function expandSkill(command: string): string {
  const skillName = command.slice(1);
  return `use the ${skillName} skill`;
}
```

#### Guidance

Place each visual next to the short text it supports. Keep only the calls, files, props, states, and boundaries needed to answer the user's current question or the options to resolve the current discussion point.

You may use one of these, you may use several, it is unlikely you will use all of them. Use your judgement and don't overwhelm the user.

### Evidence

Concrete evidence that the change works. Show a before and after.

Screenshots are S-tier - when the environment is set up for it and the change is visual.

`gh pr create` and `gh pr comment` cannot upload images, and the GitHub API has no endpoint for them. Attach screenshots in this order:

1. **Browser upload (preferred).** When a browser tool signed in to GitHub is available, open the PR, drag or file-attach the images into a comment box and submit it. GitHub hosts them as durable `user-attachments` URLs. Posting the comment is a publication step, so the delivery caller's authority applies.
2. **Assets branch (fallback).** With no browser, commit the images to a throwaway branch such as `pr-assets/<pr-number>` (never the PR's own branch, the target or the default branch), push it, and link the `raw.githubusercontent.com` URLs from the body. This works for public repositories; in a private one the images do not render for other viewers. Say in the PR that the branch can be deleted after merge.
3. **Preview link.** If neither is possible, link the deployment preview and name the routes and viewports to check, and say the images are not attached.

Check each image for secrets and private information before it is published, and keep the files small.

Execution-based evidence is A-tier. Test results, console output. Show the exact test that now fails and passes, using pseudocode.

### Merge Danger

Describe whether it's a one-way or two-way door. You can walk back through two-way doors, but not one-way doors. A PR that is cheap to roll back is lower risk. Changes that involve destructive actions or hard-to-reverse decisions are one-way doors.

The blast radius is the potential impact or scope of the changes introduced by this PR. Consider all possibilities. Examples are layout shift, breakages for consumers, mobile responsiveness, etc.

## Authorized publication handoff

This skill writes the body; it does not authorize publishing it. Before a delivery caller submits it, check for an existing PR for the exact branch/base, follow the repository template/title conventions, and inspect all text and attachments for secrets and unrelated private details. Include observed proof and honest gaps, preserve human contributor credit, and omit generated-tool attribution. The delivery caller owns submission, returned-URL verification, chat attachment where available, and subsequent CI/review monitoring.

## Credits

The Summary visuals come from Dex Horthy's `show-me` skill; see [credits](references/credits.md).
