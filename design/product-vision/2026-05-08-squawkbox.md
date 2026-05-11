# Squawkbox: Voice and Text Access to Homelab Agents

## Problem and Motivation

Karl runs Claude Code agents on a Mac mini in his homelab.
Today, the only way to interact with those agents is to be sitting in front of the Mac mini —
  or to remote into it from another desk-bound device.
Much of the value of having a persistent, capable agent is lost when access requires a desk:
  ideas surface while driving, walking, or doing chores;
  long-running tasks finish without anyone there to react;
  questions about the household's projects come up in the family Slack
  but answering them means walking to the office.

Existing third-party voice-to-Claude-Code clients (Happy, ElevenLabs Agents, etc.)
  are functional but expensive at sustained usage,
  bind voice to a specific vendor stack,
  and route audio through cloud relays that the family doesn't control.
At Karl's projected usage of ~1,500 voice minutes per month,
  the third-party path lands around $130/month and includes a known bug in the most direct integration.
A self-hosted alternative is technically practical today
  and would land closer to $25–45/month
  while keeping audio and conversation data inside the family's own infrastructure.

## Vision

Squawkbox is the family's voice-and-text gateway to its homelab agents.
It runs on the existing Mac mini alongside the Claude Code sessions it bridges,
  is reachable from any phone via a regular phone call or from the family Slack workspace,
  and behaves predictably enough to be usable hands-free while driving.

The core loop is simple:
  Karl speaks to Squawkbox from his phone or Slack,
  Squawkbox routes the message to the right Claude Code session on the Mac mini,
  Claude Code does whatever it does,
  and Squawkbox speaks or writes the answer back through the same channel.
Long-running agent activity continues independently of any active conversation;
  the next time Karl reconnects, he can pick up where things left off.

The system is built in layers so that each layer can evolve independently:
  the audio transport (phone call vs. in-app vs. Slack) is decoupled from speech-to-text,
  which is decoupled from text-to-speech,
  which is decoupled from how messages are delivered into the running Claude Code session.
This makes it cheap to swap a cloud STT provider for a local one,
  to add a new channel without touching the agent integration,
  or to migrate from a polling integration pattern to push-based Claude Code Channels later.

The first usable version targets a single user (Karl) over phone calls,
  with whatever combination of services makes the integration cheapest to land first.
Subsequent iterations widen the system —
  hands-free voice permission handling,
  text-based access for the rest of the family,
  reduced reliance on third-party services as cost and privacy pressures grow —
  without invalidating the foundational architecture.

## Success Metrics

- Karl can start a voice conversation with a Claude Code session running on the Mac mini
    from any phone, anywhere with cell service, in under 10 seconds from intent to first audio.
- Voice conversations work hands-free end-to-end:
    initiating, talking, approving permission requests, and ending the call
    require no physical interaction with the phone screen.
- Sustained-use cost stays under $50/month at Karl's projected ~1,500 voice minutes per month,
    inclusive of all third-party services.
- No audio recordings, transcripts, or conversation content are stored by any third-party
    cloud service except in transit for live STT and TTS.
- The family can ask questions of and direct tasks to homelab agents from the family Slack workspace
    using natural conversational text, with responses appearing in the same channel.

## Requirements

This vision is being implemented through the following requirements:

- [Outbound Call Trigger via Apple Shortcuts](../product-requirements/2026-05-08-outbound-call-trigger.md) —
    Authenticated Apple Shortcut that asks Squawkbox to call Karl's phone (must have).
- [Secure Voice Conversations With Homelab Claude Code Sessions](../product-requirements/2026-05-08-secure-voice-calls.md) —
    Phone-based voice conversations between Karl and Claude Code sessions on the Mac mini (must have).
- [Voice Session Management](../product-requirements/2026-05-08-voice-session-management.md) —
    Choose, resume, and reconnect to specific Claude Code sessions across phone calls (must have).
- [Hands-Free Voice Permission Handling](../product-requirements/2026-05-08-voice-permission-handling.md) —
    Approve or deny Claude Code permission requests safely while driving (must have).
- [Slack Text Conversations With Claude Code Sessions](../product-requirements/2026-05-08-slack-text-channel.md) —
    Two-way text bridge between the family Slack workspace and Claude Code sessions (nice to have).
- [Slack Permission Button Flow](../product-requirements/2026-05-08-slack-permission-flow.md) —
    Interactive Slack message buttons for approving or denying Claude Code permission requests (nice to have).
