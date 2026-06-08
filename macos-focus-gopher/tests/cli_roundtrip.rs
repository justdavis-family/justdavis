//! End-to-end: the real `focus-gopher` CLI binary connects to a running helper
//! over a Unix domain socket, prints the `FocusState` as pretty JSON on stdout,
//! and exits with the documented outcome-driven exit code. Mirrors the
//! in-process `tests/socket_roundtrip.rs` but drives the binary as a subprocess
//! via `assert_cmd`.
//!
//! The pipeline-touching `get_focus()` reads the host's real Focus database,
//! so the *value* it returns depends on the host environment (which Focus is
//! on, whether the helper has FDA, etc.). These tests assert the **contract**:
//! the CLI faithfully relays whatever `FocusState` the helper returns, with the
//! matching exit code. Deterministic value assertions live in `tests/parsing.rs`
//! which drives the pure parser against captured fixtures.

use assert_cmd::Command;
use macos_focus_gopher::focus;
use macos_focus_gopher::model::{FocusState, Outcome};
use macos_focus_gopher::{server, socket};
use std::io::{BufRead, BufReader, Write};
use std::thread;

#[test]
fn cli_round_trips_focus_state_and_exits_with_outcome_code() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("focus-gopher.sock");

    let listener = socket::bind(&path).unwrap();
    let server_thread = thread::spawn(move || server::serve_once(&listener).unwrap());

    let output = Command::cargo_bin("focus-gopher")
        .unwrap()
        .arg("--socket-path")
        .arg(&path)
        .output()
        .unwrap();
    server_thread.join().unwrap();

    // The exit code follows the outcome: 0 for `Determined`, 1 for `Failed`.
    let stdout = std::str::from_utf8(&output.stdout).expect("stdout is UTF-8");
    let printed: FocusState = serde_json::from_str(stdout)
        .unwrap_or_else(|e| panic!("stdout is not a valid FocusState ({e}); stdout={stdout}"));
    let expected_exit = match printed.outcome {
        Outcome::Determined(_) => 0,
        Outcome::Failed { .. } => 1,
    };
    assert_eq!(
        output.status.code(),
        Some(expected_exit),
        "exit code should agree with outcome (expected {expected_exit}); \
         outcome={:?}; stderr={}",
        printed.outcome,
        String::from_utf8_lossy(&output.stderr),
    );

    // The CLI faithfully relays whatever the helper returned. Compare the
    // printed FocusState to a fresh `get_focus()` call: both touch the same
    // host state so they should agree (unless host state changed between
    // calls — unlikely in a sub-second test window).
    assert_eq!(printed, focus::get_focus());

    // Pretty-printed: at least one internal newline (not just the trailing
    // one). Compact one-line JSON would only have the trailing newline, so a
    // future regression away from pretty-printing fails here.
    assert!(
        stdout.trim_end_matches('\n').contains('\n'),
        "stdout should be pretty-printed JSON; got: {stdout}",
    );
}

#[test]
fn cli_exits_with_transport_error_when_helper_unreachable() {
    let dir = tempfile::tempdir().unwrap();
    // A path inside an existing directory but with no helper bound to it.
    let path = dir.path().join("absent.sock");

    let output = Command::cargo_bin("focus-gopher")
        .unwrap()
        .arg("--socket-path")
        .arg(&path)
        .output()
        .unwrap();

    assert_eq!(
        output.status.code(),
        Some(2),
        "expected exit 2 (CLI/transport error); stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr),
    );
    assert!(
        output.stdout.is_empty(),
        "stdout should be empty on transport error; got: {}",
        String::from_utf8_lossy(&output.stdout),
    );
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("focus-gopher failed"),
        "stderr should describe the failure; got: {stderr}",
    );
}

#[test]
fn cli_exits_with_protocol_error_when_helper_replies_garbage() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("focus-gopher.sock");

    // Stand up an ad-hoc peer that accepts one connection, discards the
    // request line, and writes back well-formed JSON that doesn't deserialize
    // into a `FocusState`. The real helper would never do this; this guards
    // the CLI's behavior when the wire contract is violated — exit 2 (no
    // FocusState was obtained), nothing on stdout, diagnostic on stderr.
    let listener = socket::bind(&path).unwrap();
    let server_thread = thread::spawn(move || {
        let (stream, _) = listener.accept().unwrap();
        let mut reader = BufReader::new(stream.try_clone().unwrap());
        let mut request = String::new();
        reader.read_line(&mut request).unwrap();
        let mut writer = stream;
        writer.write_all(b"{\"not\":\"a focus state\"}\n").unwrap();
        writer.flush().unwrap();
    });

    let output = Command::cargo_bin("focus-gopher")
        .unwrap()
        .arg("--socket-path")
        .arg(&path)
        .output()
        .unwrap();
    server_thread.join().unwrap();

    assert_eq!(
        output.status.code(),
        Some(2),
        "expected exit 2 (protocol error); stdout={} stderr={}",
        String::from_utf8_lossy(&output.stdout),
        String::from_utf8_lossy(&output.stderr),
    );
    assert!(
        output.stdout.is_empty(),
        "stdout should be empty on protocol error; got: {}",
        String::from_utf8_lossy(&output.stdout),
    );
    let stderr = String::from_utf8_lossy(&output.stderr);
    assert!(
        stderr.contains("focus-gopher failed"),
        "stderr should describe the failure; got: {stderr}",
    );
}

#[test]
fn cli_help_includes_worked_examples() {
    let output = Command::cargo_bin("focus-gopher")
        .unwrap()
        .arg("--help")
        .output()
        .unwrap();

    assert!(
        output.status.success(),
        "--help should exit 0; status={:?} stderr={}",
        output.status,
        String::from_utf8_lossy(&output.stderr),
    );
    let stdout = String::from_utf8(output.stdout).expect("--help output is UTF-8");
    for needle in ["--socket-path", "Examples:", "Exit codes:"] {
        assert!(
            stdout.contains(needle),
            "--help should contain `{needle}`; got: {stdout}",
        );
    }
}
