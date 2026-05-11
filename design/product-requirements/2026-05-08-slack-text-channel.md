---
title: Slack Text Conversations With Claude Code Sessions
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

# Slack Text Conversations With Claude Code Sessions

## Summary

The family Slack workspace gains a Squawkbox bot user that family members can message
  in dedicated channels or DMs.
Messages addressed to the bot are routed to a Claude Code session running on the Mac mini,
  agent responses are streamed back into the same Slack thread,
  and multiple family members can use the bridge concurrently —
  each gets their own session.

## User Story

As a member of the Davis family,
  I want to ask the homelab agent questions and direct tasks to it from Slack
  so that I can get help with household projects, code, and home admin
  without leaving the family Slack workspace I'm already in.

## Acceptance Criteria

### Slack Workspace Integration

- [ ] Squawkbox registers as a Slack bot user in the family workspace
        with permission to read messages, post messages, and use interactive components.
- [ ] The bot can be invited to any channel and responds to messages that @-mention it
        or that are sent in a DM with the bot.
- [ ] When invited to a channel, the bot posts a brief introduction explaining
        how to talk to it and how to start a session.
- [ ] The bot does not respond to messages it is not directly addressed in,
        even if those messages are in the same channel.

### Conversation Flow

- [ ] A family member can start a new Claude Code session with a slash command
        (e.g. `/squawkbox new <description>`) or by addressing the bot for the first time
        in a thread.
- [ ] Replies in a thread continue the same session.
- [ ] Replies in the parent channel start a new session by default;
        a per-user `parent_channel_continues_session` setting can change this
        to "address the most recent session in this channel".
- [ ] Agent responses are posted back to the same thread,
        with streaming updates as the agent generates them.
        Streaming updates are batched at no more than one Slack `chat.update` call
        per thread per second to stay within Slack's rate limits;
        a final non-batched update conveys the completed response.
- [ ] Long agent responses are paginated cleanly so they do not exceed Slack's message limits;
        attachments use Slack's built-in code block, file, and link previews.
- [ ] A user can stop an in-progress agent run by reacting to the agent's message
        with a configured emoji (e.g. `:stop:`)
        or sending the bot a message in-thread containing "stop."

### Multi-User Support

- [ ] Sessions are scoped per Slack user;
        one family member's session is not visible to another
        unless explicitly shared.
- [ ] The bot identifies which user it is responding to and addresses them by name in long-form replies.
- [ ] Family members other than Karl can be granted Slack access without being granted
        voice-call access;
        the two requirements have independent authorization.

### Reliability

- [ ] If the Mac mini is unreachable when a Slack message arrives,
        the bot replies in-thread that the system is offline
        and the message is queued for retry on the next connectivity check.
- [ ] If a Claude Code session crashes mid-conversation,
        the bot posts a clear message in-thread offering to start a new session.
- [ ] All Slack API rate limits are respected;
        the bot does not get blocked or throttled by ordinary family use.

### Privacy

- [ ] No conversation content from Slack is stored anywhere outside Slack and the Mac mini.
- [ ] Audit logs of which user messaged which session live on the Mac mini,
        not in any cloud service.

### Testing

- [ ] An automated integration test against a mocked Slack Events API verifies that
        a bot-mention triggers a Claude Code session
        and that the response posts back to the same thread.
- [ ] An automated integration test verifies the streaming-update rate limit
        (no more than one `chat.update` per thread per second).
- [ ] An automated integration test verifies that messages from a non-allowed user
        are ignored or rejected with a configurable message.
- [ ] Manual smoke test from each family member's Slack account passes before each release.

## Out of Scope

- Slack channels other than the family's own workspace.
        Squawkbox is single-tenant for one workspace.
- File uploads to or from the bot.
        Initial version handles text only;
        file handling can be added later if needed.
- Permission request handling.
        That is captured in the
        [Slack Permission Button Flow](2026-05-08-slack-permission-flow.md) requirement.

## References

### Vision

- [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md) —
    Provides text access for the family, complementing voice access for Karl.

### Engineering Design

- [Squawkbox Architecture](../engineering-designs/2026-05-08-squawkbox-architecture.md) —
    Slack channel adapter, multi-session routing, and per-user authorization.

### Related Requirements

- [Slack Permission Button Flow](2026-05-08-slack-permission-flow.md) —
    Permission request UX layered on top of this text bridge.

### Implementation

- None yet.
