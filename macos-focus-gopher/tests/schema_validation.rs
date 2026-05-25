//! Conformance to the published, versioned JSON Schema.
//!
//! Unique assurance: every shape (and the real `get_focus()` output) validates
//! against `schema/focus-state.v1.schema.json`, *and* the schema's `oneOf`
//! rejects structurally-incoherent documents (both `determined` + `failed`,
//! missing fields, an unknown error code). This guards both the published
//! external contract and the schema file itself — neither the serde tests nor
//! the byte-exact tests do that.
//!
//! Related but distinctly valuable suites (these three share only fixture data;
//! each asserts something the others do not):
//!   - `src/model.rs` unit tests — the serde mapping itself: structural
//!     (`Value`) equality, round-trip, the `ErrorCode` snake_case strings, and
//!     serde-layer rejection of malformed input.
//!   - `tests/json_shape.rs` — the byte-exact compact wire encoding (field order
//!     and whitespace) that a raw `nc`/`socat` consumer reads.

use macos_focus_gopher::focus::get_focus;
use macos_focus_gopher::model::{ErrorCode, Focus, FocusState, MacosCompatibility, Outcome};
use serde_json::{json, Value};

const SCHEMA_SRC: &str = include_str!("../schema/focus-state.v1.schema.json");

fn validator() -> jsonschema::Validator {
    let schema: Value = serde_json::from_str(SCHEMA_SRC).expect("schema must be valid JSON");
    jsonschema::validator_for(&schema).expect("schema must compile")
}

fn value(state: FocusState) -> Value {
    serde_json::to_value(state).unwrap()
}

#[test]
fn well_formed_focus_states_validate() {
    let validator = validator();
    let valid = vec![
        // (a) determined, focus on
        value(FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Determined(Focus::FocusOn {
                name: "Sleep".into(),
            }),
        }),
        // (b) determined, focus off
        value(FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Determined(Focus::FocusOff {}),
        }),
        // (c) determined on an unknown macOS version
        value(FocusState {
            macos_version: "26.0".into(),
            macos_compatibility: MacosCompatibility::Unknown {
                message: "please report whether this works".into(),
            },
            outcome: Outcome::Determined(Focus::FocusOn {
                name: "Do Not Disturb".into(),
            }),
        }),
        // (d) failed
        value(FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Failed {
                error: ErrorCode::FocusPermissionDenied,
                message: "Full Disk Access is required.".into(),
            },
        }),
        // the stub output itself
        serde_json::to_value(get_focus()).unwrap(),
    ];
    for v in valid {
        assert!(validator.is_valid(&v), "expected valid against schema: {v}");
    }
}

#[test]
fn incoherent_documents_are_rejected() {
    let validator = validator();
    let invalid = vec![
        // both `determined` and `failed` present
        json!({
            "macos_version": "15.5", "macos_compatibility": "supported",
            "determined": { "focus_off": {} },
            "failed": { "error": "internal_error", "message": "x" }
        }),
        // neither `determined` nor `failed`
        json!({ "macos_version": "15.5", "macos_compatibility": "supported" }),
        // `focus_on` without a name
        json!({
            "macos_version": "15.5", "macos_compatibility": "supported",
            "determined": { "focus_on": {} }
        }),
        // an error code outside the taxonomy
        json!({
            "macos_version": "15.5", "macos_compatibility": "supported",
            "failed": { "error": "not_a_real_code", "message": "x" }
        }),
        // missing the shared `macos_version`
        json!({ "macos_compatibility": "supported", "determined": { "focus_off": {} } }),
    ];
    for v in invalid {
        assert!(!validator.is_valid(&v), "expected rejected by schema: {v}");
    }
}
