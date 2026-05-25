//! End-to-end: a client connects to a running helper over a real Unix domain
//! socket and receives the (stubbed) `FocusState`, which validates against the
//! published JSON Schema. This is the project's headline deliverable right now.

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

#[test]
fn bind_leaves_an_existing_parent_directorys_permissions_alone() {
    // Regression guard: `bind` must not rewrite the permissions of a directory it
    // did not create (e.g. an override pointing into a shared dir like /tmp).
    let dir = tempfile::tempdir().unwrap();
    std::fs::set_permissions(dir.path(), std::fs::Permissions::from_mode(0o755)).unwrap();
    let path = dir.path().join("focus-gopher.sock");

    let _listener = socket::bind(&path).unwrap();

    let dir_mode = std::fs::metadata(dir.path()).unwrap().permissions().mode() & 0o777;
    assert_eq!(
        dir_mode, 0o755,
        "bind must not alter a pre-existing directory"
    );
}

#[test]
fn bind_creates_a_missing_parent_directory_as_user_only() {
    let dir = tempfile::tempdir().unwrap();
    let path = dir.path().join("nested").join("focus-gopher.sock");

    let _listener = socket::bind(&path).unwrap();

    let parent_mode = std::fs::metadata(path.parent().unwrap())
        .unwrap()
        .permissions()
        .mode()
        & 0o777;
    assert_eq!(parent_mode, 0o700, "a created socket dir must be user-only");
}
