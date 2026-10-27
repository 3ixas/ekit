# Visual answers

Use when Elias asks to be shown something ("show me", "draw it", "what does it look like"), or when a flow, structure, or change is clearer as a picture than as prose. Adapted from Dex Horthy's `show-me` skill (HumanLayer).

Skip the preamble. Pick the smallest view that makes the key point clear, and place each view next to the one or two sentences it supports. Usually one view is enough and several is the most; never all of them.

| Point to make | View |
|---|---|
| Logic or an algorithm | Pseudocode in a `text` block |
| Runtime control flow | A call tree, indented by call depth |
| UI structure | A component tree with the hooks, state, and package boundaries that matter, and the file for the root |
| File responsibility or a broad refactor | A shallow file tree with a short comment per entry |
| Interaction between components, services, or actors | A Mermaid sequence or flow diagram |
| Data shape or contract | The type, table, or request and response shape, trimmed to the fields that matter |
| What changes in an existing shape | The same view as a `diff` block, with `+` and `-` lines |

Use `diff` when the surrounding shape already exists and the point is what changes. Show the complete block when most of it is new, when omitted context would hide ownership or order, or when Elias needs a copyable target shape.

For a visual UI, a layout or state comparison, or a concept too dense for Mermaid, write one focused HTML file: a diagram, an infographic, or a short slide sequence. Match the product's colours, type, and components, use real labels and data, and make it work on desktop and mobile. Publish it through the host's artifact or file-sharing tool when one exists; otherwise say where the file is.

Keep only the calls, files, props, states, and boundaries needed to answer the current question.
