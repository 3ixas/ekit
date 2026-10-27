# Create an item

Illustrative only: a user creates an item through a CLI and can retrieve it in a separate invocation.

## Sub-features

- Create an item with a title.
- Retrieve the saved title from persistent storage.
- Reject an empty title without writing data.

## How to get to it (user POV)

Run the app's documented create command. Record additional UI entrypoints separately if they exist and are in scope.

## Driving it with the project CLI

Preconditions: the built CLI is available, a run-owned disposable data directory is empty, and proof artifacts are stored outside it. Substitute actual observed commands for this illustrative syntax.

1. Run `app --data-dir <scratch> doctor`; require the expected build and data directory.
2. Run `app --data-dir <scratch> create --title "Release checklist"`; capture command, stdout, stderr, and exit code, including the returned ID.
3. In a separate process, run `app --data-dir <scratch> get <returned-id>`; require the saved title. Capture this second view as persistence evidence.
4. Attempt an empty title; require a validation error and confirm no additional item exists.
5. Remove only this run's disposable data; confirm captured transcripts remain at the guide's evidence location.

## Gotchas

A successful create response alone does not prove persistence. Missing fixtures or unavailable tools must be reported, not worked around by weakening the expected result. This example's commands must never be presented as target-app evidence.
