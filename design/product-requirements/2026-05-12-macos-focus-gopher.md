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

A small macOS helper that an unprivileged local client (e.g. an LLM/agent system) can query to learn
  the current macOS Focus state, without the client process itself holding Full Disk Access or any
  other broad macOS privacy permission.
It answers exactly one question — "what is the current Focus state?" — callable over a local socket or
  via a one-line command, and it has a stable identity so the macOS permission it needs is tied to the
  helper rather than to the client's churning identity.
The helper performs the privileged read itself and answers from a fixed, documented schema: a Focus is
  on (with its name), no Focus is on, or the state could not be determined — the last reported as an
  explicit error with guidance, never a silent "no Focus" — along with whether the running macOS version
  is known to be supported.

## User Story

As an agent system operator, I want a narrow macOS helper that reports the current Focus state
  over a local socket (or a one-line command), so that my agent can react to Focus
  without itself holding Full Disk Access or broad macOS automation permissions,
  and without the agent's identity churn breaking that access.

## Acceptance Criteria

### Privacy and Trust

- [ ] A client can learn the current Focus state without itself holding Full Disk Access or any other
        broad macOS privacy permission.
- [ ] Talking to the helper grants a client no Full Disk Access, Accessibility, Screen Recording, or
        Automation permission.
- [ ] Whatever macOS permission the helper needs (Full Disk Access) is held by the helper, not by any
        client. Granting it is a one-time manual step in System Settings (macOS offers no programmatic
        prompt); on build-from-source installs the user re-applies it after an upgrade, and an optional
        signed distribution (later) removes that re-grant.
- [ ] The helper's access is not broken by the client being rebuilt, reinstalled, or launched
        differently — the permission is tied to the helper's stable identity, not the client's.

### Capability and Surface

- [ ] The helper answers exactly one question — the current Focus state — callable over a local socket
        or via a one-line command; both expose the same single operation and nothing more.
- [ ] The helper is read-only: it never changes Focus, notifications, or any system setting.
- [ ] The helper offers no general-purpose or arbitrary capability — no reading arbitrary files,
        running shell commands, running Shortcuts, or running AppleScript — so a client that can reach
        it gains only the ability to read Focus state.

### Response and Behavior

- [ ] A consumer can unambiguously distinguish: no Focus is active; an active Focus together with its
        name; the helper could not determine the state (with a machine-readable reason and a
        human-readable explanation); and the running macOS version being unsupported.
- [ ] A failure to determine the state is always reported explicitly — never as a silent "no Focus is
        on".
- [ ] When the state cannot be determined because the helper lacks Full Disk Access, the response says
        so and tells the user exactly what to grant and where to fix it.
- [ ] The active Focus is reported whether it was turned on manually or by a schedule/automation.
- [ ] The helper fails gracefully — a missing, unreadable, or malformed Focus database yields an
        explicit error, not a crash.
- [ ] The command-line wrapper exits non-zero when the state cannot be determined (and zero otherwise),
        so scripts can branch on the exit code without parsing the output.
- [ ] The response conforms to a fixed, versioned, published schema (a JSON Schema) referenced from the
        project's documentation, so consumers can validate and rely on it; the answer interface stays
        stable even as macOS changes the underlying data format.

### macOS Support Reporting

- [ ] Each response states whether the running macOS version is known-supported, known-unsupported, or
        unknown.
- [ ] On an unknown (unlisted) macOS version, the response asks the user to report whether it worked,
        so coverage can be extended.
- [ ] On a failure, the response asks the user to file an issue or PR with their macOS version, the
        helper version, and the error.

### Installation, Documentation, and Adoption

- [ ] The helper installs with a single command (e.g. Homebrew or `cargo install`), setting itself up
        to run and putting the command-line wrapper on the user's `PATH`.
- [ ] The documentation explains, prominently, how to grant Full Disk Access to the helper (the precise
        steps), including that on build-from-source installs the grant must be re-applied after an
        upgrade.
- [ ] The `README.md` clearly and concisely explains who the Focus Gopher is for, what problem it
        solves, and how to start using it — written to engage both human and agent readers, with at
        least one short, deliberately slow/clear screen-recording GIF demonstrating it, and including or
        referencing (depending on length) the full `--help`/`man` documentation.
- [ ] The `--help` output and/or `man` page are clear, concise, useful to both human and agent readers,
        and include worked examples for every common operation and its result.
- [ ] The project ships bundled agent skills plus a simple command that installs them into the user's
        home directory or a specified project for common agent harnesses (e.g. Claude Code, Codex).
- [ ] The project has a clear OSS license (MIT, unless a better-established commercially-friendly choice
        is preferred at the time).
- [ ] The project has a `CONTRIBUTING.md` that orients contributors by briefly introducing the
        architecture and development workflow (largely by linking to these design docs) and by pointing
        at the repository-root `CONTRIBUTING.md`, without duplicating its content.

## References

### Vision

- [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md) —
    The product context: letting unprivileged agents read macOS Focus state via a narrow,
    stable-identity helper.

### Engineering Design

- [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md) —
    The technical approach (the *how*): a Rust helper packaged as a stable-identity `.app` LaunchAgent
    (Developer ID signing/notarization an optional later enhancement), a Unix-domain-socket JSON
    protocol with a thin CLI wrapper, the `FocusState` data model and retrieval pipeline, the
    compatibility table, and the testing approach.

### Analysis

- [macOS Focus Database Format and Stability](../analyses/2026-05-12-macos-focus-db-format.md) —
    Where the Focus state lives, how the format has held up across macOS 12–15, and the basis for the
    compatibility-table seeding (specific versions vs. major-version wildcards).
- [`FocusState` JSON Response Shape: Flat vs. Tagged Union](../analyses/2026-05-12-focus-state-json-shape.md) —
    Why `FocusState` is an externally-tagged discriminated union mirroring the helper's internal sum
    type (no transport status code, so the body carries the discriminant), and why the CLI wrapper also
    carries the success/failure signal in its exit code.
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
