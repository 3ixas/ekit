# Python interfaces and delivery

## Command-line applications

Treat the CLI as a stable interface. Keep command names, arguments, environment variables, exit codes, stdout, and stderr deliberate. Make non-interactive behavior predictable; confirm destructive actions only when the request did not already authorize them. Test commands through the installed or canonical entry point rather than importing an internal function alone.

## Web services

Keep transport parsing, authentication, domain behavior, persistence, and external integrations in distinct owners. Validate request and external response data at boundaries. Make transaction scope, timeout, retry, idempotency, and cancellation behavior explicit. Do not hide blocking work inside an async path.

Use framework-native dependency and lifecycle mechanisms where they clarify resource ownership. Avoid framework models leaking into the core domain when that couples business rules to transport or storage.

## Packages and releases

Declare build backend, package discovery, Python requirement, metadata, and included data in `pyproject.toml`. Build both wheel and source distribution when publishing, inspect their contents, create a clean environment, install the artifact, and test public imports and entry points. A passing test suite from the source checkout does not prove the package is complete.

Keep the public import surface intentional. Document installation, a minimal working example, supported versions, and behavior-changing migration notes. Release only from the exact verified revision and follow the repository's release process.

## Documentation

Use executable examples for behavior users are expected to copy. Keep references close to the public API they describe and update code, tests, and docs in the same change. Do not introduce a documentation framework migration for a local edit.
