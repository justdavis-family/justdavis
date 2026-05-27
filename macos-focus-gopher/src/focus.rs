//! `get_focus()` — the single read-only operation the helper exposes.
//!
//! Orchestrates the retrieval pipeline described in
//! `design/engineering-designs/2026-05-12-macos-focus-gopher.md`:
//!
//! 1. Detect the macOS version.
//! 2. Look the version up in the [compatibility table](crate::compatibility).
//! 3. Read the two Focus database files
//!    (mapping `EPERM` → [`ErrorCode::FocusPermissionDenied`]).
//! 4. Parse them into a [`Focus`].
//! 5. Wrap into a [`FocusState`] with the version and compatibility metadata.
//!
//! Each internal error type
//! ([`VersionDetectError`](crate::macos_version::VersionDetectError),
//!  [`ReadFailure`](crate::focus_db::ReadFailure),
//!  [`ParseFailure`](crate::focus_db::ParseFailure))
//! is mapped here into the wire-level [`ErrorCode`]. The internal types are
//! `thiserror` enums for ergonomic propagation; the wire enum is what crosses
//! the socket and lives in the published JSON Schema. They are deliberately
//! distinct (per the project's Rust conventions).

use std::path::PathBuf;

use crate::compatibility::look_up_compatibility;
use crate::focus_db::{
    parse_focus, paths::default_db_dir, read_focus_files, ParseFailure, ReadFailure,
};
use crate::macos_version::{detect_macos_version, VersionDetectError};
use crate::model::{ErrorCode, FocusState, MacosCompatibility, Outcome};

/// Determine the current Focus state.
pub fn get_focus() -> FocusState {
    let exe = resolve_current_exe();

    let version = match detect_macos_version() {
        Ok(v) => v,
        Err(VersionDetectError::NotMacos) => {
            return FocusState {
                macos_version: "unknown".to_string(),
                macos_compatibility: MacosCompatibility::Unsupported,
                outcome: Outcome::Failed {
                    error: ErrorCode::MacosUnsupported,
                    message: "Focus Gopher only runs on macOS.".to_string(),
                },
            };
        }
        Err(e) => {
            return FocusState {
                macos_version: "unknown".to_string(),
                macos_compatibility: MacosCompatibility::Unknown {
                    message: "Focus Gopher could not detect the running macOS version.".to_string(),
                },
                outcome: Outcome::Failed {
                    error: ErrorCode::InternalError,
                    message: format!("Could not determine the macOS version: {e}"),
                },
            };
        }
    };

    let compatibility = look_up_compatibility(&version);

    // Short-circuit when the version is explicitly marked unsupported.
    // (Unreachable today — the M3 compatibility table contains no `Unsupported`
    // entries — but it keeps the contract honest as the table grows.)
    if matches!(compatibility, MacosCompatibility::Unsupported) {
        return FocusState {
            macos_version: version,
            macos_compatibility: MacosCompatibility::Unsupported,
            outcome: Outcome::Failed {
                error: ErrorCode::MacosUnsupported,
                message: "This macOS version is explicitly marked unsupported by Focus Gopher."
                    .to_string(),
            },
        };
    }

    let outcome = read_and_parse(exe.as_deref());

    FocusState {
        macos_version: version,
        macos_compatibility: compatibility,
        outcome,
    }
}

/// Read both Focus database files, parse them, and produce a wire [`Outcome`]
/// for the disk-touching portion of the pipeline.
fn read_and_parse(canonical_exe: Option<&std::path::Path>) -> Outcome {
    let Some(dir) = default_db_dir() else {
        return Outcome::Failed {
            error: ErrorCode::FocusDbUnreadable,
            message: "Could not locate the Focus database directory ($HOME is not set)."
                .to_string(),
        };
    };

    let raw = match read_focus_files(&dir) {
        Ok(raw) => raw,
        Err(ReadFailure::PermissionDenied) => {
            return Outcome::Failed {
                error: ErrorCode::FocusPermissionDenied,
                message: fda_message(canonical_exe),
            };
        }
        Err(ReadFailure::Unreadable { path, source }) => {
            return Outcome::Failed {
                error: ErrorCode::FocusDbUnreadable,
                message: format!("Focus database file {path:?} could not be read: {source}"),
            };
        }
    };

    match parse_focus(&raw.assertions, &raw.mode_configurations) {
        Ok(focus) => Outcome::Determined(focus),
        Err(ParseFailure::Malformed { file, source }) => Outcome::Failed {
            error: ErrorCode::FocusDbMalformed,
            message: format!("Focus database file {file:?} is not valid JSON: {source}"),
        },
        Err(ParseFailure::SchemaUnknown { where_at }) => Outcome::Failed {
            error: ErrorCode::SchemaUnknown,
            message: format!("Focus database schema not recognized: {where_at}"),
        },
        Err(ParseFailure::NameUnresolved(identifier)) => Outcome::Failed {
            error: ErrorCode::FocusNameUnresolved,
            message: format!(
                "An active Focus was detected (identifier {identifier:?}) but its display \
                 name could not be resolved. Please file an issue with your macOS version, \
                 the helper version, and this identifier."
            ),
        },
    }
}

/// Best-effort canonical path to the running helper binary, used in the FDA
/// missing-grant message so the user knows *which* binary to grant access to.
/// Returns `None` if `current_exe()` or `canonicalize()` fails; the caller
/// degrades gracefully to a generic message.
fn resolve_current_exe() -> Option<PathBuf> {
    match std::env::current_exe().and_then(|p| p.canonicalize()) {
        Ok(p) => Some(p),
        Err(e) => {
            tracing::warn!(
                error = %e,
                "Could not resolve the canonical helper binary path; the missing-FDA message will be generic."
            );
            None
        }
    }
}

/// Human-readable, actionable Full Disk Access missing-grant message.
///
/// Includes the canonical resolved binary path (when known) plus the System
/// Settings deep link. The exact deep-link URL is the one called out in the
/// FDA / signing / distribution analysis.
fn fda_message(canonical_exe: Option<&std::path::Path>) -> String {
    const DEEP_LINK: &str =
        "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles";

    match canonical_exe {
        Some(path) => format!(
            "Full Disk Access is required to read the Focus database. \
             Grant it to the Focus Gopher helper binary at {path:?} via \
             System Settings → Privacy & Security → Full Disk Access (deep link: {DEEP_LINK}). \
             On unsigned / build-from-source installs the grant is keyed to the binary's \
             cdhash and must be re-applied after every rebuild.",
            path = path.display(),
        ),
        None => format!(
            "Full Disk Access is required to read the Focus database. \
             Grant it to the Focus Gopher helper binary via System Settings → \
             Privacy & Security → Full Disk Access (deep link: {DEEP_LINK}). \
             On unsigned / build-from-source installs the grant is keyed to the binary's \
             cdhash and must be re-applied after every rebuild."
        ),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::Focus;

    /// The pipeline must always return a valid `FocusState`, regardless of host
    /// environment. This is the *contract* property — the strictest assertion
    /// we can make without knowing whether the host has FDA / is on a
    /// supported macOS / has the database accessible.
    #[test]
    fn get_focus_returns_a_well_formed_focus_state() {
        let state = get_focus();
        // `macos_version` is always present.
        assert!(!state.macos_version.is_empty(), "macos_version must be set");
        // The outcome is exactly one of the two legal variants, and a Failed
        // outcome always carries a non-empty message.
        match &state.outcome {
            Outcome::Determined(Focus::FocusOn { name }) => {
                assert!(!name.is_empty(), "FocusOn requires a non-empty name");
            }
            Outcome::Determined(Focus::FocusOff {}) => {}
            Outcome::Failed { message, .. } => {
                assert!(!message.is_empty(), "Failed requires a non-empty message");
            }
        }
    }

    #[test]
    fn fda_message_includes_deep_link() {
        let msg = fda_message(None);
        assert!(
            msg.contains("Privacy_AllFiles"),
            "deep link must be present"
        );
        assert!(msg.contains("Full Disk Access"), "must name the grant");

        let with_path = fda_message(Some(std::path::Path::new(
            "/Applications/Focus.app/Contents/MacOS/focus-gopherd",
        )));
        assert!(with_path.contains("/Applications/Focus.app"));
    }
}
