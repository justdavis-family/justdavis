//! Look up a macOS version in the helper's compatibility table.
//!
//! The table is keyed by major version. M3 ships with macOS 26 (Tahoe) verified
//! against real captured fixtures; the format-stability analysis identifies
//! macOS 12–15 as candidates for inclusion once they have been verified in this
//! codebase. Any version not in the table is reported as `Unknown` with a
//! "please file an issue" message — the outcome's `Determined`/`Failed` field
//! still conveys whether parsing actually worked.
//!
//! See `design/analyses/2026-05-12-macos-focus-db-format.md` for the rationale.

use crate::model::MacosCompatibility;

/// Look up a version string (e.g. `"26.4.1"`) in the compatibility table.
///
/// The lookup is by **major** component only — point releases within a verified
/// major share the same verdict.
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
