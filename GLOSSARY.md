# EKit

The vocabulary for managing Elias's owned skills and the upstream sources they draw from.

## Language

**EKit**:
Elias's canonical personal collection of agent skills, shared instructions, and supporting tools. It is the collection used in his daily setup, including its maintained public source.
_Avoid_: Public mirror, showcase, second maintained collection

**Disposition**:
The decision recorded in an assessment about what happens to one upstream entry: merge, own, candidate, defer, or reject.
_Avoid_: Adoption, status

**Adopted**:
A merge or own disposition that has landed in an owned bundle and is cited as a source in that bundle's `metadata.json`. A disposition without that citation is not adopted.
_Avoid_: Merged (when only decided), done

**Source method**:
A pinned snapshot of an upstream method kept in an owned skill's references, opened only when the task needs that specific method.
_Avoid_: Vendored skill, copy

**Options round**:
A grilling round that answers a generative or taste decision by showing three concrete options side by side, each diverging on a named axis, one of them a stretch option, with a recommendation; the user picks, combines, or rejects all, and the choice seeds the next, more concrete round.
_Avoid_: Variants round, menu, A/B

**Stretch option**:
The bolder of an options round's three options, one the user is unlikely to have considered, included to widen the range rather than to be chosen by default. Omitted, with the reason stated, when the decision is too narrow for one.
_Avoid_: Wildcard, crazy idea

**Exploration trail**:
The record of an options round sequence kept in the phase's durable document: for each round, the options and their axes, the choice, and why the others lost.
_Avoid_: History, log

**Public baseline**:
The reviewed version of Elias's personal skill collection selected as the starting point of its public history. It excludes the original private development history.
_Avoid_: Full-history publication, public export (when implying a second maintained collection)

**Private archive**:
The preserved original skill-repository history and associated records retained outside the public baseline. It remains private recovery and reference material.
_Avoid_: Public backup branch, discarded history

**Lead**:
The role that owns judgement-heavy and open-ended work: orchestrating ticket graphs, grilling, specs, tickets, diagnosing bugs of unknown cause, long interactive sessions, and reviewing an Engineer's work. The role table names the model that fills it.
_Avoid_: Main model, orchestrator model, Opus (when meaning the role)

**Engineer**:
The role that owns bounded work against an approved brief: implementing approved tickets, reviewing a Lead's work, and exploring a codebase to answer a defined question. It escalates to the Lead rather than settling an open decision. The role table names the model that fills it.
_Avoid_: Worker model, cheap model, Neon (when meaning the role)

**Role table**:
The single mapping from each role to the provider, model and reasoning level that fill it, plus the fallback when that provider is unavailable. Skills name roles, never models.
_Avoid_: Model routing (when meaning the mapping), model config

**Escalation**:
An Engineer handing a ticket back to the Lead because it reached a decision the approved brief does not settle, or failed review twice on the same issue, with its branch and evidence preserved.
_Avoid_: Fallback (that is the provider-unavailable path), bail-out

**Routing outcome**:
The one-line record a run leaves of how its routing played out: which role and model implemented, which role reviewed, how many review findings were raised and accepted, any rework, or the cause of an escalation. The run writes it; Elias never does.
_Avoid_: Metric, score, evaluation

**Routing review**:
The Lead's reading of all routing outcomes since the last review, done when a model in the role table gets a new version or when Elias asks. It ends in proposed role-table changes that Elias accepts or rejects.
_Avoid_: Evaluation programme, trial, benchmark
