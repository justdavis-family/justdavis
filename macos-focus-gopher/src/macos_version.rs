//! Detect the macOS version the helper is running on.
//!
//! Shells out to `sw_vers -productVersion`, which is always present on macOS and
//! avoids pulling in another Rust dependency. On non-macOS targets the function
//! compiles to a stub that returns [`VersionDetectError::NotMacos`] so the crate
//! still builds on Linux CI.

use thiserror::Error;

/// A failure to detect the macOS version.
///
/// Internal to the library; `get_focus()` maps these into wire-level
/// [`crate::model::ErrorCode`] values.
#[derive(Debug, Error)]
pub enum VersionDetectError {
    /// The crate is running on a non-macOS target. Hard error rather than a
    /// silent zero version so callers know the difference between "we asked but
    /// macOS said `unknown`" and "we never asked".
    #[error("not running on macOS")]
    NotMacos,

    /// `sw_vers` exited non-zero or produced output we could not parse.
    #[error("sw_vers failed: {0}")]
    SwVersFailed(String),

    /// `sw_vers` could not be spawned.
    #[error(transparent)]
    Io(#[from] std::io::Error),
}

/// Detect the running macOS version as a string (e.g. `"15.5"`, `"26.4.1"`).
#[cfg(target_os = "macos")]
pub fn detect_macos_version() -> Result<String, VersionDetectError> {
    let output = std::process::Command::new("sw_vers")
        .arg("-productVersion")
        .output()?;
    if !output.status.success() {
        return Err(VersionDetectError::SwVersFailed(
            String::from_utf8_lossy(&output.stderr).trim().to_string(),
        ));
    }
    let version = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if version.is_empty() {
        return Err(VersionDetectError::SwVersFailed(
            "sw_vers produced empty output".to_string(),
        ));
    }
    Ok(version)
}

/// Stub: macOS version cannot be detected on non-macOS targets.
#[cfg(not(target_os = "macos"))]
pub fn detect_macos_version() -> Result<String, VersionDetectError> {
    Err(VersionDetectError::NotMacos)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    #[cfg(target_os = "macos")]
    fn returns_a_dotted_version_on_macos() {
        let version = detect_macos_version().expect("sw_vers should succeed on macOS");
        // e.g. "15.5" or "26.4.1" — at least one dot, only digits and dots.
        assert!(
            version.contains('.'),
            "expected dotted version, got {version:?}"
        );
        assert!(
            version.chars().all(|c| c.is_ascii_digit() || c == '.'),
            "expected only digits and dots, got {version:?}"
        );
    }

    #[test]
    #[cfg(not(target_os = "macos"))]
    fn errors_on_non_macos() {
        match detect_macos_version() {
            Err(VersionDetectError::NotMacos) => {}
            other => panic!("expected NotMacos, got {other:?}"),
        }
    }
}
