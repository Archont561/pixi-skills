//! pixi-skills — the CLI binary (also a pixi extension: `pixi skills ...`).
//!
//! Thin over skills-core + the provider crates. Real clap command tree lands
//! in Phase 2 (see `.knowledge/crates/pixi-skills-cli.md`); this is the
//! Phase 0 skeleton so the workspace builds and CI runs today.

// The CLI binary talks to the user through stdout/stderr; that is its job.
// (Per-crate exceptions live here, not in Cargo.toml: with `lints.workspace
// = true` cargo forbids `[lints.*]` overrides in the same crate.)
#![allow(clippy::print_stdout, clippy::print_stderr)]

fn main() {
    println!("pixi-skills 0.1.0 (workspace scaffold)");
}
