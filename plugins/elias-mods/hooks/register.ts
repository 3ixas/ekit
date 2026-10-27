import type { Hook, On, PluginOptions } from 'claude-code'
import {
  bandRows,
  barometerRow,
  barometerText,
  composeBand,
  enabledFeatures,
  handoffThreshold,
  recordTurn,
  reportedSurface,
  statusText,
  type BandRow,
  type Feature,
  type Reading,
  type SessionInfo,
} from './band.js'
import {
  appendGuardEvent,
  chipText,
  guardReport,
  judgeLoad,
  loadPolicy,
  readGuardLog,
  routeRow,
  type LoadedPolicy,
  type PolicyIo,
  type RouteEntry,
  type RoutePolicy,
} from './route.js'
import {
  acceptAll,
  answeredCount,
  answersRound,
  composeReply,
  isComplete,
  parseRound,
  plural,
  sentToast,
  sheetPane,
  sheetRow,
  type Answer,
  type Question,
} from './sheet.js'

// Features the user left on, set once per load from userConfig
let features: Feature[] = []
// Rows features have contributed to the band, keyed by feature id
const contributions = new Map<string, BandRow['build']>()
// Where this session runs, reported in the placeholder row and /elias-mods
let info: SessionInfo = { surface: 'unknown', version: 'unknown' }
// Surfaces that attached or drew the band, in order: the fallback when the roster reads empty.
// Kept across /clear, since an attached app does not attach again.
let seen: string[] = []
// /elias-mods is the plugin's skills/elias-mods, so Desktop's command menu lists it
// even from a probe that runs no hooks; this module answers it before it expands.
const COMMAND = 'elias-mods:elias-mods'
// Context barometer: the last main-thread reading and the fill per turn before it
let reading: Reading | undefined
let history: number[] = []
// Skill route: the skills of Elias's current (or last) turn, shown on the row.
// A typed /skill expands before its turn starts (seen live: prompt.submit,
// skill.prompt, turn.start), so loads between turns wait in `pending` and become
// the route when the turn starts. A subagent's Skill call between turns belongs to
// no turn of Elias's: it and its expansion are left out. pendingWarn carries the
// guard's warning from a Skill call to its expansion. The policy loads once per
// plugin load, on first use, since /reload-plugins re-runs this module without a
// session.start.
let route: RouteEntry[] = []
let pending: RouteEntry[] = []
let inTurn = false
const pendingWarn = new Set<string>()
const backgroundLoads = new Set<string>()
let policyLoad: Promise<LoadedPolicy> | undefined
// The answer sheet pane's id, which its ui.render requestId also carries
const SHEET_PANE = 'answer-sheet'
// Grilling answer sheet: the round Claude's last turn ended with and Elias's answers
// so far. The round stays open until a turn starts from his own prompt, sent from
// the sheet or typed; a notification's turn leaves it open, and so does closing the
// pane, which the band row reopens. answering says whether the latest prompt.submit
// was his; the next turn.start consumes it.
let round: Question[] | undefined
let answers = new Map<number, Answer>()
let sending = false
let answering = false

type Engine = Parameters<Hook<'session.start'>>[0]
const policyOf = ($: Engine) => {
  const io: PolicyIo = { exists: (path) => $.fs.exists(path), list: (path) => $.fs.list(path), read: (path) => $.fs.read(path) }
  return (policyLoad ??= loadPolicy($.plugin.root, io))
}
const clearRoute = () => {
  route = []
  pending = []
  inTurn = false
  pendingWarn.clear()
  backgroundLoads.clear()
  contributions.delete('skill_route')
}
const showRoute = ($: Engine, policy: RoutePolicy | undefined) => {
  if (route.length) contributions.set('skill_route', routeRow(route, policy))
  else contributions.delete('skill_route')
  $.ui.invalidate('ui.render')
}
// A load joins the running turn, or waits for the next one to start
const addLoad = ($: Engine, entry: RouteEntry, policy: RoutePolicy | undefined) => {
  if (!inTurn) pending = [...pending, entry]
  else {
    route = [...route, entry]
    showRoute($, policy)
  }
}

const isOn = (id: string) => features.some((feature) => feature.id === id)


// Asked (the band row's button), the pane takes the keyboard and is placed at any
// width; opened on its own after a turn it leaves the keyboard where it is
const openSheet = async ($: Engine, asked: boolean) => {
  if (!round) return
  await $.ui.open({ id: SHEET_PANE, title: `Grilling round · ${plural(round.length, 'question')}`, closeOnEscape: true, ...(asked ? { focus: true as const } : {}) })
}
const closeSheet = async ($: Engine) => {
  round = undefined
  answers = new Map()
  sending = false
  contributions.delete('answer_sheet')
  $.ui.invalidate('ui.render')
  // A hook refusing the close keeps its pane: the sheet then says no round is open
  await $.ui.close({ id: SHEET_PANE }).catch(() => undefined)
}
// A turn's final message: a round it ends with opens the sheet; anything else draws nothing
const showRound = async ($: Engine, message: string) => {
  const questions = parseRound(message)
  if (!questions.length) return
  round = questions
  answers = new Map()
  sending = false
  const reopen = () =>
    void openSheet($, true).catch((error: unknown) => {
      $.ui.toast(`Answer sheet did not open: ${error instanceof Error ? error.message : String(error)}`)
    })
  contributions.set('answer_sheet', sheetRow(questions.length, reopen))
  $.ui.invalidate('ui.render')
  // The band row stays as the way in if the pane cannot open now
  await openSheet($, false).catch(() => undefined)
}
// Submits the composed reply as Elias's own words, then closes the sheet itself: this
// plugin's prompt.submit hook never sees its own submission (traced live), so the turn
// it starts does not close it
const sendAnswers = async ($: Engine) => {
  if (!round || sending || !isComplete(round, answers)) return
  sending = true
  const text = composeReply(round, answers)
  try {
    const result = await $.prompt.submit({ text, asUser: true })
    if (result.drop !== undefined) throw new Error(result.drop)
  } catch (error) {
    sending = false
    $.ui.toast(`Answers not sent: ${error instanceof Error ? error.message : String(error)}`)
    return
  }
  $.ui.toast(sentToast(text))
  await closeSheet($)
}

function noteSurface(surface: string) {
  if (!seen.includes(surface)) seen = [...seen, surface]
}

// Rule for every feature: mods may observe, hold, or refuse a tool call, never approve one.
export function register(on: On, options: PluginOptions) {
  features = enabledFeatures(options)
  const threshold = handoffThreshold(options)
  // Warn-only until the guard log shows how often refusing would fire
  const refuse = options.skill_guard_refuse === true

  on('session.start', async ($, e, next) => {
    // A new session (or /clear) starts the barometer over
    reading = undefined
    history = []
    contributions.delete('barometer')
    clearRoute()
    if (round) await closeSheet($)
    // The Desktop app attaches after the session starts, so this is often empty here
    info = { surface: reportedSurface(await $.session.surfaces(), seen), version: (await $.session.version()).version }
    // Evidence that the mod loaded, readable outside the session. Every session
    // shares the store, so each entry names the session that wrote it.
    const session = await $.session.id()
    await $.store.set('lastLoad', { ...info, session, features: features.map((feature) => feature.id), at: new Date().toISOString() })
    return next(e)
  })

  // An app such as Desktop connected: record it, and redraw the band for it
  on('session.attach', async ($, e, next) => {
    noteSurface(e.surface)
    info = { ...info, surface: e.surface }
    await $.store.set('lastAttach', { ...info, session: await $.session.id(), at: new Date().toISOString() })
    $.ui.invalidate('ui.render')
    return next(e)
  })

  // Fires after each main-thread turn and when a rate-limit window moves; only a
  // measurement that moved the fill adds a point to the sparkline.
  on('session.measure', async ($, e, next) => {
    if (!isOn('barometer')) return next(e)
    const usage = await $.session.usage()
    if (e.changed.includes('context')) history = recordTurn(history, usage.context.percent)
    reading = { context: usage.context, rateLimits: usage.rateLimits }
    contributions.set(
      'barometer',
      barometerRow(reading, history, {
        threshold,
        now: () => Date.now(),
        // /handoff waits until the session is idle, so say at once that the press landed
        onHandoff: () => {
          $.ui.toast('Handoff starts as soon as Claude is idle')
          void $.command.run({ command: 'handoff' }).catch((error: unknown) => {
            $.ui.toast(`Handoff did not start: ${error instanceof Error ? error.message : String(error)}`)
          })
        },
      }),
    )
    $.ui.invalidate('ui.render')
    return next(e)
  })

  // Elias's turn ends; the row keeps showing it until the next one starts. A
  // subagent's turn completing (agentId set) is part of his turn, not its end.
  // Anything still pending is a load that ran while the module did not know a turn
  // was running (a reload mid-turn): it belongs to the turn that just ended.
  // A grilling round it ended with opens the answer sheet.
  on('turn.complete', async ($, e, next) => {
    if (!e.agentId) {
      inTurn = false
      pending = []
      if (isOn('answer_sheet') && e.reason === 'answer') await showRound($, e.answer)
    }
    return next(e)
  })
  // A new turn: its route is whatever was typed since the last one, and a turn
  // started from Elias's own prompt has answered any open grilling round
  on('turn.start', async ($, e, next) => {
    inTurn = true
    if (round && answering) await closeSheet($)
    answering = false
    if (isOn('skill_route')) {
      route = pending
      pending = []
      showRoute($, (await policyOf($)).policy)
    }
    return next(e)
  })

  // Notes whether the prompt is Elias's, for the turn it starts. Observes only.
  on('prompt.submit', ($, e, next) => {
    answering = answersRound(e.origin)
    return next(e)
  })

  // The model loading a skill, in the main thread or a subagent of this turn:
  // requested skills stay loadable, and a supporting-only skill with
  // no primary this turn is logged, then let through (or refused once
  // skill_guard_refuse is on). Never approves anything.
  on('tool.call', { tool: 'Skill' }, async ($, e, next) => {
    if (!isOn('skill_route')) return next(e)
    const skill = e.skill
    if (!inTurn && e.agentId) {
      backgroundLoads.add(skill)
      const result = await next(e)
      // Refused further down, so no expansion will come to be skipped
      if (result.deny) backgroundLoads.delete(skill)
      return result
    }
    const { policy } = await policyOf($)
    const verdict = judgeLoad(skill, inTurn ? route : pending, policy, refuse)
    if (verdict.kind === 'allow') return next(e)
    const kind = 'supporting-without-primary'
    await $.store.set('guardLog', appendGuardEvent(await $.store.get('guardLog'), { skill, kind, at: new Date().toISOString() }))
    if (verdict.kind === 'warn') {
      pendingWarn.add(skill)
      const result = await next(e)
      // Refused further down, so no expansion will claim the warning
      if (result.deny) pendingWarn.delete(skill)
      return result
    }
    // Refused here: shown warned, since no expansion will add it
    addLoad($, { skill, warned: true }, policy)
    return { deny: verdict.reason }
  })
    // A guard that fails lets the skill load: routing advice must never break a skill
    .catch(($, e, next) => next(e))

  // Every skill expansion, typed (/name), loaded by the model, or preloaded
  on('skill.prompt', async ($, e, next) => {
    if (!isOn('skill_route') || backgroundLoads.delete(e.skill)) return next(e)
    const { policy } = await policyOf($)
    addLoad($, { skill: e.skill, warned: pendingWarn.delete(e.skill) }, policy)
    return next(e)
  })

  // The text fallback: works on every surface, including ones that draw nothing.
  // `/elias-mods guard` reports how often the skill guard would have fired.
  on('command.run', { command: COMMAND }, async ($, e) => {
    if (e.args.trim() === 'guard') {
      const { note } = await policyOf($)
      return { text: guardReport(readGuardLog(await $.store.get('guardLog')), refuse, note) }
    }
    const lines = [statusText({ ...info, surface: reportedSurface(await $.session.surfaces(), seen) }, features)]
    // reading is only ever set while the barometer is on, route while the skill route is
    if (reading) lines.push(barometerText(reading, history, Date.now()))
    if (route.length) lines.push(`skills ${chipText(route, (await policyOf($)).policy)}`)
    if (round) lines.push(`grilling round open · ${plural(round.length, 'question')} · ${answeredCount(round, answers)} answered`)
    return { text: lines.join('\n') }
  })

  // The answer sheet: Accept or answer each question, then Send
  on('ui.render', { component: 'Pane', requestId: SHEET_PANE }, ($, e) => {
    const elements = $.ui.resolve(e)
    // A pane left up across a reload, whose round the module no longer holds
    if (!round) return elements.Text({ dimColor: true, children: ['No grilling round is open.'] })
    const questions = round
    // Redraws only when a question's answered state changes, so typing is not redrawn under the cursor
    const update = (number: number, answer: Answer | undefined) => {
      const before = answeredCount(questions, answers)
      const wasAccepted = answers.get(number)?.kind === 'accept'
      if (answer) answers.set(number, answer)
      else answers.delete(number)
      if (answeredCount(questions, answers) !== before || wasAccepted !== (answer?.kind === 'accept')) $.ui.invalidate('ui.render')
    }
    return sheetPane(questions, answers, {
      // Always a change of accepted state, so always a redraw: the field shows a typed answer cleared
      onAccept: (number) => update(number, answers.get(number)?.kind === 'accept' ? undefined : { kind: 'accept' }),
      // An emptied field takes back a typed answer, never an Accept
      onOverride: (number, text) => {
        if (text.trim()) update(number, { kind: 'override', text })
        else if (answers.get(number)?.kind === 'override') update(number, undefined)
      },
      onAcceptAll: () => {
        answers = acceptAll(questions, answers)
        $.ui.invalidate('ui.render')
      },
      onSend: () => void sendAnswers($),
    })(elements)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (!features.length) return next(e)
    noteSurface(e.surface)
    const elements = $.ui.resolve(e)
    const theirs = await next(e)
    const rows = bandRows({ ...info, surface: e.surface }, features, contributions, e.props.maxRows)
    return composeBand(elements, e.surface, rows, theirs, { columns: e.props.bodyColumns })
  })
}
