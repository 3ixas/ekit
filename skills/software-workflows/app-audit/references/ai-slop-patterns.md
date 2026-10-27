# AI-template and unfinished-product patterns

Use these patterns as questions during the visual and product pass, not as a scorecard or a ban list. A design is not slop merely because it uses gradients, cards, rounded corners, dark colours, or familiar components. Compare the work with the product, its design file, and the references Elias chose.

| Pattern to notice | Evidence to look for | Useful correction |
|---|---|---|
| A generic landing-page silhouette | Centered hero, oversized slogan, gradient glow, and identical rows of cards appear regardless of the product's real purpose. | Let the actual task, content, and reference hierarchy determine the layout. Remove decoration that carries no meaning. |
| Effects without a reason | Blurs, glass, gradients, shadows, pill shapes, or animation compete with the content or repeat everywhere by default. | Keep effects that reinforce hierarchy or product identity; simplify the rest. |
| A design system assembled by accident | Similar buttons, headings, spacing, radii, icons, or surfaces change from page to page without a product reason. | Reuse the project's existing tokens and components; correct the shared source when possible. |
| Fake credibility or invented content | Placeholder logos, testimonials, ratings, customer counts, metrics, or sample claims look real. | Remove them or replace them only with verified product information. |
| Controls that only look interactive | Links have no destination, buttons do nothing, menus are static drawings, or controls report success without completing an action. | Connect each control to its real behaviour, make its state clear, or present it as non-interactive content. |
| Happy-path-only screens | Missing loading, empty, validation, error, recovery, and not-found states leave blank space or generic failure text. | Add context-specific status, a useful next step, and a route back to a working state. |
| One-screen responsiveness | Fixed widths, clipped content, tiny touch targets, horizontal scrolling, and broken long text appear away from the designer's viewport. | Test realistic widths and content extremes; let layout and typography adapt without losing hierarchy. |
| Semantics added as an afterthought | Heading order is confusing, controls lack accessible names, focus is invisible, or informative images have no useful text alternative. | Fix semantics and keyboard behaviour at the component source; use an empty alternative for decorative images. |
| Stock or mismatched imagery | Generic stock visuals, placeholder art, inconsistent icon families, or images that contradict the copy weaken the product's identity. | Use relevant, licensed assets that support the chosen references and provide appropriate alternatives. |
| Default launch residue | Generic page titles, repeated descriptions, a default icon or social card, preview-domain canonicals, staging URLs in the sitemap, or unfinished robots rules remain. | Check each public route and the real target host; align indexability, canonical URLs, icons, and social assets with intended release state. |
| Debug and build residue | Console errors, debug logs, test routes, unsafe source artifacts, exposed credentials, or oversized route bundles ship without a reason. | Remove or protect only confirmed accidental residue; preserve useful production diagnostics and measure bundle impact against project context. |

Do not replace a distinctive interface with a generic “premium” template. Fix the observed inconsistency or unfinished behaviour while preserving the product's visual character.
