//! End-to-end: the real `focus-gopher` CLI binary connects to a running helper
//! over a Unix domain socket, prints the (stubbed) `FocusState` as pretty JSON
//! on stdout, and exits with the documented outcome-driven exit code. Mirrors
//! the in-process `tests/socket_roundtrip.rs` but drives the binary as a
//! subprocess via `assert_cmd`.

use assert_cmd::Command;
use macos_focus_gopher::focus;
use macos_focus_gopher::model::{FocusState, Outcome};
use macos_focus_gopher::{server, socket};
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

    // The stubbed get_focus() returns a `failed` outcome, so the CLI exits 1.
    assert_eq!(
        output.status.code(),
        Some(1),
        "expected exit 1 (failed outcome); stderr={}",
        String::from_utf8_lossy(&output.stderr),
    );

    // stdout is the pretty-printed FocusState; parse it and compare to the
    // canonical stub to prove the CLI faithfully round-tripped the data.
    let stdout = std::str::from_utf8(&output.stdout).expect("stdout is UTF-8");
    let printed: FocusState = serde_json::from_str(stdout)
        .unwrap_or_else(|e| panic!("stdout is not a valid FocusState ({e}); stdout={stdout}"));
    assert_eq!(printed, focus::get_focus());
    assert!(
        matches!(printed.outcome, Outcome::Failed { .. }),
        "stub outcome should be `failed`; got {:?}",
        printed.outcome,
    );

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
    for needle in ["--socket-path", "Examples:", "focus-state.v1.schema.json"] {
        assert!(
            stdout.contains(needle),
            "--help should contain `{needle}`; got: {stdout}",
        );
    }
}
