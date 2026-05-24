# Strong Typing and Information Preservation

## Principle

Model data using strongly-typed structures that preserve all available information.
Avoid lossy transformations or premature data simplification.
This holds at boundaries too: a serialized or stored representation should preserve the type's
  *guarantees*, not only its data — encode sum types as tagged unions (a discriminant plus that
  variant's fields) that mirror the in-memory type, never as co-present nullable fields, so illegal
  states stay unrepresentable on the wire as they are in code.

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
- Flattening an internal sum type onto the wire as independently-nullable fields, so the serialized
    form can express combinations the in-memory type cannot — and a hand-maintained reshape between
    layers can drift out of sync with the domain model.

## When to Break This Rule

- Performance-critical code paths where type information incurs measurable overhead.
- External API boundaries that require a *specific wire format* — adapt the encoding, but still
    preserve the type's guarantees per the principle above (tagged unions; never flatten a sum type
    into nullable siblings), not merely its information.
- Display/presentation logic where simplification aids user understanding (but keep full data in model).

## Relationship to Other Principles

- Enables **comprehensive error modeling** - types make error cases explicit.
- Supports **fail fast and loud** - type mismatches are caught at compile time.
- Underpins **clear, unambiguous, easily-parsed data models** - tagged unions at the boundary are how
    "separate orthogonal facts, never collapse states" is enforced on the wire.
