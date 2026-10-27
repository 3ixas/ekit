---
name: code-review
description: "Review a branch, PR, or staged/working-tree diff from a fixed point along independent Standards and Spec axes. Automatically choose regular or deep structural review from the change; honour explicit regular, deep structural review, or thermonuclear review requests. Runs parallel reviewers and reports each axis separately."
---

Two-axis review of the diff between the current checkout and a fixed point the user supplies:

- **Standards**: does the code conform to this repo's documented coding standards?
- **Spec**: does the code faithfully implement the originating issue / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context, then this skill aggregates their findings.

Read the repository tracker configuration. If `docs/agents/issue-tracker.md` is missing, use the most efficient supported tracker capability available on this host; prefer `gh`/`gh api` for structured GitHub state, and report when no tracker is configured.

**When another skill calls this one.** `implement`, `implement-spec`, and other pipelines run this review unattended and pass the fixed point, the staged paths or diff, the spec pointer, and, when they have one, a proof plan mapping each acceptance claim to a check with its observed result. In that mode never ask the user anything: use what was supplied, and if the spec is missing, skip the Spec sub-agent and report "no spec available".

Review is read-only at either depth: report findings without editing or committing. The calling workflow owns fixes and re-review; depth does not grant wider implementation authority. `implement` supplies one slice; `implement-spec` supplies the integrated feature. Judge the supplied scope, without adding review stages, another coordinator, or model/reasoning overrides.

For repeated implementation/delivery review, the caller uses [bounded review-loop controls](references/review-loop.md). Return stable finding IDs and the reviewed snapshot so later rounds can focus on changes and unresolved findings without losing either axis. A standalone review remains one read-only pass.

## Process

### 1. Pin the fixed point

Whatever the user said is the fixed point (a commit SHA, branch name, tag, `main`, `HEAD~5`, etc.). If they didn't specify one, ask for it. The fixed point may be the commit immediately before an uncommitted slice.

Resolve the fixed point with `git rev-parse <fixed-point>`. If the checkout is clean, capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`. If the caller requests an exact staged-slice review, capture `git diff --cached <fixed-point>`, `git diff --cached --name-status <fixed-point>`, and `git status --short`; this includes staged new files and excludes unrelated unstaged work. If the user instead asks for all staged and unstaged work, capture `git diff <fixed-point>` and status, and read any untracked files that belong to the slice. An untracked file cannot be recovered from a diff, so require it to be staged as part of an exact slice or inspect its full contents explicitly. Do not silently review a moving branch or unrelated working-tree changes.

Before going further, confirm the fixed point resolves and the selected diff is non-empty. A bad ref or empty diff should fail here, not inside two parallel sub-agents.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in the commit messages (`#123`, `Closes #45`, GitLab `!67`, etc.), fetched via the workflow in `docs/agents/issue-tracker.md`.
2. A path the user passed as an argument.
3. A spec file under `docs/`, `specs/`, or `.scratch/` matching the branch name or feature.
4. If nothing is found, ask the user where the spec is. If they say there isn't one, the **Spec** sub-agent will skip and report "no spec available".

### 3. Identify the standards sources

Anything in the repo that documents how code should be written, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.

On top of whatever the repo documents, the Standards axis always carries the **smell baseline** below: a fixed set of Fowler code smells (_Refactoring_, ch.3) that applies even when a repo documents nothing. Two rules bind it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress the smell.
- **Always a judgement call.** Each smell is a labelled heuristic ("possible Feature Envy"), never a hard violation. Like any standard here, skip anything tooling already enforces.

Each smell reads *what it is* → *how to fix*; match it against the diff:

- **Mysterious Name**: a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code**: the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy**: a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps**: the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession**: a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches**: the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery**: one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change**: one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality**: abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains**: long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man**: a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest**: a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

### 4. Select review depth

Inspect the pinned diff, relevant surrounding code and callers, and available requirements. Choose depth automatically unless the user or caller explicitly constrained it; unattended calls also choose automatically.

- **Regular** is the default for local, cohesive changes with straightforward structure and ownership.
- **Deep** is warranted by material changes to responsibilities, state modelling, or cross-layer coordination; related conditions scattered across multiple places; or a concrete opportunity to remove substantial complexity that needs investigation. Read [deep structural review](references/deep-structural-review.md) when selecting deep, including explicit "deep structural review" or "thermonuclear review" requests.
- File length and diff size alone do not select deep. Security or performance concerns load the relevant specialist when needed; those concerns alone do not require structural redesign.
- State "Review depth: regular/deep — <reason grounded in this change>" before the reports. Proceed within the requested review scope without asking permission. An explicit regular-only constraint wins; recommend a deeper follow-up if warranted.

The Standards reviewer may escalate regular to deep when new evidence warrants it, unless depth was explicitly constrained. It reads the linked reference and returns the revised depth and reason for the coordinator to report. Inspect adjacent code to support findings, but keep findings tied to the selected change. If useful investigation exceeds that scope, state what remains unreviewed and recommend a concrete invocation, such as `On the <branch> checkout, use code-review against <base> for a deep structural review including <broader area>`; do not silently expand the review.

At either depth, supplement the smell baseline with these structural checks:

- Avoidable branching, flags, or wrappers; unclear type contracts; responsibility leaking across layers; and duplication of canonical utilities. Show the practical cost and a concrete simpler shape before raising a finding.
- Size, casts, and optionality are signals to investigate, not violations on their own. A file crossing 1,000 lines is not a blocker without a demonstrated problem or an applicable documented rule.
- Distinguish **demonstrated regressions** from **optional improvements**. A plausible alternative design alone does not block approval. Structural findings identify the affected file/hunk, evidence, consequence, and remedy. Keep concrete optional proposals separate from blocking findings and omit speculative or cosmetic advice.

When a change affects shared state, persistence, background work or a potentially large input, establish the expected deployment and workload from project evidence before judging scale. Check whether process-local state, check-then-write sequences, unbounded growth or repeated per-item work can fail there. State any material assumption, tie findings to a concrete failure case, and keep hypothetical future scale separate from demonstrated regressions.

### 5. Spawn both sub-agents in parallel

**Standards sub-agent prompt** should include:

- The exact diff command, working-tree status when relevant, and commit list. For a staged-slice review, use only the supplied staged paths and fixed point.
- The list of standards-source files you found in step 3, **plus the smell baseline from step 3** pasted in full (the sub-agent has no other access to it).
- The selected depth, reason, any explicit depth constraint, and all step 4 structural checks and scope boundaries. For deep review, include the linked reference's contents; otherwise supply its path so the reviewer can read it if escalation is justified. Keep the model and reasoning selected for the calling run.
- When step 4's workload check applies, include the expected deployment and workload evidence or material assumptions, and its checks for process-local state, check-then-write races, unbounded growth and repeated per-item work. Keep hypothetical future scale separate from demonstrated regressions.
- The brief: "Report, per file/hunk where relevant, (a) every place the diff violates a documented standard: cite the standard (file + the rule); and (b) concrete baseline smells or structural problems: label the heuristic and quote the hunk. Explain practical consequences and a concrete remedy. Distinguish documented violations, demonstrated regressions, and optional improvements; a documented repo standard overrides the baseline. Skip anything tooling enforces. Return final depth and reason, including any escalation. Keep the report under 400 words; prioritize material findings and state any coverage limit rather than silently omitting them."

**Spec sub-agent prompt** should include:

- The exact diff command, working-tree status when relevant, and commit list. For a staged-slice review, use only the supplied staged paths and fixed point.
- The path or fetched contents of the spec.
- The caller's proof plan with observed results, when supplied.
- The brief: "Report: (a) requirements the spec asked for that are missing or partial; (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look implemented but where the implementation looks wrong; (d) when a proof plan is supplied, acceptance claims with no proof, a Fail or Skip result, or proof that does not exercise the claim (a test that asserts its own mock, a check on the wrong surface, a build standing in for behaviour). Quote the spec line for each finding. Under 400 words."

If the spec is missing, skip the Spec sub-agent and note this in the final report.

### 6. Aggregate

Present the final depth and reason, then the two reports under `## Standards` and `## Spec` headings, verbatim or lightly cleaned. Within Standards, distinguish blocking findings from optional structural improvements; no optional suggestion changes an otherwise clear review outcome. Do **not** merge or rerank findings across axes, because the two axes are deliberately separate (see _Why two axes_).

End with a one-line summary: blocking findings and optional suggestions per axis, and the worst issue _within each axis_ (if any). Don't pick a single winner across axes: that's the reranking the separation exists to prevent. Preserve any scope limitations and concrete follow-up invocation in the report, including unattended calls; the calling workflow applies its existing scope-decision boundary.

## Why two axes

A change can pass one axis and fail the other:

- Code that follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Code that does exactly what the issue asked but breaks the project's conventions → **Spec pass, Standards fail.**

Reporting them separately stops one axis from masking the other.

## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [pstack-show-me-your-work](references/source-methods/pstack-show-me-your-work.md)
- [compound-code-review](references/source-methods/compound-code-review.md)
- [trailofbits-differential-review](references/source-methods/trailofbits-differential-review.md)
