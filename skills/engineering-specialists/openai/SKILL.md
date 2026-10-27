---
name: openai
description: Build or troubleshoot OpenAI API and agent features using current official documentation, safe credential checks, explicit tool boundaries, and meaningful evaluation.
---

# Openai

## Outcome

An implementation grounded in the current API with validated configuration and honest model-output evidence.

## Method

Inspect installed SDK and project architecture; consult official OpenAI docs for current models and APIs; centralize prompts and schemas; validate configuration at boot; separate deterministic checks from live-model evaluations; test positive, negative, and repeated cases; preserve raw outcomes and uncertainty; never print keys.

Done when configuration and deterministic checks pass, the evaluation report separates observed model outcomes from expectations, and unavailable live cases are named.

## Boundaries

Do not pin volatile API facts in this skill or treat stochastic output as deterministic correctness.
