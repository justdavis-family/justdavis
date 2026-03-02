# Strong Typing and Information Preservation

## Principle

Model data using strongly-typed structures that preserve all available information.
Avoid lossy transformations or premature data simplification.

## Rationale

- Type systems catch bugs at compile time rather than runtime.
- Preserving information enables better debugging and future feature development.
- Explicit types make code self-documenting and easier to understand.
- Information loss is irreversible - once data is discarded, it cannot be recovered.

## Examples

**Good (preserves information with strong types):**
- Use Rust's `enum` types to model all possible states explicitly.
- Use Swift's `struct` and `enum` types with associated values.
- Store timestamps with full precision, don't truncate to dates unless required by domain logic.
- Keep original error context when wrapping errors.

**Bad (loses information or uses weak typing):**
- Using `String` for data that has more specific structure (stringly-typed data).
- Discarding error details when converting between error types.
- Truncating timestamps or numeric precision "because we don't need it yet."
- Using `bool` when the domain has three or more states.

## When to Break This Rule

- Performance-critical code paths where type information incurs measurable overhead.
- External API boundaries that require specific formats (but preserve full info internally).
- Display/presentation logic where simplification aids user understanding (but keep full data in model).

## Relationship to Other Principles

- Enables **comprehensive error modeling** - types make error cases explicit.
- Supports **fail fast and loud** - type mismatches are caught at compile time.
