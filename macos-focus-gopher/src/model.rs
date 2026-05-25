//! The `FocusState` wire model: the single fixed-schema object returned by
//! `get_focus()`. See `design/engineering-designs/2026-05-12-macos-focus-gopher.md`.
//!
//! The wire shape mirrors the internal sum type rather than flattening it onto a
//! bag of nullable siblings, so invalid combinations are unrepresentable in code
//! *and* on the wire (the published JSON Schema's `oneOf` enforces the same at
//! the boundary). See `design/analyses/2026-05-12-focus-state-json-shape.md`.

use serde::{Deserialize, Serialize};

/// The single fixed-schema object returned by `get_focus()`.
///
/// `outcome` is `#[serde(flatten)]`ed so its variant key (`determined` /
/// `failed`) appears at the top level alongside the shared metadata.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct FocusState {
    /// The detected macOS version, e.g. `"15.5"`.
    pub macos_version: String,
    pub macos_compatibility: MacosCompatibility,
    #[serde(flatten)]
    pub outcome: Outcome,
}

/// Whether the running macOS version is on the known-compatibility list.
///
/// Externally tagged: `"supported"` | `"unsupported"` | `{ "unknown": { "message": … } }`.
/// Whether parsing actually worked is conveyed by [`Outcome`], not by this field.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum MacosCompatibility {
    Supported,
    Unsupported,
    Unknown { message: String },
}

/// The outcome of the focus lookup. Externally tagged: `"determined"` | `"failed"`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Outcome {
    /// The helper determined the state; the value is itself a tagged union.
    Determined(Focus),
    /// The helper could not determine the state. Carries a stable machine-readable
    /// `error` code plus a human-readable `message` with guidance for that error.
    Failed { error: ErrorCode, message: String },
}

/// A determined focus state. Externally tagged: `"focus_on"` | `"focus_off"`.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Focus {
    /// A Focus is active; carries its human-readable name (always present — an
    /// active-but-unnameable Focus is reported as [`ErrorCode::FocusNameUnresolved`]).
    FocusOn { name: String },
    /// No Focus is active. Serializes to an empty object `{}` (a struct variant,
    /// *not* a unit variant, so the wire form is `{"focus_off":{}}`).
    FocusOff {},
}

/// Stable, machine-readable failure codes. `snake_case` on the wire.
///
/// New codes may be added over time; existing codes are never repurposed.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum ErrorCode {
    /// The Focus database exists but access was denied (an `EPERM` on `open()`),
    /// overwhelmingly meaning the helper lacks Full Disk Access.
    FocusPermissionDenied,
    /// A required database file is missing or unreadable for a non-permission reason.
    FocusDbUnreadable,
    /// A database file exists but is not parseable (truncated/partial write, invalid JSON).
    FocusDbMalformed,
    /// The file parsed as JSON but its structure matches no known schema.
    SchemaUnknown,
    /// An active Focus was detected but its identifier could not be mapped to a name.
    FocusNameUnresolved,
    /// The running macOS version is explicitly marked unsupported.
    MacosUnsupported,
    /// An unexpected helper-side failure.
    InternalError,
}

#[cfg(test)]
mod tests {
    // These tests cover the serde mapping of the model types themselves: that our
    // derives and attributes (`flatten`, `rename_all`, the empty-struct
    // `FocusOff {}`) produce the intended structure and round-trip faithfully, that
    // every `ErrorCode` renders to the right snake_case string, and that malformed
    // input is rejected at the serde layer. Comparisons are by `serde_json::Value`,
    // so they are order-insensitive.
    //
    // Related but distinctly valuable suites (these three share only fixture data;
    // each asserts something the others do not):
    //   - `tests/json_shape.rs` — the byte-exact compact wire encoding (field order
    //     and whitespace), which the `Value`-equality comparisons here cannot catch.
    //   - `tests/schema_validation.rs` — conformance to the published JSON Schema,
    //     and that the schema rejects structurally-incoherent documents.
    use super::*;
    use serde_json::json;

    // The four canonical response shapes from the engineering design (examples a–d).

    fn focus_on_state() -> FocusState {
        FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Determined(Focus::FocusOn {
                name: "Sleep".into(),
            }),
        }
    }

    fn focus_off_state() -> FocusState {
        FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Determined(Focus::FocusOff {}),
        }
    }

    fn unknown_compatibility_state() -> FocusState {
        FocusState {
            macos_version: "26.0".into(),
            macos_compatibility: MacosCompatibility::Unknown {
                message: "macOS 26.0 is not on the known-supported list.".into(),
            },
            outcome: Outcome::Determined(Focus::FocusOn {
                name: "Do Not Disturb".into(),
            }),
        }
    }

    fn failed_state() -> FocusState {
        FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Failed {
                error: ErrorCode::FocusPermissionDenied,
                message: "Full Disk Access is required.".into(),
            },
        }
    }

    #[test]
    fn serialize_focus_on() {
        assert_eq!(
            serde_json::to_value(focus_on_state()).unwrap(),
            json!({
                "macos_version": "15.5",
                "macos_compatibility": "supported",
                "determined": { "focus_on": { "name": "Sleep" } }
            })
        );
    }

    #[test]
    fn serialize_focus_off() {
        assert_eq!(
            serde_json::to_value(focus_off_state()).unwrap(),
            json!({
                "macos_version": "15.5",
                "macos_compatibility": "supported",
                "determined": { "focus_off": {} }
            })
        );
    }

    #[test]
    fn serialize_unknown_compatibility() {
        assert_eq!(
            serde_json::to_value(unknown_compatibility_state()).unwrap(),
            json!({
                "macos_version": "26.0",
                "macos_compatibility": {
                    "unknown": { "message": "macOS 26.0 is not on the known-supported list." }
                },
                "determined": { "focus_on": { "name": "Do Not Disturb" } }
            })
        );
    }

    #[test]
    fn serialize_failed() {
        assert_eq!(
            serde_json::to_value(failed_state()).unwrap(),
            json!({
                "macos_version": "15.5",
                "macos_compatibility": "supported",
                "failed": {
                    "error": "focus_permission_denied",
                    "message": "Full Disk Access is required."
                }
            })
        );
    }

    #[test]
    fn error_codes_serialize_to_snake_case() {
        let cases = [
            (ErrorCode::FocusPermissionDenied, "focus_permission_denied"),
            (ErrorCode::FocusDbUnreadable, "focus_db_unreadable"),
            (ErrorCode::FocusDbMalformed, "focus_db_malformed"),
            (ErrorCode::SchemaUnknown, "schema_unknown"),
            (ErrorCode::FocusNameUnresolved, "focus_name_unresolved"),
            (ErrorCode::MacosUnsupported, "macos_unsupported"),
            (ErrorCode::InternalError, "internal_error"),
        ];
        for (code, expected) in cases {
            assert_eq!(serde_json::to_value(code).unwrap(), json!(expected));
        }
    }

    #[test]
    fn all_examples_round_trip() {
        for state in [
            focus_on_state(),
            focus_off_state(),
            unknown_compatibility_state(),
            failed_state(),
        ] {
            let encoded = serde_json::to_string(&state).unwrap();
            let decoded: FocusState = serde_json::from_str(&encoded).unwrap();
            assert_eq!(decoded, state);
        }
    }

    // Note: an outcome carrying *both* `determined` and `failed` is illegal, but
    // `#[serde(flatten)]` over an externally-tagged enum does not reject it at the
    // serde layer — the published JSON Schema's `oneOf` is the wire-level guard for
    // that coherence, exercised in `tests/schema_validation.rs`. In code, the
    // `Outcome` enum already makes the combination unconstructable.

    #[test]
    fn deserialize_rejects_focus_on_without_name() {
        let missing_name = json!({
            "macos_version": "15.5",
            "macos_compatibility": "supported",
            "determined": { "focus_on": {} }
        });
        assert!(serde_json::from_value::<FocusState>(missing_name).is_err());
    }
}
