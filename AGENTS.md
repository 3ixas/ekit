# EKit repository

This repository is the editable source of truth for Elias's personal skills and shared instructions across Codex, Claude Code, and OpenCode. Host-specific installed copies and instruction projections are generated output.

## Work here

- Read the root README and the relevant group README before changing a skill.
- Keep each skill under exactly one lifecycle and group: `skills/`, `candidates/`, or `paused/`, then `<group>/<skill-id>`.
- Keep `SKILL.md` concise and disclose branch-specific detail through linked references.
- Record every upstream source, immutable ref, path, digest, licence, adaptation, and review date in `metadata.json`.
- Keep personal facts and project facts in their authoritative systems rather than generic skills.
- Update the maintained provenance inventory when a source disposition changes; keep private assessments outside the publication source.

## Validate and activate

Run `python3 scripts/skills.py check` and `python3 -m unittest discover -s tests -v` after source changes. Preview each host projection with `sync`, `claude-sync`, and `opencode-sync`; apply only after reviewing the exact additions, changes, removals, global instructions, and rollback path. Runtime files under `~/.agents/skills` and `~/.claude/skills` must not be edited by hand. OpenCode reads the shared `~/.agents/skills` source and the generated `~/.config/opencode/AGENTS.md` instructions.

Use `doctor`, `claude-doctor`, and `opencode-doctor` to check the generated host projections. Read [the cross-agent portability guide](docs/agent-portability.md) before changing setup or interpreting a live-session limitation.

Upstream updates are review inputs. `updates` never overwrites owned work. Use `skill-review`, then `skill-authoring`, then validate and sync.

Preserve unrelated user changes. Commits use concise conventional messages without generated-tool attribution.
