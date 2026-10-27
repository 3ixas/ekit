// The shared band above the prompt. Each feature contributes at most one row;
// this file holds no mods API calls, so register.ts resolves elements and passes them in.
import type { ElementTable, PluginOptions, RenderElement, RenderSurface, SessionContextUsage, SessionRateLimit } from 'claude-code'

// Box, Text and Button draw on every surface; Svg is present only where the band draws it
export type BandElements = Pick<ElementTable, 'Box' | 'Text' | 'Button'> & { Svg?: ElementTable<'desktop'>['Svg'] }

// Desktop first: only the Desktop app gets Svg rows, every other surface the text
// line. Mobile and VS Code can draw Svg too but stay on the text line for now.
// Seen under `claude plugin test`: $.ui.resolve hands Svg to the terminal as well,
// where it draws an empty box, so the band checks the surface, not the table.
const drawsSvg = (surface: RenderSurface) => surface === 'desktop'

// A feature's id is also its userConfig option. Priority decides which rows stay when
// the band has fewer rows than features to show: lowest number kept first.
export type Feature = { id: string; label: string; priority: number }
export type SessionInfo = { surface: string; version: string }
// What a row has to fit in: the band's width in cells
export type BandLayout = { columns: number }
export type BandRow = { key: string; build: (elements: BandElements, layout: BandLayout) => RenderElement }

// Features in band order, top to bottom: the row Elias acts on sits nearest the
// prompt, and is the last to go when rows are short; the skill route goes first
export const FEATURES: readonly Feature[] = [
  { id: 'barometer', label: 'context barometer', priority: 2 },
  { id: 'skill_route', label: 'skill route', priority: 3 },
  { id: 'answer_sheet', label: 'answer sheet', priority: 1 },
]

// A feature is on unless its option is explicitly false
export function enabledFeatures(options: PluginOptions | undefined): Feature[] {
  return FEATURES.filter((feature) => options?.[feature.id] !== false)
}

// The apps drawing this session; a plain -p run has none
export function surfaceName(surfaces: readonly string[]): string {
  return surfaces.join('+') || 'headless'
}

// The surface /elias-mods names: the session's roster, or the surfaces the mod saw
// attach or draw when the roster reads empty, as it did in Desktop on 2026-10-24
export function reportedSurface(roster: readonly string[], seen: readonly string[]): string {
  return surfaceName(roster.length ? roster : seen)
}

// One line describing the loaded mod, used by the placeholder row and /elias-mods
export function statusText(info: SessionInfo, features: readonly Feature[]): string {
  const names = features.length ? features.map((feature) => feature.label).join(', ') : 'none'
  return `elias-mods · ${info.surface} · Claude Code ${info.version} · features: ${names}`
}

// Rows features have contributed, in band order, at most maxRows of them by priority.
// While none has a row, one placeholder row shows the band is ours.
export function bandRows(
  info: SessionInfo,
  features: readonly Feature[],
  contributions: ReadonlyMap<string, BandRow['build']>,
  maxRows = Infinity,
): BandRow[] {
  const kept = new Set(
    features
      .filter((feature) => contributions.has(feature.id))
      .sort((a, b) => a.priority - b.priority)
      .slice(0, Math.max(1, maxRows))
      .map((feature) => feature.id),
  )
  const rows = features.flatMap((feature) => {
    const build = kept.has(feature.id) ? contributions.get(feature.id) : undefined
    return build ? [{ key: feature.id, build }] : []
  })
  if (rows.length) return rows
  return [{ key: 'placeholder', build: ({ Text }) => Text({ dimColor: true, wrap: 'truncate-end', children: [statusText(info, features)] }) }]
}

// Context barometer (#7)

// The figures $.session.usage() reports after a main-thread turn
export type Reading = { context: SessionContextUsage; rateLimits: readonly SessionRateLimit[] }

// Turns the sparkline remembers
export const HISTORY_TURNS = 24
// Context percent at which the Handoff button appears, unless handoff_at says otherwise
export const DEFAULT_HANDOFF_AT = 70

export function handoffThreshold(options: PluginOptions | undefined): number {
  const value = options?.handoff_at
  return typeof value === 'number' && value >= 1 && value <= 100 ? value : DEFAULT_HANDOFF_AT
}

// Adds one turn's fill; a turn with no reported fill leaves the history as it was
export function recordTurn(history: readonly number[], percent: number | undefined): number[] {
  if (percent === undefined) return [...history]
  return [...history, percent].slice(-HISTORY_TURNS)
}

export function shouldOfferHandoff(reading: Reading, threshold: number): boolean {
  return (reading.context.percent ?? 0) >= threshold
}

// 124000 → 124k, 1000000 → 1M
export function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${Number((tokens / 1_000_000).toFixed(1))}M`
  return `${Math.round(tokens / 1000)}k`
}

export function contextText({ context }: Reading): string {
  const percent = context.percent === undefined ? '–' : `${context.percent}%`
  const tokens = context.tokens === undefined ? '' : ` · ${formatTokens(context.tokens)}/${formatTokens(context.window)}`
  return `context ${percent}${tokens}`
}

const LIMIT_NAMES: Record<string, string> = { five_hour: '5h', seven_day: '7d', spend_limit: 'spend' }

// 2h10m, 3d4h, 12m; nothing for a reset that is missing, unreadable or past
export function formatResetIn(resetsAt: string | undefined, now: number): string {
  const at = resetsAt ? Date.parse(resetsAt) : NaN
  const minutes = Math.round((at - now) / 60_000)
  if (!(minutes > 0)) return ''
  const days = Math.floor(minutes / 1440)
  const hours = Math.floor((minutes % 1440) / 60)
  if (days) return `${days}d${hours}h`
  if (hours) return `${hours}h${minutes % 60}m`
  return `${minutes}m`
}

// "5h 34% resets 2h10m · 7d 12%"; empty when the account reports no limits
export function limitsText(rateLimits: readonly SessionRateLimit[], now: number): string {
  return rateLimits
    .map((limit) => {
      const resetIn = formatResetIn(limit.resetsAt, now)
      return `${LIMIT_NAMES[limit.kind] ?? limit.kind} ${limit.percentUsed}%${resetIn ? ` resets ${resetIn}` : ''}`
    })
    .join(' · ')
}

const BLOCKS = '▁▂▃▄▅▆▇█'

// The sparkline as block characters, for surfaces without Svg
export function sparklineText(history: readonly number[]): string {
  return history.map((percent) => BLOCKS[Math.min(BLOCKS.length - 1, Math.floor((Math.max(0, percent) / 100) * BLOCKS.length))]).join('')
}

export const SPARK_WIDTH = 96
export const SPARK_HEIGHT = 18
// Below these band widths, in cells, the barometer drops its plan limits, then its
// sparkline; the context reading itself never wraps
export const LIMITS_MIN_COLUMNS = 72
export const SPARK_MIN_COLUMNS = 44

// Context percent per turn on a fixed 0–100 scale, with the handoff threshold dashed
export function sparklineSvg(history: readonly number[], threshold: number): string {
  const y = (percent: number) => (SPARK_HEIGHT - 1 - (Math.min(100, Math.max(0, percent)) / 100) * (SPARK_HEIGHT - 2)).toFixed(1)
  const step = history.length > 1 ? (SPARK_WIDTH - 2) / (history.length - 1) : 0
  const points = history.map((percent, i) => `${(1 + i * step).toFixed(1)},${y(percent)}`).join(' ')
  const line = history.length > 1 ? `<polyline points="${points}" fill="none" stroke="#8a8f98" stroke-width="1.5" stroke-linejoin="round"/>` : ''
  const latest = history.at(-1)
  const last = latest === undefined ? '' : `<circle cx="${(1 + (history.length - 1) * step).toFixed(1)}" cy="${y(latest)}" r="2" fill="#8a8f98"/>`
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" width="${SPARK_WIDTH}" height="${SPARK_HEIGHT}" viewBox="0 0 ${SPARK_WIDTH} ${SPARK_HEIGHT}">` +
    `<line x1="0" x2="${SPARK_WIDTH}" y1="${y(threshold)}" y2="${y(threshold)}" stroke="#d9a441" stroke-width="1" stroke-dasharray="3 3"/>` +
    line +
    last +
    `</svg>`
  )
}

// The barometer as one line, for the terminal and /elias-mods; a narrow band drops
// the plan limits, then the sparkline
export function barometerText(reading: Reading, history: readonly number[], now: number, columns = Infinity): string {
  const limits = columns >= LIMITS_MIN_COLUMNS ? limitsText(reading.rateLimits, now) : ''
  const spark = columns >= SPARK_MIN_COLUMNS ? sparklineText(history) : ''
  return [`${contextText(reading)}${spark ? ` ${spark}` : ''}`, limits].filter(Boolean).join(' · ')
}

export type BarometerOptions = { threshold: number; now: () => number; onHandoff: () => void }

// The barometer row: an Svg sparkline where the surface has one, block characters
// elsewhere. A single Svg point is a dot lost beside the threshold line, so the Svg
// waits for two turns; a single block character reads fine. Narrow
// bands drop the plan limits, then the sparkline, so the context reading never wraps.
export function barometerRow(reading: Reading, history: readonly number[], options: BarometerOptions): BandRow['build'] {
  return ({ Box, Text, Button, Svg }, { columns }) => {
    const now = options.now()
    const over = shouldOfferHandoff(reading, options.threshold)
    const children: RenderElement[] = []
    // Text in a Box that may shrink, so it truncates rather than pushing Handoff out
    const shrinking = (text: RenderElement) => Box({ flexShrink: 1, minWidth: 0, children: [text] })
    if (Svg) {
      const limits = columns >= LIMITS_MIN_COLUMNS ? limitsText(reading.rateLimits, now) : ''
      children.push(shrinking(Text({ bold: over, wrap: 'truncate-end', children: [contextText(reading)] })))
      if (history.length > 1 && columns >= SPARK_MIN_COLUMNS) {
        children.push(
          Svg({
            source: sparklineSvg(history, options.threshold),
            alt: `Context fill over the last ${history.length} turns: ${history.join('%, ')}%`,
            width: SPARK_WIDTH,
            height: SPARK_HEIGHT,
          }),
        )
      }
      if (limits) children.push(shrinking(Text({ dimColor: true, wrap: 'truncate-end', children: [limits] })))
    } else {
      children.push(shrinking(Text({ bold: over, wrap: 'truncate-end', children: [barometerText(reading, history, now, columns)] })))
    }
    if (over) children.push(Button({ key: 'handoff', label: 'Handoff', variant: 'primary', onPress: () => options.onHandoff() }))
    return Box({ flexDirection: 'row', gap: 1, alignItems: 'center', children })
  }
}

// The band: our rows in order, then whatever mods after us drew
export function composeBand(
  elements: BandElements,
  surface: RenderSurface,
  rows: readonly BandRow[],
  theirs: RenderElement | null | undefined,
  layout: BandLayout,
): RenderElement {
  const { Box } = elements
  const usable: BandElements = drawsSvg(surface) ? elements : { ...elements, Svg: undefined }
  const children = rows.map((row) => Box({ key: row.key, flexDirection: 'row', alignItems: 'center', children: [row.build(usable, layout)] }))
  if (theirs) children.push(theirs)
  return Box({ flexDirection: 'column', children })
}
