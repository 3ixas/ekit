# Options rounds

The way a strong agency develops an idea with its client: show concrete, divergent developments, let the client choose, then develop the chosen branch into the next, more concrete round.

## When

Use an options round for a **generative or taste decision**: what something could be, how it could feel, what shape it takes. Keep ordinary question rounds for facts, constraints, priorities, and yes/no calls.

- "Show me options" forces an options round.
- "Just decide" skips it: take the recommendation and record the options you would have shown.
- With no user to answer (a pipeline or headless run), do the same as "just decide".

An options round can share a round with ordinary questions. Number it like a question.

## Shape

Show **three options side by side**, never one after another.

- Each option diverges from the others on an axis you can name in a phrase: audience, tone, ambition, interaction model, density, business model, and so on. Near-identical options fail.
- Exactly one is a **stretch option**: bolder than Elias is likely to have considered, there to widen the range. If the decision is too narrow for one (a label, a single spacing value), say so and show three grounded options.
- Give a recommendation and the one-line reason, as with any grilling question.
- Invite a reply in any of these forms: pick one, combine named parts ("A's audience with C's tone"), or reject all and say why. A rejection shapes the next round as much as a pick does.

```
❓ **Q3** - **<decision>** (options round)

| | A: <name> | B: <name> | C: <name> (stretch) |
|---|---|---|---|
| Axis | <what A varies> | <what B varies> | <what C varies> |
| <option content, per the ladder below> | … | … | … |

➡️ <recommended option and why>. Pick, combine, or reject all.
```

## Ladder

Options get more concrete as the loop descends, never more numerous:

| Stage | Each option is |
|---|---|
| Idea | A concept card: one-line pitch, who it's for, what makes it distinct, the bet it makes |
| Direction | The concept card plus a quick visual sketch when the idea has an interface: mood, layout, tone |
| Design | A rendered mock of the key screen or flow |
| Detail | A focused variant of one component, flow, or state |

The chosen option becomes the starting point of the next round, one stage down. The next round's three options are developments of that choice, not fresh starts.

## Rendering

Text options fit in the table above. For visual options, render all three side by side with what the host offers: inline visuals or an artifact page in Claude, and HTML files or images with their paths in Codex. When an owning skill names the surface (for example `interface-design` with Claude Design or Stitch), use that surface and its confirmation rules. When a choice depends on feeling an interaction live, `prototype`'s picker can render the branches.

## Exploration trail

After each options round, add one line to the phase's durable document: the idea's note or repo doc, the scope document, or `DESIGN.md`'s exploration record.

`Round <n> (<stage>): A <name> [<axis>], B <name> [<axis>], C <name> [<axis>, stretch]. Chose <choice>, because <reason>. Others lost because <reason>.`

When no durable document exists yet, keep the trail in the conversation and write it once the owning skill creates one.

## Backtracking and stopping

Elias can return to any earlier option ("go back to B from the direction round"). Resume from that option at its stage, using the trail.

Stop branching when choices no longer change what the product is or how it feels, when the next level is implementation detail, or when Elias says "that's the one". From then on, refine one change at a time with ordinary questions.
