# Contributing to Focus Gopher

See the [repository-level CONTRIBUTING.md](../CONTRIBUTING.md)
  for the general development workflow, PR process, and conventions
  that apply to all projects in this monorepo.
This file covers setup specific to Focus Gopher.

> **Early development.**
> Focus Gopher is being built milestone by milestone.
> Right now it ships only the project skeleton and the `get_focus()` *contract*
>   (the wire model, its JSON Schema, the socket protocol, and a stubbed `get_focus()`);
>   real Focus parsing, the CLI, install, and distribution come later.

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

### 3. Poke the Helper Over the Socket

Until the `focus-gopher` CLI is wired up,
  you can exercise the running helper directly over its socket:

```bash
# Run the helper (it prints the socket path it is listening on):
MISE_EXPERIMENTAL=1 mise run ':build'
FOCUS_GOPHER_SOCKET=/tmp/focus-gopher-dev/focus-gopher.sock ./target/debug/focus-gopherd &

# In another shell, send the one request the protocol supports:
printf '{"op":"get_focus"}\n' | nc -U /tmp/focus-gopher-dev/focus-gopher.sock
```

For now, the reply is always a stubbed `failed` / `macos_unsupported` `FocusState`
  (no Focus database is read yet).
