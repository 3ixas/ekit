---
name: payments
description: Design, implement, review, or verify payment and subscription flows using current provider documentation and strict money, webhook, and idempotency rules.
---

# Payments

## Outcome

A payment flow whose state transitions, amounts, authorization, recovery, and evidence are correct.

## Method

Model the payment lifecycle and source of truth; represent money exactly; verify raw webhook signatures; make processing idempotent; handle retries, duplicates, refunds, disputes, and subscription transitions; isolate test/live environments; protect keys and sensitive data; verify with provider events.

For Stripe webhook or subscription verification, use [Stripe testing](references/stripe-testing.md) and check current official documentation and installed CLI/SDK versions before choosing commands. Other providers do not load this reference.

## Boundaries

Provider setup, pricing, and production actions require current evidence and authority.
