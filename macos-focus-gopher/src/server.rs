//! The socket server: a small blocking accept-loop. For each connection it reads
//! one request and writes one `FocusState` reply. No async runtime — a one-shot
//! request/response per connection needs none.

use crate::{focus, protocol};
use std::io::BufReader;
use std::os::unix::net::{UnixListener, UnixStream};

/// Serve connections forever. A per-connection error is logged and the loop
/// continues — one misbehaving client must not take the helper down.
pub fn serve(listener: &UnixListener) -> crate::Result<()> {
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                if let Err(e) = handle_connection(stream) {
                    tracing::warn!(error = %e, "connection error");
                }
            }
            Err(e) => tracing::warn!(error = %e, "accept error"),
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
pub fn serve_once(listener: &UnixListener) -> crate::Result<()> {
    let (stream, _addr) = listener.accept()?;
    handle_connection(stream)
}

fn handle_connection(stream: UnixStream) -> crate::Result<()> {
    // Access control is the socket's private per-user directory ($TMPDIR); see the
    // `socket` module. No peer-uid check is needed (or possible without `unsafe`).
    let mut reader = BufReader::new(stream.try_clone()?);
    // There is exactly one request for now; reading it validates the protocol framing.
    let _request = protocol::read_request(&mut reader)?;

    let state = focus::get_focus();
    let mut writer = stream;
    protocol::write_response(&mut writer, &state)
}
