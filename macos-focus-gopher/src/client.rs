//! A minimal in-process client of the socket protocol. The `focus-gopher` CLI
//! (M2) builds on this; for now it backs the round-trip integration test.

use crate::model::FocusState;
use crate::protocol::{self, Request};
use crate::socket;
use std::io::{self, BufReader};
use std::path::Path;

/// Connect to the helper at `path`, perform `get_focus`, and return the reply.
pub fn get_focus(path: &Path) -> io::Result<FocusState> {
    let stream = socket::connect(path)?;
    let mut writer = stream.try_clone()?;
    protocol::write_request(&mut writer, &Request::GetFocus)?;
    let mut reader = BufReader::new(stream);
    protocol::read_response(&mut reader)
}
