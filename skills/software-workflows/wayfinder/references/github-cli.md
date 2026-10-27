# GitHub issue tracking

Use issues only when an exploration needs a durable, shared work record. Resolve the exact repository with `gh repo view --json nameWithOwner --jq .nameWithOwner` or from the supplied issue URL, and check `gh auth status -h github.com` in a host/keyring-enabled context. On macOS, a sandboxed shell may not see the keyring; if its status is invalid or unavailable, rerun the status and the operation in the host context before asking for reauthentication. A successful host-context status for the expected account is authoritative. Never use `--insecure-storage` or put the token in plaintext.

Use `gh issue view` to load an existing exploration, and create or update a reviewed draft with `gh issue create` or `gh issue edit` using `--body-file` and an explicit `--repo`. Use `gh api` for fields the issue commands do not expose. Read the result back and verify the title, body, labels, links, and issue number.

Prefer `gh`/`gh api` for structured issue state; use another supported GitHub capability when it is materially better or the CLI is unavailable. If no capability is available, keep a local record and report the blocker.
