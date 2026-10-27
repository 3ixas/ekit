---
name: api-design
description: Design HTTP, RPC, event, webhook, or public module contracts around consumers, compatibility, errors, idempotency, and boundary evidence.
---

# API Design

## Outcome

A usable contract with explicit semantics and an evolution path.

## Method

Identify consumers and access patterns; define names, inputs, outputs, errors, pagination, idempotency, versioning, and observability; validate before mutation; distinguish partial from total results; test public import/wire behaviour; assess Hyrum effects and migration needs.

Done when the consumer-facing contract and compatibility decisions are recorded, with a successful request/import and the relevant invalid, duplicate, or partial-result cases checked or explicitly unverified.

## Boundaries

Internal structural ownership stays with architecture; domain concepts stay with domain-modeling.
