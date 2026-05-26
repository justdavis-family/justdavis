//! The `focus-gopher` CLI: connects to the helper's per-user socket, performs
//! one `get_focus()` request, pretty-prints the returned `FocusState` as JSON
//! on stdout, and exits with an outcome-driven code so shell scripts can branch
//! without parsing the JSON. Most behavior lives in the library; this binary is
//! glue (parse args, init logging, dispatch).

use anyhow::Context;
use clap::Parser;
use macos_focus_gopher::client;
use macos_focus_gopher::logging::{self, LogFormat};
use macos_focus_gopher::model::{FocusState, Outcome};
use macos_focus_gopher::socket;
use std::io::Write;
use std::path::PathBuf;
use std::process::ExitCode;

/// Exit code returned when the CLI itself could not obtain a `FocusState` —
/// helper not running, socket unreachable, malformed reply, etc. Distinct from
/// the `failed` outcome (exit 1) so scripts can branch on it.
const EXIT_CLI_ERROR: u8 = 2;

/// Query the Focus Gopher helper for the current Focus / Do Not Disturb state.
///
/// Connects to the per-user Unix domain socket, performs `get_focus()`, and
/// pretty-prints the resulting `FocusState` JSON on stdout. Logs go to stderr.
#[derive(Debug, Parser)]
#[command(name = "focus-gopher", version, after_help = AFTER_HELP)]
struct Args {
    /// Socket path to query (default: `$TMPDIR/focus-gopher.sock`).
    #[arg(long)]
    socket_path: Option<PathBuf>,
    /// Log output format.
    #[arg(long, default_value = "auto")]
    log_format: LogFormat,
}

const AFTER_HELP: &str = "\
Exit codes:
  0  outcome is `determined` (a FocusState was successfully read)
  1  outcome is `failed` (the helper returned an explicit error code and
     guidance message in the printed FocusState)
  2  the CLI could not obtain a FocusState at all (helper not running, socket
     unreachable, malformed reply, ...); nothing is printed on stdout and a
     diagnostic is logged to stderr

Examples:
  # Print the current FocusState as pretty JSON on stdout (default socket).
  focus-gopher

  # Query a non-default socket path.
  focus-gopher --socket-path /custom/path/focus-gopher.sock

  # Branch on the exit code in a shell script.
  if state=$(focus-gopher); then
    echo \"got: $state\"
  else
    echo \"exit $?: see stderr for details\" >&2
  fi

The printed FocusState conforms to the published JSON Schema at
`macos-focus-gopher/schema/focus-state.v1.schema.json`. This CLI is a thin
client for the `focus-gopherd` helper daemon; see the project README for the
socket protocol and helper installation.";

fn main() -> ExitCode {
    let args = Args::parse();
    logging::init(args.log_format);
    match run(args) {
        Ok(code) => ExitCode::from(code),
        Err(e) => {
            tracing::error!(error = format!("{e:#}"), "focus-gopher failed");
            ExitCode::from(EXIT_CLI_ERROR)
        }
    }
}

fn run(args: Args) -> anyhow::Result<u8> {
    let path = match args.socket_path {
        Some(path) => path,
        None => socket::socket_path().context("determining the socket path")?,
    };
    let state = client::get_focus(&path)
        .with_context(|| format!("querying the helper at {}", path.display()))?;
    print_state(&state).context("writing the FocusState to stdout")?;
    Ok(match state.outcome {
        Outcome::Determined(_) => 0,
        Outcome::Failed { .. } => 1,
    })
}

/// Pretty-print `state` as JSON on stdout, with a trailing newline. A
/// `BrokenPipe` (the reader closed stdout — e.g. `focus-gopher | head`) is
/// treated as success: every byte we could deliver was delivered.
fn print_state(state: &FocusState) -> std::io::Result<()> {
    let mut json = serde_json::to_string_pretty(state).expect("FocusState is always serializable");
    json.push('\n');
    let mut stdout = std::io::stdout().lock();
    swallow_broken_pipe(stdout.write_all(json.as_bytes()))?;
    swallow_broken_pipe(stdout.flush())
}

fn swallow_broken_pipe(r: std::io::Result<()>) -> std::io::Result<()> {
    match r {
        Err(e) if e.kind() == std::io::ErrorKind::BrokenPipe => Ok(()),
        other => other,
    }
}
