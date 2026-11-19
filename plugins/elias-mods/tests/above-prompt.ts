import type { RenderPropsOf, RenderSurface } from 'claude-code'
import type { MountTarget } from 'claude-code/testing'

// What Claude Code passes to an AbovePrompt hook. Typed against the SDK, so a prop it newly requires fails here once
export function abovePrompt<S extends RenderSurface>(
  surface: S,
  { columns = 120, rows = 40, props = {} }: { columns?: number; rows?: number; props?: Partial<RenderPropsOf['AbovePrompt']> } = {},
): MountTarget<S, 'AbovePrompt'> {
  return {
    plugin: 'elias-mods',
    component: 'AbovePrompt',
    requestId: 'above-prompt',
    surface,
    viewport: { columns, rows },
    props: {
      hasSurvey: false,
      isCollapsed: false,
      isWorking: false,
      maxRows: 6,
      bodyColumns: columns - 10,
      scroll: { offset: 0, bodyRows: 6 },
      view: {},
      ...props,
    },
  }
}
