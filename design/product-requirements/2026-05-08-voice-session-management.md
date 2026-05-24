---
title: Voice Session Management
status: draft
vision:
  - 2026-05-08-squawkbox
depends_on:
  - 2026-05-08-secure-voice-calls
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-05-08-squawkbox-architecture.md
prs: []
---

# Voice Session Management

## Summary

**This requirement is deferred to a later phase.**
The initial Squawkbox system bridges a call to exactly one configured Claude Code session,
  which matches the Claude Code Channels model of one channel per session.
Supporting several sessions through a single service and phone number adds a
  connection-and-routing harness that should not be taken on
  until the basic single-session voice loop is solid.

When built, this requirement lets the operator run multiple Claude Code sessions concurrently,
  pick which session to talk to at the start of (or during) a call,
  hang up and dial back in later to resume the same session,
  and queue new tasks against a session that is mid-task rather than interrupting it.

## User Story

As the operator, I want to manage several Claude Code sessions across many phone calls
  so that I can pick up long-running agent work where I left off,
  steer multiple parallel projects from my car or while walking,
  and feed new work to a busy agent without interrupting whatever it's already doing.

## Acceptance Criteria

### Session Selection

- [ ] The operator can choose, at the start of a call, which Claude Code session to talk to
        from a list of currently-running sessions on the homelab host.
- [ ] The outbound-call trigger accepts an optional session identifier chosen at trigger time.
- [ ] If no session is specified, Squawkbox audibly lists the available sessions
        and prompts the operator to pick one.
- [ ] The operator can switch sessions mid-call by saying a recognized command
        (e.g. "switch to <session name>").

### Session Continuity

- [ ] Hanging up the call leaves the underlying Claude Code session running and intact;
        the session is not killed, paused, or otherwise mutated by the disconnect.
- [ ] Reconnecting to a previously-used session resumes its conversation history;
        the agent is aware of what was discussed previously without re-prompting.
- [ ] Long-running agent work continues independently of any active call;
        the next reconnect surfaces any progress or output produced while disconnected.

### Mid-Task Task Queueing

- [ ] The operator can give new tasks to the agent during a call
        even when the agent is mid-task — the new task is queued behind the current one
        rather than interrupting it.
- [ ] The operator can ask Squawkbox what the agent is currently working on
        and hear an audible status summary.
- [ ] The operator can cancel a queued task by saying a recognized phrase
        (e.g. "cancel that last one") before the agent starts on it.

### Testing

- [ ] Automated tests verify that two calls to the same session share conversation history,
        that hanging up does not kill the session,
        and that a task queued mid-task is processed in order after the current task completes.

## Out of Scope

- Cross-session context sharing (one session referring to another's work).
  Each session is independent.
- Migrating an existing session between hosts.
  Sessions live on the homelab host for their lifetime.

## References

### Vision

- [Squawkbox: Voice Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Long-running session management is what makes the homelab agent valuable
    when access is intermittent;
    listed there as deferred to a later phase.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Session registry, agent adapter, and per-session orchestrator design.

### Related Requirements

- [Secure Voice Conversations With Homelab Claude Code Sessions](2026-05-08-secure-voice-calls.md) —
    The single-session voice bridge that this requirement extends with multi-session capability.
- [Outbound Call Trigger via Apple Shortcuts](2026-05-08-outbound-call-trigger.md) —
    This requirement adds the optional session identifier to the trigger.

### Implementation

- None yet.
