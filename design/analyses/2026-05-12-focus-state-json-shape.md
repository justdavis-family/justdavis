# `FocusState` JSON Response Shape: Flat vs. Nested

## Question

The [macOS Focus Gopher](../engineering-designs/2026-05-12-macos-focus-gopher.md) returns a single
  `FocusState` object from its one operation, `get_focus()`, over a local socket (and, via a thin CLI
  wrapper, as JSON on stdout).
Should that object be **flat** —

```json
{"ok": true, "focus_enabled": true, "focus_name": "Sleep",
 "macos_version": "15.5", "macos_compatibility": "supported", "message": null}
```

— or **nested**, grouping the "answer" and the "metadata" —

```json
{"focus": {"enabled": true, "name": "Sleep"},
 "meta": {"ok": true, "errors": null, "macos_compatibility": {"macos_version": "15.5", "rating": "supported"}}}
```

This came up in PR review (does having `ok` and `error` as flat siblings, alongside the focus fields,
  risk *immediately* violating our new "clear, unambiguous, easily-parsed data models" principle?),
  with a request to look at how popular, battle-tested, well-regarded simple JSON APIs do it.

## Findings

### What the API-design literature says

- **Envelopes (`{"data": …, "meta": …}`) earn their keep mainly for *collections* and *pagination*** —
    you should never return a bare JSON array at the top level, and an envelope gives you somewhere to
    hang `next`/`total`/`links`. For a *single* small object there is much less to gain, and most
    guidance says return the object at the top level rather than wrapping it.
- **The "`200 OK` with `success: false` in the body" complaint is specifically about HTTP** — it's bad
    because it *shadows the HTTP status code*, forcing clients to parse the body to detect failure and
    muddying monitoring. Our transport is a Unix domain socket plus a CLI printing JSON; there is no
    HTTP status code for a body-level `ok` to shadow. The recommended pattern there is "use the proper
    status channel *and* put details in the body" — which, translated to our world, is "the CLI exits
    non-zero on failure *and* the JSON carries `ok`/`error`".
- **The dominant value cited for envelopes is future extensibility** (you can add `meta` later without
    breaking the contract). For a fixed, single-operation contract that we publish as a JSON Schema,
    that argument is weak — there is nothing planned to extend, and a second operation would be its own
    schema anyway. Adding structure now for hypothetical future structure is a YAGNI violation.
- **Consistency matters more than flat-vs-nested in the abstract.** With exactly one operation and one
    response shape, there is no consistency tension to resolve.

### What well-regarded simple JSON APIs actually do

Single-resource responses in widely-used, well-liked APIs are overwhelmingly *flat at the top level*:
  Stripe returns flat objects (with an `object` type discriminator), GitHub returns flat resources, and
  most "GET one thing" endpoints return the thing's fields directly rather than wrapping a lone resource
  in `{"data": {...}}`. The `{"data": ..., "meta": ...}` / JSON:API style shows up around *collections*
  and pagination, not around a single small object.

### Does flat conflict with the "clear data models" principle?

No. That principle is about *separating orthogonal facts into their own fields* and *never collapsing
  distinct states into one ambiguous value* — it is agnostic about nesting. `FocusState` already does
  this: `ok` (did we determine the state?), `focus_enabled` (is a Focus on?), `focus_name` (do we have
  a name?), and `macos_compatibility` (is this OS version supported?) are four distinct, well-named
  fields, and a parse failure is `ok: false` with an `error` code, never `focus_enabled: false`.
  Nesting those same facts under `focus`/`meta` would not make them any more orthogonal; it would just
  add a level of indirection that every consumer (and every `jq`/`grep` one-liner) has to walk through.

### When nesting *does* earn its keep: making invalid states unrepresentable

The strongest argument for grouping fields is not aesthetics or extensibility — it is *making invalid
  states unrepresentable*. When several fields are conceptually one unit that must vary together (the
  classic example: `x`, `y`, `z` that are always all-`Some` or all-`None`, far better modeled as one
  `position: Option<Coordinates>` than three independent `Option`s), grouping them turns "every
  consumer must remember to check the combination" into "the type system checks it for you." This is
  exactly the [Strong Typing and Information
  Preservation](../engineering-principles/2026-01-07-strong-typing.md) principle.

`FocusState` *does* have such a unit: when `ok` is `false`, `focus_enabled` and `focus_name` are
  meaningless; when `focus_enabled` is `false`, `focus_name` is meaningless. A flat wire object can
  literally represent the nonsense `{"ok": false, "focus_enabled": true, …}`. So this is a real
  consideration here, not a strawman — and it is resolved by splitting the question in two:

- **The helper's *internal* model is a sum type, where the invalid states are unrepresentable.**
    The Rust side is modeled as roughly `enum FocusState { Determined { focus: Option<FocusInfo>,
    macos: MacosCompat }, Failed { error: ErrorCode, macos: MacosCompat } }` (with
    `FocusInfo { name: Option<String> }`) — there is no way to construct "failed but Focus on", or "no
    Focus but here's its name". This is where the strong-typing win is captured, in the code that
    actually branches on it.
- **The *wire* form is a flat, schema-validated projection of that sum type.** JSON has no native sum
    types; any consumer — `jq`, a shell `case`, a five-line Python script — branches on a discriminant
    regardless of whether the bytes are flat or nested. A nested `{"focus": {...}|null, "meta": {...}}`
    does not make the wire format self-checking; the consumer still has to know the `ok`/`error` rule.
    What actually constrains the valid combinations on the wire is the **published JSON Schema**
    (conditional `required`/`oneOf` on `ok`), which both flat and nested forms need equally. Given
    that, the flat projection keeps the ergonomics (shallow paths, trivial `jq`) without giving up any
    enforceable guarantee the nested form would have provided.

In short: capture the "illegal states unrepresentable" guarantee in the strongly-typed *internal*
  model (where it has teeth), and let the *wire* contract be the flat projection plus its schema.

## Recommendation

- **Keep `FocusState` flat *on the wire*, backed by a strongly-typed internal sum type.** It is one
    small, fixed-schema response; flat well-named orthogonal fields are the easiest to read, parse, and
    document, and that is what comparable well-regarded APIs do. The "make invalid states
    unrepresentable" guarantee is captured in the helper's internal model and enforced on the wire by
    the published JSON Schema, not by nesting.
- **The CLI wrapper exits non-zero when `ok` is `false`** (and zero otherwise), so shell scripts can
    branch on the exit code without parsing JSON; the JSON body still carries `ok` and `error` for
    programmatic consumers reading the socket directly. This gives us the "proper status channel *and*
    details in the body" pattern without an envelope.
- **Do not add a `meta` block, an `errors` array, or a nested `macos_compatibility` object** unless a
    concrete consumer need appears — and `errors` plural in particular is unnecessary: `get_focus()`
    either determines the state or hits exactly one failure, so a single `error` code suffices.

## References

- **Product Requirement**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- **Engineering Principles**: [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md);
    [Strong Typing and Information Preservation](../engineering-principles/2026-01-07-strong-typing.md).
- Sources:
  - [Vinay Sahni — Best Practices for Designing a Pragmatic RESTful API](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api).
  - [On shapes, sizes and envelopes (REST API ones) — fleetster Tech Blog](https://medium.com/fleetster-tech-blog/on-shapes-sizes-and-envelopes-rest-api-ones-272549d17108).
  - [Flat vs Nested REST Endpoints: Why Error Clarity Favors Flat Design](https://medium.com/@kh.taheri/flat-vs-nested-rest-endpoints-why-error-clarity-favors-flat-design-599e77054fa3).
  - [Speakeasy — Responses Best Practices in REST API Design](https://www.speakeasy.com/api-design/responses).
  - [Guidelines on JSON responses for RESTful services](https://medium.com/@sunitparekh/guidelines-on-json-responses-for-restful-services-1ba7c0c015d).
