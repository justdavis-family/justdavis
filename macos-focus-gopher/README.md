# Focus Gopher

A small, single-purpose macOS helper that reports your current **Focus / Do Not Disturb** state
  — including the name of the active Focus — to local clients,
  without those clients needing any macOS privacy permissions of their own.

> ## ⚠️ Early development — not yet usable
>
> This project is being built milestone by milestone.
> **The current state** ships the `get_focus()` *contract* — the `FocusState` wire model, its
>   published JSON Schema, the socket protocol — plus the thin `focus-gopher` CLI that speaks it.
> The helper's `get_focus()` is still **stubbed**: it always returns a `failed` result
>   without reading any Focus database, so the CLI faithfully prints (and exits non-zero on) that
>   stubbed reply.
> It builds, tests, and lints — but it does **not** read your real Focus state, install itself, or
>   distribute via Homebrew yet.
> See the [roadmap](#roadmap) below.

## What This Will Be

LLM agents and other tools running on macOS often want to know whether you are in a Focus
  (e.g. _Sleep_, _Do Not Disturb_, _Work_) before they interrupt you.
macOS only exposes that state through privacy-gated mechanisms — most directly, an undocumented
  database under `~/Library` that requires **Full Disk Access (FDA)**.
Granting FDA to a frequently-rebuilt, internet-connected, tool-using agent is a large security risk,
  and the grant is tied to a specific executable identity that churns on every rebuild.

Focus Gopher solves this by being a small, **stable-identity broker**:

- It is the only component that holds the macOS permission and reads the database.
- It exposes exactly **one read-only operation** — `get_focus()` — over a local Unix domain socket,
    plus a thin `focus-gopher` CLI wrapper for humans and shell scripts.
- It never exposes arbitrary file, shell, Shortcut, or AppleScript access.

So an unprivileged client asks one narrow question and gets one fixed-schema answer;
  the powerful permission stays confined to a small, audited, stable binary.

## Architecture

```text
client / agent ──get_focus──▶ Unix domain socket ──▶ focus-gopherd (per-user helper)
                                                          │
                                                          ▼
                                          ~/Library/DoNotDisturb/DB/*.json  (read-only; added later)
```

For the full design — technology choices, the retrieval pipeline, the error taxonomy, and the
  trade-offs — see the
  [engineering design](../design/engineering-designs/2026-05-12-macos-focus-gopher.md).

### The `FocusState` Response

Every response is one JSON object with shared metadata (`macos_version`, `macos_compatibility`)
  plus exactly one **outcome**: `determined` (the state was read) or `failed` (it could not be).
This externally-tagged shape mirrors the helper's internal types, so invalid combinations are
  unrepresentable — see the
  [JSON-shape analysis](../design/analyses/2026-05-12-focus-state-json-shape.md).
The schema is published and versioned at
  [`schema/focus-state.v1.schema.json`](schema/focus-state.v1.schema.json).

```jsonc
// a Focus is active
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "determined": { "focus_on": { "name": "Sleep" } } }

// no Focus is active
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "determined": { "focus_off": {} } }

// the state could not be determined (here: Full Disk Access not granted)
{ "macos_version": "15.5", "macos_compatibility": "supported",
  "failed": { "error": "focus_permission_denied",
    "message": "Full Disk Access is required. Grant it to the helper, then retry." } }
```

## Trying It (Developers Only)

There is no install path yet.
You can build both binaries — the `focus-gopherd` helper and the `focus-gopher` CLI — and run
  them locally:

```bash
cd macos-focus-gopher
MISE_EXPERIMENTAL=1 mise run ':build'
./target/debug/focus-gopherd &
until [ -S "$TMPDIR/focus-gopher.sock" ]; do sleep 0.1; done  # wait for it to bind
./target/debug/focus-gopher                                   # pretty FocusState JSON on stdout
```

For now, the reply is always a stubbed `failed` result (no Focus database is read yet), so the CLI
  prints that `FocusState` and exits **1**.

### Using `focus-gopher`

`focus-gopher` connects to the helper, performs `get_focus()`, pretty-prints the returned
  `FocusState` as JSON on stdout, and exits with an outcome-driven code so shell scripts can
  branch without parsing the JSON:

- **0** — outcome is `determined` (a `FocusState` was successfully read).
- **1** — outcome is `failed` (the helper returned an explicit `error` code and guidance
    `message` in the printed `FocusState`).
- **2** — the CLI could not obtain a `FocusState` at all (helper not running, socket
    unreachable, malformed reply, …);
    nothing is printed on stdout and a diagnostic is logged to stderr.

```bash
if state=$(focus-gopher); then
  echo "got: $state"
else
  echo "exit $?: see stderr for details" >&2
fi
```

Run `focus-gopher --help` for the full option list and worked examples.
For talking to the helper over its raw socket protocol
  (useful when extending the protocol itself), see
  [CONTRIBUTING.md](CONTRIBUTING.md).

## Roadmap

Today the project ships the **contract** (the wire model, JSON Schema, socket protocol) and the
  thin `focus-gopher` CLI that speaks it, but the helper's `get_focus()` is still stubbed — see
  the banner at the top.
What broadly follows: real Focus parsing, then build-from-source packaging and distribution, then
  compatibility breadth and the agent ecosystem, and finally an optional signed-distribution
  channel.

The authoritative, evolving breakdown — sequence, scope, and status — lives in the
  [delivery plan](../design/delivery-plans/2026-05-12-macos-focus-gopher.md) and the
  [milestone tracking issues](https://github.com/justdavis-family/justdavis/issues?q=is%3Aissue+label%3Amilestone),
  not here, so this README doesn't drift.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the repository-level
  [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

[MIT](LICENSE).
