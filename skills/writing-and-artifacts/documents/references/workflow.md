# Document operations and verification

## Choose the editing surface

Inspect paragraphs, heading levels, lists, tables, sections, page sizes, headers/footers, references and embedded objects before changing an existing file. Note templates, fonts and assets that affect layout. Inventory comments/revisions, content controls, fields, macros or protection when present; do not promise preservation if the chosen library cannot round-trip them. A supported native editor is preferable for features absent from a file-generation library.

Use semantic paragraph and character styles. Preserve list numbering, table header rows, column sizing, links and page-number fields when relevant. Section breaks control paper dimensions, orientation, margins and running matter. Repeated blank paragraphs and spaces are fragile substitutes for deliberate layout.

For redlines, distinguish proposed text changes, actual tracked revisions, comments and a clean copy. Use the requested form. If revision support is absent, offer a separately labelled change proposal and preserve the original rather than asserting that tracked changes were produced. Do not accept/reject all existing revisions as an incidental cleanup.

## Content and layout are different checks

After saving, reopen with a compatible reader and compare protected text, heading order, table dimensions, links and requested edits. Check for lost objects or broken relationships. Reopen checks cannot establish page flow because Word pagination depends on the rendering engine, fonts and printer metrics.

Render to PDF or page images using an available compatible office engine. Inspect all pages for a new document; for a bounded edit inspect changed and neighbouring pages, expanding to the whole document when section/style changes can propagate. Check heading separation, orphaned fragments, clipped table cells, repeated headers, footnotes, image resolution, long URLs and unexpected blank pages. Read at ordinary viewing scale as well as zoomed details. Retain the renderer and page count with the evidence.

When feasible, compare extracted rendered text with required content. A PDF may look correct while missing searchable text; extraction may pass while visible content overlaps. Neither substitutes for the other. Do not label a PDF export as proof that every Word feature survives in every office version.

## Reusable preservation case

Create a two-page editable document with a styled heading, a small table and a deliberate page break. Reopen to verify the heading style, expected cell text and break. Convert with an isolated local office profile; require two rendered pages and expected text on the intended page. Inspect both images for clipping and split content. Add an existing-document edit case when the requested operation changes revisions, comments, sections or embedded objects; the simple fixture does not prove those features.

## Tool and authority failures

Resolve the host's document runtime at use time; do not assume a particular vendor package, path or executable is installed. Python-docx can be useful for supported DOCX construction, but is not a pagination engine. If opening or rendering fails, preserve the original, report the exact failed capability and retain an unverified output only with that label. Never upload private content to obtain a convenient conversion without authority.

## Independent source basis

Operational guidance is authored for EKit from the agreed output requirements. The pinned python-docx quickstart is consulted for API semantics only; no documentation prose or example code is redistributed. See this bundle's metadata for the immutable source and digest.
