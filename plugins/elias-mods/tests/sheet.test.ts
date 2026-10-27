import { expect, test, type Engine } from 'claude-code/testing'
import type { On, PaneOpenArgs, PromptSubmitInput } from 'claude-code'
import { acceptAll, composeReply, isComplete, parseRound, sentToast, type Answer } from '../hooks/sheet.js'
import { MODS_DESIGN, ONE_BOLD, REVISITED, SKILL_REVIEW, WITH_TRAILER } from './rounds.js'

// Parsing synthetic rounds

test('an options-round table among ordinary questions', () => {
  const round = parseRound(MODS_DESIGN)
  expect(round.map((q) => q.number)).toEqual([1, 2, 3, 4])
  expect(round[0]?.title).toBe('Which panel to build first')
  // The options table is part of the question, not a question of its own
  expect(round[0]?.body).toContain('|---')
  expect(round[0]?.recommendation).toMatch(/^A, with the preview \(4\) added\./)
  expect(round[3]?.title).toBe('Can the preview use the network?')
})

test('multi-paragraph questions keep their lists and tables in the body', () => {
  const round = parseRound(SKILL_REVIEW)
  expect(round).toHaveLength(6)
  const third = round[2]
  expect(third?.title).toBe('Proposed dispositions for the remaining widgets.')
  expect(third?.body.split('\n\n').length).toBeGreaterThan(1)
  expect(third?.body).toContain('|---')
  expect(third?.recommendation).toBe('Accept as written.')
})

test('prose after the last question is not part of its recommendation', () => {
  const trailer = parseRound(WITH_TRAILER)
  expect(trailer).toHaveLength(4)
  expect(trailer[3]?.recommendation).toMatch(/^\(a\)\. It's one update/)
  expect(trailer[3]?.recommendation).not.toMatch(/definition of done|Once you answer/)

  const revisited = parseRound(REVISITED)
  expect(revisited.map((q) => [q.number, q.title])).toEqual([[17, 'So, one preview renderer per sample?']])
  expect(revisited[0]?.recommendation).not.toContain('If you confirm')
})

test('`**Q8 - Title**` headers, empty bodies, and an Insight block after the round', () => {
  const round = parseRound(ONE_BOLD)
  expect(round.map((q) => q.number)).toEqual([8, 9, 10, 11, 12])
  expect(round[0]?.title).toBe('Where the sample labels live')
  // Emphasis is dropped from the recommendation the sheet shows
  expect(round[0]?.recommendation).toMatch(/^\(b\)\. The labels stay/)
  expect(round[2]).toMatchObject({ title: 'What surrounds the preview', body: '' })
  expect(round[4]?.recommendation).not.toContain('Insight')
})

test('bold text in the body does not become the title', () => {
  const round = parseRound('❓ **Q1 - Where it lives**: **Key** point first.\n\n➡️ Here.')
  expect(round.map((q) => [q.title, q.body])).toEqual([['Where it lives', '**Key** point first.']])
})

test('anything short of a whole round parses to nothing', () => {
  expect(parseRound('')).toEqual([])
  expect(parseRound('Done. The tests pass and the commit is in.')).toEqual([])
  // A question whose recommendation was never written
  expect(parseRound(WITH_TRAILER.slice(0, WITH_TRAILER.lastIndexOf('➡️')))).toEqual([])
  // A header the parser cannot read
  expect(parseRound('❓ Q1 Which one?\n\n➡️ This one.')).toEqual([])
  // The same number twice
  expect(parseRound('❓ **Q1** - **One**: a\n\n➡️ yes\n\n❓ **Q1** - **Again**: b\n\n➡️ no')).toEqual([])
  // The format quoted in a code fence, as when explaining the grilling skill
  expect(parseRound('The skill writes:\n\n```\n❓ **Q1** - **<question title>**: <body>\n\n➡️ <your recommended answer>\n```')).toEqual([])
})

test('the reply reads as Elias types it', () => {
  const round = parseRound(MODS_DESIGN)
  const answers = new Map<number, Answer>([
    [1, { kind: 'accept' }],
    [2, { kind: 'override', text: '  Keep it for now.  ' }],
  ])
  expect(isComplete(round, answers)).toBe(false)
  const all = acceptAll(round, answers)
  // Accept all keeps a typed answer
  expect(all.get(2)).toEqual({ kind: 'override', text: '  Keep it for now.  ' })
  expect(isComplete(round, all)).toBe(true)
  expect(composeReply(round, all)).toBe('Q1 agreed.\nQ2: Keep it for now.\nQ3 agreed.\nQ4 agreed.')
  // A field typed into and emptied is no answer
  expect(isComplete(round, new Map([...all, [3, { kind: 'override', text: ' ' }]]))).toBe(false)
  // The Sent toast keeps to one short line
  const toast = sentToast(`Q1: ${'long answer '.repeat(20)}\nQ2 agreed.`)
  expect(toast).toHaveLength(100)
  expect(toast.endsWith('…')).toBe(true)
})

// The sheet in a session

const PANE = {
  plugin: 'elias-mods',
  component: 'Pane',
  requestId: 'answer-sheet',
  viewport: { columns: 160, rows: 50 },
  props: { title: 'Grilling round', isFocused: false, bodyColumns: 70, placement: 'dock', scroll: { offset: 0, bodyRows: 40 }, view: {} },
} as const

const BAND = {
  plugin: 'elias-mods',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  surface: 'desktop',
  viewport: { columns: 160, rows: 50 },
  props: { hasSurvey: false, isWorking: false, maxRows: 6, bodyColumns: 150, scroll: { offset: 0, bodyRows: 6 }, view: {} },
} as const

// The engine beneath the plugin: panes it opens and closes, prompts it submits, toasts
function stubEngine(on: On, { dropSubmit = false } = {}) {
  const seen = { opened: [] as PaneOpenArgs[], closed: [] as string[], submitted: [] as PromptSubmitInput[], toasts: [] as string[] }
  on('ui.open', ($, e) => {
    seen.opened.push(e)
    return { value: { isPlaced: true as const } }
  })
  on('ui.close', ($, e) => {
    seen.closed.push(e.id)
    return { value: undefined }
  })
  on('prompt.submit', ($, e) => {
    seen.submitted.push(e)
    return dropSubmit ? { drop: 'a hook refused it' } : { text: e.text, origin: e.origin }
  })
  on('ui.toast', ($, e) => {
    seen.toasts.push(e.text)
    return { value: undefined }
  })
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  on('store.get', () => ({ value: undefined }))
  on('session.surfaces', () => ({ value: ['desktop'] }))
  on('fs.exists', () => ({ value: false }))
  on('ui.render', () => ({ type: 'Box', props: {}, children: [] }))
  return seen
}

const ended = (answer: string, extra: { agentId?: string; reason?: 'answer' | 'aborted' } = {}) => ({
  reason: extra.reason ?? ('answer' as const),
  answer,
  durationMs: 1000,
  isAborted: extra.reason === 'aborted',
  turnId: 'turn-1',
  ...(extra.agentId ? { agentId: extra.agentId } : {}),
})

const mountSheet = ($: Engine) => $.ui.mount({ ...PANE, surface: 'desktop' })

async function bandRow($: Engine) {
  const ui = await $.ui.mount(BAND)
  const found = await ui.find({ type: 'Text', text: /^❓ grilling round/ })
  await ui.unmount()
  return found
}

test('a turn ending in a round opens the sheet, and Send submits the reply as Elias', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(MODS_DESIGN))
  // Opened without taking the keyboard from the prompt
  expect(seen.opened).toEqual([{ id: 'answer-sheet', title: 'Grilling round · 4 questions', closeOnEscape: true }])
  expect((await bandRow($))?.text).toBe('❓ grilling round · 4 questions')

  const ui = await mountSheet($)
  expect(await ui.find({ type: 'Text', text: 'Q1 · Which panel to build first' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /^➡️ Remove it\./ })).toBeDefined()
  // Send waits for every question
  expect(await ui.find({ type: 'Button', key: 'send' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: '0 of 4 answered' })).toBeDefined()

  await ui.press({ key: 'accept-1' })
  expect((await ui.find({ type: 'Button', key: 'accept-1' }))?.props.label).toBe('Accepted ✓')
  await ui.input({ key: 'override-2', text: 'Keep the debug label for now.', kind: 'change' })
  expect(await ui.find({ type: 'Text', text: '2 of 4 answered' })).toBeDefined()
  await ui.press({ key: 'accept-all' })
  expect(await ui.find({ type: 'Button', key: 'accept-all' })).toBeUndefined()

  await ui.press({ key: 'send' })
  expect(seen.submitted.map((e) => e.text)).toEqual(['Q1 agreed.\nQ2: Keep the debug label for now.\nQ3 agreed.\nQ4 agreed.'])
  expect(seen.submitted[0]?.origin).toMatchObject({ kind: 'plugin', asUser: true })
  // Shown at once, since Desktop draws the reply in the thread seconds later
  expect(seen.toasts).toEqual(['Sent: Q1 agreed. · Q2: Keep the debug label for now. · Q3 agreed. · Q4 agreed.'])
  expect(seen.closed).toEqual(['answer-sheet'])
  expect(await bandRow($)).toBeUndefined()
  await ui.unmount()
})

test('Accept takes back a typed answer, and an emptied field takes back nothing else', async ($, on) => {
  stubEngine(on)
  await $.turn.complete(ended(REVISITED))
  const ui = await mountSheet($)
  await ui.input({ key: 'override-17', text: 'Use the static renderer first.', kind: 'change' })
  await ui.press({ key: 'accept-17' })
  expect((await ui.find({ type: 'Input', key: 'override-17' }))?.props.value).toBe('')
  // Enter on the empty field leaves the Accept standing
  await ui.input({ key: 'override-17', text: '' })
  expect(await ui.find({ type: 'Button', key: 'send' })).toBeDefined()
  // A second press un-accepts
  await ui.press({ key: 'accept-17' })
  expect(await ui.find({ type: 'Text', text: '0 of 1 answered' })).toBeDefined()
  await ui.unmount()
})

test('the next turn closes the sheet: Elias answered by typing', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(MODS_DESIGN))
  const status = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(status.text).toContain('grilling round open · 4 questions · 0 answered')

  // Elias's prompt, then the turn it starts
  await $.prompt.submit({ text: '1. agreed 2. agreed', wait: false, origin: { kind: 'composer' } })
  expect(seen.closed).toEqual([])
  await $.turn.start({ text: '1. agreed 2. agreed', turnId: 'turn-2' })
  expect(seen.closed).toEqual(['answer-sheet'])
  expect(await bandRow($)).toBeUndefined()
  const after = await $.command.run({ command: 'elias-mods:elias-mods', args: '', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(after.text).not.toContain('grilling round')
})

test('a turn a notification starts leaves the round open', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(MODS_DESIGN))
  await $.prompt.submit({ text: 'Background task finished.', wait: false, origin: { kind: 'task-notification' } })
  await $.turn.start({ text: 'Background task finished.', turnId: 'turn-2' })
  // So does a continuation the engine starts with no prompt at all
  await $.turn.start({ text: '', turnId: 'turn-9' })
  expect(seen.closed).toEqual([])
  expect((await bandRow($))?.text).toBe('❓ grilling round · 4 questions')
})

test('an SDK-stamped prompt, as the Desktop app may send, closes the round', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(REVISITED))
  await $.prompt.submit({ text: 'Yes.', wait: false, origin: { kind: 'sdk' } })
  await $.turn.start({ text: 'Yes.', turnId: 'turn-2' })
  expect(seen.closed).toEqual(['answer-sheet'])
})

test('the band row reopens a closed sheet and hands it the keyboard', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(ONE_BOLD))
  const band = await $.ui.mount(BAND)
  await band.press({ key: 'answer-sheet' })
  expect(seen.opened.at(-1)).toEqual({ id: 'answer-sheet', title: 'Grilling round · 5 questions', closeOnEscape: true, focus: true })
  await band.unmount()
})

test('turns without a whole round, aborted turns and subagent turns draw nothing', async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended('Done. Tests pass.'))
  await $.turn.complete(ended(MODS_DESIGN, { reason: 'aborted' }))
  await $.turn.complete(ended(MODS_DESIGN, { agentId: 'agent-1' }))
  await $.turn.complete(ended(WITH_TRAILER.slice(0, WITH_TRAILER.lastIndexOf('➡️'))))
  expect(seen.opened).toEqual([])
  expect(await bandRow($)).toBeUndefined()
})

test('a refused submit keeps the sheet and says why', async ($, on) => {
  const seen = stubEngine(on, { dropSubmit: true })
  await $.turn.complete(ended(REVISITED))
  const ui = await mountSheet($)
  await ui.press({ key: 'accept-17' })
  await ui.press({ key: 'send' })
  expect(seen.toasts).toEqual(['Answers not sent: a hook refused it'])
  expect(seen.closed).toEqual([])
  // Still there to send again
  expect(await ui.find({ type: 'Button', key: 'send' })).toBeDefined()
  await ui.unmount()
})

test('the mobile app, which draws no Input, gets Accept alone', async ($, on) => {
  stubEngine(on)
  await $.turn.complete(ended(REVISITED))
  const ui = await $.ui.mount({ ...PANE, surface: 'mobile' })
  expect(await ui.find({ type: 'Button', key: 'accept-17' })).toBeDefined()
  await ui.unmount()
})

test('with answer_sheet off no round is read', { options: { answer_sheet: false } }, async ($, on) => {
  const seen = stubEngine(on)
  await $.turn.complete(ended(MODS_DESIGN))
  expect(seen.opened).toEqual([])
  expect(await bandRow($)).toBeUndefined()
})
