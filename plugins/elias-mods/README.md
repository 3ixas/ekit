# elias-mods

Personal Claude Code mods, designed for the Code tab of the Claude Desktop app. Every feature adds at most one row to a shared band above the prompt. See [ADR 0003](../../docs/adr/0003-claude-mods-live-beside-skills.md) for why the plugin lives in this repository.

## Rules

- Mods may observe, hold, or refuse a tool call. They never approve one. `tests/test_elias_mods.py` fails if the module hooks `tool.check`.
- Desktop first. Wherever nothing draws, `/elias-mods` reports the same status as text.
- Each feature has its own `userConfig` toggle and is on unless set to `false`.

## Features

| Feature | Option | Status |
|---|---|---|
| Context barometer | `barometer` | Available |
| Skill route and warn-only guard | `skill_route` | Available |
| Grilling answer sheet | `answer_sheet` | Available |

Until a feature contributes a row, the band shows one dim placeholder line naming the surface, the Claude Code version, and the features that are on.

### Band layout

- **Order:** top to bottom, the context barometer, the skill route, then the grilling-round row, which sits nearest the prompt because it is the one Elias acts on.
- **When rows are short** (the band's `maxRows`): the grilling round is kept first, then the barometer; the skill route goes first. The rows that stay keep their order.
- **Narrow bands** (the band's `bodyColumns`): below 72 cells the barometer drops its plan limits, and below 44 its sparkline. The context reading never wraps. The skill route and the grilling-round count truncate at the end, and the round's **Answer sheet** button keeps its width.
- **Features off:** the remaining rows keep their order. With none to show, the placeholder line takes their place.
- On Desktop the Svg sparkline waits for two measured turns, since a single point is a dot lost beside the threshold line. The text line shows its first block at once.
- **Handoff** shows a toast at once, because `/handoff` starts only when the session goes idle.

### Context barometer

After each main-thread turn (`session.measure`, which the engine raises for the main thread's turns and for rate-limit moves), the barometer reads `$.session.usage()` and shows the context fill, the token count, a sparkline of fill over the last 24 measurements that moved it, and each plan limit with its reset time. Desktop draws the sparkline as an `Svg` with the handoff threshold dashed; every other surface draws it in block characters on one line, and `/elias-mods` adds the same line. If `/handoff` cannot start, a toast says why. Plan limits are left out when the account reports none. From `handoff_at` percent (default 70) a **Handoff** button runs `/handoff`. It calls no model.

### Skill route and guard

A dim `skills implement → tdd · typescript` row lists every skill expanded this turn (typed, loaded by the model, or preloaded), in order. It keeps showing after the turn completes and is replaced when the next turn starts. A typed `/skill` expands before its turn starts, so expansions between turns wait for the next one; a background subagent's Skill call between turns belongs to no turn and is left out. Not handled, and not seen live: a background subagent's loads while a later turn runs join that turn; a skill preloaded into a subagent spawned between turns joins the next turn; a queued `/skill` that expands while the previous turn is still running is replaced when its own turn starts. A supporting skill that follows another supporting skill joins with `·`, every other step with `→`.

The guard judges each Skill tool call against the invocation lists in this repository's `skills/<group>/<id>/metadata.json`, found by walking up from the plugin to the directory holding `scripts/skills.py`, the same source the generated routing guidance comes from. A plugin running from an installed copy under `~/.claude` reads those lists from the generated `~/.claude/rules/elias-agent-skills.md` instead. Without either the guard stays off and the row still lists loads; `/elias-mods guard` names the source it used.

A turn here is Elias's turn: skills that subagents load during it join the same row, and an owner loaded anywhere in the turn covers later supporting loads. An owner is an owned skill that expanded and is not supporting-only: a primary skill, or a user-requested (`explicit`) workflow loaded by the model or typed by Elias. Plugin skills (`vercel:nextjs`) are not owned, so they own nothing and are never warned about. `tests/test_elias_mods.py` checks that the generator still writes the wording the projection parser looks for.

- A supporting-only skill loaded with no primary owned skill earlier in the turn shows `⚠` and the row turns full strength. With `skill_guard_refuse` off (the default) the load goes ahead; on, it is refused with a reason that tells Claude to load the owning primary skill first or ask Elias.
- User-requested workflows stay model-loadable. Descriptions and instructions recognize natural-language requests; this guard does not parse prompts or enforce user intent. No second slash command is required.
- Each supporting-ownership warning is appended to `guardLog` in the plugin's store as `{ skill, kind, at }`, keeping the latest 1000. `/elias-mods guard` counts them per skill: the evidence for turning on `skill_guard_refuse`.
- If the guard itself fails, the skill loads.

### Grilling answer sheet

When a main-thread turn ends with a grilling round, the sheet reads it from the turn's final message (`turn.complete`'s `answer`) in the `grilling` skill's format: `❓ **Q1** - **Title**: body`, then `➡️ recommendation`. It also reads `**Q1 - Title**`, `**Q17 (revisited)** - **Title**` and `**Q3** (was Q4) - **Title**`. A recommendation is its own paragraph, so prose after the last question is left out. A message whose round cannot be read whole, an interrupted turn, a subagent's turn and the format quoted in a code fence open nothing.

- The pane opens without taking the keyboard, titled with the question count. It lists each question's title and recommendation, with **Accept** and a field to answer otherwise. **Accept all** accepts every question not already answered. **Send** appears once every question has an answer, since `Button` has no disabled state.
- Send submits `Q1 agreed.` or `Q2: <answer>`, one line per question, through `$.prompt.submit({ asUser: true })`, so Claude reads it as Elias's own words. A refused submit keeps the sheet and says why in a toast.
- A dim `❓ grilling round · 4 questions` row stays in the band while the round is open, with an **Answer sheet** button that reopens a closed pane and gives it the keyboard. `/elias-mods` adds `grilling round open · 4 questions · 1 answered`.
- The round closes when a turn starts from Elias's own prompt (typed, through Remote Control, or sent from the sheet). A turn a notification or another session starts leaves it open, and so does closing the pane.
- The mobile app draws no `Input`, so there the sheet offers Accept alone.
- **Desktop draws a plugin's prompt late.** The transcript records the reply within 25ms of the press, but the Desktop app shows it in the thread only once Claude's response starts: about 1s with a warm prompt cache, up to 15s with a cold one (traced 2026-10-24). Send therefore shows a `Sent: Q1 agreed. · …` toast at once. Anything else that submits through `$.prompt.submit` needs the same feedback.
- This plugin's `prompt.submit` hook never sees its own `$.prompt.submit` (traced live), so `sendAnswers` closes the pane itself.

`tests/rounds.ts` holds synthetic rounds for the parser tests. They preserve the supported heading variants, options tables, multi-paragraph and empty bodies, and trailing prose without publishing conversation excerpts. Only the synthetic fixtures belong in the maintained source.

Pure logic lives in `hooks/band.ts` (the band and barometer), `hooks/route.ts` (the route and guard) and `hooks/sheet.ts` (the answer sheet); none calls the mods API.

### The `/elias-mods` command

`/elias-mods` is the plugin's `skills/elias-mods/SKILL.md`, listed as `elias-mods:elias-mods` with the alias `elias-mods`, and the hooks module answers it on `command.run` before the skill expands. It is not registered with `$.command.register`: the Desktop app checks a typed command against a list read from a Claude Code process it starts with every hook off, so a runtime registration never reaches that list and the composer said "`/elias-mods` isn't a command here" (traced in the Desktop bundle, 2026-10-24). The engine also refuses to register `elias-mods` while the skill's alias holds it. A skill cannot be `immediate`, so `/elias-mods` typed mid-turn waits for the turn to end. Where the hooks module does not run, the skill tells Claude to say the mods are not running.

## Install for daily use

The repository root holds a local marketplace, `.claude-plugin/marketplace.json`, named `elias-agent-skills` and listing this plugin. As [ADR 0003](../../docs/adr/0003-claude-mods-live-beside-skills.md) records, installing is a separate step from `sync` and `claude-sync`.

1. **Preview.** Check the marketplace and the plugin, and see what is installed now:

   ```bash
   claude plugin validate --strict /absolute/path/to/ekit
   ```

   ```bash
   claude plugin list
   ```

   Applying adds `elias-agent-skills` to `extraKnownMarketplaces` and `elias-mods@elias-agent-skills` to `enabledPlugins` in `~/.claude/settings.json`, and copies the plugin into `~/.claude/plugins/cache/`.
2. **Apply.**

   ```bash
   claude plugin marketplace add /absolute/path/to/ekit
   ```

   ```bash
   claude plugin install elias-mods@elias-agent-skills --scope user
   ```

3. **Drop the development entry, then confirm.** While `CLAUDE_CODE_PLUGIN_DIRS` is set, the development copy (`elias-mods@inline`) replaces the installed one of the same name, so the installed copy cannot load until the entry is gone (seen 2026-10-24). Remove `CLAUDE_CODE_PLUGIN_DIRS` from `env` in `~/.claude/settings.json`, start a new Code tab session, and run `/elias-mods`. The installed copy keeps its own store in `~/.claude/plugins/store/`, separate from the development copy's `elias-mods_inline-*` file, and records `lastLoad` there.

An installed copy is a snapshot. After changing the plugin, raise `version` in `.claude-plugin/plugin.json`, then:

```bash
claude plugin marketplace update elias-agent-skills
```

```bash
claude plugin update elias-mods@elias-agent-skills
```

An installed copy reads the skill guard's lists from the generated `~/.claude/rules/elias-agent-skills.md`, not from this repository (see the skill guard above).

### Disable or roll back

- **Turn off one feature:** `claude plugin configure elias-mods@elias-agent-skills` shows the options. Save a value as a string, which is stored typed, then start a new session:

  ```bash
  echo '{"barometer": "false"}' | claude plugin configure elias-mods@elias-agent-skills --values-stdin
  ```
- **Turn off every mod:**

  ```bash
  claude plugin disable elias-mods@elias-agent-skills
  ```

  `claude plugin enable elias-mods@elias-agent-skills` brings them back.
- **Roll back the install:**

  ```bash
  claude plugin uninstall elias-mods@elias-agent-skills
  ```

  ```bash
  claude plugin marketplace remove elias-agent-skills
  ```

  Then put `CLAUDE_CODE_PLUGIN_DIRS` back if you still want the development copy.

## Develop in the Desktop app

The Desktop app cannot take `--plugin-dir`, so load the plugin through `env` in `~/.claude/settings.json`. The development copy then replaces the installed one for every new session, so edits show after `/reload-plugins` without a version bump; remove the entry to go back to the installed copy:

```json
"env": { "CLAUDE_CODE_PLUGIN_DIRS": "/absolute/path/to/ekit/plugins/elias-mods" }
```

Start a new Code tab session, then run `/reload-plugins` after each edit. Each load records `{ surface, version, session, features, at }` under `lastLoad`, and each app that connects records `{ surface, version, session, at }` under `lastAttach`, in the plugin's store in `~/.claude/plugins/store/`.

Check the plugin from its directory:

```bash
claude plugin validate --strict .
```

```bash
claude plugin test
```

## Verification and privacy

The parser cases are synthetic. Repository validation and plugin tests exercise supported formats; fresh host-session behaviour must be checked separately after a deliberate installation. Private usage baselines, transcripts and historical tracker discussions are not distributed.

The optional `tools/mine_sessions.py` diagnostic reads the current user's local Claude transcript store only when run deliberately. It emits aggregate counts and does not send data anywhere, but those aggregates can still be private: keep outputs outside the repository. Its tests use disposable synthetic records; ordinary plugin use and skill installation do not run it.

## Versions

Version `0.1.3` packages the reviewed EKit baseline, including synthetic parser fixtures and the relocated local diagnostic. Refresh the marketplace and plugin separately after deliberately switching the local source; skill sync does not update the plugin cache.

Tested with Claude Code 2.1.292 (CLI) and 2.1.308 (the Desktop app's bundled copy, seen in the placeholder row on 2026-10-23). Below 2.1.299, Claude Code refuses a tree that uses `Box` spacing step names (`'md'`) or the `Text` props `size`, `weight`, `mono`, and `tabular`, and draws its own site instead. Desktop is past that line and the CLI is not, so a feature that uses those props checks `$.session.version()` first or keeps to numeric spacing and `dimColor`. The placeholder row and `/elias-mods` show the running version.

The Desktop app attaches to a session after it starts, so `lastLoad` can read `headless` in a Desktop session; `lastAttach` records the app once it connects. `/elias-mods` names the session's roster of surfaces, and when that reads empty (seen in Desktop on 2026-10-24, while the band said `desktop`) the surfaces that attached or drew the band.

While `CLAUDE_CODE_PLUGIN_DIRS` loads this directory, it is a protected path: edits need approval, and auto mode refuses them. Work on it in Ask mode.
