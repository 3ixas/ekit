# Workbook operations

## Understand the model before editing

Inventory sheets (including hidden ones when relevant), headers, units, dates, names, tables, formulas, merged cells, validation, protection and external links. Identify a small change boundary and preserve unrelated sheets and workbook features. Values that look alike may be text, numbers or dates; inspect types before converting them. Do not remove hidden data, macros or connections as a formatting cleanup.

Separate raw inputs, assumptions, calculations and presentation so a reviewer can follow a result. Label units and period, use appropriate precision and distinguish blank/not-applicable/unknown from zero. Prefer references to duplicated hard-coded assumptions. Preserve compatible table/range references and avoid converting a model to a static report unless requested.

## Calculation evidence

A file-writing library may store formula text and a cached result without evaluating the expression. A reader opened in value-only mode can therefore return an old cache or no value. A recalculation setting expresses an intention for another application; it does not prove calculation.

Use a compatible calculation engine for the workbook's actual functions. Recalculate, save, reopen, and check both formula expressions and their computed values. Test a hand-worked total or known invariant, dependencies after an input change, and relevant boundary cases such as empty inputs, zero denominators or date cutoffs. Check the used output region for spreadsheet error values and investigate them; do not broadly replace errors with blanks.

Record unsupported functions, engine differences and external links that were deliberately not refreshed. Do not claim that LibreOffice, Excel and every formula library produce identical results for all workbooks. If the user requires Excel-specific calculation, verify in that engine or disclose the gap.

## Presentation and reopen checks

Use semantic number/date formats, deliberate widths, frozen headers where useful and restrained styling. Charts need meaningful units, readable labels, truthful scales and accessible distinctions. Define print areas/orientation when printing matters and inspect page boundaries. Render important sheets or ranges, then inspect for clipped text, hidden columns, split tables, tiny type, excessive blank pages and broken chart labels.

Reopen the final file with formula-preserving and value-reading views where available. Confirm sheet names, expected formulas, formats and known outputs. Keep renderer evidence separate from calculation evidence; a screenshot of a number does not explain whether it was calculated or typed.

## Reusable preservation case and failures

The synthetic fixture has two rows: quantities 2 and 6 at prices 12 and 8. Row formulas produce 24 and 48; their total must be 72. After an engine recalculates and saves, reopen to verify both formulas and the literal 72, then render the important range. Before engine calculation, demonstrate that a formula-only write has no validated cached result; do not label it recalculated.

Discover current workbook capabilities rather than assuming a vendor runtime. XlsxWriter and openpyxl are possible construction/read tools, not universal calculation engines. A missing renderer or calculation capability produces a specific unverified result, not silent success. No private data is sent to an external converter to hide that limitation.

## Independent source basis

EKit's guidance and fixture are authored from its workbook requirements. The pinned official XlsxWriter formula documentation supplies facts about stored results and recalculation, without copying documentation text or example code. Refer to metadata for the immutable source identity.
