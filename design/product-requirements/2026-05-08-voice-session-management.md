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

Karl can run multiple Claude Code sessions on the Mac mini concurrently,
  pick which session to talk to at the start of (or during) a phone call,
  hang up and dial back in later to resume the same session,
  and queue new tasks against a session that is mid-task
  rather than interrupting it.
This requirement turns Squawkbox from a single-session voice loop
  into a tool for managing long-running agent work over the course of a day.

## User Story

As Karl, I want to manage several Claude Code sessions across many phone calls
  so that I can pick up long-running agent work where I left off,
  steer multiple parallel projects from my car or while walking,
  and feed new work to a busy agent without interrupting whatever it's already doing.

## Acceptance Criteria

### Session Selection

- [ ] Karl can choose, at the start of a call, which Claude Code session to talk to
        from a list of currently-running sessions on the Mac mini.
- [ ] If no session is specified at trigger time, Squawkbox audibly lists the available
        sessions and prompts Karl to pick one.
- [ ] Karl can switch sessions mid-call by saying a recognized command
        (e.g. "switch to <session name>").

### Session Continuity

- [ ] Hanging up the call leaves the underlying Claude Code session running and intact;
        the session is not killed, paused, or otherwise mutated by the disconnect.
- [ ] Reconnecting to a previously-used session resumes its conversation history;
        the agent is aware of what was discussed previously without re-prompting.
- [ ] Long-running agent work continues independently of any active call;
        the next reconnect surfaces any progress or output produced while disconnected.

### Mid-Task Task Queueing

- [ ] Squawkbox can address new tasks Karl gives it during the call to the agent
        even when the agent is mid-task — the new task is queued behind the current one
        rather than interrupting it.
- [ ] Karl can ask Squawkbox what the agent is currently working on
        and hear an audible status summary.
- [ ] Karl can explicitly cancel a queued task by saying a recognized phrase
        (e.g. "cancel that last one") before the agent starts on it.

### Testing

- [ ] An automated end-to-end test verifies that two simulated calls to the same session
        share conversation history, with the second call referring to topics from the first.
- [ ] An automated integration test verifies that hanging up does not kill the session.
- [ ] An automated integration test verifies that a task queued mid-task is processed
        after the current task completes, in order.

## Out of Scope

- Cross-session context sharing (one session referring to another's work).
        Each session is independent.
- Migrating an existing session between hosts.
        Sessions live on the Mac mini for their lifetime.

## References

### Vision

- [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Long-running session management is what makes the homelab agent valuable
    when access is intermittent.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Session registry, agent adapter, and per-session orchestrator design.

### Related Requirements

- [Secure Voice Conversations With Homelab Claude Code Sessions](2026-05-08-secure-voice-calls.md) —
    The voice bridge that this requirement extends with multi-session capability.
- [Outbound Call Trigger via Apple Shortcuts](2026-05-08-outbound-call-trigger.md) —
    The trigger optionally accepts a session identifier;
    this requirement defines what happens with it.

### Implementation

- None yet.
