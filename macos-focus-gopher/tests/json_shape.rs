//! Byte-exact wire encoding of the four canonical `FocusState` shapes from the
//! engineering design (examples a–d), exercised through the public crate API.
//!
//! Unique assurance: this pins the *exact compact bytes* a raw socket consumer
//! (`nc`/`socat` + `jq`) reads — field order and the absence of whitespace —
//! which the `Value`-equality comparisons in the `model.rs` unit tests cannot
//! catch (a reordering or reformatting would slip past them but fail here).
//!
//! Related but distinctly valuable suites (these three share only fixture data;
//! each asserts something the others do not):
//!   - `src/model.rs` unit tests — the serde mapping itself: structural
//!     (`Value`) equality, round-trip, the `ErrorCode` snake_case strings, and
//!     serde-layer rejection of malformed input.
//!   - `tests/schema_validation.rs` — conformance to the published JSON Schema,
//!     and that the schema rejects structurally-incoherent documents.

use macos_focus_gopher::model::{ErrorCode, Focus, FocusState, MacosCompatibility, Outcome};

fn compact(state: &FocusState) -> String {
    serde_json::to_string(state).unwrap()
}

#[test]
fn example_a_focus_on() {
    let state = FocusState {
        macos_version: "15.5".into(),
        macos_compatibility: MacosCompatibility::Supported,
        outcome: Outcome::Determined(Focus::FocusOn {
            name: "Sleep".into(),
        }),
    };
    assert_eq!(
        compact(&state),
        r#"{"macos_version":"15.5","macos_compatibility":"supported","determined":{"focus_on":{"name":"Sleep"}}}"#
    );
}

#[test]
fn example_b_focus_off() {
    let state = FocusState {
        macos_version: "15.5".into(),
        macos_compatibility: MacosCompatibility::Supported,
        outcome: Outcome::Determined(Focus::FocusOff {}),
    };
    assert_eq!(
        compact(&state),
        r#"{"macos_version":"15.5","macos_compatibility":"supported","determined":{"focus_off":{}}}"#
    );
}

#[test]
fn example_c_unknown_compatibility() {
    let state = FocusState {
        macos_version: "26.0".into(),
        macos_compatibility: MacosCompatibility::Unknown {
            message: "please report".into(),
        },
        outcome: Outcome::Determined(Focus::FocusOn {
            name: "Do Not Disturb".into(),
        }),
    };
    assert_eq!(
        compact(&state),
        r#"{"macos_version":"26.0","macos_compatibility":{"unknown":{"message":"please report"}},"determined":{"focus_on":{"name":"Do Not Disturb"}}}"#
    );
}

#[test]
fn example_d_failed() {
    let state = FocusState {
        macos_version: "15.5".into(),
        macos_compatibility: MacosCompatibility::Supported,
        outcome: Outcome::Failed {
            error: ErrorCode::FocusPermissionDenied,
            message: "Full Disk Access is required.".into(),
        },
    };
    assert_eq!(
        compact(&state),
        r#"{"macos_version":"15.5","macos_compatibility":"supported","failed":{"error":"focus_permission_denied","message":"Full Disk Access is required."}}"#
    );
}
