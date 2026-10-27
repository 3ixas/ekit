# Type boundaries

## Represent the domain

Model distinct domain states as distinct types. Use discriminated unions when behavior depends on a variant and exhaustively handle them at decision points. Prefer semantic identifiers or branded types where mixing structurally identical values would cause a real defect. Derive types from one authoritative schema rather than maintaining parallel handwritten shapes.

Use generics when the relationship between inputs and outputs matters to callers. Keep constraints narrow and inferable. Avoid conditional or recursive type machinery when a named union, overload, or explicit model is easier to read and change.

## Tell the truth at runtime boundaries

Network responses, storage, environment values, form input, message payloads, and parsed JSON begin as `unknown`. Validate them once at the boundary and pass trusted domain values inward. A type assertion does not validate runtime data. Type guards must inspect every property needed for the promised type.

Keep absence explicit. Choose omitted, `undefined`, `null`, or a domain variant according to the real contract; do not treat them as interchangeable. Preserve thrown error causes and narrow caught values before reading them.

## Work with the compiler

Read the repository's TypeScript version, `tsconfig` inheritance, module settings, generated types, and framework conventions before editing. Fix type errors at the point the model becomes inaccurate. Do not weaken strictness, add broad ambient declarations, or scatter assertions to make a check pass.

Assertions are acceptable at a proven framework or interop boundary when the evidence cannot be expressed to the compiler. Keep them narrow and explain non-obvious invariants nearby. Use `satisfies` when validating a value's shape while preserving useful inference.

## Keep contracts as narrow as real use

Optional props and parameters each add a state the code must handle. When only tests, stories, or mocks omit a value, make it required and let that support code adapt. Distinguish optional (`x?: T`) from required nullable (`x: T | null`). Derive types from live APIs (`Parameters<typeof fn>[0]`, `ReturnType`, `Extract`) rather than restating them, then delete the fallbacks that only existed for the wider type. Adapted from HumanLayer's `narrow-react-prop-types`.
