---
name: postgres
description: Design and improve PostgreSQL schemas, queries, indexes, transactions, connections, row security, and migrations using workload evidence.
---

# Postgres

## Outcome

A correct data model and measured database behaviour for the actual access patterns.

## Method

Model invariants and access patterns; choose constraints and types; inspect query plans before indexing; preserve transaction boundaries; control connection pressure; make RLS and privilege assumptions explicit; use compatible migration stages; measure after changes.

Done when the affected invariants and actor permissions are checked, and query or migration changes have comparable before/after evidence or an explicit verification limit.

## Boundaries

Do not cargo-cult indexes or apply Supabase-specific behaviour to every PostgreSQL system.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [supabase-postgres](references/source-methods/supabase-postgres.md)
