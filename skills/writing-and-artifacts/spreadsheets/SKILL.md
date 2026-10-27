---
name: spreadsheets
description: Create, edit, analyze, or verify spreadsheet files with formulas, tables, charts, formatting, and recalculation evidence.
---

# Spreadsheets

Create or edit an auditable workbook, then establish that its saved formulas, results and presentation support the requested use. Read [workbook operations](references/workflow.md) for model preservation, recalculation and rendering branches.

1. Inspect relevant sheets, ranges, formulas, named ranges, formats, charts and external connections. Record the requested change, units, protected inputs and expected outputs. Use `data-analysis` for analytical methodology.
2. Discover a compatible workbook tool, calculation engine and renderer. Work on a separate output unless replacement is authorised; preserve model structure and existing formulas outside the requested edit.
3. Express derived values as formulas where continued recalculation is expected. Use explicit units, clear input/output roles and legible number formats; do not disguise missing values or errors as zeros.
4. Recalculate with a compatible engine, save and reopen both formulas and computed values. Check known totals, dependent cells, error values and significant edge cases. Writing a formula or setting a recalculate-on-open flag is not evidence that it ran.
5. Render important ranges, print areas or charts and inspect readability, truncation and page breaks. Deliver the workbook path, verified results, actual calculation/rendering engine and remaining limits.

Do not refresh external links, enable macros, upload a workbook or alter live connected data without authority. If no compatible calculation engine is available, preserve formulas and explicitly mark computed results as unverified.
