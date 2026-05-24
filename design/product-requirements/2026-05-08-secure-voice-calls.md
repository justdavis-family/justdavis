---
title: Secure Voice Conversations With Homelab Claude Code Sessions
status: draft
vision:
  - 2026-05-08-squawkbox
depends_on:
  - 2026-05-08-outbound-call-trigger
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-05-08-squawkbox-architecture.md
prs: []
---

# Secure Voice Conversations With Homelab Claude Code Sessions

## Summary

Once an authenticated outbound call is connected to Squawkbox,
  Squawkbox bridges the call's audio to a Claude Code session on the homelab host
  and converts speech to text and back so that the operator and the agent can converse naturally.
The conversation must be low-latency enough to feel usable,
  resilient to provider failures,
  and free of any third-party storage of conversation content.

## User Story

As the operator, I want to talk to a homelab Claude Code session from my phone
  so that I can interact with my agents while driving, walking, or otherwise away from my desk —
  without compromising the security of those agents
  or the confidentiality of what we discuss.

## Acceptance Criteria

### Conversation Quality

- [ ] End-to-end voice-to-voice latency stays under 15 seconds for 95% of turns,
        measured from end-of-user-speech to start-of-agent-audio playback.
      (Ideally this would be much closer to 2 seconds for a pleasant experience,
        but it is not yet clear that a homelab setup can hit that;
        the target will be tightened once latency is measured on real hardware.)
- [ ] Speech-to-text accuracy is good enough that the operator rarely needs to repeat themselves
        for ordinary technical conversation
        (e.g. file paths, command names, project names).
- [ ] The operator can interrupt the agent mid-utterance and the agent stops speaking promptly.
      (A sub-500ms stop is the goal;
        because interruption depends only on voice-activity detection
        rather than the full STT/agent/TTS path, this target may well be achievable,
        but it will be confirmed against real hardware before being fixed.)
- [ ] Long silences during agent processing don't time out the call;
        the connection is held open as long as the agent is actively working.

### Authentication and Authorization

- [ ] Only authenticated outbound calls are bridged to Claude Code sessions;
        inbound calls are blocked or left unanswered.
      (Authenticated inbound calls are out of scope because PSTN caller ID is spoofable
        and no sufficiently strong inbound authentication path has been chosen;
        see the engineering design.)
- [ ] An incorrect or missing authentication on the trigger fails closed
        (no call is placed or bridged, and no agent interaction occurs)
        and is logged for later review.
- [ ] The operator can revoke any active credential without restarting Squawkbox
        or interrupting Claude Code sessions.

### Reliability

- [ ] If the homelab host is unreachable when a call is initiated,
        the operator receives a clear audible message indicating the system is offline,
        and the call ends gracefully.
- [ ] If the Claude Code session crashes or becomes unresponsive mid-call,
        the operator is told audibly that the session has failed
        and is offered the option to start a new session or end the call.
- [ ] If STT or TTS providers are unavailable,
        Squawkbox surfaces a clear, structured error through its normal alerting path.

### Privacy and Data Handling

- [ ] No conversation audio, transcripts, or text is persisted to any third-party cloud service
        beyond what is required for live STT and TTS request handling.
- [ ] Audio between Squawkbox and the Claude Code session never leaves the homelab's private network.
- [ ] The chosen telephony provider's call recording feature is disabled.
- [ ] The operator can configure Squawkbox to redact specific patterns from transcripts before logging
        (e.g. API keys or credentials accidentally spoken aloud).

### Testing

- [ ] Automated tests cover the authenticated-call happy path
        (a multi-turn conversation through to a graceful hang-up)
        and the rejection of an unauthenticated or inbound call.
- [ ] The feature is verified end-to-end against a real Claude Code session
        before the requirement is considered done.

## Out of Scope

- Multiple simultaneous callers or multi-party calls.
  Squawkbox supports one active call at a time.
- Choosing, resuming, or queueing tasks against specific Claude Code sessions.
  The initial system bridges a call to a single configured session;
    multi-session capability is captured in the deferred
    [Voice Session Management](2026-05-08-voice-session-management.md) requirement.
- Inbound call routing.
  Only authenticated outbound calls are supported;
    a future requirement may add inbound calls if a sufficiently strong inbound auth scheme is found.

## References

### Vision

- [Squawkbox: Voice Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    The core capability without which the vision cannot be realized.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Layered audio + STT + agent + TTS pipeline, telephony provider choice, and authentication design;
    also documents the test approach (mock providers, sandbox session) for this requirement.

### Related Requirements

- [Outbound Call Trigger via Apple Shortcuts](2026-05-08-outbound-call-trigger.md) —
    The authenticated trigger that initiates the call this requirement bridges.
- [Hands-Free Voice Permission Handling](2026-05-08-voice-permission-handling.md) —
    Permission approval flow used during conversations covered by this requirement.
- [Voice Session Management](2026-05-08-voice-session-management.md) —
    Deferred: multi-session selection, reconnection, and task queueing on top of this voice bridge.

### Implementation

- None yet.
