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

## Recommendation

- **Keep `FocusState` flat.** It is one small, fixed-schema response; flat well-named orthogonal fields
    are the easiest to read, parse, and document, and that is what comparable well-regarded APIs do.
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
- **Engineering Principle**: [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md).
- Sources:
  - [Vinay Sahni — Best Practices for Designing a Pragmatic RESTful API](https://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api).
  - [On shapes, sizes and envelopes (REST API ones) — fleetster Tech Blog](https://medium.com/fleetster-tech-blog/on-shapes-sizes-and-envelopes-rest-api-ones-272549d17108).
  - [Flat vs Nested REST Endpoints: Why Error Clarity Favors Flat Design](https://medium.com/@kh.taheri/flat-vs-nested-rest-endpoints-why-error-clarity-favors-flat-design-599e77054fa3).
  - [Speakeasy — Responses Best Practices in REST API Design](https://www.speakeasy.com/api-design/responses).
  - [Guidelines on JSON responses for RESTful services](https://medium.com/@sunitparekh/guidelines-on-json-responses-for-restful-services-1ba7c0c015d).
