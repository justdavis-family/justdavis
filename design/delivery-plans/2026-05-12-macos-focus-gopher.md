# macOS Focus Gopher Delivery Plan

## Overview

This plan sequences delivery of the
  [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md) requirement into
  thin, independently-testable milestones, per the
  [engineering design](../engineering-designs/2026-05-12-macos-focus-gopher.md).

The main delivery risk is the *undocumented, version-fragile Focus database*
  (see the [format-stability analysis](../analyses/2026-05-12-macos-focus-db-format.md)).
The plan front-loads the stable parts (the project skeleton and the wire contract), then the CLI
  wrapper (so the service is usable without `socat`/`nc` + `jq`), then parsing for the verified macOS
  versions, then build-from-source packaging/distribution, then compatibility breadth and the agent
  ecosystem — so each milestone delivers something a consumer or contributor can actually exercise, and
  so a parser surprise on a future macOS version does not block the earlier milestones.

Per the [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md),
  **code signing and notarization are deferred to a final, optional milestone (M6) that may or may not
  be reached.** The earlier milestones ship build-from-source distribution (`cargo install`, Homebrew
  formula/tap), which need no Apple Developer account and no notarization. Because Full Disk Access can
  never be granted programmatically and is invalidated on every upgrade of an unsigned build, **graceful
  missing-FDA handling — a dedicated error code, an actionable deep-linked message, and clear
  documentation — is a first-class concern of the earlier milestones, not something M6 introduces.**

## Delivery Conventions

- **Each milestone ships as its own merged PR.**
- **Public docs are built incrementally, alongside code, tests, and CI** — not deferred to the last
    milestone. Every milestone PR leaves the project's `README.md` (and `--help`/`man` and the JSON
    Schema, once they exist) accurate for the state of the project *at that point*, and the README
    states plainly that the project is not yet ready for real use until it actually is.

## Milestones

### M1 — Project skeleton and the `get_focus()` contract

**In scope:**

- Scaffold `macos-focus-gopher/` at the repo root: a Rust crate (the helper binary; the CLI binary is
    stubbed in but not yet wired up) and the `.app` bundle packaging, a `mise.toml` exposing
    `build` / `test` / `lint` / `dependencies:check` / `dependencies:update` / `ci`, wired into the
    root `mise.toml`, and CI invoking those Mise tasks.
- Define the `FocusState` model, publish its versioned **JSON Schema**, and define the line-delimited
    JSON request/response protocol over a per-user Unix domain socket.
- Implement `get_focus()` as a stub that returns a well-formed `FocusState`
    (e.g. `ok: false`, `error: "macos_unsupported"`) without touching any database file.
- Unit tests for `FocusState` encoding/decoding, JSON-Schema validation, and the socket round-trip.
- Initial `README.md` (clearly marked early-development / not yet usable), an OSS `LICENSE` (MIT), and a
    `CONTRIBUTING.md` stub that points at the repository-root `CONTRIBUTING.md` and these design docs.

**Deliverable:** the project builds, tests, and lints in CI; a local client can connect to the running
  helper over the socket and receive a well-formed (stubbed) `FocusState` that validates against the
  published schema. (For local poking before M2, a raw socket tool like `nc`/`socat` is enough.)

**Deferred to later milestones:** the CLI wrapper; any real Focus parsing; packaging as an installed
  LaunchAgent; distribution.

### M2 — The `focus-gopher` CLI wrapper

**In scope:**

- Implement the thin `focus-gopher` CLI: it connects to the socket, performs `get_focus()`, prints the
    `FocusState` as JSON, and exits non-zero when `ok` is `false` (zero otherwise).
- `--help` output with worked examples.
- Tests covering the CLI round-trip and exit-code behavior.
- `README.md` updated with CLI usage (so the service is usable without `socat`/`nc` + `jq`).

**Deliverable:** a human or agent can run `focus-gopher` and get the (stubbed, until M3) `FocusState`
  without touching the raw socket.

**Deferred:** real Focus parsing; packaging/install; distribution.

### M3 — Read-only Focus parsing on the verified macOS versions

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
    (`focus_permission_denied`, `focus_db_unreadable`, `focus_db_malformed`, `schema_unknown`,
    `macos_unsupported`, `internal_error`), with a parse/schema/permission failure never reported as
    `ok: true, focus_enabled: false`.
- **Graceful missing-FDA handling:** an `EPERM` on the (existing) Focus database is mapped to the
    dedicated `focus_permission_denied` code with an actionable `message` — the *canonical resolved*
    helper binary path to add, plus the
    `x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles` deep link — per the
    [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md).
- Fixture-based unit/integration tests: captured `Assertions.json` / `ModeConfigurations.json` shapes
    for manual-Focus-on, scheduled-Focus-on, Focus-off (including the empty file), malformed,
    unknown-schema, and permission-denied (`EPERM`) cases, per supported macOS major.
- `README.md` updated to reflect "works on macOS 12–15, run from source", **including a clear
    "grant Full Disk Access to the helper" section** (the exact System Settings steps, and that the
    grant must be re-applied after each upgrade on the build-from-source channels).
- **Dev docs — developing against the live Focus database (first milestone that reads the protected
    files):** the contributor docs (`CONTRIBUTING.md` and/or a README "Developing" section) gain a
    local-development guide: the fixture suite needs no Full Disk Access, and live-database smoke
    testing needs FDA granted either to the developer's terminal/IDE (TCC responsible-process
    attribution, for run-from-terminal iteration) or via a self-signed local code-signing certificate
    so the grant survives rebuilds — per the
    [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md).

**Deliverable:** `get_focus()` (via socket or `focus-gopher`) returns a correct `FocusState` for
  Focus-on (manual and scheduled) and Focus-off on the supported macOS versions, and an explicit error
  on unreadable/malformed/unknown data.

**Deferred:** packaging/install; distribution; broader macOS version coverage; bundled agent skills.

### M4 — Build-from-source packaging, install, and distribution

**In scope:**

- An (unsigned / ad-hoc-signed) `.app` bundle laid out at the stable path with the stable bundle
    identifier — the full bundle/LaunchAgent *architecture*, minus the Developer ID signature and
    notarization (deferred to M6).
- A per-user LaunchAgent plist and the install/uninstall flow that registers/unregisters it; socket
    lifecycle management (create on launch, clean up on exit, single-instance behavior).
- Build-from-source distribution: a Homebrew **formula (in a tap)** and `cargo install`, so the whole
    thing — bundle, LaunchAgent registration, `focus-gopher` on `PATH` — installs with a single
    command, with no Apple Developer account required (see the
    [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md)).
- Documentation of the Full Disk Access grant the *helper* needs and exactly how to grant it,
    **prominently including that an unsigned/from-source build's grant is invalidated on every upgrade
    and must be re-applied** — and confirmation that no client receives any permission as a result.
- An end-to-end test: a client connects to the installed, running helper (and `focus-gopher` works) and
    receives a `FocusState` (against a real macOS session where feasible; otherwise the real
    socket/process over fixture data), explicitly covering the `focus_permission_denied` path when FDA
    is absent.
- `README.md` updated with one-command install instructions and a short, deliberately slow/clear
    screen-recording GIF; a `man` page.
- **Dev docs + tooling — the LaunchAgent shape (first milestone that builds a user LaunchAgent):**
    because LaunchAgent-attributed access keys TCC to the helper binary's own (per-rebuild churning)
    cdhash, the contributor docs document the self-signed local code-signing certificate workflow, and
    the project ships a `mise`/build task that signs dev builds with that local certificate, so the
    Full Disk Access grant persists across rebuilds during LaunchAgent testing without an Apple
    Developer account — per the
    [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md).

**Deliverable:** an installable helper (`brew install …` from a tap, or `cargo install`) that an
  unprivileged out-of-process client can query, with honest install-and-use docs that set correct
  expectations about the manual (and per-upgrade) Full Disk Access grant.

**Deferred:** code signing, notarization, and cask distribution (M6); auto-update; broader macOS
  version coverage; bundled agent skills.

### M5 — Compatibility breadth, the agent ecosystem, and docs polish

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

### M6 — Code signing, notarization, and signed-update distribution (optional; may not be reached)

This milestone is a **nice-to-have UX improvement**, explicitly optional, and may never be done.
Everything in M1–M5 is fully usable without it; per the
  [FDA / signing / distribution analysis](../analyses/2026-05-18-macos-fda-distribution-signing.md)
  signing/notarization do **not** enable programmatic FDA granting and do **not** remove the one-time
  manual grant — their value is narrower and incremental.

**Prerequisite:** an Apple Developer Program membership ($99/yr) and a Developer ID certificate.

**In scope (the incremental UX wins):**

- Developer ID signing + Apple notarization of the existing `.app` bundle, with a stable signing
    identity, wired into the release pipeline.
- A Homebrew **cask** distributing the prebuilt, signed + notarized bundle from a hosted release
    artifact (clears the Gatekeeper launch wall that quarantined casks otherwise hit).
- The payoff, documented in the `README.md`: the Full Disk Access grant now **persists across
    updates** (TCC keys off the stable Developer ID identity rather than the per-build cdhash), and the
    OS surfaces its redirect dialog / FDA-pane pre-listing on first denial. The build-from-source
    channels (M4) remain supported and unchanged for users without the signed channel.

**Deliverable:** a signed + notarized `brew install --cask …` path whose Full Disk Access grant
  survives upgrades, alongside the still-supported build-from-source channels.

**Deferred:** auto-update.

## Explicitly Deferred (out of scope for this plan)

- A packaged client *library* (Rust, Python, or otherwise) for consumers — clients can speak the
    documented socket protocol or use the `focus-gopher` CLI until there is a concrete need.
- Distribution beyond `cargo install` and Homebrew (formula/tap, plus the optional M6 cask) —
    e.g. a standalone downloadable installer — and auto-update.
- Any operation beyond `get_focus()` — the narrow API is the point.

## References

- **Product Vision**: [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md).
- **Product Requirements**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- **Analyses**: [macOS Focus Database Format and Stability](../analyses/2026-05-12-macos-focus-db-format.md);
    [`FocusState` JSON Response Shape: Flat vs. Nested](../analyses/2026-05-12-focus-state-json-shape.md);
    [macOS Full Disk Access, Code Signing, and Distribution Channels](../analyses/2026-05-18-macos-fda-distribution-signing.md).
