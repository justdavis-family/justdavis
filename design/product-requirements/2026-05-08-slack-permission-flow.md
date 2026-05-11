---
title: Slack Permission Button Flow
status: draft
vision:
  - 2026-05-08-squawkbox
depends_on:
  - 2026-05-08-slack-text-channel
extends: []
modifies: []
replaces: []
engineering_designs:
  - 2026-05-08-squawkbox-architecture.md
prs: []
---

# Slack Permission Button Flow

## Summary

When Claude Code requests permission during a Slack-bridged session,
  Squawkbox posts an interactive Slack message in the same thread
  with Approve / Deny / More info buttons.
The button-press is conveyed back to Claude Code,
  destructive-action requests show a confirmation modal before final dispatch,
  and inactive requests time out and auto-deny.
This is the Slack-side equivalent of the hands-free voice permission flow,
  using clickable buttons instead of a voice grammar
  because Slack users are at a keyboard and can click safely.

## User Story

As a family member using the Slack bridge,
  I want to approve or deny Claude Code permission requests with a single click
  so that I don't have to type any specific phrasing,
  and so that destructive actions don't slip through with a single accidental click.

## Acceptance Criteria

### Interactive Permission Messages

- [ ] When Claude Code requests permission during a Slack session,
        Squawkbox posts an interactive message in the same Slack thread
        within 1 second of the request.
- [ ] The message contains:
        a plain-language description of the action being requested,
        any rationale provided by Claude Code,
        and Approve / Deny / More info buttons.
- [ ] A button-press is conveyed back to Claude Code within 1 second of the click.

### Timeout and Auto-Deny

- [ ] Permission requests time out after 5 minutes if no response is received.
- [ ] On timeout, Squawkbox edits the message in-place to indicate the request
        was auto-denied due to inaction, removes the buttons,
        and notifies the user in-thread.

### Destructive-Action Handling

- [ ] Permission requests classified as destructive by Claude Code's permission metadata
        show a confirmation modal on Approve click before the decision is finalized.
- [ ] The modal text restates the action and requires an explicit second confirmation click.
- [ ] The destructive-action classification comes from Claude Code itself;
        Squawkbox does not reimplement this classification.

### Auditability

- [ ] Every permission request, button-press, modal interaction, and final decision
        is logged with timestamp, Slack user ID, action description, and resolution.
- [ ] Slack permission audit logs are queryable from the same admin interface
        as voice-permission decisions.

### Testing

- [ ] An automated integration test against a mocked Slack interactivity webhook
        verifies that an Approve click conveys approval back to a mocked Claude Code session.
- [ ] An automated integration test verifies the 5-minute timeout behavior.
- [ ] An automated integration test verifies that a destructive-action approval
        requires the modal confirmation
        and that a single click does not finalize the decision.

## Out of Scope

- Voice-based permission flow.
        That is captured in the
        [Hands-Free Voice Permission Handling](2026-05-08-voice-permission-handling.md)
        requirement.
- Custom button labels or workflows per session.
        The button flow is uniform across all Slack permission requests.

## References

### Vision

- [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Per-channel permission UX that fits how each channel is actually used.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Permission handler, Slack channel adapter, and audit logging design.

### Related Requirements

- [Slack Text Conversations With Claude Code Sessions](2026-05-08-slack-text-channel.md) —
    The bridge in which these permission requests arise.
- [Hands-Free Voice Permission Handling](2026-05-08-voice-permission-handling.md) —
    Sister requirement for voice;
    this requirement covers the Slack-button equivalent.

### Implementation

- None yet.
