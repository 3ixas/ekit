# Technical Writing

Technical writing helps a specific reader understand, operate, evaluate, or change a system.

## Choose the reader’s task

- **Explanation:** Build an accurate mental model and show why it matters.
- **How-to:** Start from a concrete goal, state prerequisites, give executable steps, and verify the result.
- **Reference:** Make exact facts easy to locate; define inputs, outputs, defaults, errors, and constraints.
- **Proposal or decision:** State the problem, constraints, options, recommendation, consequences, and unresolved risks.
- **Incident or investigation:** Separate timeline and observed evidence from hypotheses, contributing conditions, impact, and follow-up.

Do not blend these forms merely to appear comprehensive. Put the reader’s likely entry point first.

## Accuracy contract

Preserve code, commands, identifiers, interfaces, paths, error messages, and quoted output exactly. Test commands and examples when the environment permits. Label illustrative pseudocode. State version or platform boundaries that change behavior. Link to canonical sources rather than paraphrasing unstable details from memory.

## Clarity

Explain the system as a knowledgeable colleague would, adjusting formality to the reader and purpose. Prefer a familiar verb when it communicates the same distinction; retain specialised terms and precise verbs when they explain actual behaviour or responsibility. Avoid making a component or abstraction sound purposeful merely to create a punchy sentence, and avoid turning a local design choice into a general principle. System subjects are useful when they accurately describe what the system does.

Introduce a term when it reduces ambiguity, then use it consistently. Explain causal relationships and tradeoffs in plain language. Keep background proportional to the task. Use diagrams, tables, examples, or headings only when they reduce the reader’s effort.

A finished procedural document includes an observable success condition and the likely recovery path for material failure modes.
