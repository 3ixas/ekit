# Three-phase defence

This is a conversational learning check grounded in the actual change. Inspect the diff, specification, tests, and relevant context before beginning. Ask one question at a time and wait for Elias's answer. Adapt the next question to what he demonstrates.

## Phase 1: Explain

Establish whether Elias can reconstruct the change:

- the problem and before/after behavior;
- the end-to-end path through the code;
- the important types, state, interfaces, and invariants;
- why each consequential implementation choice was made;
- what the tests and verification actually prove.

When an answer is incomplete, first give a small hint and invite another attempt. If the gap remains, teach the specific point using the code, then ask a fresh check question. Do not turn trivia, syntax recall, or file names into the measure of understanding.

## Phase 2: Challenge

Probe the judgment behind the work:

- strongest alternative and its tradeoff;
- boundary and failure cases;
- security, concurrency, migration, or operability where relevant;
- assumptions the design relies on;
- likely reviewer objection;
- what evidence would disprove the current conclusion.

If this reveals a real defect or missing evidence, pause the defence and report the evidence. Use verification or implementation only within the current task's authority; on a defend-only request, ask whether Elias wants a correction. Resume after the authorized work is corrected. If it reveals a larger learning gap, explain it briefly and offer the owned `learn` workflow for deliberate study.

## Phase 3: Defend

Ask Elias to give a concise reviewer-facing defence covering:

1. what changed and why;
2. why this design fits the constraints;
3. how the important behavior was proved;
4. risks, limits, and follow-up work.

Give direct feedback on accuracy, clarity, and unsupported claims. Finish when he can defend the work in his own words. This is not a score, approval gate, or substitute for code review.
