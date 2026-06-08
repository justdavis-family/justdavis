//! Locate the Focus database directory on disk.

use std::ffi::OsStr;
use std::path::PathBuf;

/// File name of the active-assertions document.
pub const ASSERTIONS_FILE: &str = "Assertions.json";

/// File name of the configured-modes document.
pub const MODE_CONFIGURATIONS_FILE: &str = "ModeConfigurations.json";

/// The per-user Focus database directory: `$HOME/Library/DoNotDisturb/DB`.
///
/// Returns `None` if `$HOME` is unset *or* set to the empty string (both are
/// POSIX-legal degenerate environments; either would build a relative path
/// that resolves against CWD and surface as a confusing "file not found"
/// rather than the clean "$HOME is not set" diagnostic the orchestrator
/// already provides).
pub fn default_db_dir() -> Option<PathBuf> {
    db_dir_from_home(std::env::var_os("HOME").as_deref())
}

/// Pure helper: apply the unset/empty rules to a HOME value (as the env
/// lookup would have returned), and produce the DB directory. Tested
/// directly so the env-lookup behavior is pinned without mutating the
/// process environment.
fn db_dir_from_home(home: Option<&OsStr>) -> Option<PathBuf> {
    let home = home?;
    if home.is_empty() {
        return None;
    }
    Some(db_dir_under_home(home))
}

/// Pure helper: build the Focus DB directory under a caller-supplied `$HOME`.
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

    #[test]
    fn db_dir_from_home_returns_none_when_unset_or_empty() {
        assert!(db_dir_from_home(None).is_none());
        assert!(db_dir_from_home(Some(OsStr::new(""))).is_none());

        let dir = db_dir_from_home(Some(OsStr::new("/home/user"))).expect("set HOME");
        assert!(dir.ends_with("Library/DoNotDisturb/DB"), "got {dir:?}");
    }
}
