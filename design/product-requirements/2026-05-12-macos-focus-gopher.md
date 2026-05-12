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
The helper is a code-signed `.app` with a stable identity, run as a per-user LaunchAgent,
  exposing exactly one read-only operation over a local Unix domain socket:
  `get_focus()`, returning a fixed-schema `FocusState`.
The helper performs the privileged, undocumented Focus-database read itself,
  reports an explicit error when it cannot determine the state (never a silent "no Focus"),
  and reports whether the running macOS version is known-supported.

## User Story

As an agent system operator, I want a narrow macOS helper that reports the current Focus state
  over a local socket, so that my agent can react to Focus
  without itself holding Full Disk Access or broad macOS automation permissions,
  and without the agent's identity churn breaking that access.

## Acceptance Criteria

### Helper Identity and Lifecycle

- [ ] The helper is distributed as a code-signed `.app` bundle installed at a stable path
        with a stable bundle identifier and a stable signing identity.
- [ ] The helper runs as a per-user LaunchAgent — not a system LaunchDaemon —
        because Focus state is user-specific and the relevant files live under the user's home directory.
- [ ] Any macOS privacy permission the helper needs (Full Disk Access, if macOS requires it
        to read the Focus database) is granted to the helper, not to any client.
- [ ] Clients that talk to the helper receive no Full Disk Access, Accessibility, Screen Recording,
        or Automation permission as a result.

### API Surface

- [ ] The helper exposes exactly one operation over a local Unix domain socket: `get_focus()`,
        returning a `FocusState`.
- [ ] The helper does not expose `read_file(path)`, `run_shell(command)`, `run_shortcut(name)`,
        `run_osascript(script)`, `query_db(path)`, or any other general-purpose or arbitrary operation.
- [ ] The helper is read-only: it never modifies Focus, notifications, or any system setting.
- [ ] The agent-facing interface (`get_focus() -> FocusState`) is stable and decoupled from the
        underlying Focus-database schema; parser changes do not change the interface.

### `FocusState` Data Model

- [ ] `FocusState` has these fields with these meanings:
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
          (e.g. `focus_db_unreadable`, `schema_unknown`).
- [ ] The helper does not include speculative fields (e.g. `normalized`, `source`)
        without a concrete consumer need.
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
        if none exists, return `ok: true`, `focus_enabled: false`, `focus_name: null`;
        if one exists, extract the active Focus identifier, read the mode-configuration data,
        and map the identifier to a human-readable Focus name.
- [ ] If parsing succeeds on a macOS version that is not on the known-supported list,
        the response sets `macos_compatibility: unknown_but_working` and includes the
        "please report this version" guidance.

### Failure Handling

- [ ] The helper tolerates missing files, unreadable files, malformed JSON, schema changes,
        and partially-written files without crashing.
- [ ] Any failure to determine the Focus state is reported explicitly:
        `ok: false`, `focus_enabled: null`, `focus_name: null`, and a stable `error` code.
- [ ] A parsing or schema failure is never reported as `ok: true`, `focus_enabled: false`.

### macOS Compatibility

- [ ] The project maintains an explicit macOS-version compatibility table,
        seeded with: macOS 14 Sonoma — supported; macOS 15 Sequoia — supported;
        macOS 26 Tahoe — unknown until tested.
- [ ] On an unknown-but-working macOS version, the response asks the user to submit an issue or PR
        marking that version as compatible.
- [ ] On a parsing failure, the response asks the user to file an issue or PR with their macOS version,
        the helper version, and the error code.

### Testing

- [ ] At least one unit or integration test covers the retrieval logic against fixture
        Focus-database files representing Focus-on, Focus-off, and malformed/unknown-schema cases,
        for each known-supported macOS version.
- [ ] An end-to-end test verifies that a client can connect to the running helper over the socket
        and receive a well-formed `FocusState` (exercised against a real macOS session where feasible,
        otherwise against fixture data with the real socket and process).

## References

### Vision

- [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md) —
    The product context: letting unprivileged agents read macOS Focus state via a narrow,
    stable-identity helper.

### Engineering Design

- [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md) —
    The technical approach: a Swift `.app` LaunchAgent, a Unix-domain-socket JSON protocol,
    and a versioned read-only parser of the macOS Focus database.

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
