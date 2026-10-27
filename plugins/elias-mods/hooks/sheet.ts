// Grilling answer sheet (#9): reads a grilling round from Claude's final message and
// builds the pane that answers it. Like band.ts, this file holds no mods API calls.
import type { ElementTable, PromptOrigin, RenderElement } from 'claude-code'
import type { BandRow } from './band.js'

// The mobile app draws no Input, so there the sheet offers Accept alone
export type SheetElements = Pick<ElementTable, 'Box' | 'Text' | 'Button'> & { Input?: ElementTable<'desktop'>['Input'] }

// One question of a round, as the grilling skill writes it:
// ❓ **Q1** - **Title**: body … ➡️ recommendation
export type Question = { number: number; title: string; body: string; recommendation: string }
export type Answer = { kind: 'accept' } | { kind: 'override'; text: string }
export type Answers = ReadonlyMap<number, Answer>

const QUESTION = /^❓️?\s*\*\*Q(\d+)\b(.*)$/
// `**Q1** - **Title**: body`, the format in the grilling skill, also seen as
// `**Q17 (revisited)** - **Title**` and `**Q3** (was Q4) - **Title**`
const SPLIT_BOLD = /^(?:\s*\([^)]*\))?\*\*(?:\s*\([^)]*\))?\s*[-–—·:]\s*\*\*(.+?)\*\*(.*)$/
// `**Q1 - Title**: body`, which rounds also use
const ONE_BOLD = /^(?:\s*\([^)]*\))?\s*[-–—·:]\s*(.+?)\*\*(.*)$/
const RECOMMENDATION = /^➡️?\s*(.*)$/
const SEPARATOR = /^\s*(-{3,}|\*{3,}|_{3,})\s*$/
const FENCE = /^\s*(```|~~~)/

const stripEmphasis = (text: string) => text.replace(/\*\*|__/g, '').trim()

export const plural = (count: number, word: string) => `${count} ${word}${count === 1 ? '' : 's'}`

// A prompt that answers the round: Elias's own, typed here or through Remote Control.
// The Desktop app may host the session as an SDK client, so its typed prompts may
// arrive as `sdk`; in a -p run no round is open. A notification or another session's
// message starts a turn without answering it. The sheet's own Send never reaches this
// plugin's hook, so sendAnswers closes the round itself.
const ELIAS_ORIGINS: ReadonlySet<PromptOrigin['kind']> = new Set(['composer', 'bridge', 'sdk'])
export function answersRound(origin: PromptOrigin): boolean {
  return ELIAS_ORIGINS.has(origin.kind)
}

// The questions of the round the message ends with, or none when the message holds
// no round or one the parser cannot read whole: the pane then draws nothing rather
// than send an answer to part of a round. A ❓ inside a code fence is not a question.
export function parseRound(message: string): Question[] {
  const questions: Question[] = []
  let current: { number: number; title: string; body: string[]; recommendation?: string[]; open: boolean } | undefined
  let inFence = false
  const finish = () => {
    if (!current) return true
    if (!current.recommendation) return false
    questions.push({
      number: current.number,
      title: current.title,
      body: current.body.join('\n').trim(),
      recommendation: stripEmphasis(current.recommendation.join('\n')),
    })
    return true
  }
  for (const line of message.split('\n')) {
    if (FENCE.test(line)) inFence = !inFence
    if (inFence) {
      if (current && !current.recommendation) current.body.push(line)
      continue
    }
    const trimmed = line.trimStart()
    const header = QUESTION.exec(trimmed)
    if (header) {
      if (!finish()) return []
      const rest = header[2] ?? ''
      const parts = SPLIT_BOLD.exec(rest) ?? ONE_BOLD.exec(rest)
      if (!parts) return []
      const title = stripEmphasis(parts[1] ?? '').replace(/:$/, '').trim()
      const first = (parts[2] ?? '').replace(/^\s*:/, '').trim()
      current = { number: Number(header[1]), title, body: first ? [first] : [], open: true }
      continue
    }
    if (!current) continue
    const recommendation = RECOMMENDATION.exec(trimmed)
    if (recommendation && !current.recommendation) {
      current.recommendation = [recommendation[1] ?? '']
      continue
    }
    if (current.recommendation) {
      // The recommendation is its paragraph: a blank line, a rule or prose after it ends it
      if (!current.open) continue
      if (!trimmed || SEPARATOR.test(trimmed)) current.open = false
      else current.recommendation.push(trimmed)
      continue
    }
    current.body.push(line)
  }
  if (!finish()) return []
  const numbers = new Set(questions.map((question) => question.number))
  if (numbers.size !== questions.length || questions.some((question) => !question.title || !question.recommendation)) return []
  return questions
}

const answered = (answer: Answer | undefined) => answer !== undefined && (answer.kind === 'accept' || answer.text.trim() !== '')

export function answeredCount(questions: readonly Question[], answers: Answers): number {
  return questions.filter((question) => answered(answers.get(question.number))).length
}

export function isComplete(questions: readonly Question[], answers: Answers): boolean {
  return answeredCount(questions, answers) === questions.length
}

// Accepts every question not already overridden
export function acceptAll(questions: readonly Question[], answers: Answers): Map<number, Answer> {
  const next = new Map(answers)
  for (const question of questions) {
    if (!answered(next.get(question.number))) next.set(question.number, { kind: 'accept' })
  }
  return next
}

// The reply Elias would have typed: one line per question, "Q1 agreed." or "Q2: <his answer>"
export function composeReply(questions: readonly Question[], answers: Answers): string {
  return questions
    .map((question) => {
      const answer = answers.get(question.number)
      return answer?.kind === 'override' && answer.text.trim() ? `Q${question.number}: ${answer.text.trim()}` : `Q${question.number} agreed.`
    })
    .join('\n')
}

// The toast Send shows at once: Desktop draws a plugin's prompt in the thread only
// seconds later, so without it a slow thread reads as a missed click
export function sentToast(reply: string): string {
  // By code point, so an emoji is never cut in half
  const line = Array.from(`Sent: ${reply.split('\n').join(' · ')}`)
  return line.length > 100 ? `${line.slice(0, 99).join('')}…` : line.join('')
}

export type SheetHandlers = {
  onAccept: (question: number) => void
  onOverride: (question: number, text: string) => void
  onAcceptAll: () => void
  onSend: () => void
}

// The pane: each question's title and recommendation, Accept, and a field to answer
// otherwise. Send is drawn only once every question has an answer; Button has no
// disabled state, so until then a count stands in its place.
export function sheetPane(questions: readonly Question[], answers: Answers, handlers: SheetHandlers) {
  return ({ Box, Text, Button, Input }: SheetElements): RenderElement => {
    const rows = questions.map((question) => {
      const answer = answers.get(question.number)
      const accepted = answer?.kind === 'accept'
      return Box({
        key: `q${question.number}`,
        flexDirection: 'column',
        children: [
          Text({ bold: true, children: [`Q${question.number} · ${question.title}`] }),
          Text({ dimColor: true, children: [`➡️ ${question.recommendation}`] }),
          Box({
            flexDirection: 'row',
            gap: 1,
            alignItems: 'center',
            children: [
              Button({
                key: `accept-${question.number}`,
                label: accepted ? 'Accepted ✓' : 'Accept',
                variant: accepted ? 'primary' : 'secondary',
                onPress: () => handlers.onAccept(question.number),
              }),
              ...(Input
                ? [
                    Input({
                      key: `override-${question.number}`,
                      placeholder: 'or answer otherwise',
                      value: answer?.kind === 'override' ? answer.text : '',
                      submitLabel: 'set',
                      onInput: (text) => handlers.onOverride(question.number, text),
                      onSubmit: (text) => handlers.onOverride(question.number, text),
                    }),
                  ]
                : []),
            ],
          }),
        ],
      })
    })
    const done = answeredCount(questions, answers)
    const footer: RenderElement[] = []
    if (done < questions.length) {
      footer.push(Button({ key: 'accept-all', label: 'Accept all', onPress: () => handlers.onAcceptAll() }))
      footer.push(Text({ dimColor: true, children: [`${done} of ${questions.length} answered`] }))
    } else {
      footer.push(Button({ key: 'send', label: 'Send', variant: 'primary', onPress: () => handlers.onSend() }))
    }
    return Box({
      flexDirection: 'column',
      gap: 1,
      children: [...rows, Box({ key: 'footer', flexDirection: 'row', gap: 1, alignItems: 'center', children: footer })],
    })
  }
}

// The band row while a round is open: the signal, and a way back to a closed pane
export function sheetRow(count: number, onOpen: () => void): BandRow['build'] {
  return ({ Box, Text, Button }) =>
    Box({
      flexDirection: 'row',
      gap: 1,
      alignItems: 'center',
      children: [
        // The count gives way before the button does
        Box({ flexShrink: 1, minWidth: 0, children: [Text({ dimColor: true, wrap: 'truncate-end', children: [`❓ grilling round · ${plural(count, 'question')}`] })] }),
        Button({ key: 'answer-sheet', label: 'Answer sheet', onPress: () => onOpen() }),
      ],
    })
}
