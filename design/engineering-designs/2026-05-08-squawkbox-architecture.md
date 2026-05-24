# Squawkbox Architecture

## Overview

Technical design for Squawkbox,
  a self-hosted voice gateway to Claude Code sessions running on a homelab host.
It is a single, swappable bridge between a phone call and a Claude Code session,
  with hands-free safety and predictable cost as first-class concerns.

See [Squawkbox: Voice Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md)
  for the product context and the requirements documents listed under References for what each
  component must deliver.
The cost and capability research behind the choices below is captured in the
  [architecture-research analysis](../analyses/2026-05-08-voice-agent-architecture-research.md).

## Architecture

Squawkbox is structured as independent layers
  so that each can evolve, be swapped, or be rewritten without disturbing the others:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Channel Adapters                                                    │
│  - Phone (Twilio/Telnyx WebSocket Media Streams)                             │
│  - Apple Shortcuts trigger (HTTP API)                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 2: STT (audio frames → text frames)                                    │
│  - OpenAI Whisper API (cloud, MVP)                                           │
│  - Local Whisper.cpp behind OpenAI-compatible endpoint (end state)           │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 3: Conversation Orchestrator                                           │
│  - Permission handler (interrupt, prompt, parse response)                    │
│  - VAD-gated turn boundary, barge-in, interruption                           │
│  - Session manager (trivial at MVP: one session; multi-session deferred)     │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 4: Agent Adapter (text in/out to a Claude Code session)                │
│  - MCP polling client (MVP — see Trade-offs)                                 │
│  - Claude Code Channels client (end state)                                   │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 5: TTS (text → audio frames)                                           │
│  - ElevenLabs Flash (cloud, MVP)                                             │
│  - Local Piper or Kokoro behind OpenAI-compatible endpoint (end state)       │
└──────────────────────────────────────────────────────────────────────────────┘
                                    │
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 6: Telephony Egress                                                    │
│  - Outbound call placement (telephony provider REST API)                     │
└──────────────────────────────────────────────────────────────────────────────┘
```

The Conversation Orchestrator is the core of the system;
  the other layers are pluggable adapters with narrow, typed interfaces.
This is what makes "swap cloud STT for local STT" or "swap MCP polling for Channels"
  a one-day change rather than a one-month rewrite.

## Technology Choices

- **HTTP API surface** for the Apple Shortcuts trigger and the web admin UI.
- **Telephony provider: Twilio at MVP.**
  Telnyx is cheaper and the architecture supports it as a swap,
  but Twilio's documentation and Media Streams maturity make it the right MVP target.
- **STT/TTS: cloud at MVP** (OpenAI Whisper + ElevenLabs Flash),
  switching to local providers (whisper.cpp + Piper or Kokoro)
  in a later milestone via the OpenAI-compatible-endpoint trick:
  the production code talks to "OpenAI" but configures `base_url` to a local server.
- **Agent adapter: MCP polling at MVP,**
  switching to Claude Code Channels in a later milestone.
  Channels is the architecturally cleaner end state but is too new for the MVP risk budget;
  see Trade-offs.
- **Storage: SQLite** for session metadata, audit logs, and API key storage on the homelab host.
  The data volume is small and SQLite is the obvious choice for a single-host deployment.
- **Structured logging** for observability,
  matching the project-wide preference for structured, queryable logs.

### Open Decision: Orchestrator Implementation and Language

The single shakiest part of this design is the real-time audio orchestration —
  barge-in, VAD-gated turn boundaries, streaming alignment, and interruption.
Two paths are on the table, and the choice is deliberately left open
  until an early spike has built a thin voice loop both ways and compared them:

- **Hand-rolled in Rust.**
  A single static binary that fits a homelab deploy pattern and handles audio at low latency
  without garbage-collection pauses,
  using Tokio for async and `tokio-tungstenite` for the Media Streams WebSocket.
  The risk is that the orchestration logic above is genuinely hard to get right,
  and re-implementing what mature frameworks already provide is the costliest part of the build.
- **Pipecat (Python), the trusted off-the-shelf orchestrator.**
  Pipecat exists precisely to handle barge-in, streaming alignment, codec negotiation,
  lifecycle, and metrics — the hard parts above — in roughly thirty lines of pipeline definition.
  Leaning on it is arguably the leaner, more YAGNI-aligned start
  (don't rebuild a solved problem),
  at the cost of a Python runtime rather than a single static binary.

The bake-off spike (see the delivery plan) builds the smallest possible voice loop on each path,
  measures latency and implementation effort,
  and commits to one before the rest of the system is built on top of it.
moltis's `moltis-telephony` Rust crate is the closest reference for the hand-rolled path;
  Pipecat's MCP-server pattern is the closest reference for the framework path.
Whichever wins, the layer interfaces above stay the same;
  the decision is contained to Layer 3's implementation and the daemon's language.

## Data Flow: Phone Call Path (MVP)

Walking through a single voice turn end-to-end:

1. The operator taps the Apple Shortcut on their Watch.
2. The Shortcut sends `POST /v1/calls` with an API key header to the Squawkbox HTTP API.
3. Squawkbox validates the API key, looks up the destination phone number from config,
    and calls the telephony provider's REST API to place an outbound call to that number.
4. The operator answers the call.
   The provider establishes a Media Streams WebSocket back to Squawkbox,
    streaming mu-law 8 kHz audio bidirectionally.
5. Squawkbox runs a per-call orchestrator task that:
   - reads audio frames from the WebSocket
   - feeds them through a VAD (Silero VAD running locally) to detect end-of-utterance
   - on end-of-utterance, sends the buffered audio to STT and gets back a transcript
   - hands the transcript to the Agent Adapter,
       which conveys it to the configured Claude Code session and reads the response back
   - streams the response text through TTS as it arrives
   - streams the resulting audio back to the provider via the same WebSocket
6. If Claude Code requests permission mid-conversation,
    the orchestrator interrupts the in-flight TTS,
    speaks the permission prompt,
    listens for and recognizes the operator's response,
    and returns the decision to Claude Code.
7. The operator says "goodbye" or hangs up.
   The orchestrator drains the audio pipeline,
   posts a final message to Claude Code recording the end of the conversation,
   and tears down the per-call task.

## Authentication and Authorization

### Apple Shortcuts API key

A 32-byte URL-safe random key, stored in the iOS Keychain via the Shortcut definition,
  sent as an `X-Squawkbox-Key` header on every trigger request.
Squawkbox stores key fingerprints (Argon2id-hashed) in SQLite
  with creation, last-used, and revocation timestamps.
Plaintext keys are never written to disk by Squawkbox.

### Telephony authentication

Only authenticated outbound calls are bridged;
  the authenticated trigger above is the sole way to start a call.
Inbound calls are not accepted:
  PSTN caller ID is spoofable, and no sufficiently strong inbound authentication path
  has been chosen.
If inbound is revisited later, candidate approaches include authenticated SIP or WebRTC
  from a homelab-controlled client (sidestepping PSTN caller-ID spoofing entirely):
  SIP digest auth or mutual TLS, or WebRTC with a short-lived token.
That is an open investigation, not a committed path;
  see the architecture-research analysis.
As optional defense-in-depth on outbound calls,
  Squawkbox can require a DTMF digit before bridging the call to the agent.

### Network exposure

The daemon's HTTP listener binds to a Tailscale-managed socket;
  it is never bound directly to a public network interface.
Two paths reach this socket:

- From within the operator's Tailscale tailnet,
    peers connect directly to the daemon on its tailnet address.
- From the public internet,
    requests reach the daemon via Tailscale Funnel,
    which terminates TLS at a Tailscale-managed public hostname
    (`squawkbox.<tailnet>.ts.net`)
    and proxies traffic to the same socket.

The Apple Shortcuts trigger uses the public Funnel path
  when the operator is off the home network,
  protected by the API key.
The telephony provider's webhook endpoint must be publicly reachable;
  it is exposed via the same Funnel path,
  with Squawkbox validating the provider's signature on every inbound request.

## Permission Handler Design

The permission handler runs as a state machine with these states:

```text
IDLE ──> PROMPTED ──> AWAITING_RESPONSE ──> DECIDED ──> IDLE
                                  │
                                  ├── (timeout 30s) ──> AUTO_DENIED ──> IDLE
                                  │
                                  └── (ambiguous) ──> CLARIFY ──> AWAITING_RESPONSE
```

Transitions:
- `IDLE → PROMPTED`: Claude Code emits a permission request via the Agent Adapter.
   Orchestrator interrupts in-flight TTS, plays the prompt audio.
- `PROMPTED → AWAITING_RESPONSE`: prompt finishes playing, microphone gate opens.
- `AWAITING_RESPONSE → DECIDED`: STT recognizes a response that matches the
   bounded permission grammar.
- `AWAITING_RESPONSE → AUTO_DENIED`: 30 seconds elapse with no recognized response.
- `AWAITING_RESPONSE → CLARIFY`: STT recognizes speech but it doesn't match the grammar.
   Orchestrator plays "I didn't catch that — please say 'yes' or 'no'."

The permission grammar is intentionally narrow:
  approved phrases (`yes`, `approve`, `allow`, `go ahead`, `okay`)
  and denied phrases (`no`, `deny`, `stop`, `cancel`, `don't`).
For destructive actions (flagged by Claude Code's permission metadata),
  the grammar tightens further to require `yes, I'm sure` for approval.

The 30-second microphone gate after the prompt protects against false positives:
  unrelated speech happening when no permission is being requested cannot grant permission
  because the gate is closed.

## Local STT/TTS Migration

The MVP uses cloud OpenAI Whisper and ElevenLabs Flash.
The migration to local providers does not require any code changes in Squawkbox itself:
  it requires running an OpenAI-compatible local server
  (e.g., [speaches](https://github.com/speaches-ai/speaches) for STT,
   or a small wrapper around Piper or Kokoro for TTS that exposes
   `/v1/audio/transcriptions` and `/v1/audio/speech`)
  and changing Squawkbox's `[stt]` and `[tts]` config blocks to point `base_url`
  at the local server.

The migration is gated by:
- whisper.cpp turbo running on the homelab host's Apple Neural Engine
    matching cloud Whisper accuracy on the operator's normal speech, and
- a local Piper or Kokoro voice being acceptable to the operator
    relative to ElevenLabs Flash quality.

## Configuration

Single TOML config file at `~/.squawkbox/squawkbox.toml`:

```toml
[server]
listen = "100.64.0.5:8443"   # Tailscale-managed socket

[telephony]
provider = "twilio"
account_sid_env = "TWILIO_ACCOUNT_SID"
auth_token_env = "TWILIO_AUTH_TOKEN"
caller_id_number = "+15551234567"
operator_phone_number = "+15557654321"

[stt]
provider = "openai"
base_url = "https://api.openai.com/v1"
api_key_env = "OPENAI_API_KEY"
model = "whisper-1"

[tts]
provider = "elevenlabs"
base_url = "https://api.elevenlabs.io/v1"
api_key_env = "ELEVENLABS_API_KEY"
voice_id = "..."
model = "eleven_flash_v2_5"

[agent]
adapter = "mcp_polling"
poll_interval_ms = 200
session = "default"           # single session at MVP; multi-session deferred
```

Secrets are referenced by environment variable name only;
  the daemon reads them from the environment at startup,
  and the homelab uses its service manager to inject them from a secrets manager.

## Observability

- Structured logging events bound to a per-call correlation ID.
- One log line per turn: timestamp, correlation ID, latency breakdown
    (STT ms, agent ms, TTS ms, total).
- Audit log table in SQLite for every authentication attempt, every API key use,
    and every permission decision.
- Web admin UI on `localhost` exposes recent calls, permission decisions, and per-provider costs.
- Failure paths emit structured errors with a clear taxonomy:
    `Auth`, `Telephony`, `Stt`, `Agent`, `Tts`, `Internal`.
  Errors are logged with full context per the project's error-modeling principle.

## Trade-offs

| Decision | Chosen for MVP | Alternative considered | Rationale |
|---|---|---|---|
| Agent adapter | MCP polling | Claude Code Channels | Channels is newer, less battle-tested, and adds a learning-curve risk to the MVP timeline. Polling is a stable, well-documented MCP pattern. The two adapters live behind the same abstraction, so a swap is a contained later milestone. |
| Orchestrator + language | Open decision, resolved by an early bake-off spike | Commit up front to hand-rolled Rust, or up front to Pipecat | The orchestration logic (barge-in, streaming, lifecycle) is the real complexity, not the number of transports. Rather than guess, the spike builds the thinnest voice loop both ways, measures latency and effort, and commits. See "Open Decision" above. |
| STT/TTS at MVP | Cloud (OpenAI / ElevenLabs) | Local (whisper.cpp / Piper) | Cloud removes one dimension of integration risk from the MVP. The base_url-config trick makes the swap to local a configuration change, not a code change. |
| Telephony at MVP | Twilio | Telnyx, Plivo | Twilio has the most mature Media Streams docs, Anthropic-published reference patterns, and lowest setup friction. Telnyx is ~35% cheaper per minute and is the obvious second-milestone swap once Squawkbox proves out. |
| Inbound vs outbound calls | Outbound only | Inbound also accepted | PSTN caller ID is spoofable; an inbound-PSTN auth scheme would either rely on weak signals or require a DTMF-PIN dance that defeats hands-free safety on first connect. Outbound-from-trigger is strictly more secure. Authenticated SIP/WebRTC inbound is a possible future path (see analysis), not committed. |

## Success Criteria

- The MVP daemon runs as a single self-contained service on the homelab host
    under its service manager, with no manual intervention required between releases.
- An Apple Shortcut initiates an authenticated outbound call to the operator's phone
    that bridges to a working Claude Code session within 5 seconds of tap.
- Hands-free permission flow round-trips fast enough not to stall the agent
    and is testable against recorded audio fixtures.
- Cloud-provider costs at the operator's projected usage land well below the third-party baseline,
    inclusive of all line items.
- A migration to local STT/TTS in a later milestone requires zero changes to the daemon's
    code; only a configuration update.
- A migration from MCP polling to Claude Code Channels in a later milestone is contained
    to the Agent Adapter module and does not affect any other layer.

## Testing Approach

The test approach referenced by the requirements:

- **Voice conversation and trigger paths** are covered by automated tests that use
    mock STT/TTS providers and a real Claude Code session configured against a sandbox
    repository, so the agent leg is exercised for real while the paid/cloud legs are mocked.
- **Permission recognition accuracy** is measured against a checked-in set of recorded
    audio fixtures captured under realistic driving conditions, so the 95% bar is a
    repeatable measurement rather than a vibe.
- **End-to-end smoke tests** from a real Apple device and a real phone gate each release.

## References

- **Product Requirements**:
    [Outbound Call Trigger via Apple Shortcuts](../product-requirements/2026-05-08-outbound-call-trigger.md),
    [Secure Voice Conversations With Homelab Claude Code Sessions](../product-requirements/2026-05-08-secure-voice-calls.md),
    [Hands-Free Voice Permission Handling](../product-requirements/2026-05-08-voice-permission-handling.md),
    [Voice Session Management](../product-requirements/2026-05-08-voice-session-management.md) (deferred).
- **Delivery Plan**:
    [Squawkbox Delivery Plan](../delivery-plans/2026-05-08-squawkbox.md).
- **Analysis**:
    [Voice Access to Homelab Claude Code: Architecture Research](../analyses/2026-05-08-voice-agent-architecture-research.md) —
    Evaluates the third-party vs. self-hosted decision,
    surveys voice-agent options at realistic usage levels,
    and grounds the six-layer architecture, Twilio choice, MCP-polling-for-MVP,
    cloud-STT/TTS-for-MVP, and orchestrator-bake-off decisions in concrete cost and capability data.
- **Engineering Principles**:
    [YAGNI](../engineering-principles/2026-01-06-yagni.md),
    [Strong Typing and Information Preservation](../engineering-principles/2026-01-07-strong-typing.md),
    [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md),
    [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md).
- **Inspiration**:
    [moltis: telephony channel (PR #920)](https://github.com/moltis-org/moltis/pull/920) —
    moltis is an OpenClaw variant whose telephony channel
    directly inspired Squawkbox's layered architecture.
    See finding 13 in the analysis above for the current state of moltis PR #920.
