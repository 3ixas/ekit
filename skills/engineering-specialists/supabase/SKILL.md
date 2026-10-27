---
name: supabase
description: Operate Supabase projects across migrations, Auth, row-level security, Storage, Edge Functions, logs, and local or remote tooling.
---

# Supabase

## Outcome

A verified Supabase change against the intended project and environment.

## Method

Confirm project and local/remote target; inspect current schema and policies; make migrations source-controlled; test RLS by actor; preserve auth and storage boundaries; use logs and official docs; preview mutations and re-read results.

## Boundaries

Supabase does not select itself as the backend. Never infer a production target from local configuration.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [supabase-platform](references/source-methods/supabase-platform.md)
