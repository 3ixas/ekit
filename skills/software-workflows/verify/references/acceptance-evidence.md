# Acceptance evidence

## Build a claim-to-proof matrix

Turn each material acceptance statement into an observable claim. For each claim, choose the closest real surface and record the setup, action, expected result, observed result, and status: Pass, Fail, or Skip. Include state changes and side effects, not only the immediate response.

Use the strongest practical surface:

- browser or simulator for user flows, layout, focus, navigation, and accessibility;
- API or CLI for contracts, errors, and automation behavior;
- database or event inspection for persistence and state transitions;
- rendered document or artifact for visual and structural output;
- targeted automated test for deterministic logic and regression coverage.

A build proves that code compiles. A unit test proves its asserted case. Neither alone proves the integrated user path.

## Control the test

Verify the revision or working tree actually under review. Record relevant environment, fixtures, accounts, flags, and permissions without exposing secrets. Start from a known state and include negative, boundary, and repeat-action cases when they are material. For visual parity, compare against a stable reference at relevant viewport sizes and interaction states.

Separate three outcomes:

- product failure: the behavior contradicts the claim;
- harness failure: the proving mechanism is broken or inaccessible;
- environmental limitation: required state or service is unavailable.

Do not convert either of the latter two to Pass.

## Finish at exact head

After integration or a fix, rerun every check whose inputs changed. Record the exact revision when possible and inspect the final diff for unverified changes. Summarize evidence by claim and call out skipped surfaces. Screenshots and logs support a claim only when their origin and state are clear.
