---
name: observability
description: Design or improve production logs, metrics, traces, service objectives, alerts, and runbooks when operating evidence matters.
---

# Observability

## Outcome

Signals tied to user-visible failure modes and actionable operational decisions.

## Method

Start from critical journeys and failure modes; choose structured logs, RED or domain metrics, traces, SLOs, and symptom-based alerts; preserve correlation and privacy; verify signals in the real environment; add runbook actions and ownership; load OpenTelemetry detail only when selected.

Done when a representative event can be followed through the selected signals, each alert has an owner and runbook action, and unavailable environment checks are listed.

## Boundaries

Do not add telemetry infrastructure to every small app or collect sensitive data without a purpose.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [addy-observability](references/source-methods/addy-observability.md)
