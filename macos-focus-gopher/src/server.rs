//! The socket server: a small blocking accept-loop. For each connection it
//! verifies the peer is the same user, reads one request, and writes one
//! `FocusState` reply. No async runtime — a one-shot request/response per
//! connection needs none.

use crate::{focus, protocol, socket};
use std::io::{self, BufReader};
use std::os::unix::net::{UnixListener, UnixStream};

/// Serve connections forever. A per-connection error is logged and the loop
/// continues — one misbehaving client must not take the helper down.
pub fn serve(listener: &UnixListener) -> io::Result<()> {
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(e) = handle_connection(stream) {
                    eprintln!("focus-gopherd: connection error: {e}");
                }
            }
            Err(e) => eprintln!("focus-gopherd: accept error: {e}"),
        }
    }
    Ok(())
}

/// Accept and handle exactly one connection, then return.
///
/// This is test support, not part of the helper's intended API — the daemon uses
/// [`serve`]. It must be `pub` because the integration tests live in a separate
/// crate and can only drive a public entry point, so it is `#[doc(hidden)]` to
/// keep it out of the documented surface.
#[doc(hidden)]
pub fn serve_once(listener: &UnixListener) -> io::Result<()> {
    let (stream, _addr) = listener.accept()?;
    handle_connection(stream)
}

fn handle_connection(stream: UnixStream) -> io::Result<()> {
    let peer = socket::peer_uid(&stream)?;
    if peer != socket::current_uid() {
        return Err(io::Error::new(
            io::ErrorKind::PermissionDenied,
            "rejecting connection from a different user",
        ));
    }

    let mut reader = BufReader::new(stream.try_clone()?);
    // M1 has exactly one request; reading it validates the protocol framing.
    let _request = protocol::read_request(&mut reader)?;

    let state = focus::get_focus();
    let mut writer = stream;
    protocol::write_response(&mut writer, &state)
}
