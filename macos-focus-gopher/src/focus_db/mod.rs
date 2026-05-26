//! Internals for reading and parsing the macOS Focus database.
//!
//! Public entry: [`crate::focus::get_focus()`]. The submodules here implement
//! its retrieval pipeline:
//!
//! - [`paths`] resolves the on-disk location of the database files.
//! - [`reader`] reads the two files and maps low-level I/O errors into the
//!   library's [`ReadFailure`] enum (notably `EPERM`/`PermissionDenied`,
//!   which signals a missing Full Disk Access grant).
//! - [`parser`] is a **pure** function over the two file bodies (no I/O, no
//!   environment access) producing a wire [`crate::model::Focus`] or a
//!   [`ParseFailure`]. Pure-function design lets it be driven directly from
//!   fixture strings in tests.
//! - [`identifiers`] maps Apple's built-in Focus identifiers to display names.

pub mod identifiers;
pub mod parser;
pub mod paths;
pub mod reader;

pub use parser::{parse_focus, ParseFailure};
pub use reader::{read_focus_files, ReadFailure};
