//! Look up a macOS version in the helper's compatibility table.
//!
//! # What `Supported` actually means here
//!
//! The compatibility verdict (`Supported` / `Unknown` / `Unsupported`)
//! is an **advisory hint**, not a guarantee that parsing will succeed.
//! macOS's Focus database is private, undocumented plumbing,
//! and Apple can change its format in any point release within a major version.
//!
//! Today the table is keyed by **major** version.
//! A `Supported` verdict for, say, `"26.4.1"` and `"26.5"` reflects
//! that the parser has been empirically verified against *at least one* point release
//! within macOS 26 (specifically 26.4.1 in the test fixtures, plus live e2e against 26.5),
//! and that the project is choosing to optimistically extend the same verdict
//! to other 26.x point releases.
//! It is **not** a promise that every 26.x release will work.
//! If Apple has changed the format in a point release we have not verified,
//! the parser fails loudly at runtime and the call returns one of the `Failed` outcomes
//! (`focus_db_malformed`, `schema_unknown`, etc.).
//! Those `Determined` / `Failed` outcomes from `get_focus()` are the actual ground truth
//! about whether parsing succeeded;
//! `macos_compatibility` is just a hint for callers reading host telemetry,
//! not a gate they should branch on.
//!
//! Any version not in the table is reported as `Unknown`
//! with a "please file an issue" message,
//! so contributors can grow the table as new versions are verified.
//!
//! See `design/analyses/2026-05-12-macos-focus-db-format.md` (section 3)
//! for the rationale behind the major-version-wildcard compromise,
//! including the explicit acknowledgement that it is a calculated optimism.

use crate::model::MacosCompatibility;

/// Look up a version string (e.g. `"26.4.1"`) in the compatibility table.
///
/// The lookup is by **major** component only.
/// This is an optimization: returning `Supported` for `"26.4.1"`, `"26.5"`, `"26.0.1"`, etc.
/// from a single table entry avoids requiring every contributor to reverify every point release.
/// It is **not** a guarantee that the format is stable across point releases within a major
/// — see the module-level documentation for what `Supported` actually conveys.
pub fn look_up_compatibility(version: &str) -> MacosCompatibility {
    match major(version) {
        Some("26") => MacosCompatibility::Supported,
        _ => MacosCompatibility::Unknown {
            message: format!(
                "macOS {version} has not been verified against Focus Gopher. \
                 Please file an issue at https://github.com/justdavis-family/justdavis/issues \
                 with the macOS version, helper version, and whether the returned outcome \
                 was correct."
            ),
        },
    }
}

/// Extract the major-version component (everything before the first `.`),
/// returning `None` for empty input.
fn major(version: &str) -> Option<&str> {
    let major = version.split('.').next()?;
    if major.is_empty() {
        None
    } else {
        Some(major)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn macos_26_point_releases_are_supported() {
        for v in ["26.0", "26.1", "26.4.1", "26"] {
            assert!(
                matches!(look_up_compatibility(v), MacosCompatibility::Supported),
                "expected Supported for {v}"
            );
        }
    }

    #[test]
    fn other_majors_are_unknown_with_a_message() {
        for v in ["15.5", "14.0", "13", "12.3", "27.0", "11.7"] {
            match look_up_compatibility(v) {
                MacosCompatibility::Unknown { message } => {
                    assert!(
                        message.contains(v),
                        "message should mention version: {message}"
                    );
                    assert!(
                        message.contains("file an issue"),
                        "message should invite a report: {message}"
                    );
                }
                other => panic!("expected Unknown for {v}, got {other:?}"),
            }
        }
    }

    #[test]
    fn empty_version_is_unknown() {
        assert!(matches!(
            look_up_compatibility(""),
            MacosCompatibility::Unknown { .. }
        ));
    }
}
