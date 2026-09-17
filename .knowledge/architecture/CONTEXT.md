---
title: "Architecture — Context"
section: architecture
kind: context
tags: [architecture, context, monorepo, workspace, design]
relates_to:
  - architecture/workspace-layout
  - architecture/three-layer-model
  - architecture/dependency-graph
  - architecture/design-decisions
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Architecture — Context

## What This Section Covers

The architecture of pixi-skills is a **polyglot monorepo** housing Rust
crates, a Bun/Astro documentation app, and a unified task orchestration
layer powered by pixi. This section documents the structural choices
and the reasoning behind them.

## Core Architectural Principles

### 1. Monorepo with clear language boundaries
Rust code lives in `crates/`. JS/TS code lives in `apps/`. They share
nothing at the language level — no wasm bindings, no napi. The glue
is pixi tasks and file-system codegen (xtask writes MDX files that
Astro reads).

### 2. Three layers of automation
Each layer does what it is best at:
- **pixi tasks** — cross-cutting orchestration, environment selection,
  dependency ordering between tasks, CI entrypoints
- **cargo xtask** — Rust-native automation that benefits from access
  to Rust types (clap Command introspection, schemars derivation,
  toml_edit for programmatic Cargo.toml manipulation)
- **bun scripts** — JS-native automation where Astro expects a JS
  runtime (dev server, static build, type checking)

### 3. Codegen over manual sync
CLI reference docs, JSON schema for `skills.toml`, and shell
completions are all generated from the real Rust source code by xtask.
They are checked-in artifacts so the docs site can build without
compiling Rust, but they are regenerated as part of the `docs-build`
pipeline to prevent drift.

### 4. Provider trait as the extension seam
The `SkillRegistry` trait in `skills-core` is the primary extension
point. Adding a new skill source (e.g., OCI registry, S3 bucket,
local filesystem) means implementing one trait in a new crate.
No changes to `skills-core` or the CLI.

### 5. Environments as capability sets
Pixi environments (`default`, `docs`, `release`, `all`) are not
deployment targets — they are capability sets. `default` has Rust +
lint tools. `docs` has bun + biome. `release` adds convco. `all`
combines everything. This keeps the day-to-day environment fast to
resolve and small to install.

## Key Relationships

```
architecture/workspace-layout  → describes the physical structure
architecture/three-layer-model → describes the automation layering
architecture/dependency-graph  → describes the build/codegen ordering
architecture/design-decisions  → records WHY choices were made

These pages are referenced by:
  crates/*    — for understanding where each crate fits
  pixi/*      — for understanding how pixi.toml maps to the arch
  cicd/*      — for understanding the CI pipeline ordering
```

## How to Use This Section

- **New contributor?** Start with `workspace-layout.md` to orient
  yourself in the repo, then read `three-layer-model.md` to understand
  the task system.
- **Adding a new provider crate?** Read `dependency-graph.md` to see
  where it fits, then `design-decisions.md` for naming conventions.
- **Questioning a design choice?** Check `design-decisions.md` for the
  ADR — it may already be documented with trade-offs.
