# Bklit for product dashboards

Read this when implementing a chart in a React/shadcn product. Choose the analytical question, encoding, scales, units and accessible presentation first. Bklit is an optional renderer, not a reason to replace a working chart stack or choose a misleading chart.

Inspect the framework, existing charts, shadcn configuration and selected component's dependencies. Read [current installation docs](https://bklit.com/docs/installation) and the actual component source. The documented registry is `@bklit`: `https://ui.bklit.com/r/{name}.json`. Merge it into an approved project's components.json, preserving local settings; use the project's package manager to add only selected charts, for example `@bklit/area-chart`. Inspect the returned source and transitive dependencies before installation. Match semantic tokens and real data rather than copying demo numbers.

Verify empty, loading, error, single-point, zero, negative and missing-value states when relevant, long labels, resizing and reduced motion. Keep scales truthful, dates and units explicit, tooltips usable with keyboard/touch where supported, and provide an accessible text/table alternative for essential values. Choose animation only when it improves interpretation.

The reviewed chart components are MIT. Bklit Studio is separately restricted by LICENSE-STUDIO.md: permission to use the hosted tool does not permit copying Studio's source into another product. Check the exact component notices, including third-party dependencies, before reuse. No analytics service, Studio source, account or new renderer is installed merely by loading this reference.
