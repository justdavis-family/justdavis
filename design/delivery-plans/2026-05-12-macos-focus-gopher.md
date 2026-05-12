# macOS Focus Gopher Delivery Plan

## Overview

This plan sequences delivery of the [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md)
  requirement into thin, independently-testable milestones,
  per the [engineering design](../engineering-designs/2026-05-12-macos-focus-gopher.md).

The main delivery risk is the *undocumented, version-fragile Focus database*.
The plan front-loads the stable parts (the project skeleton and the wire contract),
  then tackles parsing for one macOS version, then packaging/install, then compatibility breadth —
  so each milestone delivers something a consumer or contributor can actually exercise,
  and so a parser surprise on a future macOS version does not block the earlier milestones.

## Milestones

### M1 — Project skeleton and the `get_focus()` contract

**In scope:**

- Scaffold `macos-focus-gopher/` at the repo root: a Swift package and `.app` target,
    a `mise.toml` exposing `build` / `test` / `lint` / `dependencies:check` / `dependencies:update` /
    `ci`, wired into the root `mise.toml`, and CI invoking those Mise tasks.
- Define the `FocusState` model and the line-delimited JSON request/response protocol over a
    per-user Unix domain socket.
- Implement `get_focus()` as a stub that returns a well-formed `FocusState`
    (e.g. `ok: false`, `error: "macos_unsupported"`, or a fixed `unsupported` response) without
    touching any database file.
- Unit tests for `FocusState` encoding/decoding and the socket round-trip.

**Deliverable:** the project builds, tests, and lints in CI;
  a local client can connect to the running helper over the socket and receive a well-formed
  (stubbed) `FocusState`.

**Deferred to later milestones:** any real Focus parsing; packaging as an installed LaunchAgent.

### M2 — Read-only Focus parsing on the current macOS version

**In scope:**

- macOS-version detection.
- Parsing `Assertions.json` to determine whether an active Focus assertion exists,
    and extracting the active Focus identifier when one does.
- Parsing `ModeConfigurations.json` to map the identifier to a human-readable Focus name.
- The compatibility-table lookup feeding `macos_compatibility`.
- The full failure taxonomy with explicit `error` codes
    (`focus_db_unreadable`, `focus_db_malformed`, `schema_unknown`, `macos_unsupported`,
    `internal_error`), with a parse/schema failure never reported as `ok: true, focus_enabled: false`.
- Fixture-based unit/integration tests: captured `Assertions.json` / `ModeConfigurations.json` shapes
    for Focus-on, Focus-off, malformed, and unknown-schema cases, for the developer's macOS version.

**Deliverable:** `get_focus()` returns a correct `FocusState` for Focus-on and Focus-off
  on a known-supported macOS version, and an explicit error on unreadable/malformed/unknown data.

**Deferred:** packaging/install; broad multi-version compatibility (only the developer's macOS version
  is required to be fully exercised here, though the parser should be structured to add versions).

### M3 — LaunchAgent packaging and install

**In scope:**

- A code-signed `.app` bundle, installed at the stable path, with a stable bundle identifier
    and signing identity.
- A per-user LaunchAgent plist and the install/uninstall flow that registers/unregisters it.
- Socket lifecycle management (create on launch, clean up on exit, single-instance behavior).
- Documentation of the macOS privacy permission the *helper* needs (Full Disk Access, if required)
    and how to grant it — and confirmation that no client receives any permission as a result.
- An end-to-end test: a client connects to the installed, running helper and receives a `FocusState`
    (against a real macOS session where feasible; otherwise the real socket/process over fixture data).

**Deliverable:** an installable helper that an unprivileged out-of-process client can query.

**Deferred:** distribution mechanics beyond a local install (notarization, auto-update).

### M4 — macOS compatibility breadth and contributor workflow

**In scope:**

- Seed the in-repo compatibility table: macOS 14 Sonoma — supported; macOS 15 Sequoia — supported;
    macOS 26 Tahoe — unknown until tested.
- Wire `macos_compatibility: unknown_but_working` (parsing succeeded on an unlisted version) with the
    "please submit an issue or PR marking this version as compatible" `message`,
    and the parse-failure `message` asking for an issue/PR with macOS version, helper version,
    and error code.
- Contributor documentation: how to add support for a new macOS version
    (capture fixtures, add/adjust the parser if the schema changed, add the table entry, add tests).

**Deliverable:** graceful, well-signposted behavior on macOS versions not yet on the supported list,
  and a documented path for contributors to extend coverage.

## Explicitly Deferred (out of scope for this plan)

- A packaged client library (Swift, Python, or otherwise) for consumers — clients can speak the
    documented socket protocol directly until there is a concrete need.
- Distribution beyond a local install: notarization, a download/installer, auto-update.
- Any operation beyond `get_focus()` — the narrow API is the point.

## References

- **Product Vision**: [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md).
- **Product Requirements**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
