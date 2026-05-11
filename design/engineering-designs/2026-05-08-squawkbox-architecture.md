# Squawkbox Architecture

## Overview

Technical design for Squawkbox,
  the family's voice and text gateway to Claude Code sessions running on the homelab Mac mini.
Addresses the need for a single, swappable, self-hosted bridge between
  several user-facing channels (PSTN call, Slack text, Slack Huddle)
  and one or more Claude Code sessions,
  with hands-free safety and predictable cost as first-class concerns.

See [Squawkbox: Voice and Text Access to Homelab Agents](../product-vision/2026-05-08-squawkbox.md)
  for the product context and the requirements documents listed under References for what each
  component must deliver.

## Architecture

Squawkbox is structured as six independent layers
  so that each can evolve, be swapped, or be rewritten without disturbing the others:

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Layer 1: Channel Adapters                                                    │
│  - Phone (Twilio/Telnyx WebSocket Media Streams)                             │
│  - Slack text (Events API + Web API)                                         │
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
│  - Session manager (which Claude Code session is this turn for?)             │
│  - Permission handler (interrupt, prompt, parse response)                    │
│  - VAD-gated turn boundary, barge-in, interruption                           │
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
│ Layer 6: Telephony / Channel Egress                                          │
│  - Outbound call placement (Twilio REST API)                                 │
│  - Slack message posting (Web API)                                           │
└──────────────────────────────────────────────────────────────────────────────┘
```

The Conversation Orchestrator is the core of the system;
  the other layers are pluggable adapters with narrow, typed interfaces.
This is what makes "swap cloud STT for local STT" or "swap MCP polling for Channels"
  a one-day change rather than a one-month rewrite.

## Technology Choices

- **Rust** for the core daemon.
  Single static binary deploy fits Karl's homelab pattern,
  matches existing skill in Rust-based homelab tooling,
  and handles audio at low latency without garbage-collection pauses.
- **Hand-rolled audio pipeline** in Rust with Tokio for async,
    `bytes` for buffer management,
    and `tokio-tungstenite` for the Twilio Media Streams WebSocket.
  Pipecat (via PyO3 bindings) and LiveKit Agents (Rust SDK) were considered and rejected;
    see the Audio framework row in the Trade-offs table.
  Hand-rolling is justified by the YAGNI principle:
    Squawkbox needs only one channel adapter at MVP and one well-defined audio shape
    (mu-law 8 kHz from Twilio),
    not the broad menu of transports that Pipecat or LiveKit support.
- **`hyper` or `axum`** for the HTTP API surface
  (Apple Shortcuts trigger, Slack webhook receiver, web admin UI).
- **Twilio** for telephony at MVP.
  Telnyx is cheaper and the architecture supports it as a swap,
  but Twilio's documentation and Media Streams maturity make it the right MVP target.
- **OpenAI Whisper API** for STT at MVP and **ElevenLabs Flash** for TTS at MVP,
  switching to local providers (whisper.cpp + Piper or Kokoro)
  in a later milestone via the OpenAI-compatible-endpoint trick:
  the production code talks to "OpenAI" but configures `base_url` to a local server.
- **MCP polling** for the agent adapter at MVP,
  switching to Claude Code Channels in a later milestone.
  Channels is the architecturally cleaner end state but is too new for the MVP risk budget;
  see Trade-offs.
- **`slack-morphism`** (Rust Slack SDK) for the Slack channel adapter.
- **`sqlx` with SQLite** for session metadata, audit logs, and API key storage on the Mac mini.
  The data volume is small and SQLite is the obvious choice for a single-host deployment.
- **`tracing` with `tracing-subscriber`** for structured logging,
  matching the project-wide preference for structured observability.

## Data Flow: Phone Call Path (MVP)

Walking through a single voice turn end-to-end:

1. Karl taps the Apple Shortcut on his Watch.
2. The Shortcut sends `POST /v1/calls` with API key header to the Squawkbox HTTP API.
3. Squawkbox validates the API key, looks up Karl's destination phone number from config,
    and calls the Twilio REST API to place an outbound call to that number.
4. Karl answers the call.
   Twilio establishes a Media Streams WebSocket back to Squawkbox,
    streaming mu-law 8 kHz audio bidirectionally.
5. Squawkbox spawns a per-call orchestrator task that:
   - reads audio frames from the Twilio WS
   - feeds them through a VAD (Silero VAD running locally) to detect end-of-utterance
   - on end-of-utterance, sends the buffered audio to Whisper API and gets back a transcript
   - hands the transcript to the Agent Adapter,
       which conveys it to the chosen Claude Code session and reads the response back
   - streams the response text through ElevenLabs Flash TTS as it arrives
   - streams the resulting audio back to Twilio via the same WebSocket
6. If Claude Code requests permission mid-conversation,
    the orchestrator interrupts the in-flight TTS,
    speaks the permission prompt,
    listens for and recognizes Karl's response,
    and returns the decision to Claude Code.
7. Karl says "goodbye" or hangs up.
   The orchestrator drains the audio pipeline,
   posts a final message to Claude Code recording the end of the conversation,
   and tears down the per-call task.

## Data Flow: Slack Text Path

1. A family member @-mentions the Squawkbox bot in a Slack channel or DM.
2. Slack delivers the message to Squawkbox's `/v1/slack/events` HTTP endpoint.
3. Squawkbox validates the Slack signing secret,
    identifies the user and intended session,
    and conveys the message text to the appropriate Claude Code session via the Agent Adapter.
4. As the agent generates a response, Squawkbox streams updates to the Slack thread
    using `chat.update` calls bounded by Slack's rate limits.
5. Permission requests are posted as interactive Slack messages with Approve/Deny buttons;
    button presses come back via the same `/v1/slack/events` endpoint
    and are routed to the agent.

## Authentication and Authorization

### Apple Shortcuts API key

A 32-byte URL-safe random key, stored in iOS Keychain via the Shortcut definition,
  sent as `X-Squawkbox-Key` header on every trigger request.
Squawkbox stores key fingerprints (Argon2id-hashed) in SQLite
  with creation, last-used, and revocation timestamps.
Plaintext keys are never written to disk by Squawkbox.

### Telephony authentication

Outbound calls use the same authenticated trigger as above.
Inbound calls are not accepted at MVP;
  if they are added later, authentication will require both:
1. Caller ID match against a tight allowlist (Karl's phone numbers only).
2. DTMF PIN entry within the first 10 seconds, with three-strike lockout.
The combination provides defense in depth against caller-ID spoofing.

### Slack authentication

Slack Events API requests are authenticated by Slack's signing secret on every webhook,
  with the request timestamp validated against the local clock to a 5-minute tolerance
  to mitigate replay attacks.
Per-user authorization comes from a Squawkbox-side allowlist mapping Slack user IDs
  to permitted sessions and capabilities.

### Network exposure

The daemon's HTTP listener binds to a Tailscale-managed socket;
  it is never bound directly to a public network interface.
Two paths reach this socket:

- From within the family's Tailscale tailnet,
    peers connect directly to the daemon on its tailnet address.
- From the public internet,
    requests reach the daemon via Tailscale Funnel,
    which terminates TLS at a Tailscale-managed public hostname
    (`squawkbox.<tailnet>.ts.net`)
    and proxies traffic to the same socket.

The Apple Shortcuts trigger uses the public Funnel path
  when Karl is off the home network,
  protected by the API key.
The Twilio webhook endpoint must be publicly reachable;
  it is exposed via the same Funnel path,
  with Squawkbox validating Twilio's signature on every inbound request.

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
- whisper.cpp turbo running on the Mac mini's Apple Neural Engine
    matches cloud Whisper accuracy on Karl's normal speech, and
- a local Piper or Kokoro voice is acceptable to Karl's family
    relative to ElevenLabs Flash quality.

## Configuration

Single TOML config file at `~/.squawkbox/squawkbox.toml`:

```toml
[server]
listen = "100.64.0.5:8443"   # Tailscale IP

[telephony]
provider = "twilio"
account_sid_env = "TWILIO_ACCOUNT_SID"
auth_token_env = "TWILIO_AUTH_TOKEN"
caller_id_number = "+15551234567"
karl_phone_number = "+15557654321"

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

[slack]
enabled = false               # MVP defers Slack
signing_secret_env = "SLACK_SIGNING_SECRET"
bot_token_env = "SLACK_BOT_TOKEN"
allowed_user_ids = []
```

Secrets are referenced by environment variable name only;
  the daemon reads them from the environment at startup,
  and the homelab uses systemd to inject them from a secrets manager.

## Observability

- Structured `tracing` events bound to a per-call or per-message correlation ID.
- One log line per turn: timestamp, correlation ID, channel, latency breakdown
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
| Agent adapter | MCP polling | Claude Code Channels | Channels is newer, less battle-tested, and adds a learning-curve risk to the MVP timeline. Polling is a stable, well-documented MCP pattern. The two adapters live behind the same trait, so a swap is a contained later milestone. |
| Audio framework | Hand-rolled with Tokio | Pipecat (Python) or LiveKit Agents (Rust SDK) | Squawkbox needs one transport (Twilio Media Streams) at MVP, not the broad menu these frameworks ship. YAGNI says: don't take the dep until a second transport demands it. |
| STT/TTS at MVP | Cloud (OpenAI / ElevenLabs) | Local (whisper.cpp / Piper) | Cloud removes one dimension of integration risk from the MVP. The base_url-config trick makes the swap to local a configuration change, not a code change. |
| Telephony at MVP | Twilio | Telnyx, Plivo | Twilio has the most mature Media Streams docs, Anthropic-published reference patterns, and lowest setup friction. Telnyx is ~35% cheaper per minute and is the obvious second-milestone swap once Squawkbox proves out. |
| Inbound vs outbound calls | Outbound only | Inbound also accepted | PSTN caller ID is spoofable; an inbound-call auth scheme would either rely on weak signals or require a DTMF-PIN dance that defeats hands-free safety on first connect. Outbound-from-trigger is strictly more secure and only marginally less convenient. |
| Language | Rust | Python, Go, TypeScript | Single static binary, low-latency audio handling, matches Karl's existing homelab tooling preferences, and aligns with the [moltis](https://github.com/moltis-org/moltis) ecosystem he is already familiar with. |

## Success Criteria

- The MVP daemon runs as a single Rust binary on the Mac mini under launchd or systemd
    with no manual intervention required between releases.
- An Apple Shortcut on Karl's Watch initiates an authenticated outbound call to his phone
    that bridges to a working Claude Code session within 5 seconds of tap.
- Hands-free permission flow round-trips in under 3 seconds for ordinary actions
    and is testable against recorded audio fixtures.
- Cloud-provider costs at 1,500 voice minutes per month land between $25 and $45
    inclusive of all line items.
- A migration to local STT/TTS in a later milestone requires zero changes to the daemon's
    Rust code; only a configuration update.
- A migration from MCP polling to Claude Code Channels in a later milestone is contained
    to the Agent Adapter module and does not affect any other layer.

## References

- **Product Requirements**:
    [Outbound Call Trigger via Apple Shortcuts](../product-requirements/2026-05-08-outbound-call-trigger.md),
    [Secure Voice Conversations With Homelab Claude Code Sessions](../product-requirements/2026-05-08-secure-voice-calls.md),
    [Voice Session Management](../product-requirements/2026-05-08-voice-session-management.md),
    [Hands-Free Voice Permission Handling](../product-requirements/2026-05-08-voice-permission-handling.md),
    [Slack Text Conversations With Claude Code Sessions](../product-requirements/2026-05-08-slack-text-channel.md),
    [Slack Permission Button Flow](../product-requirements/2026-05-08-slack-permission-flow.md).
- **Delivery Plan**:
    [Squawkbox Delivery Plan](../delivery-plans/2026-05-08-squawkbox.md).
- **Analysis**:
    [Voice Access to Homelab Claude Code: Architecture Research](../analyses/2026-05-08-voice-agent-architecture-research.md) —
    Evaluates the third-party vs. self-hosted decision,
    surveys voice-agent options at Karl's usage level,
    and grounds the six-layer architecture, Twilio choice, MCP-polling-for-MVP,
    and cloud-STT/TTS-for-MVP decisions in concrete cost and capability data.
- **Engineering Principles**:
    [YAGNI](../engineering-principles/2026-01-06-yagni.md),
    [Strong Typing and Information Preservation](../engineering-principles/2026-01-07-strong-typing.md),
    [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md),
    [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md).
- **Inspiration**:
    [moltis: telephony channel (PR #920)](https://github.com/moltis-org/moltis/pull/920) —
    moltis is an OpenClaw variant whose recently-merged telephony channel
    directly inspired Squawkbox's layered architecture.
    See finding 13 in the analysis above for the current state of moltis PR #920.
