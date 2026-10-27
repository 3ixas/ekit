# Screenshot critique

Independently written for this repository, informed by TasteSkill v2's critique method and blind-test record (`Leonxlnx/taste-skill`, pinned in `metadata.json`). Its house-style bans are not adopted; the passes below are the parts its blind jurors' judgements support.

## Judge the render, not the code

Critique screenshots of the rendered interface, never the source. Whoever wrote the code reads their intentions into it; a screenshot shows only what is there. When the host supports subagents, give the screenshots, the brief, and `DESIGN.md` to a fresh-context reviewer that did not build the screens.

Capture the real page or exploration screens at about 1440, 768, and 390 px wide: the first screen at each width, then full-page sheets. Use the browser the host provides; record the widths and states captured.

## The passes

Make each pass separately; do not blend them.

1. **One second.** Glance and look away. There should be exactly one answer to "what did I see": a word, an image, an object. "A website" means there is no focal point.
2. **Squint.** Blur the text into grey bars. The screen should reduce to two or three masses of clearly different size. Many similar small masses means nothing leads.
3. **Cover the logo.** Could this screen belong to a competitor or another industry if the name and headline noun were swapped? If so, the direction has not reached it. Scroll on: does the idea survive past the first screen, or does the page turn into stock blocks?
4. **Edges.** Count the distinct left edges of text blocks down the page. A composed page reuses two or three on purpose; six means things were placed one at a time.
5. **Space.** Related things close, unrelated things far, the gap between sections clearly larger than any gap inside one. Distinguish a hole (accidental emptiness beside a short column or a removed decoration) from a rest.
6. **Type and colour.** A decisive jump from body to headline; five sizes or fewer; no orphaned last word on a headline; no paragraph wider than about 75 characters. Name the colour proportions; an accent that appears everywhere points at nothing.
7. **Sameness.** Write one word for each section's layout (split, list, full-bleed, grid, statement). The same word twice in a row, or three times on a page, is the template showing.
8. **Phone.** Is the phone layout a composition of its own, with its own crops and line breaks, or the desktop squeezed? Is its first screen still one clear thing?
9. **Fullness and substance.** Does every section deliver its information completely, at a readable size? Is the primary action a real control on the first screen? A sparse page that reads as an unfinished wireframe is underbuilt, not restrained.
10. **Collisions.** Is anything lying over a headline, statement, or control at any scroll position? Does anything run off the phone screen or scroll sideways without clearly meaning to?

## Fix and stop

Name the three largest problems, fix them from the decisions in `DESIGN.md`, recapture, and repeat. Stop after three rounds or when no pass finds a material problem, and report what remains. In TasteSkill's blind tests, a rich page full of familiar devices beat a clean page that was thin every time: removing defaults is not a substitute for substance, so passes 3 and 9 come before any polish.
