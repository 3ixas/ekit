# Retained upstream material

The source inventory records the shipped collection, not a blanket clearance or a new grant. `retained-sources.json` maps every source record owned by this ticket to its bundle, immutable identity where supplied, upstream location/digest, copying treatment and portable notice companion. The six artifact and analytics owners use independently sourced replacement guidance and separate primary-source records in their metadata; their operational references and preservation cases are integrated in this baseline. They are outside this retained-upstream snapshot inventory.

## Declarations and modifications

The exact [Vercel Labs README](https://github.com/vercel-labs/agent-skills/blob/063bee94c3f4df8453406c830b0a7df0f2860278/README.md#license) and [Compound Writing README](https://github.com/EveryInc/compound-writing/blob/18702f0ece9f2b852e305807e0271b2d550d9b4b/README.md#license) declare MIT. Their respective records in `licenses/declared-mit-vercel-labs.txt` and `licenses/declared-mit-compound-writing.txt` preserve those declarations and standard terms. A missing standalone LICENSE does not negate the declarations. No upstream copyright holder or year is invented: the inspected pins do not supply that line.

Seven Vercel and two Compound Writing source-method bodies match the pinned upstream files once the local heading/fence and boundary newline are removed. Their metadata now records copied treatment. This is a body comparison, not a claim that the entire wrapped local file is byte-identical. Exact upstream blob identities and SHA-256 hashes are supplied.

For divergent source-methods, the inventory supplies a complete comparison patch against the immutable source, the unchanged local file hash and adapted treatment. A local derivative is not an exact upstream version. The pstack comparisons show additions to grounding, design checkpoints and caller-first scaffolding, local workflow/review/authority constraints and technical-writing explanation. The patch states what differs; historical authorship of individual deltas is not asserted. The MIT notice remains attached. A difference from a pin is not evidence that the pin itself has no licence.

Five Trail of Bits snapshots retain their exact source bodies, attribution and wrapper/relocation declarations under CC BY-SA 4.0. Embedded Emil payload comparisons distinguish exact payloads from the documented greeting removal. The Taste, Cloudflare, Libraries.dev, candidate and paused asset mappings preserve their existing source identities and modification treatment. The missing exact-path Compound Engineering `ce-debug` attribution remains in the Debug metadata.

## Offline retention

Keep the entire bundle, including `metadata.json`, `NOTICE.txt`, `LICENSE.txt` where present, and `references/licenses/`. The portable directory contains the full recorded notices or explanatory limitation records named by that bundle's source metadata. A reference-only or restrictive record is not an open-source grant. Root notices alone are insufficient for a separately downloaded directory; retain these bundle companions and essential source references.

`LICENSE_SCOPE.md` limits the root MIT licence to eligible original contributions. It cannot override MIT attribution conditions, Apache notice obligations, Creative Commons share-alike terms, asset/font licences, or restrictions on package text. No upstream executable or method body was rewritten by this provenance-only slice.

## Integrated replacements and remaining gates

The four artifact entrypoints and two analytics source snapshots have been replaced with independently authored methods. The artifact runner and the analytical owners’ linked preservation cases exercise the accepted output seams; primary-source API/fact references live in each owner’s metadata. The originals remain private. Public access to a package is not redistribution permission; removing metadata alone would not establish either permission or preservation.

Reference-only and proprietary source records are not evidence of a copying grant. If a later content check discovers additional copied material outside this mapped snapshot/asset inventory, preserve it privately and resolve its rights before publication. Linked media/fonts are checked at use; no third-party remote asset is cleared merely by its parent toolkit's MIT licence. The final integrated candidate must refresh affected hashes, repeat extraction checks and undergo the separate privacy/rights/public-history gate.

## Recheck after integration

Run `python3 scripts/source_inventory.py check` from the repository root. It fails if a retained method/asset changed, owned source metadata drifted, a portable notice is absent/stale, or a notice pointer is missing. The six artifact/data owners are deliberately excluded from this retained-method inventory: their separate replacement dispositions and preservation cases remain part of candidate verification.

After reviewing an owned metadata or notice change, update any new `NOTICE.txt` pointers explicitly and run `python3 scripts/source_inventory.py refresh-metadata`, then `check`. Refresh updates only the owned metadata list and notice companions. It cannot update a changed method/asset hash, recreate a primary source comparison, or grant permission; those require an explicit revised provenance record and review. Keep these checks in the clean-archive and integration proof, alongside the ordinary repository validator and unit suite.

Refresh validates the chosen checkout and every inventory, metadata, notice, canonical licence and companion path before writing. Symlinked roots/components and paths escaping the chosen root are rejected; a rejected preflight leaves existing companions, inventory and external bytes unchanged. It shares the checkout-path boundary with the selective export tool. This path check is not a transaction guarantee for unrelated I/O failures or a concurrent hostile filesystem.

The HumanLayer 2024 companion preserves the actual pinned upstream attribution/header and includes the complete Apache 2.0 terms. Run `python3 -m unittest discover -s tests -p 'test_portable_licenses.py' -v` to verify both the canonical Apache families and raw standalone HumanLayer bundle downloads, without relying on root licences supplied by the selective helper. `test_source_inventory.py` exercises the public refresh/check CLI and rejected indirection before writes.
