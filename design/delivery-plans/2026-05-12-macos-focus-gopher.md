# macOS Focus Gopher Delivery Plan

## Overview

This plan sequences delivery of the
  [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md) requirement into
  thin, independently-testable milestones, per the
  [engineering design](../engineering-designs/2026-05-12-macos-focus-gopher.md).

The main delivery risk is the *undocumented, version-fragile Focus database*
  (see the [format-stability analysis](../analyses/2026-05-12-macos-focus-db-format.md)).
The plan front-loads the stable parts (the project skeleton and the wire contract),
  then tackles parsing for the verified macOS versions, then packaging/distribution, then compatibility
  breadth and the agent ecosystem — so each milestone delivers something a consumer or contributor can
  actually exercise, and so a parser surprise on a future macOS version does not block the earlier
  milestones.

## Delivery Conventions

- **Each milestone ships as its own merged PR.**
- **Public docs are built incrementally, alongside code, tests, and CI** — not deferred to the last
    milestone. Every milestone PR leaves the project's `README.md` (and `--help`/`man` and the JSON
    Schema, once they exist) accurate for the state of the project *at that point*, and the README
    states plainly that the project is not yet ready for real use until it actually is.

## Milestones

### M1 — Project skeleton and the `get_focus()` contract

**In scope:**

- Scaffold `macos-focus-gopher/` at the repo root: a Rust crate (the helper binary plus the
    `focus-gopher` CLI wrapper) and the `.app` bundle packaging, a `mise.toml` exposing
    `build` / `test` / `lint` / `dependencies:check` / `dependencies:update` / `ci`, wired into the
    root `mise.toml`, and CI invoking those Mise tasks.
- Define the `FocusState` model, publish its versioned **JSON Schema**, and define the line-delimited
    JSON request/response protocol over a per-user Unix domain socket; the CLI wrapper relays
    `get_focus()` over that socket and prints the result.
- Implement `get_focus()` as a stub that returns a well-formed `FocusState`
    (e.g. `ok: false`, `error: "macos_unsupported"`) without touching any database file.
- Unit tests for `FocusState` encoding/decoding, schema validation, and the socket/CLI round-trip.
- Initial `README.md` (clearly marked early-development / not yet usable), an OSS `LICENSE` (MIT), and a
    `CONTRIBUTING.md` stub that points at the repository-root `CONTRIBUTING.md` and these design docs.

**Deliverable:** the project builds, tests, and lints in CI;
  a local client can connect to the running helper over the socket — or run `focus-gopher` — and
  receive a well-formed (stubbed) `FocusState` that validates against the published schema.

**Deferred to later milestones:** any real Focus parsing; packaging as an installed LaunchAgent;
  distribution.

### M2 — Read-only Focus parsing on the verified macOS versions

**In scope:**

- macOS-version detection.
- Parsing `Assertions.json` to determine whether a manually-activated Focus exists and extract its
    identifier; consulting `ModeConfigurations.json` for schedule/automation-activated Foci; the
    empty-file "Focus is off" case.
- Mapping identifiers to human-readable Focus names via `ModeConfigurations.json` and a fixed table for
    built-in Foci.
- The compatibility-table lookup feeding `macos_compatibility`, seeded per the format-stability
    analysis (the macOS 12–15 majors, verified against a current point release of each).
- The full failure taxonomy with explicit `error` codes
    (`focus_db_unreadable`, `focus_db_malformed`, `schema_unknown`, `macos_unsupported`,
    `internal_error`), with a parse/schema failure never reported as `ok: true, focus_enabled: false`.
- Fixture-based unit/integration tests: captured `Assertions.json` / `ModeConfigurations.json` shapes
    for manual-Focus-on, scheduled-Focus-on, Focus-off (including the empty file), malformed, and
    unknown-schema cases, per supported macOS major.
- `README.md` updated to reflect "works on macOS 12–15, run from source"; first cut of `--help` output
    with examples.

**Deliverable:** `get_focus()` returns a correct `FocusState` for Focus-on (manual and scheduled) and
  Focus-off on the supported macOS versions, and an explicit error on unreadable/malformed/unknown data.

**Deferred:** packaging/install; distribution; broader macOS version coverage; bundled agent skills.

### M3 — Packaging, install, and distribution

**In scope:**

- A code-signed and notarized `.app` bundle, installed at the stable path, with a stable bundle
    identifier and signing identity.
- A per-user LaunchAgent plist and the install/uninstall flow that registers/unregisters it; socket
    lifecycle management (create on launch, clean up on exit, single-instance behavior).
- A Homebrew formula (or tap) so the whole thing — bundle, LaunchAgent registration, `focus-gopher` on
    `PATH` — installs with a single command.
- Documentation of the macOS privacy permission the *helper* needs (Full Disk Access, if required) and
    how to grant it — and confirmation that no client receives any permission as a result.
- An end-to-end test: a client connects to the installed, running helper (and the CLI wrapper works)
    and receives a `FocusState` (against a real macOS session where feasible; otherwise the real
    socket/process over fixture data).
- `README.md` updated with one-command install instructions and a short, deliberately slow/clear
    screen-recording GIF; a `man` page.

**Deliverable:** an installable helper (`brew install …`) that an unprivileged out-of-process client can
  query, with honest install-and-use docs.

**Deferred:** auto-update; broader macOS version coverage; bundled agent skills.

### M4 — Compatibility breadth, the agent ecosystem, and docs polish

**In scope:**

- Maintain/expand the compatibility table: add macOS versions as they are verified (updating the
    format-stability analysis as needed), wire `macos_compatibility: unknown_but_working` (parsing
    succeeded on an unlisted version) with the "please submit an issue or PR" `message`, and the
    parse-failure `message` asking for an issue/PR with macOS version, helper version, and error code.
- Contributor documentation: how to add support for a new macOS version (capture fixtures, adjust the
    parser if the schema changed, add the table entry, add tests).
- Ship bundled **agent skills** plus a command that installs them into the user's home directory or a
    specified project for common agent harnesses (e.g. Claude Code, Codex).
- Final `README.md` / `--help` / `man` polish for both human and agent audiences (engaging content,
    clear examples for every common operation, the JSON Schema referenced from the docs).

**Deliverable:** graceful, well-signposted behavior on macOS versions not yet on the supported list, a
  documented path for contributors to extend coverage, and a project that is easy for humans and agents
  to discover, install, and use.

## Explicitly Deferred (out of scope for this plan)

- A packaged client library (Rust, Python, or otherwise) for consumers — clients can speak the
    documented socket protocol or use the CLI wrapper until there is a concrete need.
- Distribution beyond Homebrew (e.g. a standalone downloadable installer) and auto-update.
- Any operation beyond `get_focus()` — the narrow API is the point.

## References

- **Product Vision**: [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md).
- **Product Requirements**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- **Analysis**: [macOS Focus Database Format and Stability](../analyses/2026-05-12-macos-focus-db-format.md).
