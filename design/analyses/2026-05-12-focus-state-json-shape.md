# `FocusState` JSON Response Shape: Flat vs. Tagged Union

## Question

The [macOS Focus Gopher](../engineering-designs/2026-05-12-macos-focus-gopher.md) returns a single
  `FocusState` object from its one operation, `get_focus()`, over a local socket (and, via a thin CLI
  wrapper, as JSON on stdout).
The response is conceptually a *sum type*: either the helper **determined** the state (a Focus is on,
  with its name, or no Focus is on) or it **failed** (with an error code), plus a little shared metadata.
Should the wire form be a **flat object of nullable siblings** —

```json
{"ok": true, "focus_enabled": true, "focus_name": "Sleep",
 "macos_version": "15.5", "macos_compatibility": "supported", "message": null}
```

— or a **tagged discriminated union** that mirrors the sum type —

```json
{"macos_version": "15.5", "macos_compatibility": "supported",
 "determined": {"focus_on": {"name": "Sleep"}}}
```

This came up in PR review (does having `ok` and `error` as flat siblings, alongside the focus fields,
  risk *immediately* violating our new "clear, unambiguous, easily-parsed data models" principle?).
This analysis initially landed on **flat**; a deeper survey then reversed that to a **tagged union**.
It records the final decision and the reasoning, including why the first pass was wrong.

## Findings

### Two Different Questions, Often Conflated

"Nesting" bundles two unrelated decisions that should be judged separately:

- A **`data`/`meta` envelope** — about collections, pagination, links, and forward-compatible
    extensibility. For a *single* small object this buys little, and adding it now for hypothetical
    future structure is a YAGNI violation. Not what we need.
- A **discriminated (tagged) union** — about success-vs-error (or variant) *coherence*: making
    "determined" and "failed" structurally distinct so the incoherent mixes can't occur. This is the
    axis that actually matters for a single success-XOR-error response.

The first pass conflated the two: it argued (correctly) against an envelope and then carried that
  conclusion over to the union question, where it does not apply.

### Why the "flat is fine" Precedent Does Not Transfer to Us

Single-resource responses in big, well-liked REST APIs *are* mostly flat — GitHub, Stripe, Twilio,
  much of Slack. But they are flat largely because **HTTP status carries the success-vs-error
  discriminant**: the body does not have to encode coherence because the status code already did. We
  have **no HTTP layer** — a Unix domain socket plus a CLI printing JSON — so the body must carry the
  discriminant itself.

The right comparison is systems that pack success-XOR-error into one JSON object with no transport
  status to lean on, and those do *not* go flat:

- **JSON-RPC 2.0** (and **LSP**, built on it): a Response object MUST contain `result` *or* `error` and
    **MUST NOT** contain both — a structural discriminated union, not optional sibling fields
    ([spec](https://www.jsonrpc.org/specification)). This is the closest structural analogue to
    `get_focus()`.

Honest counter-evidence, kept on the record:

- The **Slack Web API** is essentially our proposed flat shape — top-level `{"ok": false, "error":
    "..."}`, often returned under HTTP 200, so it is a real flat precedent that does *not* lean on
    status ([docs.slack.dev](https://docs.slack.dev/apis/web-api/)). But its body is coherent only by
    convention (nothing stops `{"ok": false, …success fields…}`), it is tuned for a vast
    dynamically-typed consumer base, and it is not trying to mirror a producer-side sum type — the
    opposite of our situation.
- **GraphQL** deliberately allows a *partial* response (`data` *and* `errors` together)
    ([graphql.org](https://graphql.org/learn/response/)) — a reason to avoid a strict XOR. We have no
    partial state, so it does not apply.

### Keep the Wire Aligned With the Internal Model (serde, Fowler, "parse, don't validate")

The helper is a Rust producer with a real sum type. That makes the alignment argument concrete:

- **serde** offers four enum representations ([serde.rs](https://serde.rs/enum-representations.html)):
    externally tagged (default), internally tagged, adjacently tagged, and untagged. A flat
    struct-of-optionals is closest to **untagged**, which the docs flag as the fragile one — variants
    are told apart only by which optional fields happen to be present. A tagged enum makes **the wire
    *be* the serialized internal sum type**, removing the hand-maintained flattening layer that can
    drift out of sync — exactly the cross-layer-divergence bug class to avoid.
- **Martin Fowler, Local DTO** ([martinfowler.com](https://martinfowler.com/bliki/LocalDTO.html)): he
    is against reshaping the wire away from the domain model unless there is a "significant mismatch."
    For a one-call helper there is none, so flattening would be gratuitous divergence, not a feature.
- **"Parse, don't validate"** (Alexis King,
    [lexi-lambda](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/)): the wire is the
    boundary; a tagged shape lets each consumer parse straight into its own sum type instead of
    re-deriving "if not ok, ignore focus_enabled."

### Making Invalid States Unrepresentable — in Code *and* on the Wire

The strongest argument for grouping is *making invalid states unrepresentable* — the
  [Strong Typing and Information Preservation](../engineering-principles/2026-01-07-strong-typing.md)
  principle. `FocusState` has such a unit: "failed but a Focus is on" and "no Focus but here's its name"
  are nonsense. With the tagged union, both the internal model and the wire exclude them structurally:

- The **internal Rust model** is a sum type (`Outcome::Determined(Focus)` vs. `Failed { error }`, with
    `Focus::FocusOn { name }` vs. `FocusOff`), so the bad combinations are unconstructable in code.
- The **wire** is that sum type's externally-tagged serialization, so the bad combinations are absent
    on the wire too — and the published **JSON Schema** adds a `oneOf` as belt-and-suspenders. (JSON
    Schema can express this coherence for *any* representation — flat or tagged — via
    `oneOf`/`if`-`then`/`const`, so schema power does not decide the shape; what a schema cannot do is
    force an ad-hoc consumer that never validates to branch correctly, which is an argument for making
    the structure itself unambiguous.)

### Why "Focus on but no name" Is a Failure, Not a Partial Success

A tempting fourth state is "a Focus is on, but its identifier could not be mapped to a name." We model
  this as a **failure** (`focus_name_unresolved`), not a partial success, for three reasons:

- **The name is the primary thing consumers want**; the on/off boolean is secondary. A nameless "Focus
    is on" does not satisfy the main use case.
- **It is effectively hypothetical as a steady state.** Names resolve from `ModeConfigurations.json`
    (user Foci, which must be configured to be active) plus a fixed table for the small set of
    built-ins; community tools resolve names reliably, and there is no evidence of a real
    "active-but-permanently-unnameable" Focus. The realistic causes — schema/format drift, a transient
    mid-write race, or a brand-new built-in identifier on a new macOS version — are all symptoms of a
    problem (a coverage/parse gap), not a legitimate ongoing state.
- **YAGNI:** modeling it as a success variant would complicate every consumer's success path for a
    state we cannot evidence. Reporting it as `failed` with `focus_name_unresolved` (end-to-end, not a
    CLI-only nicety) keeps the common path simple.

This is *not* collapsing a positive result into a failure (which our
  [clear-data-models](../engineering-principles/2026-05-12-clear-data-models.md) principle forbids):
  by the evidence an unnameable active Focus is a symptom of incomplete parsing, not a legitimate
  positive result, and the dedicated error code keeps the taxonomy clear rather than lossy.

## Recommendation

- **Make `FocusState` an externally-tagged discriminated union that mirrors the internal sum type**,
    not a flat object of nullable siblings. We have no transport status code, so (like JSON-RPC / LSP)
    the body carries the discriminant; the tagged form keeps the wire aligned with the Rust model (no
    divergent mapping), makes illegal states unrepresentable on the wire as well as in code, and is
    obvious to a human without consulting the schema.
- **Hide Rust's `Result`/`Option` plumbing behind domain-named keys** — `determined`/`failed` and
    `focus_on`/`focus_off`, never serialized `Ok`/`Err`/`null`. The shapes:

```jsonc
// (a) determined, Focus on
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "determined": { "focus_on": { "name": "Sleep" } } }

// (b) determined, Focus off
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "determined": { "focus_off": {} } }

// (c) determined on an unknown (unlisted) macOS version — the unknown variant carries the report message
{ "macos_version": "26.0",
  "macos_compatibility": { "unknown": { "message": "macOS 26.0 is not on the known-supported list. Please file an issue or PR reporting whether Focus parsing works here, so it can be added." } },
  "determined": { "focus_on": { "name": "Do Not Disturb" } } }

// (d) failure — the failed variant carries the guidance message (here, FDA remediation)
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "failed": { "error": "focus_permission_denied",
    "message": "Full Disk Access is required. Grant it to /Applications/FocusGopher.app under System Settings > Privacy & Security > Full Disk Access, then retry." } }
```

- **`focus_on` always carries a real `name`**; an active Focus whose name cannot be resolved is a
    `failed` with `focus_name_unresolved`, not a partial success (see above).
- **Shared metadata stays at the top level** (`macos_version` and `macos_compatibility`), since it is
    reported on both success and failure. **Human-readable guidance lives *inside the variant that owns
    it*** — a `message` on the `macos_compatibility` `unknown` variant (report whether this version
    works) and a `message` on the `failed` variant (what went wrong / how to fix or report) — rather
    than as a single overloaded, free-floating top-level field. Because the CLI prints the raw JSON, the
    text must travel on the wire; attaching each message to its triggering variant keeps it
    single-purpose and means it can't appear without its condition.
- **The CLI wrapper exits non-zero when the outcome is `failed`** (and zero otherwise), so shell
    scripts can branch on the exit code without parsing JSON.
- **No `data`/`meta` envelope and no `errors` array** — YAGNI; `get_focus()` either determines the
    state or hits exactly one failure, so a single `error` code suffices.

## References

- **Product Requirement**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- **Engineering Principles**: [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md);
    [Strong Typing and Information Preservation](../engineering-principles/2026-01-07-strong-typing.md).
- Sources:
  - [JSON-RPC 2.0 Specification — `result` XOR `error`](https://www.jsonrpc.org/specification).
  - [serde — enum representations (externally/internally/adjacently/untagged)](https://serde.rs/enum-representations.html).
  - [Alexis King — Parse, don't validate](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/).
  - [Martin Fowler — Local DTO](https://martinfowler.com/bliki/LocalDTO.html).
  - [Slack Web API — top-level `ok`/`error`](https://docs.slack.dev/apis/web-api/).
  - [GraphQL — response (`data` + `errors`, partial responses)](https://graphql.org/learn/response/).
