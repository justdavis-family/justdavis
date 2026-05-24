---
title: Outbound Call Trigger via Apple Shortcuts
status: draft
vision:
  - 2026-05-08-squawkbox
depends_on: []
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-05-08-squawkbox-architecture.md
prs: []
---

# Outbound Call Trigger via Apple Shortcuts

## Summary

The operator invokes an Apple Shortcut on an iPhone or Apple Watch
  that asks Squawkbox to place a call back to their phone.
The Shortcut authenticates to Squawkbox using an API key stored locally on the Apple device,
  Squawkbox places an outbound call via its telephony provider to a pre-configured phone number,
  and the resulting call is treated as fully authenticated for voice-conversation purposes.
This avoids the security weakness of inbound calls
  (PSTN caller ID is spoofable)
  and works from any iPhone or Apple Watch, even away from a car or desk.

## User Story

As the operator, I want to start a voice conversation with my homelab agent
  by tapping a Shortcut on my watch
  so that I can begin a hands-free conversation while driving
  without using a passcode, biometric, or any unsecured PSTN convention,
  knowing that only I can trigger such a call.

## Acceptance Criteria

### Trigger Flow

- [ ] Tapping a Squawkbox Shortcut on iPhone or Apple Watch causes Squawkbox to place
        an outbound call to the pre-configured phone number within 5 seconds of the tap.
- [ ] The Shortcut works from the Apple Watch face complications, the iOS Shortcuts app,
        Siri voice invocation, and the iOS Action Button.
- [ ] The call is bridged to the single configured Claude Code session;
        the trigger carries no session-selection input.
      (Choosing among multiple sessions is deferred to the
        [Voice Session Management](2026-05-08-voice-session-management.md) requirement.)

### Authentication

- [ ] The Shortcut authenticates to Squawkbox using a long, randomly-generated API key
        stored on the Apple device's keychain.
- [ ] An invalid, expired, or revoked API key results in the trigger request being rejected
        with no outbound call placed,
        and the rejection is logged in Squawkbox's audit log.
- [ ] The operator can rotate or revoke an API key out-of-band
        (without rebuilding the Shortcut);
        the Shortcut prompts to enter the new key on next invocation.
- [ ] Trigger requests reach Squawkbox via two paths:
        directly over the operator's Tailscale tailnet when the source device is on Tailscale,
        and via Tailscale Funnel over HTTPS when the source device is on the public internet.
        API key authentication is required on both paths.

### Outbound Call Behavior

- [ ] Squawkbox places the outbound call only to a phone number stored in its configuration.
        The trigger request cannot specify a destination number;
        this prevents a stolen API key from being used to make calls to arbitrary numbers.
- [ ] If the operator declines or misses the outbound call,
        no telephony-provider charges are incurred beyond the standard call-attempt fees.
- [ ] If the outbound call connects, the call is treated as authenticated for the
        [Secure Voice Conversations](2026-05-08-secure-voice-calls.md) requirement;
        no further authentication challenge is required during the call.
- [ ] Squawkbox can be configured to require the recipient to press a specific DTMF digit
        before the call is bridged to the agent, as defense-in-depth
        against an attacker physically holding the operator's phone.

### Reliability

- [ ] If the telephony provider is unavailable, the Shortcut surfaces a clear error
        on the Apple device that triggered it.
- [ ] If Squawkbox itself is unreachable, the Shortcut surfaces a clear error,
        distinguishing this case from telephony-provider failure
        so the operator knows whether to investigate the homelab or the network.

### Testing

- [ ] Automated tests cover a valid trigger (an outbound call is dispatched to a mocked
        telephony provider with the configured destination number),
        an invalid API key (no call placed, audit entry written),
        and a destination-number override attempt (rejected).
- [ ] The trigger is verified end-to-end from a real Apple device before the requirement is done.

## Out of Scope

- Triggers from non-Apple devices.
  Android or web-based triggers can be added later if needed.
- Conference calls or callbacks to multiple recipients.
- Session selection at trigger time.
  Deferred to the
    [Voice Session Management](2026-05-08-voice-session-management.md) requirement.
- Any telephony or voice flow other than placing the call.
  Once the call connects, the
    [Secure Voice Conversations](2026-05-08-secure-voice-calls.md) requirement covers the rest.

## References

### Vision

- [Squawkbox: Voice Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Provides the authenticated trigger that initiates a voice conversation.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    HTTP API surface, API key storage, and outbound-call telephony plumbing.

### Related Requirements

- [Secure Voice Conversations With Homelab Claude Code Sessions](2026-05-08-secure-voice-calls.md) —
    The conversation flow this trigger initiates.
- [Voice Session Management](2026-05-08-voice-session-management.md) —
    Deferred: adds session selection at and during call time on top of this trigger.

### Implementation

- None yet.
