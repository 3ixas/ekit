---
name: python
description: Guide Python setup, implementation, typing, quality, CLIs, packaging, documentation, and backend work using the project's actual conventions and current tooling.
---

# Python

## Outcome

Idiomatic, maintainable Python that fits the existing project and its supported versions.

## Method

Inspect pyproject, lockfile, version, commands, layout, and chosen tools; preserve project conventions; keep boundaries typed and failures explicit; use src layouts where they serve libraries; validate packaging and public imports when relevant; call testing, security, API, performance, CI, release, and migration specialists as needed.

Read only the relevant guide:

- [references/project-and-quality.md](references/project-and-quality.md) for setup, typing, tests, dependencies, or maintenance.
- [references/interfaces-and-delivery.md](references/interfaces-and-delivery.md) for CLIs, web services, packaging, documentation, or releases.

## Boundaries

Do not force uv, Ruff, mypy, Sphinx, FastAPI, SQLAlchemy, or a packaging migration.


## Owned source methods

These snapshots preserve the reviewed upstream methods. The steps above are enough for ordinary use; open a snapshot only when the task needs the specific method it names.

- [trailofbits-modern-python](references/source-methods/trailofbits-modern-python.md)
