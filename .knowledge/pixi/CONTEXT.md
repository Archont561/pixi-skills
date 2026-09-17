---
type: Overview
title: "Pixi — Context"
description: "Role of pixi in the planned workspace, dependency provisioning, and task orchestration."
section: pixi
kind: context
tags: [pixi, context, environments, tasks, conda-forge, reproducibility]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Pixi — Context

## What This Section Covers

The `pixi.toml` file at the workspace root is the single source of
truth for all environments, dependencies, and tasks. This section
explains how it is structured and why.

## Role of Pixi in This Project

Pixi serves three roles simultaneously:

### 1. Toolchain manager
Pixi installs Rust, bun, biome, taplo, cargo-deny, cargo-nextest, and
all other tools from conda-forge. Every developer and CI runner gets
the exact same versions, pinned in `pixi.lock`. No "works on my
machine" problems.

### 2. Task runner
`pixi run <task>` is the universal entry point. Tasks compose into
dependency chains (`docs-build` depends on `cli-docs` + `schema` +
`docs-build-raw`). Tasks can target specific environments and set
`cwd` for apps in subdirectories.

### 3. Environment multiplexer
Different workflows need different tools. A Rust developer doesn't
need bun. A docs contributor doesn't need cargo-deny. Pixi features
let us define capability sets, and environments combine features into
installable units.

## Design Decisions

### Why not just use cargo + bun directly?
- `cargo` doesn't know about bun. `bun` doesn't know about cargo.
  Neither can express "generate CLI docs with Rust, then build the
  Astro site with bun."
- Without pixi, CI needs separate setup actions for Rust and bun,
  with independent version management and caching.
- pixi provides a single lockfile (`pixi.lock`) that captures both
  toolchains, ensuring reproducibility.

### Why conda-forge (not rustup + nvm + npx)?
- conda-forge packages are pre-built binaries — no compilation.
  `cargo install cargo-nextest` takes minutes. `pixi add cargo-nextest`
  takes seconds.
- conda-forge has a consistent package metadata format, dependency
  resolution, and platform support matrix.
- pixi.lock pins exact builds (not just versions) with content hashes.

### Why features, not just environments?
Features are composable. Environments are the Cartesian product.
```
feature:rust + feature:lint = environment:default
feature:docs               = environment:docs
feature:rust + feature:lint + feature:release = environment:release
all features               = environment:all
```
Adding a new tool means adding it to the right feature. The environment
composition is automatic.

## Environment Quick Reference

| Environment | Features | Use Case |
|---|---|---|
| `default` | rust, lint | Day-to-day Rust development |
| `docs` | docs | Docs site development |
| `release` | rust, lint, release | Cutting releases |
| `all` | rust, lint, docs, release, all | CI, full builds |

## Related Concepts

- [Pixi Environments](./environments.md)
- [Pixi Tasks](./tasks.md)
- [Pixi Features](./features.md)
- [conda-forge Packages](./conda-forge-packages.md)
- [Three-Layer Task Model](../architecture/three-layer-model.md)
