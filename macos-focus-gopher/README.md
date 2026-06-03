# Focus Gopher

A small, single-purpose macOS helper that reports your current **Focus / Do Not Disturb** state
  — including the name of the active Focus — to local clients,
  without those clients needing any macOS privacy permissions of their own.

> ## Status — read-only Focus parsing on macOS 26
>
> This project is being built milestone by milestone.
> Today's milestone ships **real Focus parsing**: the helper reads
>   `~/Library/DoNotDisturb/DB/Assertions.json` and `ModeConfigurations.json`,
>   maps the active Focus identifier to a human-readable name, and returns
>   a `FocusState` over its local socket (or via the `focus-gopher` CLI).
> Tested on macOS 26 (Tahoe); other macOS versions report
>   `macos_compatibility: unknown` and we ask you to file an issue.
> The helper still has to be **built from source** and the **Full Disk Access** grant
>   is a manual System Settings step that has to be re-applied after every rebuild;
>   one-command install via Homebrew and a signed/notarized distribution channel come later.
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
                                          ~/Library/DoNotDisturb/DB/*.json  (read-only)
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

## Trying It (developers only)

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

Without Full Disk Access granted to the helper, the reply is a `failed` `FocusState`
  with `error: focus_permission_denied` and a `message` containing the helper's resolved
  binary path and a deep link to the System Settings pane.
The CLI prints that JSON and exits **1**.
With FDA granted (see the next section), the reply is a `determined` `FocusState`
  reflecting the host's current Focus state (`focus_on` with the active Focus's name,
  or `focus_off` if nothing is active);
  the CLI prints that JSON and exits **0**.

## Compatibility

Focus Gopher's parser has been verified against **macOS 26.4.1** (committed test fixtures)
  and **macOS 26.5** (live e2e on the development host).
Matching is **by exact version string**:
  these two specific versions report `macos_compatibility: supported`;
  other 26.x point releases — and any other macOS version — report
  `macos_compatibility: unknown` until they too are verified.
Apple can change the private Focus-DB format in any point release,
  so we report only what we have actually exercised.

When a queried version isn't in the verified list but its major has at least one verified
  sibling (e.g. on a hypothetical macOS 26.6),
  the `unknown` message names those siblings so users can gauge confidence and report back.
For majors with no verified entries (currently macOS 12 Monterey through 15 Sequoia,
  and macOS 27 and later), the message is a generic "please file an issue" invitation.

Whether parsing actually worked is conveyed by the outcome (`determined` or `failed`),
  independent of the compatibility field — that is the actual ground truth;
  `macos_compatibility` reports **whether we've checked the running version**,
  not whether parsing will succeed.

See the [format-stability analysis](../design/analyses/2026-05-12-macos-focus-db-format.md)
  (section 3) for the policy rationale and the work item of growing the verified list
  as contributors verify additional versions.

> ### Known macOS 26 limitation: schedule-triggered Foci
>
> When a Focus is activated by a user-defined schedule trigger on macOS 26, no file under
>   `~/Library/DoNotDisturb/DB/` reflects the active state — `donotdisturbd` keeps that
>   information in memory. Focus Gopher will currently report `focus_off` in that case.
> Manually-toggled Foci (built-in or user-created) are detected correctly.
> Tracking the gap and an investigation plan: see the
>   [project issue tracker](https://github.com/justdavis-family/justdavis/issues?q=is%3Aissue+focus+gopher+schedule).

## Granting Full Disk Access

The helper needs **Full Disk Access** to read the macOS Focus database. The grant is
  always a manual System Settings step (there is no programmatic prompt on any channel),
  and **on build-from-source installs the grant is keyed to the binary's cdhash, so it
  must be re-applied after every rebuild.**

To grant access:

1. Open System Settings → **Privacy & Security** → **Full Disk Access**.
   (Or paste this deep link into Safari / your launcher:
   `x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles`.)
2. Add the **resolved path to the `focus-gopherd` binary** (the one the
    `focus_permission_denied` message will print). The resolved path matters because
    cargo and Homebrew both symlink into `bin/`, and TCC matches the real binary.
3. Re-run `focus-gopher` to verify: exit code **0** with a `determined` outcome means the
    grant is live.

For contributors developing against the live Focus database, an alternative dev workflow
  using a self-signed code-signing certificate (so the cdhash stays stable across rebuilds)
  is described in [CONTRIBUTING.md](CONTRIBUTING.md#developing-against-the-live-focus-database).

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

Today the project ships the **contract** (the wire model, JSON Schema, socket protocol),
  the thin `focus-gopher` CLI that speaks it, and **real read-only Focus parsing** verified
  against macOS 26.
What broadly follows: build-from-source packaging and distribution (Homebrew formula + cargo
  install + a per-user LaunchAgent), then compatibility breadth (the rest of macOS 12–15) and
  the agent ecosystem, and finally an optional signed-distribution channel.

The authoritative, evolving breakdown — sequence, scope, and status — lives in the
  [delivery plan](../design/delivery-plans/2026-05-12-macos-focus-gopher.md) and the
  [milestone tracking issues](https://github.com/justdavis-family/justdavis/issues?q=is%3Aissue+label%3Amilestone),
  not here, so this README doesn't drift.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the repository-level
  [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

[MIT](LICENSE).
