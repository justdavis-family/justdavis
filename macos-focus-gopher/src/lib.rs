//! Focus Gopher: a per-user macOS helper that reads the current Focus / Do Not
//! Disturb state and exposes it to local clients through a single read-only
//! operation (`get_focus()`), brokering the macOS privacy permission so that
//! unprivileged clients never need Full Disk Access themselves.
//!
//! See the project `README.md` and the design docs under `design/` for the
//! full picture.

pub mod client;
pub mod compatibility;
pub mod error;
pub mod focus;
pub mod focus_db;
pub mod logging;
pub mod macos_version;
pub mod model;
pub mod protocol;
pub mod server;
pub mod socket;

pub use error::{Error, Result};
