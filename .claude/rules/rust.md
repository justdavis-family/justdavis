# Rust Conventions

Baseline conventions for Rust applications in this monorepo.
See the engineering design
  [Rust Application Conventions](/design/engineering-designs/2026-05-25-rust-application-conventions.md)
  for the rationale and trade-offs behind each choice.

## Baseline Facilities

Every Rust binary uses the same plumbing:

- **Logging**: `tracing` + `tracing-subscriber`.
  Format is TTY-aware — human-readable on a terminal, one JSON object per line when piped
    (so operators can use `jq`) — and forced with `--log-format auto|text|json`.
  Filter levels via `RUST_LOG` (`EnvFilter`).
  Write logs to stderr; keep stdout for the program's own output.
  Libraries emit events only; they never install a subscriber (only binaries configure logging).
- **Errors**: `thiserror` for library error types; `anyhow` at binary entry points.
  Keep these internal propagation errors distinct from serialized/wire error types,
    which are modeled explicitly as domain types.
- **CLI**: `clap` v4 with the derive API.
- **Signals**: long-running binaries handle `SIGINT` / `SIGTERM` via `signal-hook`
    for graceful shutdown (release sockets and other resources, then exit).

## Structure

- Keep logic and typed errors in a library crate; keep binaries thin.
- Initialize logging, parse arguments, and install signal handlers in `main`, not in libraries.

## Tooling

Formatting and linting are enforced by each project's `mise` `lint` task
  (`cargo fmt --check` and `cargo clippy` with warnings denied);
  see [`mise-conventions.md`](mise-conventions.md).
