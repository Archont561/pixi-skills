---
type: Reference
title: "rustfmt & clippy"
description: "Planned Rust formatting and linting configuration with rustfmt and clippy."
section: tooling
kind: detail
tags: [tooling, rustfmt, clippy, formatting, linting, rust]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# rustfmt & clippy

The standard Rust formatting and linting tools. Both ship with the
Rust toolchain installed by pixi from conda-forge.

---

## rustfmt

### Purpose

Formats all Rust source code to a consistent style. Removes
formatting debates from code review — if `cargo fmt --check` passes,
the formatting is correct.

### Configuration: `rustfmt.toml`

```toml
# rustfmt.toml (workspace root)

# Maximum line width
max_width = 100

# Formatting choices
use_field_init_shorthand = true       # Foo { x } instead of Foo { x: x }
use_try_shorthand = true              # ? instead of try!()
```

Several settings the earlier draft of this page listed are **not** in
the committed file, because they are **nightly-only** rustfmt features
(measured with the conda-forge stable toolchain, 2026-09-21 — stable
rustfmt warns "unstable features are only available in nightly channel"
and ignores them):

- `indent_style` (block vs visual indent)
- `format_code_in_doc_comments`
- `imports_granularity` / `group_imports` (module-granularity import
  grouping)

Enable any of them only if a nightly rustfmt job is added (ADR-worthy).
Also, `edition` is not set: `cargo fmt` passes each crate's edition
from its manifest (all crates are edition 2024), and pinning a
different one in `rustfmt.toml` would only risk diverging from it.

### Key Formatting Choices

| Setting | Value | Rationale |
|---|---|---|
| `max_width = 100` | 100 chars | Wider than default 80 — modern monitors can handle it. Reduces line wrapping in function signatures with generic bounds. |
| `use_field_init_shorthand = true` | Enabled | `Foo { x }` instead of `Foo { x: x }`. |

### Stable vs Nightly Features

Every setting in the committed `rustfmt.toml` is **stable** — the file
was pruned to the stable set in 2026-09-21 after stable rustfmt warned
that the earlier draft's `indent_style` and `format_code_in_doc_comments`
were nightly-only. The nightly-only features we deliberately do *not*
use include `indent_style`, `format_code_in_doc_comments`,
`imports_granularity`, `group_imports`, `imports_layout`, and
`wrap_comments` — if one of them is wanted, it should be discussed as
an ADR, since it would require pinning a nightly toolchain in
`pixi.toml`.

---

## clippy

### Purpose

Rust's official linter. Catches common mistakes, suggests idiomatic
patterns, and enforces project-specific coding standards.

### Configuration: `Cargo.toml` (workspace level)

Clippy is configured via the `[workspace.lints.clippy]` section in
the root `Cargo.toml`:

```toml
# Cargo.toml (workspace root)

[workspace.lints.clippy]
# ── Deny (CI fails) ────────────────────────────────────────────────
# These are bugs or serious code smells:
unwrap_used = "deny"                  # Use ? or expect() with context
panic = "deny"                        # No panics in library code
dbg_macro = "deny"                    # No debug prints in committed code

# ── Warn (context-dependent) ──────────────────────────────────────
expect_used = "warn"                  # Prefer ? with anyhow/thiserror
todo = "warn"                         # TODOs should be tracked in issues
print_stdout = "warn"                 # Use tracing instead of println!
print_stderr = "warn"                 # Use tracing instead of eprintln!

# ── Warn (style and idiom suggestions) ─────────────────────────────
needless_pass_by_value = "warn"
redundant_closure_for_method_calls = "warn"
cloned_instead_of_copied = "warn"
flat_map_option = "warn"
implicit_clone = "warn"
inefficient_to_string = "warn"
manual_let_else = "warn"
semicolon_if_nothing_returned = "warn"
trivially_copy_pass_by_ref = "warn"
unnested_or_patterns = "warn"
unused_self = "warn"

# ── Allow (explicitly permitted) ───────────────────────────────────
# These are intentionally allowed:
module_name_repetitions = "allow"     # skills_core::skill::Skill is fine
too_many_arguments = "allow"          # Complex constructors are acceptable
missing_errors_doc = "allow"          # Errors are self-explanatory via types

[workspace.lints.rust]
# Compiler-level lints only — a clippy lint here (or the reverse)
# triggers `renamed_and_removed_lints`.
unsafe_code = "forbid"                # No unsafe code (stricter than deny)
missing_docs = "warn"                 # Public items should be documented
unused_imports = "deny"               # Clean imports
dead_code = "warn"                    # Remove unused code
```

> `missing_errors_doc` used to be a rustc lint; recent toolchains moved
> it to clippy (measured 2026-09-21 on rust 1.98: a `[lints.rust]` entry
> for it warns `renamed_and_removed_lints`). It lives in the clippy
> table above.

### Per-Crate Lint Inheritance

Each crate inherits workspace lints:

```toml
# crates/skills-core/Cargo.toml
[lints]
workspace = true
```

Individual crates **cannot** override specific lints in their own
`Cargo.toml` while `lints.workspace = true` — cargo rejects the mix
with "cannot override `workspace.lints` in `lints`" (measured, 2026-09-21).
Per-crate exceptions therefore live in the source, at crate level:

```rust
// crates/pixi-skills/src/main.rs (CLI binary)
// The CLI binary uses println! for user output; that is its job.
#![allow(clippy::print_stdout, clippy::print_stderr)]
```

### Clippy Lint Categories

| Category | Examples | Our approach |
|---|---|---|
| `correctness` | Infinite loops, invalid regex | All enabled (default) |
| `suspicious` | Redundant comparisons, unused results | All enabled |
| `style` | Inconsistent naming, verbose patterns | Selected warnings |
| `complexity` | Unnecessary complexity, long functions | Selected warnings |
| `perf` | Unnecessary allocations, slow patterns | All enabled |
| `pedantic` | Very strict style rules | Selected only |
| `nursery` | Experimental lints | Not enabled |
| `cargo` | Cargo.toml issues | Not enabled (taplo + xtask lint handles this) |
| `restriction` | Very restrictive rules | Selected only (`unwrap_used`, `panic`, `dbg_macro`) |

---

## pixi Task Integration

```toml
# pixi.toml
[feature.rust.tasks]
fmt-rust       = "cargo fmt --all"
fmt-check-rust = "cargo fmt --all -- --check"
lint-rust      = "cargo clippy --workspace --all-targets -- -D warnings"

# Composites
fmt       = { depends-on = ["fmt-rust", "fmt-toml"] }
fmt-check = { depends-on = ["fmt-check-rust", "fmt-check-toml"] }
lint      = { depends-on = ["lint-rust", "lint-toml", "lint-deps", "lint-workspace"] }
```

### Command Reference

| Command | Purpose |
|---|---|
| `cargo fmt --all` | Format all crates in the workspace |
| `cargo fmt --all -- --check` | Check formatting (CI — no modifications) |
| `cargo clippy --workspace --all-targets` | Lint all crates, all targets (lib, bin, test, bench) |
| `cargo clippy --workspace --all-targets -- -D warnings` | Treat warnings as errors (CI) |
| `cargo clippy --workspace --fix` | Auto-fix applicable lint suggestions |

### The `-- -D warnings` Flag

In CI, clippy runs with `-D warnings` (deny warnings). This means
any clippy warning fails the build. Locally, developers can run
clippy without this flag to see warnings without failing:

```bash
pixi run lint-rust                    # CI mode: -D warnings
cargo clippy --workspace --all-targets  # Dev mode: warnings only
```

---

## Editor Integration

### VS Code / Cursor

```jsonc
// .vscode/settings.json
{
  "rust-analyzer.check.command": "clippy",
  "rust-analyzer.check.allTargets": true,
  "rust-analyzer.rustfmt.extraArgs": ["--config-path", "rustfmt.toml"],
  "[rust]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "rust-lang.rust-analyzer"
  }
}
```

This configures rust-analyzer to:
- Run clippy (not just `cargo check`) on save
- Check all targets (lib, bin, test)
- Use the workspace `rustfmt.toml` for formatting
- Format on save

### Zed

Zed uses rust-analyzer natively. Configure in `.zed/settings.json`:

```jsonc
{
  "lsp": {
    "rust-analyzer": {
      "initialization_options": {
        "check": {
          "command": "clippy",
          "allTargets": true
        }
      }
    }
  }
}
```

---

## Suppress Lints (When Necessary)

### Inline suppression

```rust
#[allow(clippy::too_many_arguments)]
fn complex_constructor(/* ... */) { /* ... */ }
```

### Module-level suppression

```rust
// At the top of a file
#![allow(clippy::module_name_repetitions)]
```

### Workspace-level suppression

Add to `[workspace.lints.clippy]` in root `Cargo.toml` (preferred
for project-wide decisions).

### Convention

Always add a comment explaining WHY a lint is suppressed:

```rust
// This function genuinely needs 8 parameters because it maps
// directly to the provider API response fields.
#[allow(clippy::too_many_arguments)]
fn from_api_response(/* ... */) { /* ... */ }
```

---

## Common Issues and Solutions

### Issue: clippy and rustfmt disagree on import ordering
**Solution**: This shouldn't happen with our config. If it does,
run `cargo fmt` first (it handles import formatting), then
`cargo clippy` (it doesn't care about import order with our settings).

### Issue: clippy false positive on a valid pattern
**Solution**: Suppress with `#[allow(clippy::...)]` + comment. If
the false positive is systemic, add to `[workspace.lints.clippy]`
with `"allow"` and document the reason.

### Issue: New Rust version introduces new clippy lints that break CI
**Solution**: This is expected when pixi updates the Rust toolchain.
Fix the new warnings (preferred) or temporarily allow them in
`[workspace.lints.clippy]` with a tracking issue to fix properly.
Pinning the Rust version in `pixi.toml` (`rust = "=1.80"`) prevents
surprise lint changes but delays security updates — use judiciously.

## Related Concepts

- [Tooling — Context](./CONTEXT.md)
- [Pixi Tasks](../pixi/tasks.md)
- [Config Files](../conventions/config-files.md)
