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

Karl invokes an Apple Shortcut on his iPhone or Apple Watch
  that asks Squawkbox to place a call back to his phone.
The Shortcut authenticates to Squawkbox using an API key stored locally on Apple devices,
  Squawkbox places an outbound call via its telephony provider to Karl's pre-configured phone number,
  and the resulting call is treated as fully authenticated for voice-conversation purposes.
This avoids the security weakness of inbound calls
  (PSTN caller ID is spoofable)
  and works on any iPhone or Apple Watch even when Karl is away from his car or desk.

## User Story

As Karl, I want to start a voice conversation with my homelab agent by tapping a Shortcut on my watch
  so that I can begin a hands-free conversation while driving without using a passcode, biometric,
  or any unsecured PSTN convention,
  knowing that only I can trigger such a call.

## Acceptance Criteria

### Trigger Flow

- [ ] Tapping a Squawkbox Shortcut on iPhone or Apple Watch causes Squawkbox to place
        an outbound call to Karl's pre-configured phone number within 5 seconds of the tap.
- [ ] The Shortcut works from the Apple Watch face complications, the iOS Shortcuts app,
        Siri voice invocation, and the iOS Action Button.
- [ ] The Shortcut accepts an optional Claude Code session identifier as input
        (chosen at trigger time) so that Karl can pre-select which session he wants to talk to.
- [ ] If no session identifier is supplied, Squawkbox uses Karl's default session
        and begins the call by audibly stating which session is being used.

### Authentication

- [ ] The Shortcut authenticates to Squawkbox using a long, randomly-generated API key
        stored on the Apple device's keychain.
- [ ] An invalid, expired, or revoked API key results in the trigger request being rejected
        with no outbound call placed,
        and the rejection is logged in Squawkbox's audit log.
- [ ] Karl can rotate or revoke an API key out-of-band
        (without rebuilding the Shortcut);
        the Shortcut prompts to enter the new key on next invocation.
- [ ] Trigger requests reach Squawkbox via two paths:
        directly over the family's Tailscale tailnet when the source device is on Tailscale,
        and via Tailscale Funnel over HTTPS when the source device is on the public internet.
        API key authentication is required on both paths.

### Outbound Call Behavior

- [ ] Squawkbox places the outbound call only to a phone number stored in its configuration.
        The trigger request cannot specify a destination number;
        this prevents a stolen API key from being used to make calls to arbitrary numbers.
- [ ] If Karl declines or misses the outbound call, no charges to Squawkbox's telephony provider
        are incurred beyond the standard call-attempt fees.
- [ ] If the outbound call connects, the call is treated as authenticated for the
        [Secure Voice Conversations](2026-05-08-secure-voice-calls.md) requirement;
        no further authentication challenge is required during the call.
- [ ] Squawkbox can be configured to require the recipient to press a specific DTMF digit
        before the call is bridged to the agent, as defense-in-depth
        against an attacker physically holding Karl's phone.

### Reliability

- [ ] If the telephony provider is unavailable, the Shortcut surfaces a clear error to Karl
        on the Apple device that triggered it.
- [ ] If Squawkbox itself is unreachable, the Shortcut surfaces a clear error,
        distinguishing this case from telephony-provider failure
        so Karl knows whether to investigate the homelab or his network.

### Testing

- [ ] An automated integration test simulates a valid trigger request and verifies that
        Squawkbox dispatches an outbound call to its mocked telephony provider
        with the configured destination number.
- [ ] An automated integration test simulates an invalid API key and verifies that
        no outbound call is placed and an audit log entry is written.
- [ ] An automated integration test simulates a request that attempts to override the
        destination phone number and verifies the override is rejected.
- [ ] Manual smoke test passes from Karl's Apple Watch before each release.

## Out of Scope

- Triggers from non-Apple devices.
        Karl uses Apple devices exclusively;
        Android or web-based triggers can be added later if other family members need to call themselves.
- Conference calls or callbacks to multiple recipients.
- Any telephony or voice flow other than placing the call.
        Once the call connects, the
        [Secure Voice Conversations](2026-05-08-secure-voice-calls.md) requirement covers the rest.

## References

### Vision

- [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Provides the authenticated trigger that initiates a voice conversation.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    HTTP API surface, API key storage, and outbound-call telephony plumbing.

### Related Requirements

- [Secure Voice Conversations With Homelab Claude Code Sessions](2026-05-08-secure-voice-calls.md) —
    The conversation flow this trigger initiates.

### Implementation

- None yet.
