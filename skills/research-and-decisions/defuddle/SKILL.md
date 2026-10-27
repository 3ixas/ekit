---
name: defuddle
description: Support webpage reading or research by extracting clean Markdown with Defuddle CLI when normal fetching is noisy, incomplete, or cluttered. URLs ending in .md are already Markdown; use the host's normal fetch tool directly.
---

# Defuddle

Use Defuddle CLI as extraction support for the owning reading or research workflow when a standard web page's navigation, ads, or clutter obscure its content. Verify the returned title and body match the requested page; disclose missing or truncated content before summarizing it.

If not installed: `npm install -g defuddle`

## Usage

Always use `--md` for markdown output:

```bash
defuddle parse <url> --md
```

Save to file:

```bash
defuddle parse <url> --md -o content.md
```

Extract specific metadata:

```bash
defuddle parse <url> -p title
defuddle parse <url> -p description
defuddle parse <url> -p domain
```

## Output formats

| Flag | Format |
|------|--------|
| `--md` | Markdown (default choice) |
| `--json` | JSON with both HTML and markdown |
| (none) | HTML |
| `-p <name>` | Specific metadata property |
