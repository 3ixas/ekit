# Evaluation validity

Use before a score decides which change to retain. Reuse the project's harness and evidence; scale these checks to the consequence and cost of a wrong decision.

## Establish what the score measures

Name the intended outcome, the measured quantity, the smallest useful gain and the behaviours that must not regress. Label a proxy explicitly and confirm the selected result on the real outcome before claiming that outcome improved. A model rating can inform a critique; it does not establish functional correctness or user benefit.

Exercise the same path that the result will claim. For agent instructions, distinguish direct injection from host discovery and tool execution. Confirm that the relevant instruction, tool or mechanism is actually reached. A build or source inspection cannot prove runtime behaviour.

## Check the measurement before tuning

- Inspect representative raw results and failure evidence. Recompute the reported aggregate from the underlying observations, preserving the case count and denominator. Separate product failures, harness/grader failures, timeouts and unavailable environments; report incomplete coverage instead of silently dropping failed cases or changing the denominator.
- Where sensitivity is uncertain, use a safe disposable known regression and a known improvement to check that the measurement moves in the right direction. Inspect the assertion and grading criteria, not just a reach marker. Do not damage the user's working artifact to test sensitivity.
- For variable results, estimate no-change variation under comparable conditions. Use paired baseline/candidate runs or repetitions when warranted. If a useful gain is smaller than the variation the available sample can resolve, report inconclusive; propose better measurement or additional budget rather than choosing the lucky result.
- Pin cases, expected outputs, grader, aggregation, relevant dependencies and environment. A material change to those conditions invalidates the comparison: review the change and establish a new baseline. Never weaken a check to retain a candidate.

## Preserve the evidence boundary

Keep diagnostic cases separate from final confirmation cases where overfitting is plausible. Do not expose held-out answers or traces to the change proposer. Local files in the same readable workspace are not structurally hidden: report that limitation. Repeatedly consulting a confirmation result to choose changes turns it into tuning evidence; obtain fresh confirmation before making a generalisation claim.

For model evaluations, retain each output/transcript with the grade from that same execution, the actual model/configuration and available usage. Include failed calls, retries and judges in accounting; do not rerun a model merely to recreate missing evidence. Re-grade stored outputs when only the grader changes, while re-baselining the comparison under the corrected grader. Keep raw evidence outside the instruction context and read only the cases needed for the hypothesis.

Report measured change, preservation checks, measurement limitations and unexecuted confirmation separately. An invalid or interrupted evaluation cannot establish a win.
