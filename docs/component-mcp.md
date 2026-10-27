# Free component and Motion documentation MCPs

These integrations supply current technical sources. They do not choose product direction, replace owned skills, or grant authority to install components in unrelated projects.

## Host configuration

The approved setup uses the account-free HTTP server `https://mcp.motion.dev` and the shared stdio command `npx -y shadcn@4.22.1 mcp`. The shadcn release is pinned for predictable startup; review release changes before updating it. Node/npm must be available in the receiving host environment. The first npx run may download the pinned CLI to npm's cache.

Codex stores the entries in `~/.codex/config.toml` as `mcp_servers.motion` (URL) and `mcp_servers.shadcn` (command/args). Claude Code stores matching user-scope entries in `~/.claude.json` under `mcpServers`. Configure them with the host's MCP administration commands rather than running an upstream skill installer. Do not add Motion+ or a Magic UI server for this setup. OpenCode's skill projection is separate; this task does not configure its MCP client.

Restart or open a fresh host session after configuration. Confirm the new tools are visible and perform one Motion documentation search plus one shadcn registry search/view. Read returned documentation/resources or component source before implementation. An entry in a config file or a successful direct protocol probe proves configuration/server access, not that an existing desktop session has refreshed its tool catalogue. Verify the host receiving the work.

## Project registries

In an approved project's existing `components.json`, merge only a registry needed for the selected component:

| Namespace | Registry |
|---|---|
| `@kokonutui` | `https://kokonutui.com/r/{name}.json` |
| `@react-bits` | `https://reactbits.dev/r/{name}.json` |
| `@bklit` | `https://ui.bklit.com/r/{name}.json` |

Keep existing aliases, registries and customized components. Match TypeScript/CSS or Tailwind variants and inspect transitive dependencies and licence notices. Registry search/view is read-only; adding components changes that project and requires its task authority. These examples do not initialize shadcn or alter any project automatically. Magic UI can be read through its official component docs and registry; inspect its current installation docs when selected.

## Failure and access

If an MCP is unavailable, use current official documentation and selected source with available research tools; report the missing integration. A public premium demo or metadata result is not source access. Motion's free/paid capability descriptions can differ between source snapshots and documentation, so use live tools and returned entitlement rather than promises about free easing, audits or editors.

## Rollback

The dated assessment records the backup directory for both original configs. To remove only these integrations, remove `motion` and `shadcn` through each host's MCP commands (Claude requires user scope). To restore the full original config, compare it with the backup first and preserve any changes made since installation. Never overwrite a newer configuration blindly. Managed skill rollback uses the timestamped snapshots reported by each sync command, independently of these MCP backups.
