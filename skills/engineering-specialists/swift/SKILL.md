---
name: swift
description: Apply Swift language, concurrency, testing, API, ownership, and performance guidance using the project's deployment target and toolchain.
---

# Swift

## Outcome

Clear, safe Swift that fits the current platform and concurrency model.

## Method

Inspect Swift/Xcode versions; model data with value types and state explicitly; stay single-threaded until profiling says otherwise, noting that from Swift 6.2 `async` alone does not leave the caller's actor; respect Sendable and actor isolation; make cancellation and errors observable; avoid unnecessary type erasure; follow project testing conventions, defaulting to Swift Testing for new tests; measure performance and retain platform availability checks.

Done when the affected target builds with the project’s compiler settings and relevant behaviour checks pass; report any unavailable platform or runtime checks.

## Boundaries

Apple interface decisions belong to apple-design and project operation belongs to ios.

Read [Emil Kowalski's modern Swift guide](references/source-methods/emil-write-swift.md) for Swift 6 concurrency, `some` versus `any`, API design, ARC, macros, and migrating to Swift 6.
