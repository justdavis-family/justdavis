//! Socket path derivation and secure bind/connect helpers.
//!
//! macOS has no `XDG_RUNTIME_DIR`-style blessed per-user socket directory, and
//! `sockaddr_un.sun_path` is capped (~104 bytes), so M1 pins a deliberately-short
//! path: `<$TMPDIR or /tmp>/focus-gopher-<uid>/focus-gopher.sock`. The per-user
//! `0700` subdir plus the `0600` socket keep it reachable only by its owner; the
//! server additionally checks the peer's uid on accept.
//!
//! On macOS `$TMPDIR` is the per-user, `0700`, user-owned
//! `confstr(_CS_DARWIN_USER_TEMP_DIR)` directory; reading that via `confstr`
//! directly (rather than the env var) is a possible future hardening. The
//! preferred long-term design hands the listener off from `launchd` via
//! `launch_activate_socket()`; that swap lands in M4 and only needs to replace
//! [`bind`] — nothing else in the server changes.

use std::ffi::OsString;
use std::fs;
use std::io;
use std::os::unix::fs::{MetadataExt, PermissionsExt};
use std::os::unix::io::AsRawFd;
use std::os::unix::net::{UnixListener, UnixStream};
use std::path::{Path, PathBuf};

/// The effective uid of the current process.
pub fn current_uid() -> u32 {
    // SAFETY: `geteuid` is always safe — it takes no arguments and cannot fail.
    unsafe { libc::geteuid() }
}

/// The per-user socket path, honoring the `FOCUS_GOPHER_SOCKET` override.
pub fn socket_path() -> PathBuf {
    resolve_socket_path(
        std::env::var_os("FOCUS_GOPHER_SOCKET"),
        std::env::var_os("TMPDIR"),
        current_uid(),
    )
}

/// Pure path derivation (no environment or syscalls), so it is directly testable.
fn resolve_socket_path(
    override_var: Option<OsString>,
    tmpdir: Option<OsString>,
    uid: u32,
) -> PathBuf {
    if let Some(path) = override_var {
        return PathBuf::from(path);
    }
    let base = tmpdir
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("/tmp"));
    base.join(format!("focus-gopher-{uid}"))
        .join("focus-gopher.sock")
}

/// Bind a listener at `path`: ensure a user-only (`0700`) parent dir, unlink any
/// stale socket, bind, and restrict the socket to `0600`.
///
/// A parent directory that does not yet exist is created `0700`. A parent that
/// already exists is left untouched apart from a check that the current user owns
/// it — we never rewrite the permissions of a pre-existing directory (which, for
/// an override pointing at e.g. `/tmp`, would be a destructive surprise).
pub fn bind(path: &Path) -> io::Result<UnixListener> {
    if let Some(parent) = path.parent() {
        if parent.exists() {
            if fs::metadata(parent)?.uid() != current_uid() {
                return Err(io::Error::new(
                    io::ErrorKind::PermissionDenied,
                    "socket directory is not owned by the current user",
                ));
            }
        } else {
            fs::create_dir_all(parent)?;
            fs::set_permissions(parent, fs::Permissions::from_mode(0o700))?;
        }
    }
    match fs::remove_file(path) {
        Ok(()) => {}
        Err(e) if e.kind() == io::ErrorKind::NotFound => {}
        Err(e) => return Err(e),
    }
    let listener = UnixListener::bind(path)?;
    fs::set_permissions(path, fs::Permissions::from_mode(0o600))?;
    Ok(listener)
}

/// Connect to the socket at `path`, after verifying it is owned by the current
/// user and not accessible by anyone else.
pub fn connect(path: &Path) -> io::Result<UnixStream> {
    verify_owner(path)?;
    UnixStream::connect(path)
}

/// The uid of the process on the other end of `stream`.
///
/// There is no single stable, portable API for this: std's `peer_cred` is still
/// unstable, so we go through `libc`. Linux/Android use `getsockopt(SO_PEERCRED)`
/// (the `libc` crate does not declare `getpeereid` for those targets), while the
/// BSD/Apple family uses `getpeereid`.
#[cfg(any(target_os = "linux", target_os = "android"))]
pub fn peer_uid(stream: &UnixStream) -> io::Result<u32> {
    let mut cred: libc::ucred = unsafe { std::mem::zeroed() };
    let mut len = std::mem::size_of::<libc::ucred>() as libc::socklen_t;
    // SAFETY: the fd is valid for the lifetime of `stream`; `cred`/`len` are valid
    // out-params sized for `SO_PEERCRED`.
    let rc = unsafe {
        libc::getsockopt(
            stream.as_raw_fd(),
            libc::SOL_SOCKET,
            libc::SO_PEERCRED,
            std::ptr::addr_of_mut!(cred).cast(),
            &mut len,
        )
    };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(cred.uid)
}

/// See the Linux variant above.
#[cfg(not(any(target_os = "linux", target_os = "android")))]
pub fn peer_uid(stream: &UnixStream) -> io::Result<u32> {
    let mut uid: libc::uid_t = 0;
    let mut gid: libc::gid_t = 0;
    // SAFETY: the fd is valid for the lifetime of `stream`; the out-pointers are valid.
    let rc = unsafe { libc::getpeereid(stream.as_raw_fd(), &mut uid, &mut gid) };
    if rc != 0 {
        return Err(io::Error::last_os_error());
    }
    Ok(uid)
}

fn verify_owner(path: &Path) -> io::Result<()> {
    let meta = fs::metadata(path)?;
    if meta.uid() != current_uid() {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "socket is not owned by the current user",
        ));
    }
    if meta.permissions().mode() & 0o077 != 0 {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "socket is accessible beyond its owner",
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn override_var_takes_precedence() {
        let path = resolve_socket_path(Some("/custom/fg.sock".into()), Some("/tmp/x".into()), 501);
        assert_eq!(path, PathBuf::from("/custom/fg.sock"));
    }

    #[test]
    fn uses_tmpdir_with_per_user_subdir() {
        let path = resolve_socket_path(None, Some("/var/folders/ab/T/".into()), 501);
        assert_eq!(
            path,
            PathBuf::from("/var/folders/ab/T/focus-gopher-501/focus-gopher.sock")
        );
    }

    #[test]
    fn falls_back_to_tmp_when_tmpdir_unset() {
        let path = resolve_socket_path(None, None, 501);
        assert_eq!(
            path,
            PathBuf::from("/tmp/focus-gopher-501/focus-gopher.sock")
        );
    }
}
