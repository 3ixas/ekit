# Obsidian formats and CLI

Query current Obsidian help when syntax or supported properties may have changed. These are decision rules, not a replacement for current documentation.

## Markdown

Preserve Obsidian-flavoured Markdown: wiki links, embeds, block references, callouts, tags, comments, properties, and task syntax. Quote YAML strings when type inference could change their meaning. Keep list and callout indentation valid. When renaming a heading or note, inspect inbound links before changing the target.

## Bases

Treat a `.base` file as a typed view over note properties. Inspect the existing property types and view configuration before editing filters, formulas, groupings, summaries, or column order. Use valid property references and verify the rendered view after changes; a parseable YAML file can still express the wrong dataset.

## Canvas

Treat `.canvas` as JSON with stable node and edge IDs. Preserve unknown fields. Keep node geometry finite and readable, avoid overlapping important nodes, and ensure every edge references existing node IDs. File nodes use vault-relative paths. Validate JSON and inspect the canvas visually after structural changes.

## CLI

The Obsidian CLI operates on a running app. Use an explicit vault when more than one vault could be active. Prefer exact `path=` targeting for mutations and read the note before replacement. Parameters use `key=value`; flags are bare. Run `obsidian help` for the installed command set. After a write, read the target again and validate affected links, properties, tasks, or queries.

For plugin or theme work, reload the changed plugin, inspect errors and console output, and verify the real UI. Do not run arbitrary vault-context JavaScript when a bounded CLI command can do the job.
