# GitHub issue operations

Use the local GitHub CLI or API for issue work. Resolve the exact repository from the supplied issue URL or, from the project root, with `gh repo view --json nameWithOwner --jq .nameWithOwner`. Check `gh auth status -h github.com` before any remote operation in a host/keyring-enabled context. On macOS, a sandboxed shell may not see the keyring; if its status is invalid or unavailable, rerun the status and the operation in the host context before asking for reauthentication. A successful host-context status for the expected account is authoritative. Never use `--insecure-storage` or put the token in plaintext.

Draft the full Markdown body in a file, then use commands such as:

```sh
gh issue view 123 --repo OWNER/REPO --json number,title,body,state,labels,url
gh issue list --repo OWNER/REPO --state all --limit 100 --json number,title,state,url,labels
gh issue create --repo OWNER/REPO --title "..." --body-file /path/to/body.md --label "..."
gh issue edit 123 --repo OWNER/REPO --body-file /path/to/body.md
```

Use `gh api` for fields or endpoints that `gh issue` does not expose, for example `gh api repos/OWNER/REPO/issues/123` or `gh api --method POST repos/OWNER/REPO/issues -f title='...' -F body=@/path/to/body.md`. Read the created or edited issue back with `gh issue view` and verify its title, body, labels, links, and number before reporting success. Keep dependency links in the issue body unless a supported API operation is specifically required.

Prefer `gh`/`gh api` for structured issue state; use another supported GitHub capability when it is materially better or the CLI is unavailable. If no capability is available, preserve the local draft and report the blocker.
