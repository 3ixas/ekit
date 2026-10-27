# Knowledge And Productivity

`explicit` means user-requested in natural language or dictation; special command syntax is optional. Model loading remains enabled, and action permissions remain separate.

Use Todoist for current tasks and keep durable personal knowledge, direction and commitment reviews in Obsidian. FlowSavvy remains a preserved legacy source.

| Skill | Invocation | Purpose |
|---|---|---|
| `email-assistant` | explicit | Review personal Gmail, prepare replies and cleanup, offer clickable decisions, and verify expressly approved changes. |
| `flowsavvy` | explicit | Read, plan, create, update, reschedule, complete, or review FlowSavvy tasks using live configuration and verified connector state. |
| `flowsavvy-project` | explicit | Turn eligible `WORK` or `CURRENT FOCUS` tasks into approved project lists with structured child tasks and dependencies. |
| `todoist-project` | explicit | Shape an existing Todoist task or fresh idea into an approved child project and actionable tasks. |
| `flowsavvy-feature-request` | explicit | Turn a rough FlowSavvy product idea into the service's exact three-field feature-request form without changing tasks or schedule. |
| `obsidian` | automatic | Retrieve, create, update and validate Obsidian knowledge, direction and current focus. |
| `planning` | explicit | Reconcile daily and weekly Todoist work against personal focus, history and calendar; discuss decisions and apply agreed changes. |

## Common paths

- Current tasks: Todoist. Personal facts, direction and commitment reviews: `obsidian`, using the live vault guide. Fixed commitments: Calendar. FlowSavvy remains available when explicitly requested.

- Daily and weekly personal planning: `planning` uses the explicitly requested Todoist planning library and loads `obsidian` for direction and focus. Resolve providers live; a planning request does not activate or alter integrations.
