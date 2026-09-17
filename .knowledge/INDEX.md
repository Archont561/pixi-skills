---
title: "pixi-skills Knowledge Base"
section: root
kind: index
tags: [index, navigation, overview]
relates_to: []
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# pixi-skills — Knowledge Base Index

This knowledge base documents the full design, architecture, tooling,
and conventions of the `pixi-skills` project. It is intended to be
read by AI coding agents, new contributors, and maintainers alike.

> **Start here.** Every section has its own `INDEX.md` for navigation
> and `CONTEXT.md` for framing. Detail pages contain the actual content.

---

## Sections

### 🏗️ [Architecture](./architecture/INDEX.md)
The structural design of the monorepo — workspace layout, the
three-layer task model (pixi → xtask/bun → toolchains), crate
dependency graph, and key design decisions (ADRs).

### 📦 [Crates](./crates/INDEX.md)
Documentation for every Rust crate in the workspace: `skills-core`,
all provider crates, the `pixi-skills` CLI binary, and the `xtask`
automation crate.

### 📚 [Docs App](./docs-app/INDEX.md)
The Astro Starlight documentation site living in `apps/pixi-skills-docs/`.
Covers Starlight configuration, content structure, custom components,
and the bun + pixi coexistence model.

### 🔧 [Tooling](./tooling/INDEX.md)
Every developer tool in the stack: Biome, Taplo, cargo-deny,
cargo-nextest, convco, rustfmt, and clippy. Config file locations,
key settings, and how pixi invokes each.

### 🌿 [Pixi](./pixi/INDEX.md)
The `pixi.toml` anatomy: environments, features, tasks, and
dependency declarations. How pixi provisions both the Rust toolchain
and the bun/JS runtime from conda-forge.

### 🚀 [CI/CD](./cicd/INDEX.md)
GitHub Actions workflows, the `setup-pixi` integration, caching
strategy, the full release workflow (convco → xtask → tag → dist),
and cross-compilation + distribution artifacts.

### 🌍 [Landscape](./landscape/INDEX.md)
Competitive analysis: skills.sh, npm-skills, the pixi/rattler
ecosystem. Our differentiation — lockfiles, reproducibility, supply
chain security, multi-language support.

### 📐 [Conventions](./conventions/INDEX.md)
Project-wide conventions: conventional commits + scopes, the skill
format (agentskills.io folder spec + YAML frontmatter + companion
`skill.toml`, per ADR-008), crate/package/file naming rules, and the
config file map.

### 🗺️ [Roadmap](./roadmap/INDEX.md)
MVP phases (Phase 0–5), milestone definitions, and priority ordering.
What ships first and why.

---

## File Kind Legend

| `kind` | Purpose |
|---|---|
| `index` | Navigation — links to children within a section |
| `context` | Framing — principles, scope, how section relates to others |
| `detail` | Content — the actual knowledge, spec, or decision record |

## Quick Navigation by Role

**I am writing Rust code →**
Start at [Crates/CONTEXT](./crates/CONTEXT.md),
then [Architecture/dependency-graph](./architecture/dependency-graph.md)

**I am working on the docs site →**
Start at [Docs App/CONTEXT](./docs-app/CONTEXT.md),
then [Docs App/content-structure](./docs-app/content-structure.md)

**I am setting up tooling or CI →**
Start at [Pixi/CONTEXT](./pixi/CONTEXT.md),
then [Tooling/CONTEXT](./tooling/CONTEXT.md)

**I am making a release →**
Start at [CI/CD/release-workflow](./cicd/release-workflow.md),
then [Conventions/commit-conventions](./conventions/commit-conventions.md)

**I am evaluating this project →**
Start at [Landscape/differentiation](./landscape/differentiation.md)
