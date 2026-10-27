# PDF operation checks

## Inspect first

Use a parser for page count, dimensions, boxes, rotation, metadata and forms; use extraction to distinguish searchable text from a scanned page. If the source is encrypted, signed, malformed or protected, establish the authorised operation and likely consequences before writing. Do not bypass access controls or claim a signature remains valid after modifying signed content.

Reading tables requires a visual comparison: extraction order may cross columns or discard merged-cell structure. OCR output needs spot checks for names, numbers, punctuation and reading order. Preserve original page references when quoting or summarising material.

## Branches

- Creation: choose page size, margins, fonts and intended reading order. Use a document layout system when paragraphs/tables need flow. Ensure output can be reopened and important content can be searched when that is a requirement.
- Page selection/merge: state selected pages and their order using human page numbers; convert carefully to the library's indexing. Check count and boundary pages after saving, including whether links/bookmarks still target meaningful destinations.
- Rotation/crop/scale: distinguish page rotation from a content transformation and distinguish page boxes from the content coordinate system. Check rendered orientation and retained content against the requested region. A geometry change can leave content outside the visible box.
- Forms: inspect actual field names/types, fill with suitable tools and verify values on reopening and in a renderer. Appearance regeneration may be necessary; do not assume a stored field value is visible. Flatten only when requested and explain the loss of editability.
- Redaction: use a removal-capable workflow, not rectangles or crop boxes. Reopen and inspect text extraction, images, annotations, layers and metadata relevant to the threat. If secure removal cannot be established, return an explicit blocker rather than a "redacted" copy.

## Verification sequence

Reopen the saved output, check page count/order and numeric geometry, inspect required text/values, then render the pages affected by the operation. Inspect all pages for a newly generated PDF. Include page boundaries and zoom for fonts or small form controls; use multiple extraction/render tools when malformed input makes one reader unreliable. Accessibility/tagging needs its own check; appearance alone proves none of it.

The representative synthetic case is a searchable two-page PDF, followed by selecting and rotating one page. Assert one output page, its expected rotation and dimensions, and its expected retained text. Render and inspect the transformed page. This case does not prove secure redaction, OCR, form filling, digital signatures or PDF/UA conformance.

## Capability failures and source basis

A PDF runtime and a renderer are capabilities to discover in the current host, not assumed executable paths. Pypdf is useful for parsing and page operations; it is not itself a page rasteriser. If rendering or OCR is absent, separate what was checked from what remains unverified. Avoid transmitting private pages to external converters without authority.

EKit's workflow is independently authored from the operation requirements. The pinned pypdf geometry documentation supplies API facts, including the distinction between view boxes and retained contents; no upstream prose or examples are included.
