# Artifact preservation cases

These synthetic cases exercise the artifact owners' saved-file, rendering and calculation seams. They require an installed Python environment with python-docx, python-pptx, openpyxl, pypdf and reportlab, plus local `soffice` and `pdftoppm` executables. Resolve capabilities in the current host; this repository does not bundle or install those libraries/tools.

Run from the repository root with a **new disposable directory**:

```sh
python3 scripts/verification/artifact_preservation.py --output-dir /path/to/new-disposable-output
```

The fixture contains no personal, employer or supplied source data and performs no upload. Conversion uses the local office tool. Each fixture run uses an isolated office profile inside its output directory. Do not run it against a valuable existing directory; creation refuses an existing output directory.

Expected checks: a two-page DOCX with a heading and table reopens and exports to two pages with the right text; a selected PDF page retains its text and declared rotation/geometry; an editable two-slide deck reopens, its shapes lie within slide bounds and both slides export; a workbook's formulas survive compatible-engine recalculation, values reopen as 24, 48 and total 72, and its print area exports to one page. A formula-only workbook deliberately has no verified cached total before recalculation. The literal outputs are independent hand-worked expectations, not values inferred from successful writes.

Inspect **every** generated PNG listed in `results.json`. Numeric/structural assertions produce a pending visual inspection, never an automatic layout pass. Check the document pages for clipping, heading/table readability and the intended page break; the rotated page for retained text/orientation; both slides at presentation scale for overflow/hierarchy; the workbook printout for labels, numbers and page fit. Record observed visual results separately, including renderer or font differences. Retain logs and actual exit status if conversion fails; missing tools or unsupported engine output are unverified capabilities.

These cases do not establish faithful editing of tracked revisions, comments, embedded objects or media; secure PDF redaction, OCR, form appearances, signatures, accessibility/tagging; complex spreadsheet function compatibility; or another application's exact rendering. Add task-specific evidence at those seams when requested. A missing required capability remains a blocker to the corresponding claim.

The operational guidance and fixture code are independently authored from EKit's accepted capability requirements. Official API documentation is consulted only for facts, with immutable sources and digests in each owner's metadata. No restricted runtime entrypoint, vendor helper or upstream documentation example is distributed here.
