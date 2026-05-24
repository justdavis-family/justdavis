//! The `focus-gopher` CLI. Stubbed in M1 (not yet wired up); M2 implements the
//! thin client that connects to the socket, performs `get_focus()`, prints the
//! `FocusState` as JSON, and exits non-zero on a `failed` outcome.

fn main() {
    eprintln!("focus-gopher: the CLI is not yet wired up (arriving in milestone 2).");
    eprintln!(
        "For now, run the helper `focus-gopherd` and speak the line-delimited JSON \
         socket protocol directly (e.g. with `nc -U <socket-path>`)."
    );
    eprintln!("See the project README for details.");
}
