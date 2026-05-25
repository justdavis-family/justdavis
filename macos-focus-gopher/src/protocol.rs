//! The line-delimited JSON request/response protocol spoken over the socket.
//!
//! The client sends one fixed request object terminated by a newline; the helper
//! replies with exactly one `FocusState` object terminated by a newline. There is
//! no general "send an arbitrary command" path — the only request is `get_focus`.
//!
//! Separation of concerns: this module owns the *wire format* only — the request
//! type and the symmetric read/write framing for both directions. It deliberately
//! holds the encode and decode halves together so they cannot drift, and it knows
//! nothing about transport roles. Those live elsewhere: [`crate::client`] connects
//! and speaks this protocol, and [`crate::server`] accepts connections and answers
//! it. Both depend on this module; it depends on neither.

use crate::model::FocusState;
use serde::{Deserialize, Serialize};
use std::io::{self, BufRead, Write};

/// A request from a client. The protocol intentionally has exactly one operation.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(tag = "op", rename_all = "snake_case")]
pub enum Request {
    /// Retrieve the current Focus state.
    GetFocus,
}

/// Write one request as a single compact JSON line (object + `\n`).
pub fn write_request<W: Write>(writer: &mut W, request: &Request) -> crate::Result<()> {
    write_line(writer, request)
}

/// Read exactly one newline-terminated request object.
pub fn read_request<R: BufRead>(reader: &mut R) -> crate::Result<Request> {
    read_line(reader)
}

/// Write one `FocusState` as a single compact JSON line (object + `\n`).
pub fn write_response<W: Write>(writer: &mut W, state: &FocusState) -> crate::Result<()> {
    write_line(writer, state)
}

/// Read exactly one newline-terminated `FocusState` object.
pub fn read_response<R: BufRead>(reader: &mut R) -> crate::Result<FocusState> {
    read_line(reader)
}

fn write_line<W: Write, T: Serialize>(writer: &mut W, value: &T) -> crate::Result<()> {
    let mut bytes = serde_json::to_vec(value)?;
    bytes.push(b'\n');
    writer.write_all(&bytes)?;
    writer.flush()?;
    Ok(())
}

fn read_line<R: BufRead, T: for<'de> Deserialize<'de>>(reader: &mut R) -> crate::Result<T> {
    let mut line = String::new();
    if reader.read_line(&mut line)? == 0 {
        return Err(io::Error::new(
            io::ErrorKind::UnexpectedEof,
            "expected one newline-terminated JSON object, got EOF",
        )
        .into());
    }
    Ok(serde_json::from_str(line.trim_end())?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::model::{Focus, FocusState, MacosCompatibility, Outcome};
    use serde_json::json;
    use std::io::Cursor;

    fn sample() -> FocusState {
        FocusState {
            macos_version: "15.5".into(),
            macos_compatibility: MacosCompatibility::Supported,
            outcome: Outcome::Determined(Focus::FocusOff {}),
        }
    }

    #[test]
    fn request_serializes_with_op_tag() {
        assert_eq!(
            serde_json::to_value(Request::GetFocus).unwrap(),
            json!({ "op": "get_focus" })
        );
    }

    #[test]
    fn read_request_parses_get_focus() {
        let line = format!("{}\n", json!({ "op": "get_focus" }));
        let mut input = Cursor::new(line.into_bytes());
        assert_eq!(read_request(&mut input).unwrap(), Request::GetFocus);
    }

    #[test]
    fn read_request_rejects_unknown_op() {
        let line = format!("{}\n", json!({ "op": "run_shell" }));
        let mut input = Cursor::new(line.into_bytes());
        assert!(read_request(&mut input).is_err());
    }

    #[test]
    fn read_request_rejects_empty_input() {
        let mut input = Cursor::new(Vec::new());
        assert!(read_request(&mut input).is_err());
    }

    #[test]
    fn response_is_one_object_and_one_trailing_newline() {
        let mut buf = Vec::new();
        write_response(&mut buf, &sample()).unwrap();
        assert_eq!(buf.iter().filter(|&&b| b == b'\n').count(), 1);
        assert_eq!(*buf.last().unwrap(), b'\n');
    }

    #[test]
    fn response_round_trips_through_framing() {
        let mut buf = Vec::new();
        write_response(&mut buf, &sample()).unwrap();
        let mut cursor = Cursor::new(buf);
        assert_eq!(read_response(&mut cursor).unwrap(), sample());
    }

    #[test]
    fn request_round_trips_through_framing() {
        let mut buf = Vec::new();
        write_request(&mut buf, &Request::GetFocus).unwrap();
        let mut cursor = Cursor::new(buf);
        assert_eq!(read_request(&mut cursor).unwrap(), Request::GetFocus);
    }
}
