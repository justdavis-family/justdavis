# Squawkbox Delivery Plan

## Overview

This plan slices the Squawkbox vision and its requirements into ten milestones,
  each delivering something independently usable and testable.
The slicing is biased toward landing the smallest possible end-to-end vertical first
  (Apple Watch tap → Karl's phone rings → he talks to Claude Code → he hangs up)
  and then widening it.
Cloud STT/TTS is used for the first several milestones to remove integration risk;
  local providers are introduced once the rest of the system is stable.

Total scope across all milestones implements:

- [Outbound Call Trigger via Apple Shortcuts](../../product-requirements/2026-05-08-outbound-call-trigger.md).
- [Secure Voice Conversations With Homelab Claude Code Sessions](../../product-requirements/2026-05-08-secure-voice-calls.md).
- [Voice Session Management](../../product-requirements/2026-05-08-voice-session-management.md).
- [Hands-Free Voice Permission Handling](../../product-requirements/2026-05-08-voice-permission-handling.md).
- [Slack Text Conversations With Claude Code Sessions](../../product-requirements/2026-05-08-slack-text-channel.md).
- [Slack Permission Button Flow](../../product-requirements/2026-05-08-slack-permission-flow.md).

For broader context, see the
  [Squawkbox vision](../../product-vision/2026-05-08-squawkbox.md)
  and the
  [Squawkbox architecture](../../engineering-designs/2026-05-08-squawkbox-architecture.md).

## Milestone 1: "It Rings" — Outbound Call Plumbing

**Goal:** The Apple Watch Shortcut causes the Mac mini to call Karl's phone.
No agent integration yet;
  the call is bridged to a static "Hello, this is Squawkbox" recording.

**Scope:**

- Rust daemon skeleton with `axum` HTTP API and structured logging.
- `POST /v1/calls` endpoint that validates an API key against an SQLite-backed allowlist
    and dispatches a call via Twilio's REST API.
- Twilio account configured with an outbound number and a TwiML endpoint pointing at the daemon.
- TwiML endpoint plays a static greeting and hangs up.
- Apple Shortcut definition documented and tested from Karl's Watch.
- Tailscale Funnel exposes the HTTP API for off-network triggers.

**Out of scope:** STT, TTS, Claude Code integration, Slack, anything resembling a conversation.

**Done when:** Karl can stand outside the house, tap the Watch,
  and hear his Mac mini speak from his phone.

## Milestone 2: "It Hears You" — Audio Pipeline + STT

**Goal:** The Mac mini receives Karl's voice over an active phone call
  and produces a transcript visible on the admin UI.
Validates the audio pipeline + STT integration before introducing TTS or agent complexity.

**Scope:**

- Twilio Media Streams WebSocket handler in the daemon.
- Silero VAD running locally for end-of-utterance detection.
- OpenAI Whisper API integration (cloud STT).
- Daemon plays the static greeting from Milestone 1, then listens for input.
- End-of-utterance audio is sent to Whisper and the transcript is appended to a per-call
    session log surfaced in the admin UI.
- Latency dashboard logs time-to-transcript for STT.

**Out of scope:** TTS, Claude Code integration, permission handling, multi-session, Slack.

**Done when:** Karl can call the system, speak a sentence, hang up,
  and immediately see the transcript on the admin web UI.

## Milestone 3: "It Talks Back" — Voice Loop Without Agent

**Goal:** A working full-duplex voice loop where the Mac mini transcribes Karl's speech
  and reads back a canned response.
Closes out the cloud-audio pipeline as a complete capability,
  ready for an agent to be plugged into.

**Scope:**

- ElevenLabs Flash integration (cloud TTS).
- Hard-coded response logic: every transcript echoes back as
    "I heard you say: <transcript>."
- End-to-end latency dashboard now logs time-to-first-byte for STT and TTS,
    and full-turn latency.

**Out of scope:** Claude Code integration, permission handling, multi-session, Slack,
  local STT/TTS.

**Done when:** Karl can call the system, talk, and hear back a transcribed echo
  with under 2 seconds of voice-to-voice latency.

## Milestone 4: "It Talks to Claude Code" — Single-Session MVP

**Goal:** The voice loop is bridged to one Claude Code session running on the Mac mini.
This is the first milestone that delivers genuine product value
  and partially satisfies the Secure Voice Conversations requirement.

**Scope:**

- Agent Adapter trait in Rust with one implementation: MCP polling client.
- A small custom MCP server that exposes a single Claude Code session
    (chosen at daemon startup time)
    with two tools: `submit_message` and `poll_response`.
- Conversation orchestrator wiring: STT transcript → MCP submit → TTS speak.
- End-to-end test using a mocked MCP server.
- Manual smoke test: Karl asks Claude Code to summarize a recent commit, hears the answer.

**Out of scope:** Permission handling, multiple sessions, Slack, anything else.

**Done when:** Karl can ask Claude Code questions about a sandbox repository
  during a phone call and get useful spoken answers.

## Milestone 5: "It Won't Get Me Killed" — Hands-Free Permissions

**Goal:** Permission requests from Claude Code are surfaced and resolved verbally.
Closes the Hands-Free Voice Permission Handling requirement.

**Scope:**

- Permission state machine (`IDLE → PROMPTED → AWAITING_RESPONSE → DECIDED`).
- Permission grammar with approve/deny phrase recognition.
- Strict-confirmation grammar for destructive actions, gated on Claude Code's permission metadata.
- 30-second timeout with auto-deny.
- Per-tool/per-command allowlist for pre-approved low-risk operations.
- Audit log table in SQLite for every permission decision.
- End-to-end test that injects a permission request mid-conversation
    and verifies the decision propagates back to Claude Code.

**Out of scope:** Multi-session, Slack, anything else.

**Done when:** Karl can drive while Claude Code does file edits and shell commands,
  approving or denying as needed by speaking only.

## Milestone 6: "Multi-Session" — Pick a Session at Call Time

**Goal:** Karl can choose which Claude Code session to talk to at the start of the call.
Closes the Voice Session Management requirement
  and the rest of the Secure Voice Conversations requirement.

**Scope:**

- Session registry: discovery of running Claude Code sessions on the Mac mini,
    indexed by user-friendly name.
- Apple Shortcut accepts an optional session name as a parameter.
- If no session is provided, the daemon begins the call by audibly listing available
    sessions and prompting Karl to choose one.
- Per-session MCP polling clients run independently;
    one active call talks to one session.
- Reconnection logic: hanging up leaves the session running;
    dialing back in to the same session resumes its history.
- Mid-task task queueing: new requests during agent activity are queued, not interrupting.

**Out of scope:** Slack, local providers, Channels migration.

**Done when:** Karl can manage three concurrent Claude Code sessions
  from his car over the course of an afternoon.

## Milestone 7: "The Family Joins" — Slack Text Bridge

**Goal:** The family Slack workspace gets a Squawkbox bot
  that handles text-only conversations with per-user sessions.
Closes the Slack Text Conversations requirement.

**Scope:**

- Slack Events API webhook handler in the daemon.
- Slack channel adapter using `slack-morphism`.
- Per-user authorization model and per-user session scoping.
- Streaming responses to Slack threads via `chat.update`,
    batched at no more than one update per thread per second to respect Slack rate limits.
- Slack-side audit logging matching the existing voice audit log shape.

**Out of scope:** Interactive permission buttons, voice over Slack.

**Done when:** Erica can DM the bot to ask the agent a question
  and get a useful streaming response in-thread.

## Milestone 8: "Slack Permissions" — Interactive Permission Buttons

**Goal:** Permission requests during Slack sessions surface as interactive Slack messages
  and are routed back to Claude Code on click.
Closes the Slack Permission Button Flow requirement.

**Scope:**

- Interactive Slack messages with Approve / Deny / More info buttons.
- 5-minute timeout with auto-deny;
    on timeout the message is edited in-place and buttons are removed.
- Confirmation modal for destructive-action permissions,
    requiring an explicit second click.
- Audit logging of every Slack-initiated permission decision,
    queryable from the same admin interface as voice-permission decisions.

**Out of scope:** Anything else.

**Done when:** Claude Code requests permission during a Slack session
  and a family member can approve or deny it with a single button click.

## Milestone 9: "It Stays Home" — Local STT/TTS Migration

**Goal:** Cloud STT and TTS providers are replaced with local equivalents
  on the Mac mini, eliminating per-minute STT/TTS billing
  and keeping audio entirely on the family's network.

**Scope:**

- Run [speaches](https://github.com/speaches-ai/speaches) on the Mac mini
    for local Whisper STT behind an OpenAI-compatible HTTP endpoint.
- Run a local TTS service (Piper or Kokoro) behind a similar OpenAI-compatible endpoint.
- Reconfigure Squawkbox's `[stt]` and `[tts]` sections to point at the local services.
- Latency and accuracy regression tests using fixed audio fixtures
    to validate that local STT meets the requirement's accuracy bar
    and that latency stays under 2 seconds voice-to-voice.
- Roll back to cloud providers via config if the local providers regress badly.

**Out of scope:** Channels migration.

**Done when:** A normal phone call uses zero cloud STT/TTS minutes
  and is at least as good as the cloud-provider experience.

## Milestone 10: "Channels" — Replace MCP Polling

**Goal:** Replace the MCP polling Agent Adapter with a Claude Code Channels-based adapter,
  eliminating the polling latency and the need for the custom MCP server.

**Scope:**

- New Agent Adapter implementation that registers as a Claude Code Channels server
    and uses `notifications/claude/channel` to push messages into the running session
    and receive responses.
- Side-by-side validation against the MCP polling adapter:
    same conversation, same outputs, lower latency.
- Migration path documentation for moving an existing session from the MCP adapter
    to the Channels adapter.
- The MCP polling adapter remains in the codebase as a fallback
    so long as Channels is still in research preview.

**Out of scope:** Anything else.

**Done when:** A typical voice turn round-trip is at least 200ms faster
  than under MCP polling, with no functional regressions.

## Sequencing and Risk

Milestones 1–4 are tightly sequenced and should be completed in order.
Milestones 5 and 6 can be done in either order,
  depending on how acute the hands-free pain is during the multi-session experience.
Milestones 7 and 8 are independent of milestones 5 and 6 and could in principle be done
  in parallel — though Karl will want to focus on one channel at a time.
Milestone 8 depends on milestone 7
  (the Slack bridge must exist before permission buttons can be layered on top).
Milestones 9 and 10 are end-state polish and can be done at any point
  after milestones 1–6 are stable.

Largest risk areas, in order of severity:

1. **Voice latency.**
   If end-to-end voice-to-voice exceeds 2 seconds reliably,
   the conversational flow degrades enough that the system feels broken.
   Milestones 2 and 3 are specifically structured to validate this risk before
   any agent complexity is added.
2. **Permission recognition accuracy in driving conditions.**
   This is harder to validate in a developer's quiet office than at highway speed.
   Plan to do real-road testing during Milestone 5.
3. **Twilio reliability and cost.**
   Twilio is the chosen MVP telephony provider primarily for documentation maturity, not cost.
   If sustained-use costs come in higher than projected,
   a Telnyx swap is a one-week migration.
4. **Slack rate limits with streaming responses.**
   Slack's `chat.update` rate limits can throttle aggressive streaming.
   Milestone 7 needs to be measured against real Slack workspace limits.
