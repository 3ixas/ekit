# Which-skill advises from a generated catalogue

`which-skill` recommends which EKit skill should own a request. Its knowledge
comes from a Skill catalogue that `scripts/skills.py` generates into the
skill's references from bundle metadata and structured Workflow path data, and
that `check` fails on when stale. The host's loaded skill listing is only a
cross-check.

Two alternatives were rejected. The host listing alone is always current but
carries only descriptions: no workflow paths, roles, authority stops, or change
dates. Reading the EKit repository live is rich but fails or drifts on a
machine where the checkout is absent or behind the installed copy. A generated,
tested catalogue ships with every projection and cannot silently diverge from
the source.

Workflow paths move from the README's prose table into structured data that
generates both the README table and the catalogue, so there is one source.

Change dates come from tracked metadata, not git. Each bundle's
`metadata.json` records an `added` date beside `reviewed`, and the catalogue's
generation date is the latest of those dates among active skills. Dates read
from git commits cannot be known before the commit that carries the catalogue
exists, so a commit or squash merge on a later day would leave `main` failing
`check`; tracked dates keep regeneration byte-identical everywhere.
