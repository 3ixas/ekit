import { expect, test, type Engine } from 'claude-code/testing'
import type { On, RenderSurface, SessionUsage } from 'claude-code'
import {
  FEATURES,
  HISTORY_TURNS,
  enabledFeatures,
  formatResetIn,
  handoffThreshold,
  limitsText,
  recordTurn,
  sparklineText,
} from '../hooks/band.js'

// What Claude Code passes to an AbovePrompt hook, apart from the app
const BAND = {
  plugin: 'elias-mods',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  viewport: { columns: 120, rows: 40 },
  props: {
    hasSurvey: false,
    isWorking: false,
    maxRows: 6,
    bodyColumns: 110,
    scroll: { offset: 0, bodyRows: 6 },
    view: {},
  },
} as const

// Stubs every test needs before its first call on $
function stubSession(on: On, saved: Map<string, unknown>, surfaces: RenderSurface[]) {
  on('session.start', () => ({ cwd: '/work' }))
  on('session.surfaces', () => ({ value: surfaces }))
  on('session.id', () => ({ value: 'session-1' }))
  on('session.version', () => ({ value: { version: '2.1.300', base: '2.1.300', builtAt: '2026-10-20T00:00:00Z' } }))
  on('store.set', ($, e) => {
    saved.set(e.key, e.value)
    return { value: undefined }
  })
  // Stands for what mods after this one draw in the band
  on('ui.render', () => ({ type: 'Text', props: {}, children: ['drawn after elias-mods'] }))
}

test('the band shows the placeholder row on Desktop and keeps later mods', async ($, on) => {
  const saved = new Map<string, unknown>()
  stubSession(on, saved, ['desktop'])
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(
    await ui.find({ type: 'Text', text: /^elias-mods · desktop · Claude Code 2\.1\.300 · features: context barometer, skill route, answer sheet$/ }),
  ).toBeDefined()
  expect(await ui.find({ type: 'Text', text: 'drawn after elias-mods' })).toBeDefined()
  await ui.unmount()
})

test('the band draws in the terminal too', async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: /^elias-mods · terminal · / })).toBeDefined()
  await ui.unmount()
})

test('/elias-mods reports the same status as text and the load is recorded', async ($, on) => {
  const saved = new Map<string, unknown>()
  stubSession(on, saved, ['desktop'])
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^elias-mods · desktop · Claude Code 2\.1\.300 · features: /)
  expect(saved.get('lastLoad')).toMatchObject({
    surface: 'desktop',
    version: '2.1.300',
    features: ['barometer', 'skill_route', 'answer_sheet'],
  })
})

test('the Desktop app attaching after start is recorded and named', async ($, on) => {
  const saved = new Map<string, unknown>()
  // A Desktop session starts with no surface; the app attaches afterwards
  stubSession(on, saved, [])
  on('session.attach', ($, e) => ({ clientId: e.clientId }))
  await $.session.start({ surface: null, isInteractive: true, cwd: '/work' })
  expect(saved.get('lastLoad')).toMatchObject({ surface: 'headless', version: '2.1.300' })

  await $.session.attach({ surface: 'desktop', clientId: 'app' })
  expect(saved.get('lastAttach')).toMatchObject({ surface: 'desktop', version: '2.1.300', session: 'session-1' })
})

// Desktop's roster read empty when /elias-mods ran on 2026-10-24, while the band said desktop
test('/elias-mods names the app that attached when the roster reads empty', async ($, on) => {
  stubSession(on, new Map(), [])
  on('session.attach', ($, e) => ({ clientId: e.clientId }))
  await $.session.start({ surface: null, isInteractive: true, cwd: '/work' })
  await $.session.attach({ surface: 'desktop', clientId: 'app' })

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^elias-mods · desktop · /)
})

test('/elias-mods names the surface that drew the band when nothing attached', async ($, on) => {
  stubSession(on, new Map(), [])
  await $.session.start({ surface: null, isInteractive: true, cwd: '/work' })
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.unmount()

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^elias-mods · desktop · /)
})

test('/elias-mods says headless where nothing attached or drew', async ($, on) => {
  stubSession(on, new Map(), [])
  await $.session.start({ surface: null, isInteractive: true, cwd: '/work' })

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^elias-mods · headless · /)
})

test('each feature is on unless its option is set to false', () => {
  expect(enabledFeatures(undefined).map((f) => f.id)).toEqual(FEATURES.map((f) => f.id))
  expect(enabledFeatures({ barometer: false, answer_sheet: false }).map((f) => f.id)).toEqual(['skill_route'])
})

// Context barometer (#7)

const MINUTE = 60_000

// A main-thread turn: what $.session.usage() reports, then the measurement the engine raises
function usageAt(percent: number, rateLimits: SessionUsage['rateLimits'] = []): SessionUsage {
  return { startedAt: 0, context: { tokens: percent * 2000, window: 200_000, percent }, rateLimits }
}

async function turns($: Engine, current: { usage: SessionUsage }, usages: readonly SessionUsage[]) {
  for (const usage of usages) {
    current.usage = usage
    await $.session.measure({ context: usage.context, rateLimits: usage.rateLimits, changed: ['context'] })
  }
}

function stubUsage(on: On) {
  const current = { usage: usageAt(0) }
  on('session.usage', () => ({ value: current.usage }))
  // The engine echoes which units moved
  on('session.measure', ($, e) => ({ changed: e.changed }))
  return current
}

test('Desktop draws the context fill and an Svg sparkline in place of the placeholder', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(10), usageAt(25), usageAt(40)])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: 'context 40% · 80k/200k' })).toBeDefined()
  const svg = await ui.find({ type: 'Svg' })
  const source = String(svg?.props.source)
  // One point per turn on a 0–100 scale, and the 70% threshold dashed
  expect(source).toContain('<polyline points="1.0,15.4 48.0,13.0 95.0,10.6"')
  expect(source).toContain('y1="5.8" y2="5.8" stroke="#d9a441" stroke-width="1" stroke-dasharray="3 3"')
  expect(svg?.props.alt).toBe('Context fill over the last 3 turns: 10%, 25%, 40%')
  // No limits reported, so no limits Text
  expect(await ui.findAll({ type: 'Text' })).toHaveLength(2)
  expect(await ui.find({ type: 'Text', text: /^elias-mods · / })).toBeUndefined()
  expect(await ui.find({ type: 'Button', key: 'handoff' })).toBeUndefined()
  await ui.unmount()
})

test('Desktop shows plan limits beside the sparkline', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  const resetsAt = new Date(Date.now() + 3 * 1440 * MINUTE + 4 * 60 * MINUTE + 20_000).toISOString()
  await turns($, current, [usageAt(20, [{ kind: 'five_hour', percentUsed: 34 }, { kind: 'seven_day', percentUsed: 12, resetsAt }])])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: '5h 34% · 7d 12% resets 3d4h' })).toBeDefined()
  await ui.unmount()
})

test('surfaces other than Desktop get the text line, mobile included', async ($, on) => {
  stubSession(on, new Map(), ['mobile'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'mobile', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(10)])

  const ui = await $.ui.mount({ ...BAND, surface: 'mobile' })
  expect(await ui.find({ type: 'Svg' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'context 10% · 20k/200k ▁' })).toBeDefined()
  await ui.unmount()
})

test('a Handoff that cannot start says so in a toast', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  // Nothing answers /handoff, as when the skill is not installed
  const toasts: string[] = []
  const failed = new Promise<void>((resolve) => {
    on('ui.toast', ($, e) => {
      toasts.push(e.text)
      if (e.text.startsWith('Handoff did not start')) resolve()
      return { value: undefined }
    })
  })
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(80)])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  await ui.press({ key: 'handoff' })
  await failed
  // The press is acknowledged at once, since /handoff waits for the session to go idle
  expect(toasts[0]).toBe('Handoff starts as soon as Claude is idle')
  expect(toasts[1]).toMatch(/^Handoff did not start: .*command\.run/)
  await ui.unmount()
})

test('the terminal gets the barometer as one line of text', async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(10), usageAt(55)])

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await ui.find({ type: 'Svg' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'context 55% · 110k/200k ▁▅' })).toBeDefined()
  await ui.unmount()
})

test('/elias-mods adds the barometer line once a turn has been measured', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(30)])

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/\ncontext 30% · 60k\/200k ▃$/)
})

test('plan limits show with their reset time, and are left out when there are none', async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  const resetsAt = new Date(Date.now() + 130 * MINUTE + 20_000).toISOString()
  await turns($, current, [usageAt(20, [{ kind: 'five_hour', percentUsed: 34, resetsAt }, { kind: 'seven_day', percentUsed: 12 }])])

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: 'context 20% · 40k/200k ▂ · 5h 34% resets 2h10m · 7d 12%' })).toBeDefined()
  await ui.unmount()

  await turns($, current, [usageAt(21)])
  const again = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await again.find({ type: 'Text', text: 'context 21% · 42k/200k ▂▂' })).toBeDefined()
  await again.unmount()
})

test('at 70% the Handoff button appears and starts /handoff', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  // Settles when the press runs /handoff; the test times out if it never does
  const ran = new Promise<string>((resolve) => {
    on('command.run', { command: 'handoff' }, ($, e) => {
      resolve(e.command)
      return { text: '' }
    })
  })
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })

  await turns($, current, [usageAt(69)])
  const below = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await below.find({ type: 'Button', key: 'handoff' })).toBeUndefined()
  await below.unmount()

  await turns($, current, [usageAt(70)])
  const at = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await at.find({ type: 'Button', text: 'Handoff' })).toBeDefined()
  await at.press({ key: 'handoff' })
  expect(await ran).toBe('handoff')
  await at.unmount()
})

test('handoff_at moves the threshold', { options: { handoff_at: 50 } }, async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(50)])

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await ui.find({ type: 'Button', key: 'handoff' })).toBeDefined()
  await ui.unmount()
})

test('with the barometer off, a measured turn draws nothing new', { options: { barometer: false } }, async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(90)])

  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Text', text: /^context / })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: /features: skill route, answer sheet$/ })).toBeDefined()
  await ui.unmount()
})

test('a rate-limit-only measurement updates limits without adding a sparkline point', async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(40)])
  current.usage = usageAt(40, [{ kind: 'five_hour', percentUsed: 80 }])
  await $.session.measure({ context: current.usage.context, rateLimits: current.usage.rateLimits, changed: ['rateLimits'] })

  const ui = await $.ui.mount({ ...BAND, surface: 'terminal' })
  expect(await ui.find({ type: 'Text', text: 'context 40% · 80k/200k ▄ · 5h 80%' })).toBeDefined()
  await ui.unmount()
})

test('barometer thresholds, history and formatting', () => {
  expect(handoffThreshold(undefined)).toBe(70)
  expect(handoffThreshold({ handoff_at: 85 })).toBe(85)
  expect(handoffThreshold({ handoff_at: 0 })).toBe(70)
  expect(handoffThreshold({ handoff_at: 'high' })).toBe(70)

  const full = Array.from({ length: HISTORY_TURNS + 5 }, (_, i) => i).reduce<number[]>((history, percent) => recordTurn(history, percent), [])
  expect(full).toHaveLength(HISTORY_TURNS)
  expect(full[0]).toBe(5)
  expect(recordTurn([10], undefined)).toEqual([10])

  expect(sparklineText([0, 50, 99, 100, 140])).toBe('▁▅███')

  const now = Date.parse('2026-10-23T12:00:00Z')
  expect(formatResetIn(undefined, now)).toBe('')
  expect(formatResetIn('not a date', now)).toBe('')
  expect(formatResetIn('2026-10-23T11:00:00Z', now)).toBe('')
  expect(formatResetIn('2026-10-23T12:12:00Z', now)).toBe('12m')
  expect(formatResetIn('2026-10-26T16:00:00Z', now)).toBe('3d4h')
  expect(limitsText([], now)).toBe('')
  expect(limitsText([{ kind: 'spend_limit', percentUsed: 101.5 }], now)).toBe('spend 101.5%')
})

// Shared band layout (#11)

const LIMITS = [{ kind: 'five_hour', percentUsed: 21, resetsAt: new Date(Date.now() + 83 * MINUTE).toISOString() }] as const

// All three rows at once: two measured turns, a skill loaded in a turn, and a turn
// that ends with a grilling round
async function everyRow($: Engine, on: On) {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  on('ui.open', () => ({ value: { isPlaced: true as const } }))
  on('fs.exists', () => ({ value: false }))
  on('skill.prompt', ($, e) => ({ text: e.text }))
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(30, [...LIMITS]), usageAt(35, [...LIMITS])])
  await $.turn.start({ text: 'grill me', turnId: 'turn-1' })
  await $.skill.prompt({ skill: 'grilling', text: 'grilling instructions' })
  await $.turn.complete({ reason: 'answer', answer: '❓ **Q1** - **One**: a\n\n➡️ Yes.', durationMs: 1, isAborted: false, turnId: 'turn-1' })
}

const ROW_KEYS = FEATURES.map((feature) => feature.id)

// The keys of the band's rows, top to bottom
async function rowKeys($: Engine, props: { maxRows?: number } = {}) {
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, ...props } })
  const boxes = await ui.findAll({ type: 'Box' })
  await ui.unmount()
  return boxes.flatMap((box) => (ROW_KEYS.includes(String(box.key)) || box.key === 'placeholder' ? [String(box.key)] : []))
}

test('the rows keep one order: barometer, skill route, then the grilling round nearest the prompt', async ($, on) => {
  await everyRow($, on)
  expect(await rowKeys($)).toEqual(['barometer', 'skill_route', 'answer_sheet'])
})

test('short of rows, the skill route goes first, then the barometer; the round stays', async ($, on) => {
  await everyRow($, on)
  expect(await rowKeys($, { maxRows: 2 })).toEqual(['barometer', 'answer_sheet'])
  expect(await rowKeys($, { maxRows: 1 })).toEqual(['answer_sheet'])
  // A band with no room still keeps the row Elias acts on
  expect(await rowKeys($, { maxRows: 0 })).toEqual(['answer_sheet'])
})

test('a narrow band drops plan limits, then the sparkline, never the context reading', async ($, on) => {
  await everyRow($, on)
  const at = async (bodyColumns: number) => {
    const ui = await $.ui.mount({ ...BAND, surface: 'desktop', props: { ...BAND.props, bodyColumns } })
    const seen = {
      context: (await ui.find({ type: 'Text', text: 'context 35% · 70k/200k' })) !== undefined,
      spark: (await ui.find({ type: 'Svg' })) !== undefined,
      limits: (await ui.find({ type: 'Text', text: /^5h 21%/ })) !== undefined,
    }
    await ui.unmount()
    return seen
  }
  expect(await at(110)).toEqual({ context: true, spark: true, limits: true })
  expect(await at(60)).toEqual({ context: true, spark: true, limits: false })
  expect(await at(40)).toEqual({ context: true, spark: false, limits: false })
})

test('the terminal line drops plan limits, then the block sparkline, as the band narrows', async ($, on) => {
  stubSession(on, new Map(), ['terminal'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'terminal', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(30, [...LIMITS]), usageAt(35, [...LIMITS])])
  const line = async (bodyColumns: number) => {
    const ui = await $.ui.mount({ ...BAND, surface: 'terminal', props: { ...BAND.props, bodyColumns } })
    const text = (await ui.find({ type: 'Text', text: /^context / }))?.text
    await ui.unmount()
    return text
  }
  expect(await line(110)).toMatch(/^context 35% · 70k\/200k ▃▃ · 5h 21% resets /)
  expect(await line(60)).toBe('context 35% · 70k/200k ▃▃')
  expect(await line(40)).toBe('context 35% · 70k/200k')
})

for (const off of ['barometer', 'skill_route', 'answer_sheet']) {
  test(`with ${off} off the other rows keep their order and no placeholder shows`, { options: { [off]: false } }, async ($, on) => {
    await everyRow($, on)
    expect(await rowKeys($)).toEqual(['barometer', 'skill_route', 'answer_sheet'].filter((key) => key !== off))
  })
}

test('one measured turn draws no Svg dot on Desktop', async ($, on) => {
  stubSession(on, new Map(), ['desktop'])
  const current = stubUsage(on)
  await $.session.start({ surface: 'desktop', isInteractive: true, cwd: '/work' })
  await turns($, current, [usageAt(35)])
  const ui = await $.ui.mount({ ...BAND, surface: 'desktop' })
  expect(await ui.find({ type: 'Svg' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'context 35% · 70k/200k' })).toBeDefined()
  await ui.unmount()
})
