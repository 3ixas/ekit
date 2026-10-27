---
name: pdf
description: Read, create, transform, inspect, or fill PDFs with extraction and rendered-page verification.
---

# PDF

Choose a PDF operation, preserve its intended content, and verify the saved result as both data and pages. Read [PDF operation checks](references/workflow.md) for geometry, forms, text extraction and failure cases.

1. Determine whether the task is reading, creating, filling, combining, extracting pages, rotating, cropping or redacting. Inspect the input's page sizes, rotation, searchable text, images, forms and relevant protection before choosing tools.
2. Work on a separate output. Use a compatible library or application for the selected operation; never assume a generic page rewrite preserves signatures, tags, form behaviour or attachments.
3. Save and reopen. Check the intended page count/order, page boxes and rotation. Extract required text or form values when applicable. Treat scanned pages as images until OCR has actually been performed and checked.
4. Render affected pages and inspect orientation, clipping, fonts, tables, annotations and visible form values. Compare content and geometry with the request, repair defects, and repeat affected checks.
5. Report the output path, checked pages, tools and limits. Keep structural validity, searchability, visual correctness and accessibility claims separate.

A crop hides a region; it does not securely remove its contents. Secure redaction requires a suitable removal operation and checks for residual text, images and hidden content. No file operation authorises external sharing or decryption beyond the user's access.
