---
title: "Taplo"
section: tooling
kind: detail
tags: [tooling, taplo, toml, formatting, validation, linting]
relates_to:
  - tooling/CONTEXT
  - pixi/tasks
  - conventions/config-files
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Taplo

A TOML formatter, linter, and language server. Ensures consistent
formatting across all TOML files in the workspace: `pixi.toml`,
`Cargo.toml`, `deny.toml`, `taplo.toml` itself, and any other TOML
configuration.

---

## Installation

```toml
# pixi.toml
[feature.lint.dependencies]
taplo = ">=0.9"
```

Installed via pixi from conda-forge. Available in the `default` and
`all` environments (via the `lint` feature).

---

## Configuration: `taplo.toml`

```toml
# taplo.toml (workspace root)

[formatting]
align_entries = false
indent_string = "    "
reorder_keys = true
column_width = 100
array_trailing_comma = true
array_auto_expand = true
array_auto_collapse = false
compact_arrays = false
compact_inline_tables = false

# Reorder keys in dependency tables for readability
[[rule]]
keys = [
  "dependencies",
  "dev-dependencies",
  "build-dependencies",
  "workspace.dependencies",
]
formatting = { reorder_keys = true }

# Don't reorder keys in [package] — name/version/edition order matters
[[rule]]
keys = ["package"]
formatting = { reorder_keys = false }

# Don't reorder pixi task definitions — logical ordering matters
[[rule]]
keys = ["feature.*.tasks", "tasks"]
formatting = { reorder_keys = false }

[exclude]
paths = [
  ".pixi/**",
  "target/**",
  "node_modules/**",
  "dist/**",
]
```

---

## What Taplo Formats

| File | Location | Notes |
|---|---|---|
| `pixi.toml` | workspace root | The most frequently edited TOML file |
| `Cargo.toml` (root) | workspace root | Workspace member declarations |
| `Cargo.toml` (crates) | `crates/*/Cargo.toml` | Per-crate dependencies |
| `Cargo.toml` (xtask) | `xtask/Cargo.toml` | xtask dependencies |
| `deny.toml` | workspace root | cargo-deny configuration |
| `taplo.toml` | workspace root | Taplo's own config (yes, it formats itself) |
| `rustfmt.toml` | workspace root | rustfmt configuration |
| `.config/nextest.toml` | `.config/` | cargo-nextest configuration |

---

## pixi Task Integration

```toml
# pixi.toml
[feature.rust.tasks]
fmt-toml       = "taplo fmt"
fmt-check-toml = "taplo check"

# Composites
fmt       = { depends-on = ["fmt-rust", "fmt-toml"] }
fmt-check = { depends-on = ["fmt-check-rust", "fmt-check-toml"] }
lint-toml = "taplo check"
lint      = { depends-on = ["lint-rust", "lint-toml", "lint-deps", "lint-workspace"] }
```

### Command Reference

| Command | Purpose | Exit code |
|---|---|---|
| `taplo fmt` | Format all TOML files in place | 0 (always) |
| `taplo fmt --check` | Check formatting without modifying | 1 if unformatted |
| `taplo check` | Validate TOML syntax + check formatting | 1 if invalid or unformatted |
| `taplo lint` | Advanced linting rules (schema validation) | 1 if violations |

**Note**: we use `taplo check` (not `taplo fmt --check`) in CI because
`check` also validates TOML syntax, not just formatting.

---

## Schema Validation

Taplo can validate TOML files against JSON Schemas. This is
particularly useful for `pixi.toml` and `Cargo.toml`:

```toml
# taplo.toml

# Validate Cargo.toml files against the official schema
[[rule]]
include = ["**/Cargo.toml"]
[rule.schema]
url = "https://json.schemastore.org/cargo.json"

# Validate pixi.toml against the pixi schema
[[rule]]
include = ["pixi.toml"]
[rule.schema]
url = "https://pixi.sh/latest/schema/manifest/schema.json"
```

This catches structural errors (wrong key names, invalid value types)
at format-check time, before any tool tries to parse the file.

---

## Editor Integration

### VS Code / Cursor

Install the Even Better TOML extension (`tamasfe.even-better-toml`),
which is powered by Taplo:

```jsonc
// .vscode/settings.json
{
  "evenBetterToml.formatter.alignEntries": false,
  "evenBetterToml.formatter.indentString": "    ",
  "evenBetterToml.formatter.reorderKeys": true,
  "evenBetterToml.formatter.columnWidth": 100,
  "[toml]": {
    "editor.defaultFormatter": "tamasfe.even-better-toml"
  }
}
```

The extension reads `taplo.toml` automatically, so settings stay
in sync between editor and CLI.

### Zed

Zed has built-in TOML support via Taplo. No additional configuration
needed — it reads `taplo.toml` from the workspace root.

---

## Formatting Philosophy

### Why reorder keys?
Alphabetically ordered keys in dependency tables make it easy to scan
for a specific dependency and produce deterministic diffs. Two
developers adding different dependencies won't create merge conflicts
if keys are sorted.

### Why NOT reorder `[package]` keys?
The conventional order is `name`, `version`, `edition`, `description`,
`license`, `repository`. This order is semantically meaningful and
universally expected. Alphabetical ordering would put `description`
before `edition`, which is confusing.

### Why NOT reorder pixi tasks?
Tasks are ordered by logical grouping (build → test → lint → format →
docs → release). Alphabetical ordering would scatter related tasks
across the file.

---

## Common Issues and Solutions

### Issue: Taplo reformats `pixi.toml` differently than pixi writes it
**Solution**: This can happen if pixi writes TOML with different
formatting preferences. Run `taplo fmt` after `pixi add` to normalize.
The `taplo.toml` config is the source of truth for formatting.

### Issue: Taplo and cargo disagree on Cargo.toml formatting
**Solution**: Taplo's formatting is independent of cargo's. After
`cargo add`, run `taplo fmt` to normalize. The two tools don't
conflict — they just have different defaults.

### Issue: Schema validation fails for valid pixi.toml features
**Solution**: pixi's schema may not cover all features in newer
versions. Pin the schema URL to a specific pixi version, or disable
schema validation for `pixi.toml` if it causes false positives.
