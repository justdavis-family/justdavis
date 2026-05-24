# Voice Access to Homelab Claude Code: Architecture Research

## Goals

Karl has been using [Happy Coder](https://happy.engineering/)'s voice mode to talk to Claude Code sessions.
At his actual usage rate the existing third-party path is uncomfortably expensive
  and binds him to a vendor stack and cloud relay he doesn't control.
This analysis evaluates whether to keep using Happy as-is,
  use Happy with a "bring your own ElevenLabs agent" configuration,
  or build a self-hosted alternative —
  and what that self-hosted alternative would actually look like and cost.
The analysis informs the design decisions captured in the
  [Squawkbox vision](../product-vision/2026-05-08-squawkbox.md),
  its requirements,
  and its [engineering design](../engineering-designs/2026-05-08-squawkbox-architecture.md).

## Questions and Uncertainties

Before committing to an architecture, the following questions needed answers:

1. Can Karl bring his own ElevenLabs agent to Happy Coder?
     What does the configuration require, and is the path documented?
2. At Karl's actual usage rate, what does Happy cost per month,
     and will he hit any caps before his subscription renews?
3. How does ElevenLabs Agents pricing compare to component-by-component alternatives —
     OpenAI Realtime, Twilio, Vapi, Retell, and a DIY composable stack?
4. Could iOS accessibility features (VoiceOver, Speak Screen) substitute for some
     voice-agent usage and reduce cost?
5. What other webapps, iOS apps, or Claude-Code-related projects offer bidirectional
     voice access to a self-hosted agent on the user's own hardware?
6. Is Anthropic's experimental Claude Code Channels feature required for use cases like this?
7. What are the architectural layers in a voice-agent system,
     and how do they relate to each other and to MCP / Channels?
8. What does Pipecat (the open-source voice-AI framework) actually do,
     and how would it fit into a homelab build?
9. What are the code/effort requirements for writing a custom Claude Code Channels plugin?
     Does it have to be in TypeScript?
10. How are MCP polling and Channels-style push-based integration different in practice,
      and when does each make sense?
11. Are on-device speech-to-text providers performant enough to replace cloud STT,
      and how much would that save at Karl's usage level?
12. What is the current state of the moltis telephony PR (#920),
      and is it ready to use?

## Findings

### 1. ElevenLabs BYOA in Happy is Viable but Undocumented

Happy Coder supports a "Bring Your Own Agent" mode in which a custom ElevenLabs Conversational
  AI agent replaces the default Happy-managed one.
The path is implementable today but the only documentation is the on-screen text in the iOS app.
GitHub issue [#472](https://github.com/slopus/happy/issues/472) is the open request for proper docs.

The custom agent must define two client tools and consume one dynamic variable:

- `messageClaudeCode(message: string)`: sends the user's instruction to Claude Code via the Happy Server.
- `processPermissionRequest(decision: "allow" | "deny")`:
    relays Karl's permission decision back to Claude Code.
- `{{initialConversationContext}}`: dynamic variable injected into the system prompt at session start,
    containing the relevant Claude Code session history.

A working configuration was reverse-engineered from issue
  [#1032](https://github.com/slopus/happy/issues/1032)
  and includes a system prompt scoped to "voice bridge between user and Claude Code,"
  the two tool JSON definitions,
  and a 117-second response timeout on the permission tool.
Issue #1032 is also a known bug:
  in Direct Connection mode the `messageClaudeCode` tool sometimes does not fire,
  meaning the agent acknowledges the user's voice input conversationally
  but never actually relays the instruction to Claude Code.
The bug remains open as of May 2026.

### 2. Happy's Cost at Karl's Actual Usage Rate Will Exceed the Subscribed Cap

The Happy Voice Subscribed tier provides 5 hours (300 minutes) of voice time per month.
Initial usage data showed 180m 19s used and 31 conversations
  in what appeared to be a rolling 30-day window.
Closer examination revealed the counter actually started ~3–5 days into the current billing cycle,
  so the genuine daily rate is much higher than first projection.

| Days into cycle | Daily rate | Projected monthly | Days until cap |
|-----------------|-----------|-------------------|----------------|
| 5 (Apr 30 start) | 36 min/day, 6.2 conv/day | ~1,080 min | ~9 |
| 4 (May 1 start) | 45 min/day, 7.75 conv/day | ~1,350 min | ~7 |
| 3 (May 2 start) | 60 min/day, 10.3 conv/day | ~1,800 min | ~5 |

The 300-minute voice cap is the binding constraint:
  the 100-conversation cap is not reached in any scenario.
At all three rates the cap will be hit well before the May 30 renewal,
  locking voice access until the next billing cycle.

For sustained-usage cost projections downstream in this analysis,
  1,500 min/mo is used as a conservative midpoint.

### 3. ElevenLabs Pricing Is Competitive in Its Tier; the Market Floor Is ~$0.07–0.10/min

ElevenLabs Conversational AI charges $0.08/min flat across every plan tier,
  with a 95% discount on continuous silence ≥10 seconds.
Plan tiers determine pre-paid minutes and concurrency, not per-minute rate.
Karl's usage at 1,500 min/mo lands at ~$95–165/mo on Happy with BYOA depending on plan choice.

Component-by-component alternatives at the same volume:

| Option | Monthly cost @ 1,500 min | Notes |
|---|---|---|
| OpenAI Realtime API (gpt-realtime) | $215 | $32/M audio in + $64/M audio out; bills silence by default |
| Vapi / Retell / Synthflow | $200–300 | Bills silence; no improvement over ElevenLabs |
| ElevenLabs Agents (BYOA via Happy) | $95–165 | 95% silence discount kicks in for Karl's pattern |
| Twilio + Anthropic API + ElevenLabs Flash (DIY) | $80 | Closest to traditional telephony bill shape |
| Composable stack (Deepgram + Haiku + Cartesia, self-hosted orchestrator) | $30 | Cheapest hosted-component path |
| Local STT + Local TTS + Anthropic API | $20 | Just Twilio PSTN minutes plus Anthropic spend |

The "speech-in, speech-out, intelligent" market floor is roughly **$0.07–0.10/min** with hosted components,
  driven by the actual cost of STT + LLM + TTS + transport + provider margin.
Building it yourself gets you to ~$0.05/min only if you self-host the orchestrator
  on hardware you already pay for.
At Karl's volume that's a savings of ~$30–50/mo over BYOA ElevenLabs.

### 4. iOS Accessibility Cannot Replace the Voice Agent

iOS provides three options that touch the "read text from an app aloud" use case,
  but none of them deliver bidirectional voice with turn detection:

- **VoiceOver**: full screen reader.
  Blind users do navigate chat apps like Slack and Messages with VoiceOver,
    so a workable (if manual, screen-focused) input-and-output UX clearly exists for those apps;
    whether Happy specifically exposes its streaming content well is undocumented.
  This bears validation by watching how blind users actually drive chat apps;
    the working assumption here is that VoiceOver covers the output side
    but does not provide the hands-free, eyes-off turn-taking a voice agent does.
- **Speak Screen**: two-finger swipe-down reads the current screen at trigger time;
    does not update as new content streams in.
  Manual re-trigger required for each new agent response.
- **Announce Notifications**: reads incoming push notifications aloud through AirPods.
  Best zero-effort option for ambient awareness, but only handles notifications,
    not in-conversation speech.

The fundamental problem for the hands-free driving use case is that none of these
  provide eyes-off, touch-free turn-taking.
VoiceOver can drive input, but by touch on a screen, not by voice while driving;
  iOS dictation can capture voice input but doesn't translate stream-of-consciousness speech
  into clean prompts the way a voice agent's bridge LLM does.
At best, accessibility features could reduce voice-agent usage by 20–30% for
  asynchronous "tell me when Claude is done" scenarios;
  they cannot substitute for the active back-and-forth that drives the bulk of usage.

### 5. Twilio Is for Telephony; In-App Voice Is a Different Architecture

A common point of confusion:
  Twilio Voice's $0.013/min outbound rate is not directly comparable to ElevenLabs Agents,
  because Twilio is for *telephony* (PSTN phone calls)
  while in-app voice uses *WebRTC* or *WebSockets* over the data plane.
The two architectures share no audio plumbing and have very different cost shapes:

- **Telephony**: bills per-minute regardless of what's spoken; easy to dial from any phone;
    works on cellular without an app; subject to carrier signaling overhead.
- **In-app WebRTC**: zero per-minute fee for the audio leg if self-hosted P2P;
    requires a client app or PWA with mic permissions; benefits from streaming codecs.

Twilio enters the picture properly when one wants the "call-a-phone-number-to-reach-Claude-Code"
  experience, which is an explicit Squawkbox requirement for hands-free driving access.
Twilio Media Streams (the WebSocket-bridged audio path) is what makes
  full-duplex in-call voice with sub-second latency possible.

### 6. Self-Hosted Voice-Agent Options Survey

Seven distinct projects or patterns offer "bidirectional voice to an agent on your own hardware"
  today, ranked by estimated cost at 1,500 min/mo:

| Option | Approach | Mobile path | Cost @ 1,500 min |
|---|---|---|---|
| Pipecat MCP Server + Claude Code | WebRTC PWA, self-hosted orchestrator | iOS Safari PWA | ~$30/mo |
| LiveKit Agents (self-hosted) + custom Claude Code wrapper | WebRTC + LiveKit SIP/PSTN optional | LiveKit iOS SDK or PWA | ~$32/mo |
| OpenClaw voice-call plugin | Twilio Media Streams + Gemini Live | PSTN call | ~$38/mo |
| Moltis (with PR #920 telephony) | Multi-provider PSTN | PSTN call or PWA | ~$45/mo |
| DIY Twilio ConversationRelay | Twilio-managed STT/TTS bridge | PSTN call | ~$80/mo |
| Happy Coder + ElevenLabs BYOA | In-app WebRTC via ElevenLabs | Native iOS app | ~$130/mo |
| DIY OpenAI Realtime API | gpt-realtime end-to-end | iOS WebRTC | ~$215/mo |

Notable near-misses that don't satisfy the "bidirectional voice to self-hosted agent" requirement:

- **Claurst** (Rust Claude Code reimplementation): mic input only; no agent voice back; terminal-only.
- **Anthropic's official Claude Code voice mode** (Q1 2026):
    push-to-talk STT only; no TTS back; local terminal only.
- **Cursor mobile + Remote Agents** (Apr 2026): voice on phone is push-to-talk transcription;
    agent doesn't speak back; cloud agent runs on Cursor's VMs, not user hardware.
- **AFK Remote**, **AgentVibes**, **CloudCLI** (siteboon/claudecodeui): each fails one of the
    three legs (bidirectional, voice, self-hosted).
- **Vapi / Retell / Synthflow**: voice loop runs in their cloud and bills silence by default.
- **Home Assistant Assist**: technically possible but no published Claude-Code conversation
    integration exists; would be DIY parallel to Pipecat with a worse client.

Relaxing the self-hosting requirement (acceptable if a hosted option is affordable at the
  expected usage level) does not rescue these near-misses:
  almost all of them fail on the bidirectional-voice leg (push-to-talk only, or no agent
  voice back), not on self-hosting.
The hosted options that *do* close the bidirectional-voice loop affordably
  (ElevenLabs Agents via Happy BYOA, ~$130/mo) are already captured in the main table above;
  they remain several times more expensive than the self-hosted floor at the same volume.

### 7. NetworkChuck's claude-phone Is the DIY Composable Stack with Free SIP Transport

NetworkChuck (YouTube/`theNetworkChuck/claude-phone`) demonstrated a self-hosted voice setup
  that uses **3CX**, a free-tier PBX (phone-system software running in 3CX's cloud),
  as the audio transport.
The architecture maps cleanly to the layered model in finding 9:

- **Layer 1 (audio transport)**: SIP between a softphone on his iPhone and 3CX,
    then SIP between 3CX and his homelab's voice-app container.
  Both legs are SIP-over-internet, so there is **no PSTN carrier involved** —
    that's where the "free phone calls" framing comes from.
- **Layer 2 (STT)**: OpenAI Whisper API.
- **Layer 3 (agent)**: Claude Code CLI in `--print` mode, wrapped by an HTTP service.
- **Layer 4 (TTS)**: ElevenLabs.
- **Layer 5 (orchestrator)**: A Dockerized voice-app using `drachtio` for SIP signaling
    and `freeswitch` for media handling; buffers audio frames, runs them through Whisper at
    end-of-utterance, calls the api-server, pipes ElevenLabs audio back.
- **Layer 6 (tooling)**: Whatever Claude Code's normal tools are.
  No Channels, no MCP — orchestrator invokes Claude directly via stdin.

The "jankiness" of his setup is not really jank;
  it's the cost of gluing five services to build what ElevenLabs Agents bundles.
Cost at 1,500 min/mo is ~$25–35/mo, competitive with Pipecat MCP Server.
The downside is the operational complexity of drachtio + freeswitch + 3CX + Docker on a Pi.

If a regular phone needs to dial in (rather than a SIP softphone),
  a SIP trunk from a carrier is required,
  and per-minute fees come back into play.

### 8. Channels Are Not Required for Voice; the Mental Model Was Confused

Anthropic launched **Claude Code Channels** in March 2026 as a research-preview feature.
The marketing framing was "bidirectional messaging into a running Claude Code session,"
  which was easy to conflate with the voice-agent problem because both involve
  "talk to Claude Code from somewhere else."
Concretely, the two are different problems:

- **Channels**: external systems push *text messages* into a running Claude Code session
    over an MCP transport.
  Bidirectional in the sense Claude can reply through the same channel,
    but the bytes are JSON over stdio or streamable-HTTP.
  The use case is "Telegram/Slack/webhook nudges Claude Code that's running in the background."
- **Voice bridge**: convert microphone audio to text, hand the text to Claude Code,
    take Claude's text response, convert to speech, play it.
  The bytes are PCM/Opus audio.

MCP itself has been bidirectional since launch — notifications, sampling
  (where the server requests an LLM call from the client),
  and elicitation (where the server asks the client to prompt the user).
What Channels added wasn't bidirectionality;
  it added one specific new pattern:
  external systems injecting messages into an *already-running* session,
  without the session having to poll.

Implication for Squawkbox: **voice does not require Channels.**
Channels would be useful for a separate "Telegram message to interrupt my driving voice call"
  feature, but that's an additional capability, not a foundational dependency.
Voice can be implemented today with regular MCP polling or even with the Claude Code SDK
  via subprocess invocation.

### 9. The Six-Layer Stack Mental Model

Every voice-agent option in the survey is a combination of choices at six layers.
Once the layers are visible, the option list stops feeling random and starts feeling
  like a Lego kit:

| Layer | Concern | Examples |
|---|---|---|
| 1. Audio transport | How sound moves between phone and server | WebRTC, PSTN/SIP, push-to-talk over HTTP |
| 2. Speech-to-text | Audio → text + turn detection | Deepgram, Whisper API, ElevenLabs Scribe, local Whisper.cpp |
| 3. Agent | Text in → text out | Claude Code, plain Anthropic API, custom agent loop |
| 4. Text-to-speech | Text → audio | ElevenLabs Flash, Cartesia, OpenAI TTS, local Piper/Kokoro |
| 5. Orchestrator | Wires layers 1–4 with concurrency, barge-in, lifecycle | Pipecat, LiveKit Agents, ElevenLabs Conv-AI, custom |
| 6. Agent tooling | How the agent reaches into the world | MCP servers, Channels, built-in tools |

Layer 6 is **orthogonal to layers 1–5.**
A Claude Code session running silently in a terminal uses layer 6 the same way
  a voice-bridged session does.
This is why "voice is plumbing for audio bytes; Channels is plumbing for text events;
  MCP is plumbing for tool calls" is a useful summary:
  three independent concerns, each with their own vendor menu,
  cross-multiplied into the apparent option explosion.

This six-layer model is the foundation of the
  [Squawkbox engineering design](../engineering-designs/2026-05-08-squawkbox-architecture.md).

### 10. Pipecat Is the Concurrency-and-Lifecycle Framework for Voice

Pipecat (`pipecat-ai/pipecat`, Apache 2.0) is an open-source Python framework
  whose entire purpose is layer 5 — the orchestrator.
A complete working voice bot is ~30 lines:

```python
pipeline = Pipeline([
    transport.input(),     # WebRTC audio in
    stt,                   # audio → text
    user_aggregator,       # build user turn into context
    llm,                   # context → response text
    tts,                   # text → audio
    transport.output(),    # WebRTC audio out
    assistant_aggregator,  # remember what bot said
])
```

Each item is a **frame processor** that consumes some frame types,
  produces others, and passes the rest through.
Frames flow downstream (audio in → audio out);
  control signals (interruption events, metrics) flow upstream.
Pipecat manages the asyncio plumbing: spawning concurrent tasks per processor,
  bounded queues between them, and an `InterruptionFrame` mechanism that cancels
  in-flight TTS, drops queued audio, and resets the LLM's pending generation
  whenever the VAD detects the user starting to speak.

Concretely, things Pipecat handles that would each be 100–500 lines of custom code:

- Barge-in (interrupt agent mid-utterance, cleanly).
- Streaming alignment (TTS chunks arrive async; flush correctly on interrupt).
- Codec negotiation (Opus for WebRTC, mu-law for telephony, transparent to user code).
- Lifecycle (peer connection setup, disconnection handling, reconnection).
- Metrics (time-to-first-byte per stage, end-of-utterance to start-of-bot-speech latency).

The choice for Squawkbox MVP is whether to take the dep on Pipecat or hand-roll in Rust.
Per the YAGNI engineering principle,
  hand-rolling is justified for the MVP because Squawkbox needs only one transport
  (Twilio Media Streams) and one well-defined audio shape (mu-law 8 kHz).
If a second transport (WebRTC PWA, additional SIP provider) becomes a real requirement,
  re-evaluating the framework choice is a reasonable later milestone.
Pipecat's MCP server pattern remains the cheapest off-the-shelf option
  for the Squawkbox use case if hand-rolling proves more painful than expected.

### 11. MCP Polling Limitations Make Channels the Better End-State Pattern

MCP polling — having Claude Code call a "did anything happen?" MCP tool periodically —
  is the obvious pre-Channels pattern for getting external messages into a session.
Three significant limitations:

1. **Latency vs. cost tradeoff.**
   Poll every 1 second for fast pickup and burn requests; poll every 60 seconds for cheap
     and accept up to a minute of message-queue delay.
   No good answer.
2. **The model reacts between turns, never mid-tool-execution.**
   Claude Code can in fact watch background processes (the Monitor tool)
     and receive externally-pushed events (Channels) without the model itself
     looping on a poll tool — the harness delivers each event reactively.
   But every such event is surfaced *between* agent turns, not during one:
     if Claude is mid-tool-call, an incoming message queues until that turn completes.
   A naive poll-tool loop is worse still:
     either it burns tokens on every poll even when nothing has happened,
     or it only checks on user-input boundaries,
     so external messages don't arrive until the user speaks.
3. **Nothing interrupts a running tool call.**
   Even with aggressive polling there's a window where Claude is mid-tool-call
     and hasn't checked the queue.
   Channels notifications land between agent steps, which is better,
     but they still do not preempt an in-flight turn.

Channels addresses the first two cleanly:
  server-pushed events are immediate and free of token cost.
It does not magically interrupt a running tool call —
  no mechanism does; external events land between turns either way —
  but it removes the latency-vs-cost dial and the user-input-boundary problem entirely.
For Squawkbox the implication is that **MCP polling is acceptable for the MVP**
  (it's stable, well-documented, and lower implementation risk than a research-preview feature),
  but **Channels is the right end-state.**
Both adapters live behind the same agent-adapter abstraction in the engineering design,
  so the swap is a contained later milestone
  (see the Channels milestone in the delivery plan).

### 12. Channels Plugins Are Small and Language-Agnostic

A working one-way Channels plugin is ~30 lines of TypeScript,
  including imports and the HTTP listener.
Tiered roughly:

| Plugin shape | Approximate LOC | What's added |
|---|---|---|
| One-way (alerts in, no reply) | ~30 | Just `Server` constructor with `claude/channel` capability + notification call |
| Two-way (chat bridge) | ~85 | Adds tool registration, `ListTools`/`CallTool` handlers, reply tool schema |
| Two-way + permission relay | ~130 | Adds `claude/channel/permission` capability + verdict regex |
| Sender-allowlisted | ~150 | Adds gate-on-sender check |

Real bridges (Telegram, Discord) are larger (~300–600 LOC) but most of the bulk is
  platform-specific glue — pairing flow, polling the platform's API, parsing message types,
  handling attachments.
The Channels-specific code itself stays small.

**Language is not constrained to TypeScript.**
The Channels protocol is just MCP plus Claude-Code-specific capability declarations
  (`claude/channel`, `claude/channel/permission`)
  and notification methods (`notifications/claude/channel`).
Any language with an MCP SDK can implement a Channels plugin —
  Python, TypeScript, Go, Rust, Java, Kotlin, C#, Swift, and Ruby all have official SDKs.
The reason Anthropic's reference plugins are TypeScript+Bun is partly that Bun ships with
  a built-in HTTP server and TS support without ceremony,
  and partly just convention from the team that wrote them.

For Squawkbox this means the eventual Channels-based agent adapter can be written in Rust
  (matching the rest of the daemon) without any tooling friction.
The minor caveats:
  the `claude/channel` capability is a Claude Code extension, not stock MCP,
  so the SDK may not expose a typed builder for it
  and the implementation may need to drop down to raw JSON for the initialize response;
  same goes for the notification method names.
None of that is structural — just a couple of `sendNotification(method, params)` escape hatches.

### 13. moltis PR #920 Is Merged and Likely Shipped in Release `20260507.05`

PR [#920](https://github.com/moltis-org/moltis/pull/920) (`feat(telephony): add phone call support via Twilio`)
  merged on May 7, 2026 with 37 commits at commit `ce09a59`.
The PR's design evolved substantially during review:

- Started with Twilio Gather (HTTP polling) for STT, with ~4–11s per-turn latency.
- Greptile review caught a missing `action` URL on the Gather causing multi-turn breakage.
- Pivoted mid-PR to **Twilio Media Streams WebSocket** (mu-law 8 kHz bidirectional)
    with sub-second latency and barge-in support.
- Added **Telnyx and Plivo providers** in addition to Twilio,
    each with their respective signature-verification schemes
    (Ed25519 for Telnyx, HMAC-SHA256 with nonce-based replay protection for Plivo).
- **Refactored telephony into a top-level `[phone]` config section** with dedicated provider
    blocks and a Settings > Phone web UI page,
    moving phone from "just another channel" to a first-class subsystem.
- Resolved Greptile P1 issues (signature verification, DTMF injection guards,
    `provider_index` memory leak, `RoutingOutbound` dispatch).
- Added MockTts and MockStt providers for testing.

Release timing:
  the merge landed at commit `ce09a59` ~16:00 UTC May 7;
  release `20260507.05` was tagged at commit `c198ac5` 56 minutes later.
At the time of the original research the CHANGELOG.md had no telephony entry,
  so the documentation lagged the binary.
This has since been confirmed: telephony shipped and is live,
  per the [moltis changelog](https://moltis.org/changelog/) (verified May 2026).

For Squawkbox this means moltis is a viable reference implementation of the same architectural
  pattern: Rust binary, multi-provider telephony, Twilio Media Streams WebSocket, configurable
  STT/TTS via the OpenAI-compatible-`base_url` trick.
moltis itself is a broader "personal agent server" than Squawkbox needs
  (it bundles Telegram/Signal/Discord/Teams channels, memory, sandboxed execution),
  but its `moltis-telephony` Rust crate is a near-direct reference for Squawkbox's
  Channel Adapter and Telephony Egress layers.

### 14. On-Device STT Is Performant Enough for the Mac mini Path

On Apple Silicon hardware, **whisper.cpp with the Whisper-turbo model** is the
  most battle-tested local STT option.
Whisper.cpp uses Core ML to run encoder inference on the Apple Neural Engine,
  more than 3× faster than CPU-only execution.
On a Mac mini, Whisper-turbo achieves ~0.5–1 second STT latency per utterance,
  with accuracy essentially equivalent to cloud Whisper at the same model size.

Other local STT options considered:

- **Voxtral Realtime** (Mistral, Feb 2026): newer streaming-first architecture but
    requires 16 GB VRAM in BF16; quantized variants exist but ecosystem is young.
- **Parakeet-TDT v3** (NVIDIA): extremely fast for English; requires GPU.
- **WhisperKit**: Native Swift framework, only useful for embedding into a macOS app.

**Configurability without custom code** is achieved via the OpenAI-compatible-API trick:
  Squawkbox's "OpenAI Whisper STT" provider accepts an arbitrary `base_url`,
  pointing at a local Whisper server (e.g.,
  [speaches](https://github.com/speaches-ai/speaches)
    — the unusual spelling is intentional; that is the project's actual name —
  whisper-asr-webservice, or LocalAI)
  that exposes `/v1/audio/transcriptions`.
Squawkbox thinks it's talking to OpenAI but it's actually hitting the Mac mini.
Zero code changes to the daemon.
The same pattern works for TTS: a local Piper or Kokoro server behind an
  OpenAI-compatible `/v1/audio/speech` endpoint.

**Streaming caveat:** cloud STT services like Deepgram emit partial transcripts
  during the user's utterance; local Whisper is predominantly batch
  (VAD detects end-of-utterance, then full-clip transcription).
That batch pass takes 0.5–1s on Apple Silicon, all of which is paid
  *after* the user stops talking, not during.
For Squawkbox's wait-heavy usage pattern this adds 200–500ms per turn vs. cloud streaming STT —
  noticeable but not ruinous, and arguably worth it for the cost and privacy wins.

**Cost impact at 1,500 min/mo:**

| Component | Cloud (current) | Local (Mac mini) | Savings |
|---|---|---|---|
| STT (Whisper API or gpt-4o-transcribe) | ~$3/mo | $0 | ~$3 |
| TTS (ElevenLabs Flash) | ~$22/mo | $0 (Piper or Kokoro) | ~$22 |
| **Total STT+TTS line items** | **~$25/mo** | **~$0** | **~$25/mo** |

STT alone is the smallest line item;
  the bigger wins from a full local STT+TTS migration are non-financial:
  privacy (no audio leaves the family network),
  no rate limits,
  no API key rotation,
  works offline if Tailscale is the only path,
  and one less third-party dependency.
The Squawkbox engineering design defers local providers to a later milestone
  to keep MVP integration risk low,
  but commits to the OpenAI-compatible-`base_url` shape so the migration is a config change.

## Decision Implications

The findings above directly informed the Squawkbox engineering design:

- **Outbound-only authentication** ([secure-voice-calls](../product-requirements/2026-05-08-secure-voice-calls.md),
    [outbound-call-trigger](../product-requirements/2026-05-08-outbound-call-trigger.md)).
  Finding 5 (Twilio is for telephony) plus the inability to authenticate inbound *PSTN* calls
    strongly enough for hands-free safety led to the choice of "Apple Shortcut → Squawkbox →
    outbound call to the operator" as the must-have authenticated voice path.
  Inbound PSTN calls are deferred indefinitely.
  One avenue worth revisiting later: authenticated inbound over SIP or WebRTC
    from a homelab-controlled client could sidestep PSTN caller-ID spoofing entirely
    (SIP digest auth or mutual TLS; WebRTC with a short-lived token),
    if mature, reliable homelab servers and iPhone clients exist for either.
    That is an open investigation, not a committed path.
- **Six-layer architecture** ([engineering design](../engineering-designs/2026-05-08-squawkbox-architecture.md)).
  Finding 9 is the conceptual scaffold for the entire engineering design.
  Each layer is swappable independently of the others.
- **MCP polling for MVP, Channels for end state.**
  Findings 11 and 12 establish that polling is acceptable for an MVP with low integration risk
    while Channels is the better end-state pattern.
  Both adapters are designed to live behind the same agent-adapter abstraction so the swap is
    contained, and the delivery plan includes a dedicated milestone for the Channels adapter.
- **Cloud STT/TTS for MVP, local for end state.**
  Finding 14 establishes that local providers are feasible and configurable without
    custom code via the `base_url` trick,
    so the MVP can de-risk integration with cloud and migrate cleanly later.
- **Orchestrator implementation left as an open decision.**
  Finding 10 establishes Pipecat as the obvious off-the-shelf orchestrator,
    and the real complexity is the orchestration logic (barge-in, streaming, lifecycle),
    not the number of transports.
  Rather than commit up front to hand-rolling this in Rust,
    the engineering design and delivery plan resolve it with an early bake-off spike:
    build the thinnest voice loop both ways (hand-rolled Rust vs. Pipecat),
    measure latency and effort, then commit.
- **Twilio as the MVP telephony provider.**
  Finding 13 (moltis PR #920 working reference) plus the maturity of Twilio's documentation
    led to choosing Twilio over Telnyx for MVP, with Telnyx queued as the obvious migration
    once costs warrant it.
- **Channels are not in the MVP.**
  Finding 8 establishes that voice does not require Channels.
  A future "Telegram pings my running session" feature would use Channels but is out of
    scope for the initial Squawkbox vision.

## References

External references that informed this analysis:

- Happy Coder repository: [github.com/slopus/happy](https://github.com/slopus/happy).
- Happy issue [#472](https://github.com/slopus/happy/issues/472): documentation request for ElevenLabs BYOA.
- Happy issue [#1032](https://github.com/slopus/happy/issues/1032): Direct Connection bug.
- ElevenLabs Agents pricing: [elevenlabs.io/pricing/agents](https://elevenlabs.io/pricing/agents).
- moltis: [github.com/moltis-org/moltis](https://github.com/moltis-org/moltis).
- moltis PR [#920](https://github.com/moltis-org/moltis/pull/920): telephony support.
- OpenClaw voice-call plugin: [docs.openclaw.ai/plugins/voice-call](https://docs.openclaw.ai/plugins/voice-call).
- Pipecat: [docs.pipecat.ai](https://docs.pipecat.ai).
- LiveKit Agents: [github.com/livekit/agents](https://github.com/livekit/agents).
- Anthropic Channels reference: [code.claude.com/docs/en/channels-reference](https://code.claude.com/docs/en/channels-reference).
- whisper.cpp Core ML / ANE support: [github.com/ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp).
- speaches local Whisper server: [github.com/speaches-ai/speaches](https://github.com/speaches-ai/speaches).
- NetworkChuck claude-phone: [github.com/theNetworkChuck/claude-phone](https://github.com/theNetworkChuck/claude-phone).
