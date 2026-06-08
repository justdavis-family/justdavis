//! The Focus Gopher helper daemon: binds the per-user socket and serves
//! `get_focus()` requests against the live macOS Focus database.

use anyhow::Context;
use clap::Parser;
use macos_focus_gopher::logging::{self, LogFormat};
use macos_focus_gopher::{server, socket};
use signal_hook::consts::{SIGINT, SIGTERM};
use signal_hook::iterator::Signals;
use std::path::PathBuf;
use std::process::ExitCode;

/// Serve the current Focus state over a per-user Unix domain socket.
#[derive(Debug, Parser)]
#[command(name = "focus-gopherd", version)]
struct Args {
    /// Socket path to bind (default: `$TMPDIR/focus-gopher.sock`).
    #[arg(long)]
    socket_path: Option<PathBuf>,
    /// Log output format.
    #[arg(long, default_value = "auto")]
    log_format: LogFormat,
}

fn main() -> ExitCode {
    let args = Args::parse();
    logging::init(args.log_format);
    match run(args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            tracing::error!(error = format!("{e:#}"), "focus-gopherd failed");
            ExitCode::FAILURE
        }
    }
}

fn run(args: Args) -> anyhow::Result<()> {
    let path = match args.socket_path {
        Some(path) => path,
        None => socket::socket_path().context("determining the socket path")?,
    };

    let listener = socket::bind(&path).with_context(|| format!("binding {}", path.display()))?;
    install_signal_cleanup(path.clone()).context("installing signal handlers")?;

    tracing::info!(socket = %path.display(), "listening");

    server::serve(&listener).context("serving connections")?;
    Ok(())
}

/// Spawn a thread that, on `SIGINT` / `SIGTERM`, removes the socket and exits —
/// so the helper leaves no stale socket behind on a clean shutdown.
fn install_signal_cleanup(socket_path: PathBuf) -> anyhow::Result<()> {
    let mut signals = Signals::new([SIGINT, SIGTERM])?;
    std::thread::spawn(move || {
        if let Some(signal) = signals.forever().next() {
            tracing::info!(
                signal,
                "received shutdown signal; removing socket and exiting"
            );
            let _ = std::fs::remove_file(&socket_path);
            std::process::exit(0);
        }
    });
    Ok(())
}
