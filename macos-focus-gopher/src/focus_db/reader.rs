//! Read the two Focus database files from disk and surface a clear failure
//! signal when the helper lacks Full Disk Access.
//!
//! `EPERM` (POSIX) maps to [`ReadFailure::PermissionDenied`] — the dependable
//! "denied" signal called for by the engineering design. Any other I/O error
//! (`ENOENT`, malformed inode, …) becomes [`ReadFailure::Unreadable`]. Because
//! the protecting directory is itself TCC-gated, a would-be `ENOENT` can also
//! surface as `EPERM` when the helper is unprivileged, so we treat `EPERM`
//! against either file as the dominant signal even if the other one would have
//! a different code.

use std::io::ErrorKind;
use std::path::Path;
use thiserror::Error;

use super::paths::{ASSERTIONS_FILE, MODE_CONFIGURATIONS_FILE};

/// The raw bodies of the two database files, both decoded as UTF-8 strings.
#[derive(Debug, Clone)]
pub struct RawFocusFiles {
    /// Body of `Assertions.json`.
    pub assertions: String,
    /// Body of `ModeConfigurations.json`.
    pub mode_configurations: String,
}

/// A failure to read one or both of the Focus database files.
#[derive(Debug, Error)]
pub enum ReadFailure {
    /// `EPERM` / `PermissionDenied` on `open()`. Overwhelmingly means the
    /// helper lacks Full Disk Access (see the FDA / signing / distribution
    /// analysis).
    #[error("permission denied reading the Focus database (Full Disk Access required)")]
    PermissionDenied,

    /// Any other I/O failure (the file is missing, the directory does not
    /// exist, the inode is malformed, …) once permission denial has been ruled
    /// out.
    #[error("Focus database file unreadable ({path}): {source}")]
    Unreadable {
        /// Which file failed.
        path: String,
        /// Underlying I/O error.
        #[source]
        source: std::io::Error,
    },
}

/// Read both Focus database files from `dir`.
///
/// On success returns the two file bodies as strings. On failure returns
/// [`ReadFailure`]; a permission-denied result on **either** file wins (so a
/// caller can give the user a single actionable Full Disk Access message
/// regardless of which file was first attempted).
pub fn read_focus_files(dir: &Path) -> Result<RawFocusFiles, ReadFailure> {
    let assertions_path = dir.join(ASSERTIONS_FILE);
    let mode_configurations_path = dir.join(MODE_CONFIGURATIONS_FILE);

    let assertions = std::fs::read_to_string(&assertions_path);
    let mode_configurations = std::fs::read_to_string(&mode_configurations_path);

    // `EPERM` on either file wins, even if the other has a different error.
    if matches!(&assertions, Err(e) if e.kind() == ErrorKind::PermissionDenied)
        || matches!(&mode_configurations, Err(e) if e.kind() == ErrorKind::PermissionDenied)
    {
        return Err(ReadFailure::PermissionDenied);
    }

    let assertions = assertions.map_err(|source| ReadFailure::Unreadable {
        path: assertions_path.display().to_string(),
        source,
    })?;
    let mode_configurations = mode_configurations.map_err(|source| ReadFailure::Unreadable {
        path: mode_configurations_path.display().to_string(),
        source,
    })?;

    Ok(RawFocusFiles {
        assertions,
        mode_configurations,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::os::unix::fs::PermissionsExt;
    use tempfile::tempdir;

    #[test]
    fn reads_both_files_when_present() {
        let dir = tempdir().expect("tempdir");
        fs::write(dir.path().join(ASSERTIONS_FILE), "{}").expect("write assertions");
        fs::write(dir.path().join(MODE_CONFIGURATIONS_FILE), "{}").expect("write mode configs");

        let raw = read_focus_files(dir.path()).expect("read should succeed");
        assert_eq!(raw.assertions, "{}");
        assert_eq!(raw.mode_configurations, "{}");
    }

    #[test]
    fn missing_file_is_unreadable_not_permission_denied() {
        let dir = tempdir().expect("tempdir");
        // Only create one of the two files.
        fs::write(dir.path().join(ASSERTIONS_FILE), "{}").expect("write assertions");

        match read_focus_files(dir.path()) {
            Err(ReadFailure::Unreadable { path, source }) => {
                assert!(path.contains(MODE_CONFIGURATIONS_FILE), "got path {path}");
                assert_eq!(source.kind(), ErrorKind::NotFound);
            }
            other => panic!("expected Unreadable, got {other:?}"),
        }
    }

    #[test]
    fn permission_denied_on_either_file_wins() {
        let dir = tempdir().expect("tempdir");
        let assertions = dir.path().join(ASSERTIONS_FILE);
        let mode_configurations = dir.path().join(MODE_CONFIGURATIONS_FILE);
        fs::write(&assertions, "{}").expect("write assertions");
        fs::write(&mode_configurations, "{}").expect("write mode configs");
        // Strip read permission from Assertions.json. On Unix that produces
        // EACCES from `open()` which Rust normalizes to `PermissionDenied`,
        // the same kind macOS surfaces for EPERM under TCC.
        let mut perms = fs::metadata(&assertions).expect("metadata").permissions();
        perms.set_mode(0o000);
        fs::set_permissions(&assertions, perms).expect("set perms");

        let result = read_focus_files(dir.path());
        // Restore perms so tempdir can clean up.
        fs::set_permissions(&assertions, fs::Permissions::from_mode(0o644)).expect("restore perms");

        assert!(
            matches!(result, Err(ReadFailure::PermissionDenied)),
            "expected PermissionDenied, got {result:?}",
        );
    }
}
