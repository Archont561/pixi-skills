//! xtask — build automation entry point, invoked via `cargo xtask`
//! (alias in `.cargo/config.toml`) or `pixi run`.

// Build automation invoked through `cargo xtask`: its user output is the
// terminal. (Per-crate exceptions live here, not in Cargo.toml: with
// `lints.workspace = true` cargo forbids `[lints.*]` overrides in the same crate.)
#![allow(clippy::print_stdout, clippy::print_stderr)]

fn main() {
    // Phase 0 skeleton: the real subcommand dispatcher lands with xtask.
    eprintln!("cargo xtask: subcommands land in a later phase");
}
