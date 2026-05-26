//! Locate the Focus database directory on disk.

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
    let home = std::env::var_os("HOME")?;
    let mut path = PathBuf::from(home);
    path.push("Library");
    path.push("DoNotDisturb");
    path.push("DB");
    Some(path)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_db_dir_ends_with_dnd_db_when_home_is_set() {
        // SAFETY: tests run single-threaded by default with `cargo test`; we
        // restore HOME after the check so other tests are unaffected.
        let saved = std::env::var_os("HOME");
        // SAFETY: see above; restore on exit.
        unsafe { std::env::set_var("HOME", "/tmp/some-home") };
        let dir = default_db_dir().expect("HOME is set");
        assert!(dir.ends_with("Library/DoNotDisturb/DB"), "got {dir:?}");
        if let Some(saved) = saved {
            unsafe { std::env::set_var("HOME", saved) };
        } else {
            unsafe { std::env::remove_var("HOME") };
        }
    }
}
