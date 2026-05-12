# macOS Focus Gopher

## Problem and Motivation

LLM-driven agent systems running on macOS — OpenClaw and similar automation agents —
  often need to know the user's current Focus state
  (is a Focus on, and if so, which one?)
  so they can decide whether it is appropriate to interrupt, notify, or act.

macOS exposes that state only through privacy-gated mechanisms.
The underlying Focus / Do Not Disturb state lives in undocumented files under the user's home directory,
  and reading them generally requires Full Disk Access;
  the documented alternatives (Shortcuts, AppleScript) require Automation permissions.
macOS grants all of these permissions to a *specific executable identity*,
  not to "whatever is running right now".

Agents are a poor fit for that model.
They are launched through a shifting set of identities — Terminal, SSH, `uv`, Python, Node, Docker,
  OpenClaw, frequently-rebuilt binaries, and ephemeral virtual environments —
  so a permission granted today is attached to a binary that may not exist tomorrow.
Worse, granting Full Disk Access (or broad Automation permissions) *to the agent itself* is dangerous:
  agents typically have internet access, arbitrary tool use, plugins, and prompt-injection exposure,
  so the blast radius of a compromised or manipulated agent that holds Full Disk Access is enormous.

What's missing is a way for an unprivileged agent to ask a single, narrow question —
  "what is the current Focus state?" —
  without the agent process itself holding any broad macOS privacy permission.

## Vision

A small, single-purpose macOS helper — the **Focus Gopher** — that owns the macOS-specific access
  and exposes exactly one read-only operation to local clients: `get_focus() -> FocusState`.

The helper is a code-signed `.app` with a stable install path, stable bundle identifier, and stable
  signing identity, run as a per-user LaunchAgent, so the macOS privacy permission it needs
  (Full Disk Access, if macOS requires it) attaches to *the helper* and survives agent rebuilds,
  reinstalls, and identity churn.
Clients reach it over a local Unix domain socket.

The helper is deliberately *not* a general-purpose automation service.
It exposes `get_focus()` and nothing else — no `read_file(path)`, `run_shell(command)`,
  `run_shortcut(name)`, `run_osascript(script)`, or `query_db(path)` —
  so an agent that can talk to the Focus Gopher gains the ability to read Focus state and no other capability.

Because the macOS Focus database format is undocumented and changes between releases,
  the helper's value is its *stable interface*, not the schema it parses.
The response model separates orthogonal facts — whether the helper succeeded, whether a Focus is enabled,
  whether a Focus name is available, and whether this macOS version is known-supported —
  so consumers never have to guess, and a parsing failure is reported as an explicit error
  rather than silently masquerading as "no Focus is on".
The helper ships a macOS-version compatibility table, asks users to report unknown-but-working versions,
  and asks for an issue or PR (with version and error details) when parsing fails on a new release.

## Success Metrics

- An agent can retrieve the current Focus state (on/off, and the Focus name when on)
    via a single local call, without holding Full Disk Access or any other broad macOS privacy permission.
- Rebuilding, reinstalling, or relaunching the agent — or changing how it is launched —
    does not break Focus retrieval, because no macOS permission is attached to the agent's identity.
- The helper has a stable macOS identity: a fixed install path, bundle ID, and signing identity,
    updated infrequently.
- The helper exposes exactly one read-only operation and no arbitrary filesystem, shell, Shortcut,
    or AppleScript access.
- The helper's responses unambiguously distinguish *no Focus is on*, *a Focus is on* (with or without
    a resolved name), and *the state could not be determined*; a parsing failure is never reported as
    "no Focus is on".
- The helper reports whether the running macOS version is known-supported, and emits actionable
    guidance on unknown-but-working versions and on parsing failures.

## Requirements

This vision is being implemented through the following requirements:

- [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md) —
    A per-user macOS helper that reports the current Focus state over a local socket
    behind a narrow, read-only `get_focus()` API (draft).
