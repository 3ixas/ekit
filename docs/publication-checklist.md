# Public-transition checklist

This checklist governs publication of Elias's personal collection. Record each result as **pass**, **needs change**, **decision needed**, or **not applicable**, with evidence, remedy, and the reviewed revision. [Publication readiness](publication-readiness.md) describes the remaining gates; it is not approval to publish.

## Establish the exposure boundary

- [ ] Pin the local commit, worktree manifest, existing index, remote branch SHAs, tags, and settings. Separate remote content, pending tracked edits, and untracked additions.
- [ ] Inventory all remote branches and history, plus issues, PRs/reviews, comments, attachments, releases/assets, Actions workflows/runs/logs/artifacts, deployments, Pages, discussions, wiki, and project surfaces. Record unavailable surfaces explicitly.
- [ ] Review pending additions before selecting a publication candidate. Any change after the reviewed snapshot invalidates the affected checks.

## Privacy and credentials

- [ ] Scan current files and reachable historical blobs/commits for secrets with a recorded scanner version, configuration, exit status, and triaged findings.
- [ ] Review personal information, third-party details, private links, local paths, account identifiers, employer material, fixtures, conversation excerpts, patches, screenshots, and evidence files.
- [ ] Inspect commit messages, author/committer identities, and tags. Classify intentional public context separately from unnecessary exposure and private material.
- [ ] If credentials are found, revoke/rotate them first. Current-file removal does not remove history.
- [ ] Present the affected refs, backup, and clone recovery plan before any history rewrite or deletion. Do not publish unresolved exposure.

## Redistribution rights

- [ ] Inventory every active, candidate, and paused bundle and its sources, exact pins, paths, digests, licence treatment, and notices. Include standalone scripts, plugins, assets, fixtures, assessment attachments, and historical material.
- [ ] Compare retained contents with the actual upstream sources; distinguish copied/adapted content from independently written guidance and reference-only links. Structural metadata validation is not rights verification.
- [ ] Retain applicable licences, copyright notices, attribution, source links, and modification notices. Do not apply a blanket root licence over third-party content.
- [ ] Resolve unclear grants or restricted material through permission or independently sourced replacement; review historical copies too.
- [ ] Choose terms for original contributions after the rights inventory. Public reference access without a new general licence is a distinct option.

## Anonymous downloads and selective use

- [ ] Remove obsolete private/authentication assumptions from live setup and generated instructions; retain historical records as historical evidence.
- [ ] Document browser ZIP download at a recorded SHA, complete bundle contents, recursive skill dependencies, tool requirements, and licence companions.
- [ ] Document comparison, backup, selective adoption, and fresh-session checks at work. Preserve work instructions and installation ownership.
- [ ] Test a simple bundle and a bundle with references/assets from an extracted archive. Distinguish authenticated archive tests, locally built candidate archives, and actual anonymous access.
- [ ] Verify essential paths and flag inaccessible private/package references. Test the work network separately; browser access alone does not establish download access.

## Validation and publication gate

- [ ] Run `python3 scripts/skills.py check` and `python3 -m unittest discover -s tests -v`; record failures/skips as such.
- [ ] Review `sync`, `claude-sync`, and `opencode-sync` previews, including globals, removals, drift, and rollback. Applying runtime projections is separate from publication preparation.
- [ ] Inspect repository permissions, Actions permissions, protections/rulesets, and security-feature availability. Prepare authorised changes; do not silently alter live settings.
- [ ] State personal maintenance/contribution expectations without promising a supported public toolkit.
- [ ] Produce an exact candidate and final readiness report. Resolve every blocker or document an explicit applicable decision; a clean scanner is not publication approval.
- [ ] Obtain explicit authority for the exact visibility change, then verify signed-out browsing and ZIP downloads. Confirm the work-machine route separately.

## Sources

- [GitHub visibility consequences](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility): Actions history/logs become public; push rulesets are disabled; public copies may survive a return to private.
- [GitHub sensitive-data removal](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository): rotation and coordinated history cleanup.
- [GitHub licensing](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository): visibility and reuse rights are separate.
