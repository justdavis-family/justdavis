---
title: Hands-Free Voice Permission Handling
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

# Hands-Free Voice Permission Handling

## Summary

When a Claude Code session on the homelab host requests permission to perform an action
  (run a shell command, modify a file, call a tool, etc.),
  Squawkbox interrupts the active voice conversation,
  reads the permission request aloud,
  accepts a verbal approve-or-deny response from the operator,
  and conveys the decision back to Claude Code —
  all without requiring the operator to look at, touch,
  or otherwise physically interact with any device.
The flow is designed to be safe to use while driving.

## User Story

As the operator, driving on the highway,
  I want to approve or deny Claude Code's permission requests by speaking,
  so that I can continue conducting useful agent work without taking my eyes off the road
  or my hands off the wheel.

## Acceptance Criteria

### Permission Request Flow

- [ ] When Claude Code requests permission during an active voice call,
        Squawkbox promptly interrupts any in-flight agent speech and reads the request aloud.
      (A sub-500ms interruption is the goal;
        it will be confirmed against real hardware before being fixed as a hard target.)
- [ ] The spoken request includes:
        the action being requested in plain language,
        a brief rationale if one is provided by Claude Code,
        and an explicit prompt for response.
- [ ] A verbal response of "yes," "approve," "allow," "go ahead," or "okay" is recognized as approval.
- [ ] A verbal response of "no," "deny," "stop," "cancel," or "don't" is recognized as denial.
- [ ] An ambiguous response causes Squawkbox to ask for clarification audibly,
        rather than acting on a guess.
- [ ] Decisions are conveyed back to Claude Code within 1 second of recognition
        so that the agent does not stall.

### Hands-Free Safety

- [ ] No part of the permission flow requires the operator to look at a screen,
        type, tap, or perform any action other than speaking and listening.
- [ ] No part of the permission flow requires a side-channel device —
        no message to confirm,
        no email to click,
        no separate call,
        no second factor that breaks hands-free operation.
- [ ] If a response is not heard for 30 seconds,
        Squawkbox treats the request as denied
        and says audibly that the request was auto-denied due to timeout.
- [ ] The operator can request that the permission prompt be repeated by saying "repeat,"
        "say that again," or "what did you say."

### High-Stakes Action Handling

- [ ] Actions classified by Claude Code as destructive
        (e.g. `rm -rf`, `git push --force`, file deletion, money movement)
        require a stricter confirmation phrase such as "yes, I'm sure"
        rather than the standard "yes."
- [ ] The classification of "high stakes" comes from Claude Code itself
        via its existing permission-request metadata;
        Squawkbox does not reimplement this classification.
- [ ] The operator can configure a per-tool or per-command allowlist
        such that pre-approved low-risk operations
        (e.g. `git diff`, `ls`, `cat`)
        do not trigger a verbal prompt at all.

### Voice Recognition Robustness

- [ ] Permission responses are recognized correctly at 95% or better
        in normal driving conditions
        (windows up, road noise, music at moderate volume),
        measured against a recorded test set of 100 or more utterances
        captured under those conditions.
        The test set lives alongside the test code and is regenerated as needed;
        the measurement methodology is documented in the engineering design.
- [ ] Squawkbox uses the same STT pipeline as the regular conversation
        but applies a tighter recognition grammar to permission responses
        to reduce false-positives from ambient speech or radio.
- [ ] False-positive risk is mitigated by requiring the response to follow Squawkbox's prompt
        within a bounded window (the previous 30 seconds);
        permission cannot be granted by ambient speech that happens to match a keyword
        when no permission has been requested.

### Auditability

- [ ] Every permission request, response, and final decision is logged with timestamp,
        action description, response audio path, recognized text, and matched grammar phrase.
- [ ] The operator can review recent permission events via Squawkbox's admin interface.
- [ ] Permission audit logs are retained for at least 30 days
        and are queryable with standard CLI tools (e.g. `jq`, `grep`).

### Testing

- [ ] Automated tests verify that a permission request injected mid-conversation
        interrupts agent speech, prompts the operator, and conveys a mock response back to Claude Code;
        that destructive-action prompts require the strict phrase and are not approved by a plain "yes";
        and that the 30-second timeout auto-denies.
- [ ] A manual driving smoke test (on a quiet road, with a passenger)
        confirms recognition accuracy at speed before the requirement is considered done.

## Out of Scope

- Permission flows over any non-voice channel.
  Squawkbox is voice-first;
    this requirement covers only the spoken approve/deny flow.
- Voice biometric verification of who is responding.
  Squawkbox trusts that the person speaking on an authenticated call is the operator;
    physically passing the phone to a third party mid-call is out of scope.

## References

### Vision

- [Squawkbox: Voice Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Hands-free safety is a top-line success metric.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Permission handler, agent integration shape, and allowlist mechanism.

### Related Requirements

- [Secure Voice Conversations With Homelab Claude Code Sessions](2026-05-08-secure-voice-calls.md) —
    The conversation context in which permission requests arise.

### Implementation

- None yet.
