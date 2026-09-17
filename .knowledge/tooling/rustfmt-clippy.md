---
title: "rustfmt & clippy"
section: tooling
kind: detail
tags: [tooling, rustfmt, clippy, formatting, linting, rust]
relates_to:
  - tooling/CONTEXT
  - pixi/tasks
  - conventions/config-files
status: stable
created: 2025-01-01
updated: 2025-01-01
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

# Use the 2024 edition style (stable in Rust 1.80+)
edition = "2021"

# Maximum line width
max_width = 100

# Use block indent (not visual indent)
indent_style = "Block"

# Imports
imports_granularity = "Module"        # Group imports by module
group_imports = "StdExternalCrate"    # Order: std → external → crate

# Formatting choices
use_field_init_shorthand = true       # Foo { x } instead of Foo { x: x }
use_try_shorthand = true              # ? instead of try!()
format_code_in_doc_comments = true    # Format code blocks in /// comments
```

### Key Formatting Choices

| Setting | Value | Rationale |
|---|---|---|
| `max_width = 100` | 100 chars | Wider than default 80 — modern monitors can handle it. Reduces line wrapping in function signatures with generic bounds. |
| `imports_granularity = "Module"` | Module-level | `use std::collections::{HashMap, HashSet}` — groups related imports, reduces import line count. |
| `group_imports = "StdExternalCrate"` | Three groups | Clear visual separation: `std` → `external` crates → `crate`-internal. Deterministic ordering. |
| `format_code_in_doc_comments = true` | Enabled | Ensures code examples in `///` doc comments are formatted consistently with the rest of the codebase. |

### Stable vs Nightly Features

All settings in our `rustfmt.toml` are **stable**. We do not use
nightly-only rustfmt features (e.g., `imports_layout`,
`wrap_comments`). This ensures formatting works with the stable
toolchain installed by pixi.

If a nightly feature is desired in the future, it should be discussed
as an ADR, since it would require pinning a nightly toolchain in
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
expect_used = "warn"                  # Prefer ? with anyhow/thiserror
panic = "deny"                        # No panics in library code
todo = "warn"                         # TODOs should be tracked in issues
dbg_macro = "deny"                    # No debug prints in committed code
print_stdout = "warn"                 # Use tracing instead of println!
print_stderr = "warn"                 # Use tracing instead of eprintln!

# ── Warn (doesn't fail CI, but shows in output) ───────────────────
# Style and idiom suggestions:
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
# Compiler-level lints:
unsafe_code = "deny"                  # No unsafe code
missing_docs = "warn"                 # Public items should be documented
unused_imports = "deny"               # Clean imports
dead_code = "warn"                    # Remove unused code
```

### Per-Crate Lint Inheritance

Each crate inherits workspace lints:

```toml
# crates/skills-core/Cargo.toml
[lints]
workspace = true
```

Individual crates can override specific lints if needed:

```toml
# crates/pixi-skills/Cargo.toml (CLI binary)
[lints]
workspace = true

[lints.clippy]
# The CLI binary uses println! for user output
print_stdout = "allow"
print_stderr = "allow"
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
