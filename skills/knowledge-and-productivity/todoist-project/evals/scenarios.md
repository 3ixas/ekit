# Todoist project scenarios

1. **Existing task with a rough checklist.** A task under BNPP has links, completed and unfinished checklist items, a deadline, and a priority. The skill reads it and the current parent projects, develops the smallest useful task sequence, preserves the links and completed history, proposes the actual final outcome as the deadline holder, and waits for approval before any Todoist write.
2. **Fresh idea.** The user invokes `$todoist-project` with an idea that is not yet in Todoist. The skill establishes the desired result and a fitting life area, identifies missing decisions, proposes concrete first and final actions, and creates no placeholder source task.
3. **Too small or ongoing.** The user gives a single action or an indefinitely recurring routine. The skill recommends an ordinary task or task with subtasks instead of manufacturing a child project.
4. **Partial creation and retry.** A child project and some tasks were created before a tool error. The skill reads them back, reports exact IDs and gaps, and proposes only the missing work; it does not create duplicate tasks or discard the source task.
5. **Tool unavailable.** A host has the skill but lacks the Todoist plugin. The skill may provide a useful breakdown but does not claim to have created anything or silently use another account or service.
