# Rust Application Conventions

## Overview

Every Rust binary in this monorepo needs the same baseline plumbing — logging, error handling,
  command-line parsing, and signal handling — and those choices should be consistent across projects
  rather than re-decided each time.
This document fixes that baseline and the conventions for using it.

It is a **cross-cutting** engineering design: it is not tied to a single product requirement
  (per the engineering-designs README, codebase-wide technical decisions are valid design material),
  and it should be applied by every Rust project here.
The enforceable, terse summary lives in [`.claude/rules/rust.md`](/.claude/rules/rust.md);
  this document is the rationale and the trade-offs behind it.

These are near-consensus community choices, so no separate analysis document precedes this design;
  the rationale is captured inline per choice below.

## Technology Choices

### Logging and diagnostics: `tracing` + `tracing-subscriber`

Use [`tracing`](https://docs.rs/tracing) for instrumentation (structured events and spans)
  and [`tracing-subscriber`](https://docs.rs/tracing-subscriber) to configure output in the binary.

- **Output format is TTY-aware by default.**
  When stderr is a terminal (interactive use) emit human-readable text;
    when it is not (piped or redirected) emit one JSON object per line,
    so operators can parse the stream with `jq`.
  A `--log-format <auto|text|json>` flag forces a format; `auto` is the default.
- **Level filtering** uses `tracing_subscriber`'s `EnvFilter`, honoring the `RUST_LOG` environment
    variable; a `--log-level` flag may layer a convenience over it.
- **Logs go to stderr**, leaving stdout for a program's actual output
    (for example, a CLI printing a JSON result).
- **Libraries emit events but never install a subscriber** — only binaries configure logging.

Rationale: `tracing` is the de-facto standard, is structured and span-aware (carrying context across
  call boundaries), and has the strongest momentum.
JSON output is machine-parseable for operators, and a TTY-aware default serves both interactive
  developers and production operators with no configuration.

### Error handling: `thiserror` for libraries, `anyhow` for binaries

- **Library crates** define typed error enums with [`thiserror`](https://docs.rs/thiserror),
    so callers can match on specific variants.
- **Binary entry points** use [`anyhow`](https://docs.rs/anyhow) for ergonomic propagation (`?`),
    added context (`.context(...)`), and a clean non-zero exit.
- Keep these *internal propagation* errors distinct from any **serialized or wire** error type that is
    part of a public API contract (for example, an error enum that appears in a published JSON Schema):
    those are modeled explicitly as domain types, per
    [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md).

Rationale: this is the community-standard split — typed errors where consumers need to branch,
  ergonomic any-error where they only need to propagate and report.

### Command-line parsing: `clap` (derive)

Use [`clap`](https://docs.rs/clap) v4 with the derive API.
It gives consistent parsing and validation, and `--help` / `--version` nearly for free.

Rationale: the de-facto standard, with ergonomic derive macros and good help output.
Its heavier compile time (versus minimal parsers) is accepted for the features and consistency,
  and is mitigated by CI dependency caching.

### Signal handling: `signal-hook`

Long-running binaries (daemons and servers) install handlers for `SIGINT` and `SIGTERM` via
  [`signal-hook`](https://docs.rs/signal-hook) to shut down gracefully — releasing resources such as
  sockets or lock files — and then exit.

Rationale: simple and well-maintained, and it works without an async runtime (these are blocking,
  synchronous binaries).
It avoids hand-rolled `unsafe` `sigaction` calls.

## Architecture

The standard shape of a Rust executable here:

- A **library crate** holds the logic and its typed (`thiserror`) errors and emits `tracing` events;
    the **binary crate(s)** are thin.
- `main` parses arguments (`clap`), initializes logging (`tracing-subscriber`, TTY-aware),
    installs signal handlers (`signal-hook`) when the process is long-running,
    runs the work, and maps any error to an exit code via `anyhow`.
- Logging is configured exactly once, in the binary; libraries never configure it.

This keeps the policy decisions (how to log, how to exit, how to parse args) in the binary,
  and the reusable behavior — including the events worth logging — in the library.

## Configuration

- `RUST_LOG` — level and target filtering, in `EnvFilter` syntax.
- `--log-format auto|text|json` — output format; `auto` (the default) is text on a TTY, JSON otherwise.
- `--log-level` — an optional convenience over `RUST_LOG`.
- Diagnostic logs are written to stderr; a program's results are written to stdout.

## Trade-offs

- **Logging:** `log` + `env_logger` is simpler but unstructured and span-less; `slog` has waning
    momentum. `tracing` is chosen for structure, spans, and ecosystem support, at the cost of a
    slightly larger dependency footprint.
- **Errors:** `snafu` offers more features but more ceremony; `anyhow` everywhere would lose the typed
    errors libraries should expose; hand-rolled enums are boilerplate. `thiserror` + `anyhow` is the
    lean, standard division of labor.
- **CLI:** `argh`, `lexopt`, and `pico-args` are lighter and compile faster but offer fewer features
    and less consistent UX. `clap` is chosen for features and ubiquity; the compile cost is mitigated
    by caching.
- **Signals:** raw `sigaction` requires `unsafe`; `ctrlc` is narrower; tokio's signal handling needs
    an async runtime. `signal-hook` fits synchronous binaries.

## Success Criteria

- A new Rust binary uses `tracing` + `tracing-subscriber` (TTY-aware, JSON when piped),
    `thiserror` (library) + `anyhow` (binary), `clap` (derive),
    and `signal-hook` when it is long-running.
- Piped logs are valid JSON (parseable with `jq`); interactive logs are human-readable;
    `--log-format` forces either.
- Library crates contain no subscriber initialization and no `anyhow` in their public APIs.
- Long-running binaries exit cleanly on `SIGINT` / `SIGTERM`, releasing their resources.

## References

- **Enforceable rule**: [`.claude/rules/rust.md`](/.claude/rules/rust.md).
- **Engineering Principles**:
    [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md);
    [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md);
    [YAGNI](../engineering-principles/2026-01-06-yagni.md).
- **Crates**: [`tracing`](https://docs.rs/tracing), [`tracing-subscriber`](https://docs.rs/tracing-subscriber),
    [`thiserror`](https://docs.rs/thiserror), [`anyhow`](https://docs.rs/anyhow),
    [`clap`](https://docs.rs/clap), [`signal-hook`](https://docs.rs/signal-hook).
- This is a cross-cutting design with no single product requirement; it applies to all Rust projects
    in this repository.
