# Python project and quality

## Read the project before choosing tools

Inspect `pyproject.toml`, lockfiles, supported Python versions, package layout, test configuration, task runner, CI, and published interfaces. Preserve the project's selected environment and tools. Recommend a change only when it solves a concrete problem and include its migration cost.

For a new personal project, choose a current supported Python version and a single project manager that owns environments, locking, builds, and commands. Use a `src/` layout for distributable libraries or when preventing accidental imports matters; a small application can use a simpler layout. Separate runtime, development, and optional dependencies intentionally.

## Model behavior clearly

Type public boundaries and domain-bearing values. Prefer small explicit models over dictionaries whose required keys are implicit. Accept protocols or callables when callers need behavior rather than a concrete class. Keep `Any` at isolated compatibility boundaries and narrow `object` or `Unknown` data through validation.

Raise or return errors at the layer that can add useful context. Preserve exception causes, avoid bare catches, and do not use exceptions for expected branches when a result or domain state is clearer. Use context managers for owned resources and make cleanup behavior visible.

## Test and maintain

Test observable behavior and important failure paths. Keep unit tests around pure domain logic and add boundary or integration tests where parsing, persistence, network behavior, or framework wiring is the risk. Avoid mocks that duplicate the implementation's call sequence.

Run the project's formatter, linter, type checker, and tests using its canonical commands. Inspect generated coverage only when it answers a risk question. For dependency updates, verify the lockfile diff, supported Python range, import behavior, and affected runtime path.

Review public APIs, imports, and deprecations before moving modules. Compatibility aliases need a real consumer and a removal plan.
