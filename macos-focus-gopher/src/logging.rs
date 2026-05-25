//! Structured logging setup, per the Rust application conventions
//! (`.claude/rules/rust.md`).
//!
//! A binary calls [`init`] exactly once from `main`; the rest of the library only
//! emits `tracing` events and never installs a subscriber itself.

use clap::ValueEnum;
use std::io::IsTerminal;

/// How log records are formatted on stderr.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, ValueEnum)]
pub enum LogFormat {
    /// Human-readable on a terminal; JSON when stderr is piped or redirected.
    #[default]
    Auto,
    /// Always human-readable.
    Text,
    /// Always one JSON object per line (parseable with `jq`).
    Json,
}

/// Install the global `tracing` subscriber. Call once, from a binary's `main`.
///
/// Levels are filtered via `RUST_LOG` (`EnvFilter`), defaulting to `info`.
/// Records go to stderr, leaving stdout for a program's own output.
pub fn init(format: LogFormat) {
    let filter = tracing_subscriber::EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info"));
    let as_json = match format {
        LogFormat::Json => true,
        LogFormat::Text => false,
        LogFormat::Auto => !std::io::stderr().is_terminal(),
    };

    let builder = tracing_subscriber::fmt()
        .with_env_filter(filter)
        .with_writer(std::io::stderr);
    if as_json {
        builder.json().init();
    } else {
        builder.init();
    }
}
