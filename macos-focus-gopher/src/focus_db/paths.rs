//! Locate the Focus database directory on disk.

use std::ffi::OsStr;
use std::path::PathBuf;

/// File name of the active-assertions document.
pub const ASSERTIONS_FILE: &str = "Assertions.json";

/// File name of the configured-modes document.
pub const MODE_CONFIGURATIONS_FILE: &str = "ModeConfigurations.json";

/// The per-user Focus database directory: `$HOME/Library/DoNotDisturb/DB`.
///
/// Returns `None` if `$HOME` is unset (extremely unusual — would indicate a
/// degenerate environment).
pub fn default_db_dir() -> Option<PathBuf> {
    Some(db_dir_under_home(std::env::var_os("HOME")?.as_os_str()))
}

/// Pure helper: build the Focus DB directory under a caller-supplied `$HOME`.
/// Kept separate from [`default_db_dir`] so it can be unit-tested without
/// mutating the process environment.
fn db_dir_under_home(home: &OsStr) -> PathBuf {
    let mut path = PathBuf::from(home);
    path.push("Library");
    path.push("DoNotDisturb");
    path.push("DB");
    path
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn db_dir_under_home_appends_dnd_db_segments() {
        let dir = db_dir_under_home(OsStr::new("/tmp/some-home"));
        assert!(dir.ends_with("Library/DoNotDisturb/DB"), "got {dir:?}");
        assert!(dir.starts_with("/tmp/some-home"), "got {dir:?}");
    }
}
