---
type: Overview
title: "Crates — Context"
description: "Planned Rust crate boundaries, provider isolation, and shared responsibilities."
section: crates
kind: context
tags: [crates, context, rust, workspace, traits, providers]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Crates — Context

## What This Section Covers

Every Rust crate in the `crates/` directory. The workspace follows a
hub-and-spoke pattern: `skills-core` at the center defines traits and
models, provider crates implement the `SkillRegistry` trait, and the
`pixi-skills` CLI binary wires them together.

## Crate Dependency Hierarchy

```
pixi-skills (CLI binary)
  ├── skills-core
  ├── skills-provider-github
  │     └── skills-core
  ├── skills-provider-conda
  │     ├── skills-core
  │     ├── rattler_conda_types
  │     ├── rattler_repodata_gateway
  │     ├── rattler_package_streaming
  │     └── rattler_lock
  ├── skills-provider-prefix
  │     └── skills-core
  └── skills-provider-pypi
        └── skills-core

xtask (build automation — never depends on runtime crates directly,
       except pixi-skills for clap Command introspection)
  └── pixi-skills (as a library dependency for cli-docs generation)
```

## Design Principles for Crates

### 1. skills-core owns all shared types
`Skill`, `SkillId`, `SkillSource`, `SkillSummary`, `VersionReq` — all
defined in `skills-core`. Provider crates depend on `skills-core` but
never on each other.

### 2. The SkillRegistry trait is the extension seam
```rust
trait SkillRegistry {
    async fn search(&self, query: &str) -> Result<Vec<SkillSummary>>;
    async fn list(&self, source: &SkillSource) -> Result<Vec<SkillSummary>>;
    async fn fetch(&self, id: &SkillId, version: &VersionReq) -> Result<Skill>;
    fn supports(&self, source: &SkillSource) -> bool;
}
```
Adding a new provider = adding a new crate that implements this trait.
Zero changes to core or CLI (the CLI discovers providers at compile time
via feature flags or at runtime via a provider registry).

### 3. The CLI is thin
`pixi-skills` (the binary) contains only clap command definitions and
dispatching logic. All business logic lives in `skills-core` or the
provider crates. This keeps the binary crate fast to compile and easy
to test (integration tests call the library, not the binary).

### 4. xtask is never published
`xtask` has `publish = false` in its Cargo.toml. It exists solely for
build automation. It depends on `pixi-skills` as a library to
introspect the clap command tree for CLI docs generation, but this is
a dev-time dependency only.

### 5. Provider crates are optional features of the CLI
The CLI's Cargo.toml uses feature flags to include/exclude providers:
```toml
[features]
default = ["github", "conda"]
github  = ["dep:skills-provider-github"]
conda   = ["dep:skills-provider-conda"]
prefix  = ["dep:skills-provider-prefix"]
pypi    = ["dep:skills-provider-pypi"]
```
This allows building a minimal CLI with only the providers you need.

## Key Crate Responsibilities

| Crate | Owns | Does NOT own |
|---|---|---|
| `skills-core` | Trait defs, data models, manifest parsing, installer, agent detection | Network I/O, provider-specific logic |
| `skills-provider-*` | Network I/O, API auth, format conversion for one source | Skill installation, agent config paths |
| `pixi-skills` | CLI UX, subcommand routing, output formatting, error display | Business logic, provider implementation |
| `xtask` | Codegen, release automation, workspace linting | Runtime behavior |

## External Crate Dependencies (Key)

| External Crate | Used By | Purpose |
|---|---|---|
| `clap` v4 | pixi-skills, xtask | CLI parsing, help generation, completions |
| `rattler_*` | skills-provider-conda | conda repodata, package streaming, lock format |
| `reqwest` | provider crates | HTTP client for GitHub API, PyPI API |
| `serde` / `toml` | skills-core | Parsing skills.toml, skills-lock.toml |
| `schemars` | xtask | JSON Schema generation from Rust types |
| `xshell` | xtask | Shell command execution in xtask |
| `toml_edit` | xtask | Programmatic Cargo.toml modification |

## Related Concepts

- [skills-core](./skills-core.md)
- [pixi-skills CLI](./pixi-skills-cli.md)
- [Dependency Graph](../architecture/dependency-graph.md)
