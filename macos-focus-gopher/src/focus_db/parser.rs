//! Pure parser for the two Focus database files.
//!
//! Pure: takes string bodies, returns a [`Focus`] or [`ParseFailure`]. No I/O,
//! no environment access, no `Command`. That keeps the parser trivially
//! testable from fixture strings and lets the I/O concerns (`EPERM` mapping,
//! file location) live entirely in [`super::reader`].
//!
//! The macOS Focus database format is undocumented; see
//! `design/analyses/2026-05-12-macos-focus-db-format.md` for the shape this
//! parser is written against.

use serde_json::Value;
use thiserror::Error;

use super::identifiers::builtin_name;
use crate::model::Focus;

/// A failure to interpret the Focus database files.
///
/// Internal to the library; `get_focus()` maps these into wire-level
/// [`crate::model::ErrorCode`] values.
#[derive(Debug, Error)]
pub enum ParseFailure {
    /// A file's body is not valid JSON.
    #[error("Focus database file {file:?} is not valid JSON: {source}")]
    Malformed {
        /// Which file failed (`"Assertions.json"` or `"ModeConfigurations.json"`).
        file: &'static str,
        /// Underlying serde error.
        #[source]
        source: serde_json::Error,
    },

    /// A file's body is structurally JSON but does not match any known shape.
    /// `where_at` names the file and the path within it that failed, for log
    /// and message diagnostics.
    #[error("Focus database schema not recognized: {where_at}")]
    SchemaUnknown {
        /// A short, PII-free description of which file/path looked wrong.
        where_at: &'static str,
    },

    /// An active Focus identifier was found but could not be resolved to a
    /// human-readable name (neither in [`builtin_name`] nor in
    /// `ModeConfigurations.json`).
    #[error("active Focus identifier {0:?} could not be mapped to a name")]
    NameUnresolved(String),
}

/// Parse the bodies of `Assertions.json` and `ModeConfigurations.json` into a
/// wire-level [`Focus`].
pub fn parse_focus(assertions: &str, mode_configurations: &str) -> Result<Focus, ParseFailure> {
    let assertion_id = parse_active_identifier(assertions)?;

    let Some(identifier) = assertion_id else {
        return Ok(Focus::FocusOff {});
    };

    let name = resolve_name(&identifier, mode_configurations)?;
    Ok(Focus::FocusOn { name })
}

/// Returns the active Focus identifier from `Assertions.json`, or `None` if no
/// Focus is currently asserted.
fn parse_active_identifier(assertions: &str) -> Result<Option<String>, ParseFailure> {
    let trimmed = assertions.trim();
    if trimmed.is_empty() {
        // An empty file is the documented "Focus is off" representation.
        return Ok(None);
    }

    let root: Value = serde_json::from_str(trimmed).map_err(|source| ParseFailure::Malformed {
        file: "Assertions.json",
        source,
    })?;

    // Schema rules:
    //   - root must be an object;
    //   - root.data, if present, must be an array;
    //   - data[0], if present, must be an object.
    // A *missing* `data` (or empty `data` array, or `data[0]` lacking
    // `storeAssertionRecords`) is the "Focus off" state, not a schema error.
    let Some(data) = root.get("data") else {
        return Ok(None);
    };
    let Some(records_holder) = data
        .as_array()
        .ok_or(ParseFailure::SchemaUnknown {
            where_at: "Assertions.json: `data` is not an array",
        })?
        .first()
    else {
        return Ok(None);
    };
    let records_holder = records_holder
        .as_object()
        .ok_or(ParseFailure::SchemaUnknown {
            where_at: "Assertions.json: `data[0]` is not an object",
        })?;

    let Some(records) = records_holder.get("storeAssertionRecords") else {
        return Ok(None);
    };
    let records = records.as_array().ok_or(ParseFailure::SchemaUnknown {
        where_at: "Assertions.json: `storeAssertionRecords` is not an array",
    })?;
    let Some(first) = records.first() else {
        return Ok(None);
    };

    // Extract the active mode identifier. Its absence here (when a record
    // exists) is a schema error, not a "Focus off" state.
    let identifier = first
        .get("assertionDetails")
        .and_then(|v| v.get("assertionDetailsModeIdentifier"))
        .and_then(|v| v.as_str())
        .ok_or(ParseFailure::SchemaUnknown {
            where_at: "Assertions.json: \
                       `storeAssertionRecords[0].assertionDetails.assertionDetailsModeIdentifier` \
                       missing or not a string",
        })?;

    Ok(Some(identifier.to_string()))
}

/// Resolve a Focus identifier to its display name.
///
/// Tries the built-in table first; falls back to `ModeConfigurations.json`'s
/// `data[0].modeConfigurations[<id>].mode.name`.
fn resolve_name(identifier: &str, mode_configurations: &str) -> Result<String, ParseFailure> {
    if let Some(name) = builtin_name(identifier) {
        return Ok(name.to_string());
    }

    let trimmed = mode_configurations.trim();
    if trimmed.is_empty() {
        return Err(ParseFailure::NameUnresolved(identifier.to_string()));
    }

    let root: Value = serde_json::from_str(trimmed).map_err(|source| ParseFailure::Malformed {
        file: "ModeConfigurations.json",
        source,
    })?;

    // Navigate root.data[0].modeConfigurations[<id>].mode.name.
    let name = root
        .get("data")
        .and_then(|v| v.as_array())
        .and_then(|a| a.first())
        .and_then(|v| v.get("modeConfigurations"))
        .and_then(|v| v.get(identifier))
        .and_then(|v| v.get("mode"))
        .and_then(|v| v.get("name"))
        .and_then(|v| v.as_str());

    match name {
        Some(name) => Ok(name.to_string()),
        None => Err(ParseFailure::NameUnresolved(identifier.to_string())),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    const EMPTY_CONFIGS: &str = "{}";

    #[test]
    fn empty_body_is_focus_off() {
        assert!(matches!(
            parse_focus("", EMPTY_CONFIGS),
            Ok(Focus::FocusOff {})
        ));
        assert!(matches!(
            parse_focus("   \n\t", EMPTY_CONFIGS),
            Ok(Focus::FocusOff {})
        ));
    }

    #[test]
    fn empty_object_is_focus_off() {
        assert!(matches!(
            parse_focus("{}", EMPTY_CONFIGS),
            Ok(Focus::FocusOff {})
        ));
    }

    #[test]
    fn empty_data_array_is_focus_off() {
        assert!(matches!(
            parse_focus(r#"{"data": []}"#, EMPTY_CONFIGS),
            Ok(Focus::FocusOff {})
        ));
    }

    #[test]
    fn no_store_assertion_records_is_focus_off() {
        assert!(matches!(
            parse_focus(
                r#"{"data": [{"storeInvalidationRecords": []}]}"#,
                EMPTY_CONFIGS
            ),
            Ok(Focus::FocusOff {})
        ));
    }

    #[test]
    fn empty_store_assertion_records_is_focus_off() {
        assert!(matches!(
            parse_focus(
                r#"{"data": [{"storeAssertionRecords": []}]}"#,
                EMPTY_CONFIGS
            ),
            Ok(Focus::FocusOff {})
        ));
    }

    #[test]
    fn malformed_assertions_returns_malformed() {
        let result = parse_focus(r#"{"not json"#, EMPTY_CONFIGS);
        match result {
            Err(ParseFailure::Malformed { file, .. }) => {
                assert_eq!(file, "Assertions.json");
            }
            other => panic!("expected Malformed, got {other:?}"),
        }
    }

    #[test]
    fn unrecognized_shape_returns_schema_unknown() {
        let result = parse_focus(r#"{"unexpected": "shape"}"#, EMPTY_CONFIGS);
        // `data` is missing → focus_off (a missing key is the "off" state, not a
        // schema error). This documents the rule.
        assert!(matches!(result, Ok(Focus::FocusOff {})));

        // But a structurally-wrong `data` is a schema error.
        let result = parse_focus(r#"{"data": "not an array"}"#, EMPTY_CONFIGS);
        assert!(matches!(result, Err(ParseFailure::SchemaUnknown { .. })));

        // …and so is an assertion record without an identifier.
        let result = parse_focus(
            r#"{"data": [{"storeAssertionRecords": [{"assertionDetails": {}}]}]}"#,
            EMPTY_CONFIGS,
        );
        assert!(matches!(result, Err(ParseFailure::SchemaUnknown { .. })));
    }

    #[test]
    fn builtin_identifier_resolves_without_mode_configurations() {
        // `ModeConfigurations.json` is empty, but the built-in table covers DND.
        let assertions = r#"{"data":[{"storeAssertionRecords":[{"assertionDetails":{"assertionDetailsModeIdentifier":"com.apple.donotdisturb.mode.default"}}]}]}"#;
        match parse_focus(assertions, EMPTY_CONFIGS) {
            Ok(Focus::FocusOn { name }) => assert_eq!(name, "Do Not Disturb"),
            other => panic!("expected FocusOn(Do Not Disturb), got {other:?}"),
        }
    }

    #[test]
    fn user_identifier_resolves_via_mode_configurations() {
        let assertions = r#"{"data":[{"storeAssertionRecords":[{"assertionDetails":{"assertionDetailsModeIdentifier":"com.example.user-focus"}}]}]}"#;
        let configs = r#"{"data":[{"modeConfigurations":{"com.example.user-focus":{"mode":{"name":"My Focus"}}}}]}"#;
        match parse_focus(assertions, configs) {
            Ok(Focus::FocusOn { name }) => assert_eq!(name, "My Focus"),
            other => panic!("expected FocusOn(My Focus), got {other:?}"),
        }
    }

    #[test]
    fn unknown_identifier_returns_name_unresolved() {
        let assertions = r#"{"data":[{"storeAssertionRecords":[{"assertionDetails":{"assertionDetailsModeIdentifier":"com.example.unknown-mode"}}]}]}"#;
        match parse_focus(assertions, EMPTY_CONFIGS) {
            Err(ParseFailure::NameUnresolved(id)) => {
                assert_eq!(id, "com.example.unknown-mode");
            }
            other => panic!("expected NameUnresolved, got {other:?}"),
        }
    }
}
