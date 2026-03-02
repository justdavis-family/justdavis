# Comprehensive Error Modeling

## Principle

Model all error cases explicitly and never suppress errors without handling them.
Function and service results should expose all failure modes to enable debugging.

## Rationale

- Suppressed errors make debugging nearly impossible.
- Explicit error types force callers to handle failure cases.
- Full error context (stack traces, original causes) aids troubleshooting.
- Silent failures mask problems until they cause catastrophic issues in production.

## Examples

**Good (explicit error modeling):**
- Use Rust's `Result<T, E>` type for operations that can fail.
- Use Swift's `throws` and custom `Error` types.
- Include context in errors: what operation failed, with what inputs, and why.
- Log errors with full context before returning them.
- Chain errors to preserve original cause (e.g., Rust's `context()` or Swift's `NSError.userInfo`).

**Bad (suppresses or loses error information):**
- Using `unwrap()` in Rust or force-unwrapping (`!`) in Swift without clear justification.
- Catching errors and returning generic "something went wrong" messages.
- Using `_` to ignore `Result` or `throws` without handling.
- Logging errors but not propagating them to callers who might handle them.

## When to Break This Rule

- User-facing messages where technical details would confuse rather than help.
- Error recovery scenarios where the error has been fully handled and recovery succeeded.
- Known transient failures that are expected and handled gracefully (but log them).

## Relationship to Other Principles

- Works with **strong typing** - error types encode possible failure modes.
- Enables **fail fast and loud** - explicit errors make impossible states visible.
