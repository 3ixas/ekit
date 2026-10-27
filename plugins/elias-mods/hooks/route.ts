// Skill route chip and warn-only routing guard (#8). Pure logic: register.ts
// reads the skill metadata and the store and passes what it found in.
import type { BandRow } from './band.js'

// How a skill may be invoked, from its metadata.json `invocation` list
export type Invocation = 'primary' | 'supporting' | 'explicit'
// Owned skill id → invocation; skills not in it (plugin skills) count as neither
export type RoutePolicy = ReadonlyMap<string, Invocation>

// One skill loaded this turn, in load order
export type RouteEntry = { skill: string; warned: boolean }

// What the guard records in the shared store: names and times, never prompt text
export type GuardEvent = { skill: string; kind: 'supporting-without-primary' | 'explicit'; at: string }
export const GUARD_LOG_LIMIT = 1000

// Matches the generated routing guidance: `explicit` marks a user-requested workflow;
// `supporting` without `automatic` makes it supporting-only; the rest may own a request.
export function classify(invocation: readonly string[]): Invocation {
  if (invocation.includes('explicit')) return 'explicit'
  if (invocation.includes('supporting') && !invocation.includes('automatic')) return 'supporting'
  return 'primary'
}

// Builds the policy from each skill's metadata.json text; unreadable entries are skipped
export function buildPolicy(metadata: readonly string[]): RoutePolicy {
  const policy = new Map<string, Invocation>()
  for (const text of metadata) {
    try {
      const { id, invocation } = JSON.parse(text) as { id?: unknown; invocation?: unknown }
      if (typeof id === 'string' && Array.isArray(invocation)) policy.set(id, classify(invocation.filter((value): value is string => typeof value === 'string')))
    } catch {
      // A malformed file is not a policy entry
    }
  }
  return policy
}

// The directories that may hold this repository, nearest first: the plugin sits at
// plugins/elias-mods, so the repository is a level or two above $.plugin.root.
export function repositoryCandidates(pluginRoot: string): string[] {
  const parts = pluginRoot.replace(/\/+$/, '').split('/')
  return [1, 2, 3].map((up) => parts.slice(0, -up).join('/')).filter(Boolean)
}

// The file reads loadPolicy needs; register.ts backs them with $.fs
export type PolicyIo = {
  exists: (path: string) => Promise<boolean>
  list: (path: string) => Promise<ReadonlyArray<{ name: string; kind: string }>>
  read: (path: string) => Promise<string>
}
export type LoadedPolicy = { policy: RoutePolicy | undefined; note: string }

// The generated routing guidance claude-sync writes, for a plugin running from an
// installed copy under ~/.claude rather than from this repository
export function projectionPath(pluginRoot: string): string | undefined {
  const at = pluginRoot.indexOf('/.claude/')
  return at === -1 ? undefined : `${pluginRoot.slice(0, at)}/.claude/rules/elias-agent-skills.md`
}

// The generated guidance's wording this parser relies on; tests/test_elias_mods.py
// checks that scripts/skills.py still writes each of them
export const PROJECTION_MARKERS = {
  automatic: '- Automatically selectable skills:',
  explicit: '- Skills requiring explicit invocation:',
  supporting: '## Supporting-only skills',
} as const

// Reads the policy from the generated guidance's own lists: the automatic and
// explicit lines, and the bullets under the supporting-only heading. Unusable
// (undefined) unless all three are there, so a reworded generator turns the
// guard off rather than leaving it without primaries. Explicit wins, as in classify.
export function policyFromProjection(markdown: string): RoutePolicy | undefined {
  const lines = markdown.split('\n')
  const automatic = lines.find((line) => line.startsWith(PROJECTION_MARKERS.automatic))
  const explicit = lines.find((line) => line.startsWith(PROJECTION_MARKERS.explicit))
  const section = markdown.split(`\n${PROJECTION_MARKERS.supporting}\n`)[1]
  if (automatic === undefined || explicit === undefined || section === undefined) return undefined
  const names = (text: string, pattern: RegExp) => [...text.matchAll(pattern)].map((match) => match[1] ?? '').filter(Boolean)
  const policy = new Map<string, Invocation>()
  for (const id of names(section.split('\n## ')[0] ?? '', /^- `([^`]+)`/gm)) policy.set(id, 'supporting')
  for (const id of names(automatic, /`([^`]+)`/g)) policy.set(id, 'primary')
  for (const id of names(explicit, /`([^`]+)`/g)) policy.set(id, 'explicit')
  return policy
}

// Reads skills/<group>/<id>/metadata.json from the repository that holds this plugin,
// or else the generated guidance. Without either the guard stays off and the chip
// still lists what loaded; a read that fails counts as without.
export async function loadPolicy(pluginRoot: string, io: PolicyIo): Promise<LoadedPolicy> {
  try {
    return await readPolicy(pluginRoot, io)
  } catch (error) {
    return { policy: undefined, note: `routing policy unavailable: ${error instanceof Error ? error.message : String(error)}` }
  }
}

async function readPolicy(pluginRoot: string, io: PolicyIo): Promise<LoadedPolicy> {
  for (const repository of repositoryCandidates(pluginRoot)) {
    if (!(await io.exists(`${repository}/scripts/skills.py`))) continue
    const dirs = async (path: string) => (await io.list(path)).filter((entry) => entry.kind === 'dir').map((entry) => `${path}/${entry.name}`)
    const skillDirs = (await Promise.all((await dirs(`${repository}/skills`)).map(dirs))).flat()
    const texts = await Promise.all(skillDirs.map((dir) => io.read(`${dir}/metadata.json`).catch(() => '')))
    const policy = buildPolicy(texts)
    if (!policy.size) return { policy: undefined, note: `routing policy unavailable: no skill metadata under ${repository}/skills` }
    return { policy, note: `${policy.size} skills' metadata read` }
  }
  const projection = projectionPath(pluginRoot)
  if (projection && (await io.exists(projection))) {
    const policy = policyFromProjection(await io.read(projection))
    if (!policy?.size) return { policy: undefined, note: `routing policy unavailable: ${projection} is not in the expected form` }
    return { policy, note: `${policy.size} skills from the generated routing guidance` }
  }
  return { policy: undefined, note: 'routing policy unavailable: skill metadata not found' }
}

// An owned skill that expanded this turn and is not supporting-only owns it: a
// primary one, or a user-requested one loaded by the model or typed by Elias.
// Descriptions and instructions recognize requests; the guard does not parse prompts.
export function hasPrimary(entries: readonly RouteEntry[], policy: RoutePolicy): boolean {
  return entries.some((entry) => {
    const invocation = policy.get(entry.skill)
    return !entry.warned && (invocation === 'primary' || invocation === 'explicit')
  })
}

export type Verdict = { kind: 'allow' } | { kind: 'warn' } | { kind: 'refuse'; reason: string }

// The guard's call on a Skill tool load, given what this turn has loaded so far
export function judgeLoad(skill: string, entries: readonly RouteEntry[], policy: RoutePolicy | undefined, refuse: boolean): Verdict {
  const invocation = policy?.get(skill)
  if (!policy || invocation !== 'supporting' || hasPrimary(entries, policy)) return { kind: 'allow' }
  if (!refuse) return { kind: 'warn' }
  return {
    kind: 'refuse',
    reason: `${skill} is a supporting-only skill and no primary skill owns this turn. Load the primary skill that owns the request first, then ${skill} from it, or ask Elias.`,
  }
}

// implement → tdd · typescript: a supporting skill after another supporting one
// joins with a dot, every other step with an arrow; a warned load carries ⚠
export function chipText(entries: readonly RouteEntry[], policy: RoutePolicy | undefined): string {
  return entries
    .map((entry, i) => {
      const name = entry.warned ? `⚠ ${entry.skill}` : entry.skill
      if (i === 0) return name
      const previous = entries[i - 1]
      const joinsWithDot = previous && policy?.get(previous.skill) === 'supporting' && policy.get(entry.skill) === 'supporting'
      return `${joinsWithDot ? ' · ' : ' → '}${name}`
    })
    .join('')
}

// The band row: dim while every load is in order, full strength once one is warned
export function routeRow(entries: readonly RouteEntry[], policy: RoutePolicy | undefined): BandRow['build'] {
  const text = `skills ${chipText(entries, policy)}`
  const warned = entries.some((entry) => entry.warned)
  return ({ Text }) => Text({ dimColor: !warned, wrap: 'truncate-end', children: [text] })
}

export function appendGuardEvent(log: unknown, event: GuardEvent): GuardEvent[] {
  return [...readGuardLog(log), event].slice(-GUARD_LOG_LIMIT)
}

// The store holds whatever an earlier version wrote; keep only well-formed events
export function readGuardLog(log: unknown): GuardEvent[] {
  if (!Array.isArray(log)) return []
  return log.filter(
    (event): event is GuardEvent =>
      typeof event?.skill === 'string' &&
      typeof event?.at === 'string' &&
      (event?.kind === 'supporting-without-primary' || event?.kind === 'explicit'),
  )
}

// The evidence for switching the guard to refuse: how often it would have fired, and for what
export function guardReport(log: readonly GuardEvent[], refuse: boolean, policyNote: string | undefined): string {
  const mode = refuse ? 'refuse' : 'warn'
  const lines = [`Skill guard: ${mode} mode${policyNote ? ` · ${policyNote}` : ''}`]
  const section = (kind: GuardEvent['kind'], title: string) => {
    const events = log.filter((event) => event.kind === kind)
    if (!events.length) return lines.push(`${title}: none`)
    const counts = new Map<string, number>()
    for (const event of events) counts.set(event.skill, (counts.get(event.skill) ?? 0) + 1)
    const top = [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).map(([skill, count]) => `${skill} ×${count}`)
    lines.push(`${title}: ${events.length} since ${events[0]?.at.slice(0, 10)} (${top.join(', ')})`)
  }
  section('supporting-without-primary', 'Supporting-only loads with no primary skill')
  section('explicit', 'Historical explicit-only redirects (no longer enforced)')
  return lines.join('\n')
}
