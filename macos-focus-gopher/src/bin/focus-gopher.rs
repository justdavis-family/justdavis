//! The `focus-gopher` CLI. Stubbed for now (not yet wired up); the real client
//! will connect to the socket, perform `get_focus()`, print the `FocusState` as
//! JSON, and exit non-zero on a `failed` outcome.

use clap::Parser;
use macos_focus_gopher::logging::{self, LogFormat};
use std::path::PathBuf;

/// Query the Focus Gopher helper (early development; not yet wired up).
#[derive(Debug, Parser)]
#[command(name = "focus-gopher", version)]
struct Args {
    /// Socket path to query (default: `$TMPDIR/focus-gopher.sock`).
    #[arg(long)]
    socket_path: Option<PathBuf>,
    /// Log output format.
    #[arg(long, default_value = "auto")]
    log_format: LogFormat,
}

fn main() {
    let args = Args::parse();
    logging::init(args.log_format);
    tracing::warn!(
        socket_path = ?args.socket_path,
        "the focus-gopher CLI is not yet wired up; run focus-gopherd and speak the socket protocol directly (e.g. nc -U <socket>)"
    );
}
