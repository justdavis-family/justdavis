# Clear, Unambiguous, Easily-Parsed Data Models

## Principle

Design data models — especially those that cross a process, network, or API boundary —
  to be unambiguous and trivial to parse: a fixed schema, explicit field semantics,
  no overloaded fields, and a clear separation of orthogonal facts so a consumer never has to guess.
In particular, distinguish "the operation failed" from "the operation succeeded and the answer is
  negative"; never collapse genuinely distinct states into a single ambiguous value.

## Rationale

- An ambiguous model pushes interpretation logic — and its bugs — onto every consumer.
- Conflating "no result", "empty result", and "error" leads to silent failures:
    a parse failure that looks like "nothing here" is acted on as if nothing were wrong.
- When orthogonal facts get their own fields, consumer logic collapses to a simple decision tree,
    and the model documents itself.
- Fixed schemas are easy to validate, version deliberately, and keep stable across releases.

## Examples

**Good (clear-data-model-compliant):**

- A response that separates orthogonal facts and models its states as a tagged union — e.g.
    `FocusState`, whose outcome is `determined` (itself `focus_on` with a `name`, or `focus_off`) or
    `failed` (with an `error` code), alongside `macos_compatibility` (`supported` / `unsupported` /
    `unknown`) — so each state is its own variant rather than a set of independently-nullable fields
    that can combine into nonsense.
- Returning `{"failed": {"error": "schema_unknown", …}}` on a parse failure, rather than a
    `determined` → `focus_off` result that would disguise the failure as "no Focus is on".
- A `message` field that is explicitly human-only guidance — attached to the variant that needs it
    (e.g. `failed`, or the `unknown` compatibility variant) — with all machine-relevant facts carried
    in their own typed fields.
- A fixed, documented schema for everything that crosses the boundary.

**Bad (ambiguous or hard-to-parse models):**

- A boolean that means "off OR we couldn't tell" — two different states, one value.
- Reporting a failure as a successful negative result (silent failure).
- Tunneling structured data through a free-text `message` (or an error string) that consumers must
    pattern-match.
- Adding speculative fields (e.g. `normalized`, `source`) with no concrete consumer — clarity is not
    maximalism, and unused fields are just more surface to misinterpret.
- Reusing one field for different meanings depending on another field's value, without that being an
    explicit, documented tagged union.

## When to Break This Rule

- Cases where you must conform to an external format that is itself ambiguous — wrap and normalize it
    into a clear model at the boundary rather than propagating the ambiguity inward.

## Relationship to Other Principles

- Builds on **strong typing and information preservation** — orthogonal facts get distinct, well-typed
    fields instead of being squeezed into one stringly-typed value.
- Reinforces **comprehensive error modeling** and **fail fast and loud** — "failed" is a first-class,
    explicit state, never disguised as a benign result.
- Pairs with **least privilege** — a single narrow operation naturally has a single clear response
    schema.
- Constrained by **YAGNI** — model the facts you actually have, not hypothetical ones.
