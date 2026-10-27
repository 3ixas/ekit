# FlowSavvy live-operation contract

## Read before deciding

- Query the current connector schema and account configuration; do not rely on old registry notes.
- Paginate until the requested review is complete.
- Keep task identity distinct from scheduled calendar blocks. A past block does not prove completion.
- For replacement-style update APIs, read the full object and preserve every field the user did not ask to change.
- Treat recurring-series scope as a decision: one occurrence, this and future, or entire series.

## Mutations

Planning, reviewing, or drafting changes does not authorize writes. When writes are authorized, make the narrowest change, preserve list/calendar placement and scheduling properties, then re-read the affected objects. Report returned IDs and any scheduling consequence.

## Reviews

FlowSavvy is authoritative for tasks, completion, and scheduled work. Google Calendar owns fixed commitments. Personal Knowledge owns goals and life context. Compare these sources without copying their full contents into one another.

If the connector is unavailable or pagination is incomplete, state the exact gap and avoid claims about the complete task inventory.
