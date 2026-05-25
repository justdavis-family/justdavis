//! The `focus-gopher` CLI. Stubbed for now (not yet wired up); the real client
//! will connect to the socket, perform `get_focus()`, print the `FocusState` as
//! JSON, and exit non-zero on a `failed` outcome.

fn main() {
    eprintln!("focus-gopher: the CLI is not yet wired up.");
    eprintln!(
        "For now, run the helper `focus-gopherd` and speak the line-delimited JSON \
         socket protocol directly (e.g. with `nc -U <socket-path>`)."
    );
    eprintln!("See the project README for details.");
}
