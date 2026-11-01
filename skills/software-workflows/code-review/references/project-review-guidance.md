# Project review guidance

`REVIEW.md` is a concise, living guide to project-specific failure modes and review priorities. It is not a finding ledger, a substitute for existing standards, or authority to enlarge a review or edit the project.

Discover applicable root and affected-directory `REVIEW.md` files. Respect existing instructions, the selected diff and any narrower review scope. Pass applicable guidance to the reviewers; report an unavailable or conflicting source rather than treating it as permission to ignore higher-priority instructions.

When no applicable guide exists, a standalone review remains read-only: recommend a root `REVIEW.md` with specific, evidence-backed initial entries, or say what evidence is missing. Do not create an empty or generic checklist. When an implementation or maintenance caller has authority and its approved scope includes guide upkeep, that caller creates a short root guide before the final review snapshot. Use current project instructions, relevant code and verified failure modes; distinguish observed facts from questions. Reuse a sufficient existing project review guide instead of duplicating it.

As work reveals a confirmed review miss, false positive or incident, suggest a concise reusable lesson with its evidence and affected area. The write-authorised caller may update the guide within scope, preserving existing content and removing duplication; unconfirmed theories and one-off findings stay out. If a mechanical rule is better enforced deterministically, recommend the existing linter or check rather than a prose rule. Include every guide change in the caller's proof, exact reviewed snapshot and normal re-review loop. If the change is outside authority or scope, report a concrete proposed addition without writing it.
