# GitHub issue operations

Use the local GitHub CLI or API for issue work. Resolve the exact repository from the supplied issue URL or with `gh repo view --json nameWithOwner --jq .nameWithOwner`, then check `gh auth status -h github.com` in a host/keyring-enabled context. On macOS, a sandboxed shell may not see the keyring; if its status is invalid or unavailable, rerun the status and the operation in the host context before asking for reauthentication. A successful host-context status for the expected account is authoritative. Never use `--insecure-storage` or put the token in plaintext.

Write each reviewed issue body to a Markdown file and use explicit repository arguments:

```sh
gh issue view 123 --repo OWNER/REPO --json number,title,body,state,labels,url
gh issue create --repo OWNER/REPO --title "..." --body-file /path/to/body.md --label "..."
gh issue edit 123 --repo OWNER/REPO --body-file /path/to/body.md
gh issue comment 123 --repo OWNER/REPO --body-file /path/to/comment.md
```

Use `gh api` for unsupported issue fields or endpoints, including file-backed fields with `-F body=@/path/to/body.md`. After every authorized mutation, read the issue back with `gh issue view` and verify the exact title, body, labels, links, and number. Keep dependency links in the body unless a supported API operation is specifically required.

Prefer `gh`/`gh api` for structured issue state; use another supported capability when it is materially better or the CLI is unavailable. If no supported capability is available, keep the local drafts and report the exact access blocker.
