import { expect, test, type Engine } from 'claude-code/testing'
import type { On } from 'claude-code'
import {
  buildPolicy,
  chipText,
  classify,
  guardReport,
  loadPolicy,
  policyFromProjection,
  projectionPath,
  readGuardLog,
  repositoryCandidates,
  type RoutePolicy,
} from '../hooks/route.js'

// What Claude Code passes to an AbovePrompt hook
const BAND = {
  plugin: 'elias-mods',
  component: 'AbovePrompt',
  requestId: 'above-prompt',
  surface: 'desktop',
  viewport: { columns: 120, rows: 40 },
  props: { hasSurvey: false, isWorking: false, maxRows: 6, bodyColumns: 110, scroll: { offset: 0, bodyRows: 6 }, view: {} },
} as const

// A repository as loadPolicy reads it: skills/<group>/<id>/metadata.json, invocation lists as written
const SKILLS: Record<string, Record<string, string[]>> = {
  'software-workflows': { implement: ['automatic'], wayfinder: ['explicit'], release: ['explicit'], 'domain-modeling': ['supporting'] },
  'engineering-specialists': { tdd: ['supporting'], typescript: ['supporting'], ci: ['automatic', 'supporting'] },
}

// Stubs the engine beneath the plugin: the files, the store, and what a tool call,
// a skill expansion and a turn start do when nothing refuses them
function stubEngine(on: On, { metadata = true, listFails = false, refusedBelow = new Set<string>() } = {}) {
  const store = new Map<string, unknown>()
  on('fs.exists', ($, e) => ({ value: metadata && e.path.endsWith('/scripts/skills.py') }))
  on('fs.list', ($, e) => {
    if (listFails) throw new Error('disk on fire')
    const [, group] = e.path.match(/\/skills(?:\/([^/]+))?$/) ?? []
    const names = group ? Object.keys(SKILLS[group] ?? {}) : Object.keys(SKILLS)
    return { value: names.map((name) => ({ name, kind: 'dir' as const, size: 0, mtimeMs: 0, isLink: false })) }
  })
  on('fs.read', ($, e) => {
    const [, group = '', id = ''] = e.path.match(/\/skills\/([^/]+)\/([^/]+)\/metadata\.json$/) ?? []
    return { value: JSON.stringify({ id, invocation: SKILLS[group]?.[id] }) }
  })
  on('store.get', ($, e) => ({ value: store.get(e.key) }))
  on('store.set', ($, e) => {
    store.set(e.key, e.value)
    return { value: undefined }
  })
  // refusedBelow: skills a permission rule or a later hook refuses once
  on('tool.call', ($, e) => {
    if (e.tool === 'Skill' && refusedBelow.delete(e.skill)) return { deny: 'refused below' }
    return { result: { success: true, commandName: e.tool === 'Skill' ? e.skill : e.tool } }
  })
  on('skill.prompt', ($, e) => ({ text: e.text }))
  on('prompt.submit', ($, e) => ({ text: e.text }))
  on('turn.start', ($, e) => ({ turnId: e.turnId }))
  on('turn.complete', ($, e) => ({ text: e.answer }))
  // Stands for what mods after this one draw in the band
  on('ui.render', () => ({ type: 'Box', props: {}, children: [] }))
  return store
}

// The model loading a skill: the Skill tool call, then, unless refused, its expansion
async function load($: Engine, skill: string) {
  const call = await $.tool.call({ tool: 'Skill', skill })
  if (!call.deny) await $.skill.prompt({ skill, text: `${skill} instructions` })
  return call
}

// Elias pressing Enter in the composer; turnId when typed over a running turn
const typed = (text: string, turnId?: string) => ({ text, wait: Boolean(turnId), origin: { kind: 'composer' as const }, ...(turnId ? { turnId } : {}) })
const answered = (turnId: string, agentId?: string) => ({ reason: 'answer' as const, answer: 'done', durationMs: 1000, isAborted: false, turnId, ...(agentId ? { agentId } : {}) })

// A main-thread turn starting, as the engine raises it after Elias's prompt
const begin = ($: Engine, turnId = 'turn-1') => $.turn.start({ text: 'prompt', turnId })
// Elias typing /skill: it expands between turns, before its turn starts
const typedSkill = ($: Engine, skill: string) => $.skill.prompt({ skill, text: `${skill} instructions` })

async function chip($: Engine) {
  const ui = await $.ui.mount(BAND)
  const found = await ui.find({ type: 'Text', text: /^skills / })
  await ui.unmount()
  return found
}

test('a supporting skill loaded under a primary one passes and the chip shows the chain', async ($, on) => {
  const store = stubEngine(on)
  // Typed by Elias: an expansion without a Skill tool call, before the turn starts
  await typedSkill($, 'implement')
  await begin($)
  expect((await load($, 'tdd')).deny).toBeUndefined()
  expect((await load($, 'typescript')).deny).toBeUndefined()

  const found = await chip($)
  expect(found?.text).toBe('skills implement → tdd · typescript')
  expect(found?.props.dimColor).toBe(true)
  expect(store.get('guardLog')).toBeUndefined()
})

test('a supporting skill with no primary this turn is warned and logged, not refused', async ($, on) => {
  const store = stubEngine(on)
  await begin($)
  const call = await load($, 'domain-modeling')
  expect(call.deny).toBeUndefined()

  const found = await chip($)
  expect(found?.text).toBe('skills ⚠ domain-modeling')
  expect(found?.props.dimColor).toBe(false)
  const log = store.get('guardLog') as Record<string, unknown>[]
  expect(log).toHaveLength(1)
  // Names and times only: no prompt text, no session
  expect(Object.keys(log[0] ?? {}).sort()).toEqual(['at', 'kind', 'skill'])
  expect(log[0]).toMatchObject({ skill: 'domain-modeling', kind: 'supporting-without-primary' })
})

test('skill_guard_refuse turns the warning into a deny Claude can act on', { options: { skill_guard_refuse: true } }, async ($, on) => {
  stubEngine(on)
  await begin($)
  const call = await load($, 'domain-modeling')
  expect(call.deny).toMatch(/^domain-modeling is a supporting-only skill .* Load the primary skill that owns the request first/)
  expect((await chip($))?.text).toBe('skills ⚠ domain-modeling')
})

test('a model-loaded requested workflow needs no second slash command', async ($, on) => {
  const store = stubEngine(on)
  await begin($)
  expect((await load($, 'wayfinder')).deny).toBeUndefined()
  expect((await load($, 'domain-modeling')).deny).toBeUndefined()
  expect(store.get('guardLog')).toBeUndefined()
  expect((await chip($))?.text).toBe('skills wayfinder → domain-modeling')
})

test('an explicit-only skill Elias typed owns the turn for its supporting loads', async ($, on) => {
  const store = stubEngine(on)
  await typedSkill($, 'wayfinder')
  await begin($)
  expect((await load($, 'domain-modeling')).deny).toBeUndefined()
  expect((await chip($))?.text).toBe('skills wayfinder → domain-modeling')
  expect(store.get('guardLog')).toBeUndefined()
})

test('multiple requested workflow loads remain available in refuse mode', { options: { skill_guard_refuse: true } }, async ($, on) => {
  const store = stubEngine(on)
  await begin($)
  expect((await load($, 'wayfinder')).deny).toBeUndefined()
  expect((await load($, 'release')).deny).toBeUndefined()
  expect((await load($, 'domain-modeling')).deny).toBeUndefined()
  expect(store.get('guardLog')).toBeUndefined()
  expect((await chip($))?.text).toBe('skills wayfinder → release → domain-modeling')
})

test('a warned load refused further down leaves no warning behind', async ($, on) => {
  stubEngine(on, { refusedBelow: new Set(['domain-modeling']) })
  await begin($)
  expect((await load($, 'domain-modeling')).deny).toBe('refused below')
  await load($, 'implement')
  expect((await load($, 'domain-modeling')).deny).toBeUndefined()
  expect((await chip($))?.text).toBe('skills implement → domain-modeling')
})

test('a policy read that fails leaves the guard off without breaking the chip', async ($, on) => {
  stubEngine(on, { listFails: true })
  await begin($)
  expect((await load($, 'wayfinder')).deny).toBeUndefined()
  await load($, 'implement')
  expect((await chip($))?.text).toBe('skills wayfinder → implement')
  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: 'guard', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^Skill guard: warn mode · routing policy unavailable: /)
})

test('without skill metadata the guard stays off and the chip still lists loads', async ($, on) => {
  const store = stubEngine(on, { metadata: false })
  await begin($)
  expect((await load($, 'domain-modeling')).deny).toBeUndefined()
  expect((await load($, 'wayfinder')).deny).toBeUndefined()

  expect((await chip($))?.text).toBe('skills domain-modeling → wayfinder')
  expect(store.get('guardLog')).toBeUndefined()
  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: 'guard', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  expect(answer.text).toMatch(/^Skill guard: warn mode · routing policy unavailable: skill metadata not found\n/)
})

test('a typed skill replaces the last turn and survives the turn it starts', async ($, on) => {
  stubEngine(on)
  await begin($, 'turn-0')
  await load($, 'implement')
  await $.turn.complete(answered('turn-0'))
  // The row keeps the finished turn's skills until the next turn starts
  expect((await chip($))?.text).toBe('skills implement')

  // Seen live for a typed /typescript: submit, then expansion, then the turn
  await $.prompt.submit(typed('/typescript'))
  await typedSkill($, 'typescript')
  expect((await chip($))?.text).toBe('skills implement')
  await $.turn.start({ text: 'typescript instructions', turnId: 'turn-1' })
  expect((await chip($))?.text).toBe('skills typescript')
})

test('a refused background load does not hide a later typed skill', async ($, on) => {
  stubEngine(on, { refusedBelow: new Set(['tdd']) })
  const fromSubagent = { tool: 'Skill' as const, skill: 'tdd', agentId: 'agent-1' }
  expect((await $.tool.call(fromSubagent)).deny).toBe('refused below')
  await typedSkill($, 'tdd')
  await begin($)
  expect((await chip($))?.text).toBe('skills tdd')
})

test('loads seen before the module knew a turn was running end with that turn', async ($, on) => {
  stubEngine(on)
  // Reloaded mid-turn: no turn.start seen, so these wait as if typed
  await load($, 'implement')
  await $.turn.complete(answered('turn-1'))
  await typedSkill($, 'typescript')
  await begin($, 'turn-2')
  expect((await chip($))?.text).toBe('skills typescript')
})

test('a background subagent loading a skill between turns joins no turn', async ($, on) => {
  const store = stubEngine(on)
  await begin($, 'turn-1')
  await load($, 'implement')
  await $.turn.complete(answered('turn-1'))

  // A subagent's call carries its agentId as the engine raises it; $.tool.call's
  // own type leaves agentId out, so the call is passed as a value, not a literal
  const fromSubagent = { tool: 'Skill' as const, skill: 'tdd', agentId: 'agent-1' }
  const call = await $.tool.call(fromSubagent)
  expect(call.deny).toBeUndefined()
  await $.skill.prompt({ skill: 'tdd', text: 'tdd instructions' })
  expect((await chip($))?.text).toBe('skills implement')
  expect(store.get('guardLog')).toBeUndefined()

  // The next turn starts clean: implement no longer owns anything
  await begin($, 'turn-2')
  expect(await chip($)).toBeUndefined()
  await load($, 'tdd')
  expect((await chip($))?.text).toBe('skills ⚠ tdd')
})

test('the chip clears when the next turn starts, queued or not, and not before', async ($, on) => {
  stubEngine(on)
  await $.turn.start({ text: 'first', turnId: 'turn-1' })
  await $.skill.prompt({ skill: 'implement', text: 'implement instructions' })
  // Typed over the running turn, or a prompt no turn ever runs: nothing clears
  await $.prompt.submit(typed('later', 'turn-1'))
  await $.prompt.submit(typed('dropped'))
  expect((await chip($))?.text).toBe('skills implement')

  // A subagent finishing inside the turn does not end it: implement still owns tdd
  await $.turn.complete(answered('sub-1', 'agent-1'))
  await load($, 'tdd')
  expect((await chip($))?.text).toBe('skills implement → tdd')

  await $.turn.complete(answered('turn-1'))
  // The queued prompt's own turn
  await $.turn.start({ text: 'later', turnId: 'turn-2' })
  expect(await chip($)).toBeUndefined()
  // A primary from the turn before no longer covers a supporting load
  await load($, 'tdd')
  expect((await chip($))?.text).toBe('skills ⚠ tdd')
})

test('/elias-mods guard reports how often the guard would have fired', async ($, on) => {
  stubEngine(on)
  await begin($)
  await load($, 'domain-modeling')
  await load($, 'domain-modeling')
  await load($, 'tdd')
  await load($, 'wayfinder')

  const answer = await $.command.run({ command: 'elias-mods:elias-mods', args: 'guard', origin: { kind: 'composer' }, presentation: { isFullscreen: false, columns: 120 } })
  const today = new Date().toISOString().slice(0, 10)
  expect(answer.text).toBe(
    [
      "Skill guard: warn mode · 7 skills' metadata read",
      `Supporting-only loads with no primary skill: 3 since ${today} (domain-modeling ×2, tdd ×1)`,
      'Historical explicit-only redirects (no longer enforced): none',
    ].join('\n'),
  )
})

test('with skill_route off nothing is judged or drawn', { options: { skill_route: false } }, async ($, on) => {
  const store = stubEngine(on)
  expect((await load($, 'wayfinder')).deny).toBeUndefined()
  expect(await chip($)).toBeUndefined()
  expect(store.get('guardLog')).toBeUndefined()
})

// The generated guidance as claude-sync writes it, trimmed to one skill per list
const PROJECTION = [
  '## Invocation policy',
  '',
  '- Automatically selectable skills: `implement`, `ci`. These may own a request when relevant.',
  '- Skills requiring explicit invocation: `wayfinder`, `migration`. These workflows remain model-loadable when requested.',
  '- Supporting-only skills must not own a request.',
  '',
  '## Supporting-only skills',
  '',
  '- `domain-modeling`',
  '- `tdd`',
].join('\n')

test('an installed copy reads the policy from the generated guidance', async () => {
  expect(projectionPath('/Users/elias/.claude/plugins/cache/elias-mods/0.1.0')).toBe('/Users/elias/.claude/rules/elias-agent-skills.md')
  expect(projectionPath('/repo/plugins/elias-mods')).toBeUndefined()
  // A generator that stops writing one of the lists makes the projection unusable
  expect(policyFromProjection(PROJECTION.replace('- Automatically selectable skills:', '- Auto skills:'))).toBeUndefined()
  expect(policyFromProjection(PROJECTION.replace('## Supporting-only skills', '## Helpers'))).toBeUndefined()
  // A skill on both the explicit and supporting lists is explicit, as classify has it
  expect(policyFromProjection(`${PROJECTION}\n- \`migration\``)?.get('migration')).toBe('explicit')
  expect([...(policyFromProjection(PROJECTION) ?? [])].sort()).toEqual([
    ['ci', 'primary'],
    ['domain-modeling', 'supporting'],
    ['implement', 'primary'],
    ['migration', 'explicit'],
    ['tdd', 'supporting'],
    ['wayfinder', 'explicit'],
  ])

  const io = {
    exists: async (path: string) => path === '/Users/elias/.claude/rules/elias-agent-skills.md',
    list: async () => [],
    read: async () => PROJECTION,
  }
  const loaded = await loadPolicy('/Users/elias/.claude/plugins/cache/elias-mods/0.1.0', io)
  expect(loaded.note).toBe('6 skills from the generated routing guidance')
  expect(loaded.policy?.get('tdd')).toBe('supporting')
})

test('policy, chip and report helpers', () => {
  expect(classify(['automatic'])).toBe('primary')
  expect(classify(['automatic', 'supporting'])).toBe('primary')
  expect(classify(['supporting'])).toBe('supporting')
  expect(classify(['explicit', 'supporting'])).toBe('explicit')

  const policy = buildPolicy(['{"id":"implement","invocation":["automatic"]}', 'not json', '{"id":"tdd"}', '{"id":"tdd","invocation":["supporting"]}'])
  expect([...policy]).toEqual([
    ['implement', 'primary'],
    ['tdd', 'supporting'],
  ])

  const route: RoutePolicy = new Map([
    ['implement', 'primary'],
    ['tdd', 'supporting'],
    ['typescript', 'supporting'],
  ])
  expect(chipText([{ skill: 'implement', warned: false }, { skill: 'tdd', warned: false }, { skill: 'typescript', warned: false }], route)).toBe(
    'implement → tdd · typescript',
  )
  expect(chipText([{ skill: 'tdd', warned: true }, { skill: 'vercel:nextjs', warned: false }], route)).toBe('⚠ tdd → vercel:nextjs')

  expect(repositoryCandidates('/repo/plugins/elias-mods/')).toEqual(['/repo/plugins', '/repo', ''].filter(Boolean))
  expect(readGuardLog([{ skill: 'tdd', kind: 'explicit', at: 'x' }, { skill: 1 }, 'junk', null])).toHaveLength(1)
  expect(readGuardLog('not a list')).toEqual([])
  expect(guardReport([], true, undefined)).toBe(
    'Skill guard: refuse mode\nSupporting-only loads with no primary skill: none\nHistorical explicit-only redirects (no longer enforced): none',
  )
})
