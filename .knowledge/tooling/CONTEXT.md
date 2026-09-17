---
type: Overview
title: "Tooling — Context"
description: "Selection principles and planned integration of developer tooling across the workspace."
section: tooling
kind: context
tags: [tooling, context, linting, formatting, testing, audit]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Tooling — Context

## What This Section Covers

Every developer tool used in the pixi-skills project, beyond the core
language runtimes (Rust, bun). These tools handle formatting, linting,
testing, auditing, and commit/release automation.

## Tool Selection Principles

### 1. One tool per concern, no overlap
- Rust formatting: rustfmt (only)
- TS/JS/CSS formatting AND linting: Biome (replaces ESLint + Prettier)
- TOML formatting: Taplo (only)
- Dependency auditing: cargo-deny (only)

There is no ESLint. There is no Prettier. Biome replaces both with a
single, fast binary. This eliminates config sprawl and conflicting rules.

### 2. Prefer Rust-native tools
Every tool in this list is either written in Rust (Biome, Taplo,
cargo-deny, cargo-nextest, convco, rustfmt, clippy) or is a first-party
Rust tool. This is not ideological — Rust tools are typically:
- Single static binaries (easy to distribute via conda-forge)
- Fast (no JIT warmup, no node_modules resolution)
- Cross-platform without runtime dependencies

### 3. Everything from conda-forge
All tools are installed via pixi from conda-forge. This means:
- Versions are pinned in `pixi.lock`
- Every developer and CI runner uses the exact same tool versions
- No `cargo install` during CI (slow, uncached, version drift)
- No `npm install -g` (pollutes global state)

### 4. Tools invoked via pixi tasks, not directly
Developers type `pixi run lint`, not `cargo clippy && taplo check &&
biome check`. The pixi task layer composes tools into logical workflows.
Individual tool invocation is always possible as an escape hatch.

## Tool Responsibility Matrix

| Concern | Tool | Config File | pixi Task |
|---|---|---|---|
| Rust format | `rustfmt` | `rustfmt.toml` | `fmt-rust` |
| Rust lint | `clippy` | `Cargo.toml [lints]` | `lint-rust` |
| Rust test | `cargo-nextest` | `.config/nextest.toml` | `test` |
| TOML format | `taplo` | `taplo.toml` | `fmt-toml` |
| TS/JS/CSS format+lint | `biome` | `biome.json` | `fmt-ts`, `lint-ts` |
| Dependency audit | `cargo-deny` | `deny.toml` | `lint-deps` |
| Commit convention | `convco` | `.convco` | `commit`, `check-commits` |
| Changelog | `convco` | `.convco` | `changelog` |
| Version calc | `convco` | `.convco` | `version`, `version-bump` |

## Composite pixi Tasks

Individual tools are composed into higher-level tasks:

```
fmt-all       = fmt-rust + fmt-toml + fmt-ts
lint-all      = lint-rust + lint-toml + lint-deps + lint-workspace + lint-ts
fmt-check-all = fmt-check-rust + fmt-check-toml + fmt-check-ts
ci            = fmt-check-all + lint-all + test + test-doc + check-commits + docs-build
pre-commit    = fmt-check-all + lint-all + test
```

## Config File Locations (Quick Reference)

```
pixi-skills/
├── rustfmt.toml             # Rust formatting rules
├── biome.json               # Biome root config (TS/JS/CSS)
├── deny.toml                # cargo-deny: licenses, advisories, bans
├── taplo.toml               # TOML formatting rules
├── .convco                  # Conventional commit types + scopes
├── .config/
│   └── nextest.toml         # cargo-nextest: profiles, timeouts, retries
└── apps/pixi-skills-docs/
    └── biome.json            # Biome extension for docs app
```

## Related Concepts

- [Biome](./biome.md)
- [Taplo](./taplo.md)
- [cargo-deny](./cargo-deny.md)
- [cargo-nextest](./cargo-nextest.md)
- [convco](./convco.md)
- [rustfmt & clippy](./rustfmt-clippy.md)
- [Pixi Tasks](../pixi/tasks.md)
