---
type: Architecture
title: "Dependency Graph"
description: "Planned crate dependencies, external libraries, and code-generation ordering."
section: architecture
kind: detail
tags: [architecture, dependencies, crates, codegen, build, rattler]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Dependency Graph

This page documents three dependency graphs:
1. **Crate dependency DAG** — which crates depend on which
2. **External dependency map** — key third-party crates and why
3. **Codegen pipeline** — how generated artifacts flow through the build

---

## 1. Crate Dependency DAG

```
                    ┌──────────────┐
                    │  skills-core │
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┬──────────────┐
            │              │              │              │
            ▼              ▼              ▼              ▼
   ┌────────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
   │ provider-github│ │provider- │ │provider- │ │provider- │
   │                │ │conda     │ │prefix    │ │pypi      │
   └───────┬────────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
           │               │            │             │
           └───────────────┼────────────┼─────────────┘
                           │            │
                           ▼            │
                    ┌──────────────┐    │
                    │  pixi-skills │ ◄──┘
                    │  (CLI bin)   │
                    └──────┬───────┘
                           │
                           │ (lib dep for clap introspection)
                           ▼
                    ┌──────────────┐
                    │    xtask     │
                    │ (pub=false)  │
                    └──────────────┘
```

### Dependency Rules

1. **skills-core depends on nothing workspace-internal.**
   It is the leaf of the dependency tree. All shared types,
   traits, and models are defined here.

2. **Provider crates depend only on skills-core.**
   Providers never depend on each other. This ensures providers
   can be developed, tested, and compiled independently.

3. **pixi-skills (CLI) depends on skills-core + all providers.**
   Providers are gated behind cargo feature flags:
   ```toml
   [features]
   default = ["github", "conda"]
   github  = ["dep:skills-provider-github"]
   conda   = ["dep:skills-provider-conda"]
   prefix  = ["dep:skills-provider-prefix"]
   pypi    = ["dep:skills-provider-pypi"]
   ```

4. **xtask depends on pixi-skills as a library.**
   This is the only "upward" dependency. xtask imports the clap
   `Command` struct from pixi-skills to generate CLI docs and
   completions. This dependency is compile-time only — xtask
   is never a runtime dependency of anything.

5. **Nothing depends on xtask.**
   xtask is a terminal node. It is never `use`d by any other crate.

---

## 2. External Dependency Map

### skills-core

| Dependency | Purpose |
|---|---|
| `serde` | Serialize/deserialize Skill, SkillSource, manifests |
| `serde_json` | JSON serialization for lockfile hashes, API responses |
| `toml` | Parse skills.toml manifest |
| `semver` | Version requirement parsing and matching |
| `thiserror` | Ergonomic error types |
| `tracing` | Structured logging |
| `directories` | Platform-appropriate config/data/cache dirs |
| `which` | Detect installed agents by finding their binaries |

### skills-provider-github

| Dependency | Purpose |
|---|---|
| `reqwest` | HTTP client for GitHub API / raw content |
| `octocrab` (optional) | Typed GitHub API client (if we need more than raw fetches) |
| `tokio` | Async runtime |

### skills-provider-conda

| Dependency | Purpose |
|---|---|
| `rattler_conda_types` | Channel, PackageName, Version, MatchSpec, RepoDataRecord |
| `rattler_repodata_gateway` | Fetch + cache repodata.json from conda channels |
| `rattler_package_streaming` | Extract files from .conda / .tar.bz2 archives |
| `rattler_lock` | Read/write conda lockfiles (for lockfile integration) |
| `rattler_networking` | Authentication middleware for private channels |
| `tokio` | Async runtime |

### skills-provider-prefix

| Dependency | Purpose |
|---|---|
| `reqwest` | HTTP client for prefix.dev API |
| `rattler_conda_types` | Shared types with conda provider |
| `tokio` | Async runtime |

### pixi-skills (CLI)

| Dependency | Purpose |
|---|---|
| `clap` v4 (derive) | CLI argument parsing, help generation |
| `clap_complete` | Shell completion generation |
| `tokio` | Async runtime (main entry point) |
| `tracing-subscriber` | Log output formatting |
| `console` | Terminal colors and styling |
| `indicatif` | Progress bars for downloads/installs |
| `tabled` | Table output for `pixi skills list` |
| `dialoguer` | Interactive prompts for `pixi skills add` |

### xtask

| Dependency | Purpose |
|---|---|
| `clap` v4 (derive) | xtask's own CLI parsing |
| `xshell` | Shell command execution (cross-platform) |
| `toml_edit` | Programmatic Cargo.toml modification (preserves formatting) |
| `schemars` | JSON Schema generation from Rust types |
| `sha2` | SHA256 checksums for dist artifacts |
| `flate2` | Gzip compression for tarballs |
| `tar` | Tarball creation |
| `glob` | File pattern matching for workspace lint |
| `anyhow` | Error handling in build scripts |

---

## 3. Codegen Pipeline

### Overview

```
┌─────────────────────────┐
│     Rust source code    │
│                         │
│  pixi-skills/cli.rs     │ ──── clap Command struct
│  skills-core/manifest.rs│ ──── Config struct with #[derive(JsonSchema)]
│  pixi-skills/cli.rs     │ ──── clap Command struct (for completions)
└───────────┬─────────────┘
            │
            │  cargo xtask cli-docs
            │  cargo xtask schema
            │  cargo xtask completions
            ▼
┌─────────────────────────────────────────────┐
│           Generated artifacts               │
│                                             │
│  apps/.../src/content/docs/cli/             │
│    ├── find.mdx                             │
│    ├── add.mdx                              │
│    ├── remove.mdx                           │
│    ├── list.mdx                             │
│    ├── update.mdx                           │
│    ├── lock.mdx                             │
│    └── doctor.mdx                           │
│                                             │
│  apps/.../public/                           │
│    └── skills-schema.json                   │
│                                             │
│  completions/                               │
│    ├── pixi-skills.bash                     │
│    ├── pixi-skills.zsh                      │
│    ├── pixi-skills.fish                     │
│    └── _pixi-skills.ps1                     │
└───────────┬─────────────────────────────────┘
            │
            │  bun run build (astro build)
            ▼
┌─────────────────────────┐
│    dist/ (static HTML)  │ ──── Deployed to GitHub Pages
└─────────────────────────┘
```

### Codegen Flow (pixi task dependency chain)

```
pixi run -e all docs-build
    │
    ├──→ cli-docs          (cargo xtask cli-docs --output .../cli/)
    │       │
    │       ├── Compiles pixi-skills crate (if needed)
    │       ├── Instantiates pixi_skills::cli::build_command()
    │       ├── Recursively walks all subcommands
    │       ├── For each subcommand:
    │       │     ├── Extracts name, about, long_about, args, flags
    │       │     ├── Renders MDX with YAML frontmatter
    │       │     └── Writes to apps/.../src/content/docs/cli/{name}.mdx
    │       └── Done
    │
    ├──→ schema            (cargo xtask schema --output .../skills-schema.json)
    │       │
    │       ├── Imports skills_core::manifest::SkillsConfig
    │       ├── Calls schemars::schema_for::<SkillsConfig>()
    │       ├── Writes JSON Schema to public/skills-schema.json
    │       └── Done
    │
    └──→ docs-build-raw    (bun run build, cwd: apps/pixi-skills-docs)
            │
            ├── Depends on cli-docs + schema (pixi ensures ordering)
            ├── Astro reads src/content/docs/ (including generated cli/*.mdx)
            ├── Astro reads public/skills-schema.json (available at /skills-schema.json)
            ├── Pagefind indexes all pages (including generated CLI docs)
            └── Outputs dist/
```

### Checked-In vs Generated

| Artifact | Checked into git? | Why |
|---|---|---|
| `cli/*.mdx` | ✅ Yes | Docs contributors can preview without Rust toolchain |
| `skills-schema.json` | ✅ Yes | Referenced by external tools, should be stable URL |
| `completions/*` | ✅ Yes | Users source these without building from source |
| `dist/` | ❌ No (.gitignore) | Rebuilt in CI on every deploy |
| `CHANGELOG.md` | ✅ Yes | Human-readable release history |

Checked-in generated files are always regenerated in CI to catch drift.
The CI `docs-build` task runs codegen before Astro build, ensuring
freshness. If a developer forgets to regenerate after a clap change,
CI will produce the correct output anyway.

---

## 4. Build Ordering Summary

### Full CI build order (as executed by `pixi run -e all ci`)

```
1. fmt-check-rust        (cargo fmt --check)            [parallel group 1]
2. fmt-check-toml        (taplo check)                  [parallel group 1]
3. fmt-check-ts          (biome check, cwd: docs)       [parallel group 1]
4. lint-rust             (cargo clippy)                  [parallel group 2]
5. lint-toml             (taplo check)                   [parallel group 2]
6. lint-deps             (cargo deny check)              [parallel group 2]
7. lint-workspace        (cargo xtask lint)              [parallel group 2]
8. lint-ts               (biome check, cwd: docs)        [parallel group 2]
9. test                  (cargo nextest run)              [parallel group 3]
10. test-doc             (cargo test --doc)               [parallel group 3]
11. check-commits        (convco check)                   [parallel group 3]
12. cli-docs             (cargo xtask cli-docs)           [sequential]
13. schema               (cargo xtask schema)             [sequential]
14. docs-build-raw       (bun run build)                  [sequential, after 12+13]
```

Steps 1–11 have no mutual dependencies and could run in parallel
(pixi resolves the dependency graph). Steps 12–14 are sequential:
codegen must complete before the Astro build.

## Related Concepts

- [Crates — Context](../crates/CONTEXT.md)
- [skills-core](../crates/skills-core.md)
- [skills-provider-conda](../crates/skills-provider-conda.md)
- [xtask](../crates/xtask.md)
- [Three-Layer Task Model](./three-layer-model.md)
