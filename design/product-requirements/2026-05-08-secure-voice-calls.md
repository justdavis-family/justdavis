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

Once an authenticated phone call is connected to Squawkbox,
  Squawkbox bridges the call's audio to a Claude Code session running on the Mac mini
  and converts speech to text and back so that Karl and the agent can converse naturally.
The conversation must be low-latency enough to feel natural,
  resilient to provider failures,
  and free of any third-party storage of conversation content.

## User Story

As Karl, I want to talk to my homelab Claude Code sessions from my phone
  so that I can interact with my agents while driving, walking, or otherwise away from my desk —
  without compromising the security of those agents
  or the confidentiality of what we discuss.

## Acceptance Criteria

### Conversation Quality

- [ ] End-to-end voice-to-voice latency stays under 2 seconds for 95% of turns,
        measured from end-of-user-speech to start-of-agent-audio playback.
- [ ] Speech-to-text accuracy is good enough that Karl rarely needs to repeat himself
        for ordinary technical conversation
        (e.g. file paths, command names, project names).
- [ ] Karl can interrupt the agent mid-utterance and the agent stops speaking
        within 500ms of detected interruption.
- [ ] Long silences during agent processing don't time out the call;
        the connection is held open as long as the agent is actively working.

### Authentication and Authorization

- [ ] Only authenticated calls are bridged to Claude Code sessions.
        Unauthenticated calls receive a brief audible rejection and disconnect.
- [ ] The authentication mechanism does not rely solely on caller ID,
        because PSTN caller ID is spoofable.
- [ ] An incorrect authentication attempt fails closed
        (the call is disconnected, no agent interaction occurs)
        and is logged for later review.
- [ ] Karl can revoke any active credential without restarting Squawkbox
        or interrupting Claude Code sessions.

### Reliability

- [ ] If the Mac mini is unreachable when a call is initiated,
        the caller receives a clear audible message indicating the system is offline,
        and the call ends gracefully.
- [ ] If a Claude Code session crashes or becomes unresponsive mid-call,
        Karl is told audibly that the session has failed
        and is offered the option to start a new session or end the call.
- [ ] If STT or TTS providers are unavailable,
        Squawkbox logs a structured error following the project's error taxonomy
        and emits a notification consumable by the Mac mini's existing
        journald-based alerting setup.

### Privacy and Data Handling

- [ ] No conversation audio, transcripts, or text is persisted to any third-party cloud service
        beyond what is required for live STT and TTS request handling.
- [ ] Audio in transit between Squawkbox and the Claude Code session never leaves the Mac mini's loopback
        or the family's Tailscale network.
- [ ] The chosen telephony provider's call recording feature is disabled.
- [ ] Karl can configure Squawkbox to redact specific patterns from transcripts before logging
        (e.g. API keys, credentials accidentally spoken aloud).

### Cost Control

- [ ] Long silences during agent processing do not increase per-minute charges
        from the telephony provider beyond the inherent cost of an open call;
        provider-specific silence-discount features are enabled where supported.

### Testing

- [ ] An automated end-to-end test simulates an authenticated call,
        a multi-turn conversation, and a graceful hang-up,
        using mock STT/TTS providers and a real Claude Code session
        configured against a sandbox repository.
- [ ] An automated integration test verifies that an unauthenticated call attempt is rejected
        and produces the expected audit log entry.
- [ ] Manual smoke test from Karl's actual phone passes before each release:
        trigger a call, authenticate, ask a non-trivial question, hear an answer, hang up.

## Out of Scope

- Multiple simultaneous callers or multi-party calls.
        Squawkbox supports one active call at a time.
- Calls placed by anyone other than Karl.
        Other family members are addressed by the
        [Slack Text Conversations](2026-05-08-slack-text-channel.md) requirement.
- Choosing, resuming, or queueing tasks against specific Claude Code sessions.
        Those capabilities are captured in the
        [Voice Session Management](2026-05-08-voice-session-management.md) requirement.
- Inbound call routing without an authenticated trigger.
        This requirement is satisfied so long as Karl can reach Claude Code by voice;
        whether the call is inbound or outbound is an implementation choice
        captured in the engineering design.
        See the
        [Outbound Call Trigger via Apple Shortcuts](2026-05-08-outbound-call-trigger.md)
        requirement for the authenticated outbound path,
        which is the must-have authentication mechanism;
        a future requirement may add inbound calls if a sufficiently strong inbound auth scheme is found.

## References

### Vision

- [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    The core capability without which the vision cannot be realized.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Layered audio + STT + agent + TTS pipeline, telephony provider choice, and authentication design.

### Related Requirements

- [Outbound Call Trigger via Apple Shortcuts](2026-05-08-outbound-call-trigger.md) —
    The authenticated trigger that initiates the call this requirement bridges.
- [Voice Session Management](2026-05-08-voice-session-management.md) —
    Multi-session selection, reconnection, and task queueing on top of this voice bridge.
- [Hands-Free Voice Permission Handling](2026-05-08-voice-permission-handling.md) —
    Permission approval flow used during conversations covered by this requirement.

### Implementation

- None yet.
