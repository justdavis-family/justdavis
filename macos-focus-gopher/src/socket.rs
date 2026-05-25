//! Socket path derivation and bind/connect helpers.
//!
//! macOS has no `XDG_RUNTIME_DIR`-style blessed per-user socket directory, and
//! `sockaddr_un.sun_path` is capped (~104 bytes), so the helper places the socket
//! directly in `$TMPDIR`: `$TMPDIR/focus-gopher.sock` (overridable with the
//! `FOCUS_GOPHER_SOCKET` env var, which the tests use).
//!
//! Access control rests entirely on `$TMPDIR`'s semantics. On macOS it is the
//! per-user, mode-`0700`, user-owned `confstr(_CS_DARWIN_USER_TEMP_DIR)` directory
//! (e.g. `/var/folders/…/T/`), so a socket inside it is reachable only by its
//! owner: no other user can traverse in to connect, and no other user can create a
//! socket there to impersonate the helper. That is why this module needs neither a
//! uid in the path (there is no shared directory to namespace) nor an explicit
//! peer-uid check on connect — the directory already enforces single-user access.
//! If `$TMPDIR` is unset we error rather than fall back to a shared, world-writable
//! location like `/tmp`.
//!
//! The preferred long-term design hands the listener off from `launchd` via
//! `launch_activate_socket()`; that swap can come later and only needs to replace
//! [`bind`] — nothing else in the server changes.

use std::ffi::OsString;
use std::fs;
use std::io;
use std::os::unix::fs::PermissionsExt;
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::{Path, PathBuf};

/// The socket path: `$TMPDIR/focus-gopher.sock`, or the `FOCUS_GOPHER_SOCKET`
/// override if set. Errors if neither is available.
pub fn socket_path() -> crate::Result<PathBuf> {
    resolve_socket_path(
        std::env::var_os("FOCUS_GOPHER_SOCKET"),
        std::env::var_os("TMPDIR"),
    )
}

/// Pure path derivation (no syscalls), so it is directly testable.
fn resolve_socket_path(
    override_var: Option<OsString>,
    tmpdir: Option<OsString>,
) -> crate::Result<PathBuf> {
    if let Some(path) = override_var {
        return Ok(PathBuf::from(path));
    }
    match tmpdir {
        Some(dir) => Ok(PathBuf::from(dir).join("focus-gopher.sock")),
        None => Err(crate::Error::MissingSocketDir),
    }
}

/// Bind a listener at `path`: unlink any stale socket, bind, and restrict the
/// socket to `0600`.
///
/// The containing directory (`$TMPDIR`) is the caller's private, per-user
/// directory, so we neither create nor re-permission it — its `0700` ownership is
/// what keeps the socket reachable only by its owner.
pub fn bind(path: &Path) -> crate::Result<UnixListener> {
    match fs::remove_file(path) {
        Ok(()) => {}
        Err(e) if e.kind() == io::ErrorKind::NotFound => {}
        Err(e) => return Err(e.into()),
    }
    let listener = UnixListener::bind(path)?;
    fs::set_permissions(path, fs::Permissions::from_mode(0o600))?;
    Ok(listener)
}

/// Connect to the socket at `path`.
pub fn connect(path: &Path) -> crate::Result<UnixStream> {
    Ok(UnixStream::connect(path)?)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn override_var_takes_precedence() {
        let path = resolve_socket_path(
            Some("/custom/fg.sock".into()),
            Some("/var/folders/ab/T/".into()),
        )
        .unwrap();
        assert_eq!(path, PathBuf::from("/custom/fg.sock"));
    }

    #[test]
    fn uses_tmpdir() {
        let path = resolve_socket_path(None, Some("/var/folders/ab/T/".into())).unwrap();
        assert_eq!(path, PathBuf::from("/var/folders/ab/T/focus-gopher.sock"));
    }

    #[test]
    fn errors_when_neither_override_nor_tmpdir_is_set() {
        assert!(resolve_socket_path(None, None).is_err());
    }
}
