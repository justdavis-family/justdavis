//! End-to-end: a client connects to a running helper over a real Unix domain
//! socket and receives a `FocusState` that validates against the published
//! JSON Schema. The *value* depends on the host environment (which Focus is
//! on, whether the helper has FDA); we assert the **contract** here. See
//! `tests/parsing.rs` for deterministic value assertions against captured
//! fixtures.

use macos_focus_gopher::focus::get_focus;
use macos_focus_gopher::{client, server, socket};
use serde_json::Value;
use std::os::unix::fs::PermissionsExt;
use std::thread;

const SCHEMA_SRC: &str = include_str!("../schema/focus-state.v1.schema.json");

#[test]
fn client_receives_well_formed_focus_state_over_socket() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("focus-gopher.sock");

    let listener = socket::bind(&path).unwrap();
    let server = thread::spawn(move || server::serve_once(&listener).unwrap());

    let state = client::get_focus(&path).unwrap();
    server.join().unwrap();

    // The helper handed back the stubbed state...
    assert_eq!(state, get_focus());

    // ...and it validates against the published schema.
    let schema: Value = serde_json::from_str(SCHEMA_SRC).unwrap();
    let validator = jsonschema::validator_for(&schema).unwrap();
    let value = serde_json::to_value(&state).unwrap();
    assert!(
        validator.is_valid(&value),
        "round-trip output not schema-valid: {value}"
    );
}

#[test]
fn bind_restricts_socket_to_owner() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("focus-gopher.sock");

    let _listener = socket::bind(&path).unwrap();

    let socket_mode = std::fs::metadata(&path).unwrap().permissions().mode() & 0o777;
    assert_eq!(socket_mode, 0o600, "socket should be user-only");
}
