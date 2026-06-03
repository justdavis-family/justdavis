//! Look up a macOS version in the helper's compatibility table.
//!
//! # What `Supported` means here
//!
//! The compatibility table is an **explicit list of macOS versions the parser has been
//! empirically verified against in this codebase** (committed fixtures in
//! `tests/parsing.rs`, a live e2e walkthrough of the manual-Focus scenarios, or both).
//! Matching is by **exact version string** — verification is per-version, not per-major.
//! A version that isn't on the list reports `Unknown` even when it shares a major with a
//! listed version: we faithfully report what we have actually checked.
//!
//! Apple's Focus database is private, undocumented plumbing, and Apple can change its
//! format in any point release within a major. Reporting `Unknown` for a point release we
//! haven't exercised is the honest answer; the `Unknown` message names any sibling
//! versions in the same major that *have* been verified so the user knows what to expect
//! and what to report back.
//!
//! Note that the `macos_compatibility` field is a hint about **what we've checked**, not
//! about whether parsing will succeed. The wire model's `Determined` / `Failed` outcome
//! from `get_focus()` is the actual ground truth: if Apple has changed the format in a
//! point release we haven't verified, the parser fails loudly with one of the `Failed`
//! outcomes (`focus_db_malformed`, `schema_unknown`, etc.), regardless of what
//! `macos_compatibility` says.
//!
//! See `design/analyses/2026-05-12-macos-focus-db-format.md` (section 3) for the policy
//! rationale and the work item of growing the table as contributors verify new versions.

use crate::model::MacosCompatibility;

/// Versions of macOS that the Focus Gopher parser has been verified against in this
/// codebase.
///
/// Add a new entry only after running the parser on the new version and confirming the
/// manual-Focus scenarios pass — either by adding fixtures under `tests/fixtures/<ver>/`
/// and a `tests/parsing.rs` case, or via a live e2e walkthrough recorded in the analysis
/// and `FIXTURES.md`, or both.
const VERIFIED_VERSIONS: &[&str] = &["26.4.1", "26.5"];

/// URL inviting reports for non-verified versions.
const ISSUES_URL: &str = "https://github.com/justdavis-family/justdavis/issues";

/// Look up a version string (e.g. `"26.4.1"`) in the compatibility table.
///
/// The match is **exact** against [`VERIFIED_VERSIONS`]. A version not on the list
/// reports `Unknown`; when its major has at least one verified sibling the message names
/// the siblings, otherwise it's a generic "please file an issue" invitation. See the
/// module documentation for what `Supported` actually conveys.
pub fn look_up_compatibility(version: &str) -> MacosCompatibility {
    if VERIFIED_VERSIONS.contains(&version) {
        return MacosCompatibility::Supported;
    }
    MacosCompatibility::Unknown {
        message: unknown_message(version),
    }
}

/// Build the `Unknown` message for `version`, enriching it with sibling-major context
/// when at least one verified version shares the same major component.
fn unknown_message(version: &str) -> String {
    let siblings: Vec<&&str> = match major(version) {
        Some(m) => VERIFIED_VERSIONS
            .iter()
            .filter(|v| major(v) == Some(m))
            .collect(),
        None => Vec::new(),
    };
    if siblings.is_empty() {
        format!(
            "macOS {version} has not been verified against Focus Gopher. \
             Please file an issue at {ISSUES_URL} with the macOS version, helper \
             version, and whether the returned outcome was correct."
        )
    } else {
        let sibling_list = match siblings.as_slice() {
            [a] => format!("macOS {a}"),
            [a, b] => format!("macOS {a} and {b}"),
            rest => {
                let (last, init) = rest.split_last().expect("siblings is non-empty");
                let init_list = init
                    .iter()
                    .map(|v| format!("macOS {v}"))
                    .collect::<Vec<_>>()
                    .join(", ");
                format!("{init_list}, and macOS {last}")
            }
        };
        format!(
            "macOS {version} has not been independently verified against Focus Gopher; \
             {sibling_list} in the same major version have been verified, so the parser \
             will probably work — please file an issue at {ISSUES_URL} with whether it \
             did."
        )
    }
}

/// Extract the major-version component (everything before the first `.`), returning
/// `None` for empty input. Used only to group `VERIFIED_VERSIONS` by major when building
/// the `Unknown` message — it is *not* the matching key for the compatibility verdict.
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
    fn only_explicitly_verified_versions_are_supported() {
        for v in VERIFIED_VERSIONS {
            assert!(
                matches!(look_up_compatibility(v), MacosCompatibility::Supported),
                "expected Supported for verified version {v}"
            );
        }
        for v in [
            "26", "26.0", "26.1", "26.4", "26.4.0", "26.4.2", "26.6", "26.5.1",
        ] {
            assert!(
                matches!(look_up_compatibility(v), MacosCompatibility::Unknown { .. }),
                "expected Unknown for unverified 26.x version {v}"
            );
        }
    }

    #[test]
    fn unknown_in_verified_major_names_siblings() {
        let MacosCompatibility::Unknown { message } = look_up_compatibility("26.99") else {
            panic!("expected Unknown for 26.99");
        };
        assert!(
            message.contains("26.99"),
            "message should name the queried version: {message}"
        );
        for sibling in VERIFIED_VERSIONS {
            assert!(
                message.contains(sibling),
                "message should name sibling {sibling}: {message}"
            );
        }
        assert!(
            message.contains("same major"),
            "message should explain the relationship: {message}"
        );
        assert!(
            message.contains("file an issue"),
            "message should invite a report: {message}"
        );
    }

    #[test]
    fn unknown_in_unverified_major_uses_generic_message() {
        for v in ["15.5", "14.0", "13", "12.3", "27.0", "11.7"] {
            let MacosCompatibility::Unknown { message } = look_up_compatibility(v) else {
                panic!("expected Unknown for {v}");
            };
            assert!(
                message.contains(v),
                "message should name the queried version: {message}"
            );
            assert!(
                message.contains("file an issue"),
                "message should invite a report: {message}"
            );
            for sibling in VERIFIED_VERSIONS {
                assert!(
                    !message.contains(sibling),
                    "generic message must not name unrelated verified version {sibling}: {message}"
                );
            }
        }
    }

    #[test]
    fn empty_version_is_unknown() {
        let MacosCompatibility::Unknown { message } = look_up_compatibility("") else {
            panic!("expected Unknown for empty version");
        };
        assert!(
            message.contains("file an issue"),
            "message should invite a report even for empty input: {message}"
        );
    }
}
