# Squawkbox Delivery Plan

## Overview

This plan slices the Squawkbox vision and its requirements into milestones,
  each delivering something independently usable and testable.
The slicing is biased toward landing the smallest possible end-to-end vertical first
  (Apple Watch tap → phone rings → operator talks to Claude Code → hangs up)
  and then widening it.
Cloud STT/TTS is used for the first several milestones to remove integration risk;
  local providers are introduced once the rest of the system is stable.

Initial scope across these milestones implements:

- [Outbound Call Trigger via Apple Shortcuts](../../product-requirements/2026-05-08-outbound-call-trigger.md).
- [Secure Voice Conversations With Homelab Claude Code Sessions](../../product-requirements/2026-05-08-secure-voice-calls.md).
- [Hands-Free Voice Permission Handling](../../product-requirements/2026-05-08-voice-permission-handling.md).

[Voice Session Management](../../product-requirements/2026-05-08-voice-session-management.md)
  (multi-session selection, reconnection, and task queueing) is deferred to a later phase;
  see the Deferred section at the end.

For broader context, see the
  [Squawkbox vision](../../product-vision/2026-05-08-squawkbox.md)
  and the
  [Squawkbox architecture](../../engineering-designs/2026-05-08-squawkbox-architecture.md).

## Milestone 1: "It Rings" — Outbound Call Plumbing

**Goal:** The Apple Watch Shortcut causes the homelab host to call the operator's phone.
No agent integration yet;
  the call is bridged to a static "Hello, this is Squawkbox" recording.

**Scope:**

- Daemon skeleton with an HTTP API and structured logging.
- `POST /v1/calls` endpoint that validates an API key against an SQLite-backed allowlist
    and dispatches a call via the telephony provider's REST API.
- Telephony account configured with an outbound number and a webhook endpoint pointing at the daemon.
- Webhook plays a static greeting and hangs up.
- Apple Shortcut definition documented and tested from a real Apple device.
- Tailscale Funnel exposes the HTTP API for off-network triggers.

**Out of scope:** STT, TTS, Claude Code integration, anything resembling a conversation.

**Done when:** The operator can stand outside the house, tap the Watch,
  and hear the homelab host speak from their phone.

## Milestone 2: "Bake-Off" — Orchestrator Spike and Voice Loop

**Goal:** Resolve the open orchestrator/language decision
  (hand-rolled Rust vs. Pipecat) and prove the latency budget,
  by building the thinnest possible voice echo loop on each path and comparing them.

**Scope:**

- A minimal full-duplex voice loop on each candidate path:
    Media Streams WebSocket in, Silero VAD, cloud STT, a canned echo response,
    cloud TTS, audio back out.
- Latency measurement (time-to-first-byte per stage and full-turn voice-to-voice)
    and an honest write-up of implementation effort for each path.
- A documented decision committing to one path, recorded back in the engineering design,
    including a realistic voice-to-voice latency target derived from the measured numbers.

**Out of scope:** Claude Code integration, permission handling, multi-session, local STT/TTS.

**Done when:** The operator can call the system, talk, and hear back a transcribed echo,
  and there is a recorded decision on the orchestrator path with latency numbers behind it.

## Milestone 3: "It Talks to Claude Code" — Single-Session MVP

**Goal:** The voice loop is bridged to one Claude Code session on the homelab host.
This is the first milestone that delivers genuine product value
  and largely satisfies the Secure Voice Conversations requirement.

**Scope:**

- Agent Adapter abstraction with one implementation: MCP polling client.
- A small custom MCP server that exposes a single Claude Code session
    (configured at daemon startup) with `submit_message` and `poll_response` tools.
- Conversation orchestrator wiring: STT transcript → MCP submit → TTS speak.
- End-to-end test using a mocked MCP server and a real Claude Code session against a sandbox repo.

**Out of scope:** Permission handling, multiple sessions, anything else.

**Done when:** The operator can ask Claude Code questions about a sandbox repository
  during a phone call and get useful spoken answers.

## Milestone 4: "It Won't Get Me Killed" — Hands-Free Permissions

**Goal:** Permission requests from Claude Code are surfaced and resolved verbally.
Closes the Hands-Free Voice Permission Handling requirement.

**Scope:**

- Permission state machine (`IDLE → PROMPTED → AWAITING_RESPONSE → DECIDED`).
- Permission grammar with approve/deny phrase recognition,
    plus a stricter confirmation grammar for destructive actions gated on Claude Code's metadata.
- 30-second timeout with auto-deny.
- Per-tool/per-command allowlist for pre-approved low-risk operations.
- Audit log of every permission decision.
- End-to-end test that injects a permission request mid-conversation
    and verifies the decision propagates back to Claude Code.

**Out of scope:** Multi-session, anything else.

**Done when:** The operator can drive while Claude Code does file edits and shell commands,
  approving or denying as needed by speaking only.

## Milestone 5: "It Stays Home" — Local STT/TTS Migration

**Goal:** Cloud STT and TTS providers are replaced with local equivalents
  on the homelab host, eliminating per-minute STT/TTS billing
  and keeping audio entirely on the operator's network.

**Scope:**

- Run [speaches](https://github.com/speaches-ai/speaches) on the homelab host
    for local Whisper STT behind an OpenAI-compatible HTTP endpoint.
- Run a local TTS service (Piper or Kokoro) behind a similar OpenAI-compatible endpoint.
- Reconfigure Squawkbox's `[stt]` and `[tts]` sections to point at the local services.
- Latency and accuracy regression tests using fixed audio fixtures.
- Roll back to cloud providers via config if the local providers regress badly.

**Out of scope:** Channels migration.

**Done when:** A normal phone call uses zero cloud STT/TTS minutes
  and is at least as good as the cloud-provider experience.

## Milestone 6: "Channels" — Replace MCP Polling

**Goal:** Replace the MCP polling Agent Adapter with a Claude Code Channels-based adapter,
  eliminating the polling latency and the need for the custom MCP server.

**Scope:**

- New Agent Adapter implementation that registers as a Claude Code Channels server
    and uses `notifications/claude/channel` to push messages into the running session
    and receive responses.
- Side-by-side validation against the MCP polling adapter:
    same conversation, same outputs, lower latency.
- The MCP polling adapter remains as a fallback while Channels is in research preview.

**Out of scope:** Anything else.

**Done when:** A typical voice turn round-trip is at least 200ms faster
  than under MCP polling, with no functional regressions.

## Deferred: Voice Session Management

Multi-session support
  ([Voice Session Management](../../product-requirements/2026-05-08-voice-session-management.md))
  is deferred until the single-session voice loop is solid.
The initial system bridges a call to exactly one configured Claude Code session,
  matching the Claude Code Channels one-channel-per-session model.
Multi-session routing adds a connection-and-routing harness
  (session registry, selection at and during call time, per-session adapters)
  that should not be taken on before the basics are nailed.
When picked up, it becomes a milestone after the system is otherwise stable.

## Sequencing and Risk

Milestones 1–4 are tightly sequenced and should be completed in order.
Milestones 5 and 6 are end-state polish and can be done at any point
  after milestones 1–4 are stable.

Largest risk areas, in order of severity:

1. **Voice latency.**
   If end-to-end voice-to-voice is too slow, the conversational flow degrades enough
   that the system feels broken.
   Milestone 2 (the bake-off) exists specifically to measure this before
   any agent complexity is added, and to set a realistic latency target from real numbers.
2. **Orchestrator implementation effort.**
   Hand-rolling barge-in, streaming alignment, and lifecycle is the costliest part of the build;
   Milestone 2 compares it head-to-head against leaning on Pipecat before committing.
3. **Permission recognition accuracy in driving conditions.**
   Harder to validate in a quiet office than at highway speed;
   plan real-road testing during Milestone 4.
4. **Telephony reliability and cost.**
   Twilio is the MVP provider primarily for documentation maturity, not cost.
   If sustained-use costs come in higher than projected,
   a Telnyx swap is a contained migration.
