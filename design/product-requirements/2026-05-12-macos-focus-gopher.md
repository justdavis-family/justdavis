---
title: macOS Focus Gopher
status: draft
vision:
  - 2026-05-12-macos-focus-gopher
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-05-12-macos-focus-gopher.md
prs: []
---

# macOS Focus Gopher

## Summary

A per-user macOS helper that an unprivileged local client (e.g. an LLM/agent system) can query
  to learn the current macOS Focus state, without the client process itself holding Full Disk Access
  or any other broad macOS privacy permission.
The helper is a stable-identity app bundle (a fixed install path and bundle identifier), run as a
  per-user LaunchAgent, exposing exactly one read-only operation, `get_focus()`, returning a
  fixed-schema `FocusState`, over a local Unix domain socket — with a thin command-line wrapper for
  callers who prefer to run a command.
Developer ID code signing and notarization are an optional later enhancement — they make the Full Disk
  Access grant persist across upgrades and improve first-run signposting, but are not required for the
  helper to be fully functional.
The helper performs the privileged, undocumented Focus-database read itself,
  reports an explicit error when it cannot determine the state (never a silent "no Focus"),
  and reports whether the running macOS version is known-supported.

## User Story

As an agent system operator, I want a narrow macOS helper that reports the current Focus state
  over a local socket (or a one-line command), so that my agent can react to Focus
  without itself holding Full Disk Access or broad macOS automation permissions,
  and without the agent's identity churn breaking that access.

## Acceptance Criteria

### Helper Identity and Lifecycle

- [ ] The helper is distributed as an app bundle installed at a stable path with a stable bundle
        identifier (the unit the macOS privacy grant attaches to).
- [ ] Developer ID code signing and Apple notarization are an *optional* later enhancement, not
        required for the helper to be fully functional; when present they make the Full Disk Access
        grant persist across helper upgrades (otherwise the user re-applies it after each upgrade on
        the build-from-source channels). See the analysis referenced below.
- [ ] The helper runs as a per-user LaunchAgent — not a system LaunchDaemon —
        because Focus state is user-specific and the relevant files live under the user's home directory.
- [ ] Any macOS privacy permission the helper needs (Full Disk Access, which macOS requires to read the
        Focus database) is granted to the helper, not to any client; this grant is always a manual
        System Settings action, as macOS exposes no programmatic prompt for it.
- [ ] Clients that talk to the helper receive no Full Disk Access, Accessibility, Screen Recording,
        or Automation permission as a result.

### API Surface

- [ ] The helper exposes exactly one operation, `get_focus()`, returning a `FocusState`.
        Its primary transport is a local Unix domain socket; a thin command-line wrapper is also
        provided that performs the same `get_focus()` call over that socket and prints the `FocusState`
        as JSON. Both transports expose the same single operation and nothing more.
- [ ] The command-line wrapper exits with a non-zero status when `ok` is `false` (and zero otherwise),
        so shell scripts can branch on the exit code without parsing the JSON; the JSON body still
        carries `ok` and `error` for programmatic consumers reading the socket directly.
- [ ] The helper does not expose `read_file(path)`, `run_shell(command)`, `run_shortcut(name)`,
        `run_osascript(script)`, `query_db(path)`, or any other general-purpose or arbitrary operation.
- [ ] The helper is read-only: it never modifies Focus, notifications, or any system setting.
- [ ] The agent-facing interface (`get_focus() -> FocusState`) is stable and decoupled from the
        underlying Focus-database schema; parser changes do not change the interface.
- [ ] A versioned JSON Schema for `FocusState` is published and referenced from all of the project's
        documentation; the helper's output validates against it.

### `FocusState` Data Model

- [ ] `FocusState` is a single, flat object — a small single-purpose response, flat rather than nested
        (see the JSON-shape analysis referenced below) — with these fields and meanings:
      - `ok` (boolean): whether the helper successfully determined the Focus state.
      - `focus_enabled` (boolean or null): whether a Focus is currently active;
          `null` only when `ok` is `false`.
      - `focus_name` (string or null): the human-readable Focus name;
          `null` when Focus is off, or when the name could not be determined, or when `ok` is `false`.
      - `macos_version` (string): the detected macOS version.
      - `macos_compatibility` (enum): one of `supported`, `unknown_but_working`, `unknown`,
          or `unsupported`.
      - `message` (string or null): human-readable guidance; never load-bearing for program logic.
      - `error` (string, present on failures): a stable machine-readable error code
          (e.g. `focus_permission_denied`, `focus_db_unreadable`, `schema_unknown`).
- [ ] The helper does not include speculative fields (e.g. `normalized`, `source`, or a list of all
        known-compatible macOS versions) without a concrete consumer need.
- [ ] All four documented response shapes are produced correctly:
        (a) success, Focus on, with a name;
        (b) success, no Focus on;
        (c) success on an unknown-but-working macOS version (with `macos_compatibility:
        unknown_but_working` and a "please report this version" `message`);
        (d) failure (`ok: false`, `focus_enabled: null`, `focus_name: null`, an `error` code,
        and a "please file an issue/PR with your macOS version, helper version, and this error code"
        `message`).

### Consumer Logic

- [ ] The response model lets a consumer decide the state with a simple, unambiguous rule:
        if `ok` is `false`, the state is unknown;
        else if `focus_enabled` is `false`, Focus is off;
        else if `focus_enabled` is `true` and `focus_name` is non-null, Focus is on with that name;
        else (`focus_enabled` is `true` and `focus_name` is null) Focus is on but the name could not
        be determined.
- [ ] A consumer can distinguish "no Focus is active", "a Focus is active but unnamed/unmapped",
        "the helper failed", and "the macOS version is unsupported" from each other.

### Retrieval Logic

- [ ] Determining the Focus state follows this logic: detect the macOS version;
        check it against the known-supported list;
        read the active-assertions data and determine whether an active Focus assertion exists;
        if none exists, return `ok: true`, `focus_enabled: false`, `focus_name: null`
        (an empty active-assertions file is a valid "Focus is off" result, not an error);
        if one exists, extract the active Focus identifier, read the mode-configuration data,
        and map the identifier to a human-readable Focus name.
- [ ] The helper accounts for the documented quirks of the Focus database (see the analysis referenced
        below): a Focus activated by schedule or automation is reflected differently than a manually
        toggled one, so both the active-assertions data and the mode-configuration data are consulted.
- [ ] If parsing succeeds on a macOS version that is not on the known-supported list,
        the response sets `macos_compatibility: unknown_but_working` and includes the
        "please report this version" guidance.

### Failure Handling

- [ ] The helper tolerates missing files, permission-denied files, unreadable files, malformed JSON,
        schema changes, and partially-written files without crashing.
- [ ] Any failure to determine the Focus state is reported explicitly:
        `ok: false`, `focus_enabled: null`, `focus_name: null`, and a stable `error` code.
- [ ] A parsing or schema failure is never reported as `ok: true`, `focus_enabled: false`.
- [ ] A missing Full Disk Access grant is detected (a permission denial on the existing Focus
        database) and reported as a dedicated `focus_permission_denied` error code — never as
        `ok: true, focus_enabled: false` — with an actionable `message`: the canonical resolved helper
        binary path to add and a System Settings deep link to the Full Disk Access pane.

### macOS Compatibility

- [ ] The project maintains an explicit macOS-version compatibility table, keyed by macOS version
        string. An entry may be a specific point release (e.g. `15.5`) or a major-version wildcard
        (e.g. `15.*`). A major-version wildcard is permitted only when the format-stability analysis
        (referenced below) supports it for that major *and* the parser has been verified against at
        least one current point release of that major.
- [ ] The table is seeded per that analysis: macOS 12–15 are reasonable `supported` (wildcard) entries
        once verified; macOS 11 and earlier are out of scope (a different mechanism); the current macOS
        26 starts as `unknown` until verified.
- [ ] On an unknown-but-working macOS version, the response asks the user to submit an issue or PR
        marking that version as compatible.
- [ ] On a parsing failure, the response asks the user to file an issue or PR with their macOS version,
        the helper version, and the error code.

### Distribution and Documentation

- [ ] The helper can be installed with a single command via build-from-source channels — Homebrew
        (a formula in a tap) or `cargo install` — which handle the app bundle, the LaunchAgent
        registration, and putting the CLI wrapper on the user's `PATH`. A signed + notarized Homebrew
        cask is an optional later addition, not required here.
- [ ] The documentation explains, prominently, exactly how to grant Full Disk Access to the helper
        (the precise System Settings steps and the resolved binary path), and that on the
        build-from-source channels the grant must be re-applied after each upgrade.
- [ ] The project `README.md` clearly and concisely explains who the Focus Gopher is for, what problem
        it solves, and how to start using it — written to engage both human and agent readers, with at
        least one short, deliberately slow/clear screen-recording GIF demonstrating it, and including or
        referencing (depending on length) the full `--help`/`man` documentation.
- [ ] The `--help` output and/or `man` page are themselves clear, concise, useful to both human and
        agent readers, and include worked examples for every common operation and its result.
- [ ] The project ships bundled agent skills plus a simple command that installs them into the user's
        home directory or a specified project for common agent harnesses (e.g. Claude Code, Codex).
- [ ] The project has a clear OSS license (MIT, unless a better-established commercially-friendly choice
        is preferred at the time).
- [ ] The project has a `CONTRIBUTING.md` that orients contributors by briefly introducing the
        architecture and development workflow (largely by linking to these design docs) and by pointing
        at the repository-root `CONTRIBUTING.md`, without duplicating its content.

### Testing

- [ ] At least one unit or integration test covers the retrieval logic against fixture
        Focus-database files representing Focus-on (manual and scheduled), Focus-off (including the
        empty-file case), and malformed/unknown-schema cases, for each supported macOS major version
        (verified against at least one current point release of each).
- [ ] An end-to-end test verifies that a client can connect to the running helper over the socket
        (and that the CLI wrapper works) and receive a well-formed `FocusState` (exercised against a
        real macOS session where feasible, otherwise against fixture data with the real socket and
        process).

## References

### Vision

- [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md) —
    The product context: letting unprivileged agents read macOS Focus state via a narrow,
    stable-identity helper.

### Engineering Design

- [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md) —
    The technical approach: a Rust helper packaged as a stable-identity `.app` LaunchAgent
    (Developer ID signing/notarization an optional later enhancement), a Unix-domain-socket JSON
    protocol with a thin CLI wrapper, and a versioned read-only parser of the macOS Focus database.

### Analysis

- [macOS Focus Database Format and Stability](../analyses/2026-05-12-macos-focus-db-format.md) —
    Where the Focus state lives, how the format has held up across macOS 12–15, and the basis for the
    compatibility-table seeding (specific versions vs. major-version wildcards).
- [`FocusState` JSON Response Shape: Flat vs. Nested](../analyses/2026-05-12-focus-state-json-shape.md) —
    Why `FocusState` is a flat object rather than a nested envelope, and why the CLI wrapper carries the
    success/failure signal in its exit code as well as in `ok`.
- [macOS Full Disk Access, Code Signing, and Distribution Channels](../analyses/2026-05-18-macos-fda-distribution-signing.md) —
    Why signing/notarization are deferred optional UX improvements, how each distribution channel
    interacts with the Full Disk Access grant, and why graceful missing-FDA handling is a first-class
    early requirement.

### Engineering Principles

- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) —
    The helper exposes the narrowest capability that does the job, and brokers privileged access
    so the broad permission never reaches the agent.
- [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md) —
    `FocusState` separates orthogonal facts and never collapses "failed" into "no Focus".

### Related Requirements

- None.

### Implementation

- None yet.
