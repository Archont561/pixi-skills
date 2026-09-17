---
title: "Architecture — Index"
section: architecture
kind: index
tags: [architecture, index, navigation]
relates_to:
  - crates/INDEX
  - pixi/INDEX
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Architecture — Index

This section describes the structural design of the pixi-skills monorepo:
how the workspace is organized, why it is organized that way, and the key
decisions that shaped it.

## Pages

### [workspace-layout.md](./workspace-layout.md)
The full annotated directory tree. What lives in `crates/`, what lives
in `apps/`, where config files go, and the role of every top-level file.

### [three-layer-model.md](./three-layer-model.md)
The core automation architecture: pixi tasks as the orchestration layer,
cargo xtask for Rust-native automation, bun scripts for JS-native
automation, and standalone CLIs (taplo, biome, convco, etc.) doing one
thing well. How these three layers compose.

### [dependency-graph.md](./dependency-graph.md)
The crate dependency DAG, the build ordering, and the codegen pipeline
(xtask generates CLI docs and JSON schema that flow into the Astro build).

### [design-decisions.md](./design-decisions.md)
ADR-style (Architecture Decision Record) entries for key choices:
lockfile format (TOML vs JSON), skill packaging convention,
agent target directories, version resolution strategy, and more.

## Related Sections

- [Crates](../crates/INDEX.md) — the Rust crate details that implement
  this architecture
- [Pixi](../pixi/INDEX.md) — the pixi.toml that wires it all together
- [Tooling](../tooling/INDEX.md) — the developer tools this architecture
  orchestrates
