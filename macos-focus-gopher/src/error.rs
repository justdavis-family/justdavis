//! The library's typed error, per the Rust application conventions
//! (`.claude/rules/rust.md`): libraries expose `thiserror` error types, binaries
//! use `anyhow`.
//!
//! This is the *internal propagation* error. It is distinct from the **wire**
//! error taxonomy ([`crate::model::ErrorCode`]), which is part of the published
//! `FocusState` contract.

use thiserror::Error;

/// An error from the Focus Gopher library.
#[derive(Debug, Error)]
pub enum Error {
    /// Neither `FOCUS_GOPHER_SOCKET` nor `TMPDIR` is set, so the socket path
    /// cannot be determined.
    #[error("neither FOCUS_GOPHER_SOCKET nor TMPDIR is set; cannot locate the socket")]
    MissingSocketDir,

    /// A protocol message could not be encoded or decoded.
    #[error("protocol error: {0}")]
    Protocol(#[from] serde_json::Error),

    /// An underlying I/O failure.
    #[error(transparent)]
    Io(#[from] std::io::Error),
}

/// A `Result` whose error is the crate [`Error`].
pub type Result<T> = std::result::Result<T, Error>;
