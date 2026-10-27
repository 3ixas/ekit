# Python security

Apply these checks when the relevant Python surface exists:

- Avoid `eval`, `exec`, and dynamic imports for untrusted values. Use explicit parsers or dispatch tables.
- Run subprocesses with argument arrays and `shell=False`; if a shell is required, keep untrusted values out of the command and document the boundary.
- Use safe YAML loading and avoid deserializing untrusted pickle, marshal, or framework-native object formats.
- Construct filesystem paths from an allowed root, resolve them, and verify containment before reads, writes, extraction, or deletion. Treat archive members and symlinks as hostile.
- For outbound HTTP, validate scheme and destination, account for redirects and DNS behavior, set timeouts, bound response sizes, and avoid forwarding ambient credentials.
- Use parameterized database APIs and allowlists for identifiers that cannot be parameters.
- Generate secrets and tokens with `secrets`, compare sensitive values with constant-time helpers where meaningful, and use password-specific hashing libraries for passwords.
- Keep framework debug modes, permissive hosts, development servers, and broad CORS settings out of deployed defaults.
- Inspect package indexes, hashes or lockfiles, build hooks, dependency confusion exposure, and CI token permissions when changing dependencies.

Run the project's existing security tools first. Add a tool only when its coverage addresses the current risk and its configuration can be maintained. Confirm the tool scanned the intended paths and explain every suppression.
