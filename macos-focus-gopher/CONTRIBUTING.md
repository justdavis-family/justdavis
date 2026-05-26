# Contributing to Focus Gopher

See the [repository-level CONTRIBUTING.md](../CONTRIBUTING.md)
  for the general development workflow, PR process, and conventions
  that apply to all projects in this monorepo.
This file covers setup specific to Focus Gopher.

Focus Gopher is being built milestone by milestone;
  see the [delivery plan](../design/delivery-plans/2026-05-12-macos-focus-gopher.md)
  for what's in scope today and what's coming next.

## Design Docs (the source of truth)

The design drives the implementation.
Before changing behavior, read:

- [Delivery plan](../design/delivery-plans/2026-05-12-macos-focus-gopher.md) — the milestone breakdown.
- [Engineering design](../design/engineering-designs/2026-05-12-macos-focus-gopher.md) — the `FocusState`
    model, socket protocol, retrieval pipeline, and error taxonomy.
- [`FocusState` JSON response shape](../design/analyses/2026-05-12-focus-state-json-shape.md) — why the
    wire model is an externally-tagged union.

## Project-Specific Setup

### 1. Install mise

This project uses [mise](https://mise.jdx.dev/) for tool and task management.
Follow the [getting started guide](https://mise.jdx.dev/getting-started.html)
  to install it if you haven't already.
mise provides the pinned Rust toolchain; you do not need to install Rust separately.

### 2. Build, Test, and Lint

```bash
cd macos-focus-gopher
MISE_EXPERIMENTAL=1 mise run ':ci'
```

This builds the helper and CLI, runs the unit and integration tests
  (including JSON-Schema validation and the socket round-trip), checks formatting,
  and runs Clippy with warnings treated as errors.

### 3. Exercise the Helper

The everyday way to query the helper is the `focus-gopher` CLI
  (see the project [README.md](README.md#using-focus-gopher) for exit-code conventions):

```bash
MISE_EXPERIMENTAL=1 mise run ':build'
./target/debug/focus-gopherd &
until [ -S "$TMPDIR/focus-gopher.sock" ]; do sleep 0.1; done  # wait for it to bind
./target/debug/focus-gopher
```

Without Full Disk Access granted to the *helper binary* (the resolved
  `target/debug/focus-gopherd` path),
  the CLI prints a `focus_permission_denied` `FocusState` and exits **1**.
With it granted, the CLI prints the live `FocusState` and exits **0**
  (`determined` outcome).

If you are working on the wire protocol itself
  (changing what the helper sends or accepts),
  you can also speak the socket directly with `nc -U`:

```bash
printf '{"op":"get_focus"}\n' | nc -U "$TMPDIR/focus-gopher.sock"
```

## Developing Against the Live Focus Database

The bulk of the test suite — including the fixture-driven parser tests in
  [`tests/parsing.rs`](tests/parsing.rs) and the unit tests inside each module —
  does **not** need Full Disk Access.
Real captures live under [`tests/fixtures/`](tests/fixtures/)
  (see [`tests/fixtures/FIXTURES.md`](tests/fixtures/FIXTURES.md)
  for the inventory and the PII-scrubbing process).

For live smoke testing — running the actual helper against your real
  `~/Library/DoNotDisturb/DB/` — you need Full Disk Access. Two options:

1. **Grant FDA to your terminal / IDE.**
   On macOS, TCC attributes file access to the *responsible process*: when you
   `cargo run` the helper from your terminal, the terminal is the responsible
   process. Adding your terminal app to System Settings → Privacy & Security →
   Full Disk Access lets the helper (and anything else you launch from that
   terminal) read protected files without per-rebuild re-granting.
   This is the simplest path, but it gives full disk access to *everything*
   you run from that terminal — use it deliberately.

2. **Use a self-signed local code-signing certificate.**
   Without a stable signature the helper's TCC identity is its `cdhash`, which
   changes on every rebuild and invalidates the FDA grant. A one-time Keychain
   step lets you create a self-signed code-signing certificate and sign dev
   builds with it (`codesign -s "<local cert>"`), giving the binary a stable
   Designated Requirement and surviving rebuilds. This is the better long-term
   workflow for LaunchAgent-attributed access (the next milestone) and is
   described in the
   [FDA / signing / distribution analysis](../design/analyses/2026-05-18-macos-fda-distribution-signing.md).

The fixture-driven tests are the workflow you should reach for first — they
  run on every PR (Linux and macOS CI), produce deterministic results, and
  catch parser regressions without depending on host state.
