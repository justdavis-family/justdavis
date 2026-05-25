//! The Focus Gopher helper daemon: binds the per-user socket and serves
//! `get_focus()` requests. For now the answer is stubbed (no database is read).

use macos_focus_gopher::{server, socket};
use std::process::ExitCode;

fn main() -> ExitCode {
    let path = socket::socket_path();

    let listener = match socket::bind(&path) {
        Ok(listener) => listener,
        Err(e) => {
            eprintln!("focus-gopherd: failed to bind {}: {e}", path.display());
            return ExitCode::FAILURE;
        }
    };

    eprintln!("focus-gopherd: listening on {}", path.display());
    eprintln!(
        "focus-gopherd: early development — get_focus() is stubbed and returns \
         a failed/macos_unsupported result (no Focus database is read yet)."
    );

    match server::serve(&listener) {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("focus-gopherd: server error: {e}");
            ExitCode::FAILURE
        }
    }
}
