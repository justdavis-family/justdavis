# Squawkbox: Voice Access to Homelab Agents

## Problem and Motivation

Karl runs Claude Code agents on a Mac mini in his homelab.
Today, the only way to interact with those agents is to be sitting in front of the Mac mini —
  or to remote into it from another desk-bound device.
Much of the value of having a persistent, capable agent is lost when access requires a desk:
  ideas surface while driving, walking, or doing chores,
  and long-running tasks finish without anyone there to react.

Existing third-party voice-to-Claude-Code clients (Happy, ElevenLabs Agents, etc.)
  are functional but expensive at sustained usage,
  bind voice to a specific vendor stack,
  and route audio through cloud relays the operator doesn't control.
At Karl's projected usage of ~1,500 voice minutes per month,
  the third-party path lands around $130/month and includes a known bug in the most direct integration.
A self-hosted alternative is technically practical today
  and would land closer to $25–45/month
  while keeping audio and conversation data inside the operator's own infrastructure.

(The personal usage details above are grounding for the design.
  The rest of this document and the requirements are written for any homelab operator,
  so that Squawkbox is worth open-sourcing rather than being a one-person tool.)

## Vision

Squawkbox is a self-hosted voice gateway to a homelab's Claude Code agents.
It runs on the homelab host alongside the Claude Code session it bridges,
  is reachable from any phone via a regular phone call,
  and behaves predictably enough to be usable hands-free while driving.

The core loop is simple:
  the operator speaks to Squawkbox from a phone,
  Squawkbox routes the message to a Claude Code session on the homelab host,
  Claude Code does whatever it does,
  and Squawkbox speaks the answer back through the same call.
Long-running agent activity continues independently of any active conversation;
  the next time the operator reconnects, they can pick up where things left off.

The system is built in layers so that each layer can evolve independently:
  the audio transport is decoupled from speech-to-text,
  which is decoupled from text-to-speech,
  which is decoupled from how messages are delivered into the running Claude Code session.
This makes it cheap to swap a cloud STT provider for a local one,
  or to migrate from a polling integration pattern to push-based Claude Code Channels later,
  without disturbing the rest of the system.

The first usable version targets a single authenticated user over phone calls,
  bridged to a single Claude Code session,
  with whatever combination of services makes the integration cheapest to land first.
Subsequent iterations widen the system —
  hands-free voice permission handling,
  then, later, multi-session management and reduced reliance on third-party services —
  without invalidating the foundational architecture.

## Success Metrics

- The operator can start a voice conversation with a Claude Code session on the homelab host
    from any phone, anywhere with cell service, in under 10 seconds from intent to first audio.
- Voice conversations work hands-free end-to-end:
    initiating, talking, approving permission requests, and ending the call
    require no physical interaction with the phone screen.
- Sustained-use cost is a fraction of the equivalent third-party voice service
    at comparable usage, inclusive of all third-party services.
- No audio recordings, transcripts, or conversation content are stored by any third-party
    cloud service except in transit for live STT and TTS.

## Requirements

### Initial Scope

This vision's initial scope is delivered through the following requirements:

- [Outbound Call Trigger via Apple Shortcuts](../product-requirements/2026-05-08-outbound-call-trigger.md) —
    Authenticated Apple Shortcut that asks Squawkbox to place an outbound call (must have).
- [Secure Voice Conversations With Homelab Claude Code Sessions](../product-requirements/2026-05-08-secure-voice-calls.md) —
    Phone-based voice conversations with a Claude Code session on the homelab host (must have).
- [Hands-Free Voice Permission Handling](../product-requirements/2026-05-08-voice-permission-handling.md) —
    Approve or deny Claude Code permission requests safely while driving (must have).

### Deferred to a Later Phase

- [Voice Session Management](../product-requirements/2026-05-08-voice-session-management.md) —
    Choosing, resuming, and reconnecting to specific Claude Code sessions across calls.
  Deferred until the single-session voice loop is solid:
    multi-session routing adds a connection-and-routing harness that should not be taken on first.
  The initial system bridges one call to exactly one session,
    matching the Claude Code Channels one-channel-per-session model.

### Out of Scope

- Text or chat-based access (e.g. a Slack bot).
  Squawkbox is voice-first;
    a text channel could be a future expansion but is explicitly not in scope here.
- Inbound calls.
  Only authenticated outbound calls are supported;
    see the Secure Voice Conversations requirement for the rationale.
