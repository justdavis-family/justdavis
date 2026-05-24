//! `get_focus()` — the single read-only operation the helper exposes.
//!
//! M1 ships a stub: it returns a well-formed `FocusState` without touching any
//! database file or calling any macOS API. Real macOS-version detection and
//! Focus-database parsing land in M3 (see the delivery plan).

use crate::model::{ErrorCode, FocusState, MacosCompatibility, Outcome};

/// Determine the current Focus state.
///
/// M1 stub: returns a well-formed `failed` / `macos_unsupported` `FocusState`
/// without reading any file or calling any macOS API. Replaced by real detection
/// and parsing in M3.
pub fn get_focus() -> FocusState {
    FocusState {
        macos_version: "0.0".to_string(),
        macos_compatibility: MacosCompatibility::Unsupported,
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
    use crate::model::{ErrorCode, Outcome};

    #[test]
    fn stub_returns_failed_macos_unsupported() {
        let state = get_focus();
        match state.outcome {
            Outcome::Failed { error, .. } => assert_eq!(error, ErrorCode::MacosUnsupported),
            other => panic!("expected a failed outcome, got {other:?}"),
        }
    }
}
