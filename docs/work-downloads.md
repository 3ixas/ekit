# Download skills for work

This is Elias's personal collection. Use it as a reference for selected work skills, keeping the work machine's instructions, accounts, and project policy authoritative.

## Download a complete revision

Anonymous access works only after the repository becomes public. Until then, the following links still require permission. The [publication review](publication-readiness.md) records that gate.

1. Open [the repository](https://github.com/3ixas/ekit) in the browser. Choose a reviewed commit and record its full SHA from the commit page.
2. Download that revision using `https://github.com/3ixas/ekit/archive/FULL_COMMIT_SHA.zip`, replacing `FULL_COMMIT_SHA` with the recorded SHA. The branch's **Code → Download ZIP** option is convenient, but `main` can move; prefer the full-SHA URL so the ZIP identity is unambiguous.
3. Extract the ZIP into a review folder, separate from installed skills and employer source code. Keep the original ZIP and SHA for later comparison.
4. Select active bundles from `skills/<group>/<id>/`. Each skill is a **directory**, including all references, scripts, assets, metadata, evaluations, and notices it contains. Downloading only `SKILL.md` can leave the skill incomplete. `candidates/` and `paused/` are not active installation sources.

GitHub may redirect ZIP downloads to `codeload.github.com`. Public browser access does not prove that the work network permits ZIP or raw-file downloads. If blocked, record the exact blocked route and use an employer-approved transfer method; no GitHub login is needed for a public download.

## Review before installing

Give Claude Code the extracted checkout and the list of selected skills. Ask it to:

- Read each selected `SKILL.md`, its `metadata.json`, and linked local companions. Follow `dependencies.skills` recursively and identify dependencies named in the instructions, including conditional ones. Report any disagreement between metadata and instructions.
- Identify required tools and host features. A skill does not install an MCP server, transfer account access, or prove that a provider is available at work. Check what the work session actually supports.
- Compare the selected bundles with the existing work installation, retaining work-specific improvements. Report changed behaviour, personal assumptions, unavailable tools, and instructions that would cross personal/employer boundaries.
- Read `THIRD_PARTY_NOTICES.md`, the selected sources' files under `licenses/`, and any bundle-specific notices. Keep these with the review material and retain applicable attribution/licences with any copied material. Publication blockers in this repository's readiness report still apply to sharing it.
- Propose exact file changes and their backup/recovery path before applying the selected work update. Do not copy the personal global configuration as part of a skill update.

Example request:

```text
Review the extracted EKit revision <full SHA>, focusing on
<skill IDs>. Compare those complete bundles and their recursive dependencies
with this workstation's existing skills and instructions. Read their metadata,
linked companions and applicable notices. Identify personal assumptions,
unavailable tools, and conflicts with work policy. Treat scripts and embedded
source snapshots as review material; do not execute them during this comparison.
Return the exact proposed changes and a backup plan, without editing files.
```

After choosing the update, apply it through the work installation's own supported mechanism. A managed work installation must be updated at its owning source, rather than bypassing its ownership marker by overwriting generated files. Start a fresh Claude Code session and exercise one relevant request plus an authority/failure case. Record the SHA, selected skills, local adaptations, and observed results in the work installation's permitted local records.

## Full personal sync is a separate operation

The repository's `sync`, `claude-sync`, and `opencode-sync` commands manage a personal system, including global instructions and managed directories. `--adopt-unmanaged` is a migration operation, not a selective skill installer. Plugin/marketplace installation is also separate. Follow [the portability guide](agent-portability.md) only on a machine where those full-system changes are intended.

## Optional local review bundle

After inspecting the downloaded scripts, a work agent can assemble a separate review folder without GitHub login, Git or installation:

```sh
python3 scripts/skill_bundle.py --revision FULL_COMMIT_SHA \
  --output-dir /path/to/new-review-folder how interface-design
```

The helper copies complete active bundle directories, follows declared skill dependencies recursively, retains root and bundle licence/notice companions and maintained documentation, and writes a SHA-256 `bundle-manifest.json`. It omits personal global configuration, credentials, managed-runtime markers and plugin installation. It refuses an existing output folder and never installs anything. The revision is supplied from the downloaded commit page; hashes identify the actual exported bytes, not a network verification.

Read `instruction_mentions_requiring_review` and the actual instructions. That list is a heuristic for skill names in backticks, not a complete parser of conditional dependencies. If the requested branch needs another owned capability, rerun into a new folder with `--include SKILL_ID` (repeat as needed). A tool name in metadata still requires real host verification; no account, MCP capability or native renderer is transferred. Keep the original ZIP with the review folder.

[Offline download verification](verification/download-preservation.md) describes the repository maintainer's archive and representative bundle checks. These do not prove the work network or fresh work agent can use the result.

## Later updates

Download a new reviewed SHA, compare it with the retained previous revision and local work adaptations, then repeat the selected-bundle review. A public repository supplies readable reference files; it does not grant push access or automatically update the workstation.
