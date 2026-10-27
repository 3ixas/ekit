# Preserve check output

Use for tests, typechecks, lint, and builds whose results support a verification claim.

Run the full command without piping its output to `head`, `tail`, `rg`, or another display filter. Keep the command, revision/environment, completion status, actual exit code, and complete stdout/stderr together. Prefer a host-provided persisted transcript only if it contains the full output and final status. If the host truncates output without preserving it, rerun the check with file capture before claiming success.

Otherwise capture output in an owned, access-restricted temporary directory, outside any scratch data that cleanup will delete. For a finite command, this Bash pattern preserves both streams and the check's exit status, including when the caller uses `set -e`:

```bash
CHECK_EVIDENCE_DIR=$(mktemp -d "${TMPDIR:-/tmp}/check-evidence.XXXXXX")
check_status=0
your-check-command >"$CHECK_EVIDENCE_DIR/output.log" 2>&1 || check_status=$?
printf '%s\n' "$check_status" >"$CHECK_EVIDENCE_DIR/exit-status"
printf 'Check exit: %s; evidence: %s\n' "$check_status" "$CHECK_EVIDENCE_DIR"
(exit "$check_status")
```

Replace `your-check-command` with the real project command. The final subshell returns the check's status without explicitly exiting an interactive shell. A summary command must not become the reported check result. When live streaming through `tee`, use the shell's pipeline-status facilities to retain the check's own status and separately detect capture failure; `tee` succeeding does not prove the check passed. A capture error makes the evidence incomplete even if the check itself succeeded.

After the run finishes, inspect and filter the saved output as needed, including failure context and the final summary. Short user-facing reports are fine; preserve the underlying evidence. Redact sensitive values from reports and shared copies, restrict raw artifact access, and follow project retention rules. Do not expose secrets merely to preserve logs.

A running, timed-out, or interrupted command has no completed passing result. Mark the claim Fail or Skip according to the observed failure or harness limitation, and record the last known state. A zero exit code supports only what that command actually checked; it does not prove an integrated user journey.

Method adapted independently from HumanLayer's output-filtering hook. No hook or host-specific command matcher is installed.
