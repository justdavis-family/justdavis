//! `get_focus()` — the single read-only operation the helper exposes.
//!
//! This currently ships a stub: it returns a well-formed `FocusState` without
//! touching any database file or calling any macOS API. Real macOS-version
//! detection and Focus-database parsing come later (see the delivery plan).

use crate::model::{ErrorCode, FocusState, MacosCompatibility, Outcome};

/// Determine the current Focus state.
///
/// Currently a stub: returns a well-formed `failed` / `macos_unsupported`
/// `FocusState` without reading any file or calling any macOS API. Replaced by
/// real detection and parsing later.
pub fn get_focus() -> FocusState {
    FocusState {
        macos_version: "0.0".to_string(),
        // The version was never detected, so report Unknown ("didn't check")
        // rather than Unsupported ("checked and not on the supported list").
        macos_compatibility: MacosCompatibility::Unknown {
            message: "Focus Gopher does not detect the macOS version yet (early development)."
                .to_string(),
        },
        outcome: Outcome::Failed {
            error: ErrorCode::MacosUnsupported,
            message: "Focus parsing is not yet implemented (early development; \
                      see the project README)."
                .to_string(),
        },
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::{ErrorCode, MacosCompatibility, Outcome};

    #[test]
    fn stub_reports_unknown_compatibility_and_a_failed_outcome() {
        let state = get_focus();
        assert!(matches!(
            state.macos_compatibility,
            MacosCompatibility::Unknown { .. }
        ));
        match state.outcome {
            Outcome::Failed { error, .. } => assert_eq!(error, ErrorCode::MacosUnsupported),
            other => panic!("expected a failed outcome, got {other:?}"),
        }
    }
}
