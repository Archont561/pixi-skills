---
title: "Tooling — Index"
section: tooling
kind: index
tags: [tooling, index, navigation, biome, taplo, cargo-deny, nextest, convco]
relates_to:
  - pixi/tasks
  - pixi/conda-forge-packages
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Tooling — Index

This section documents every developer tool in the pixi-skills stack.
Each tool has its own page covering: what it does, its config file,
key settings, how pixi installs and invokes it, and common workflows.

All tools are provisioned by pixi from conda-forge. No global installs
needed.

## Pages

### [biome.md](./biome.md)
Biome — a fast, all-in-one linter and formatter for TypeScript,
JavaScript, CSS, and JSON. Replaces ESLint + Prettier. Covers the
monorepo config inheritance model (`biome.json` at root, extended in
`apps/pixi-skills-docs/biome.json`).

### [taplo.md](./taplo.md)
Taplo — TOML formatter and validator. Formats `pixi.toml`, `Cargo.toml`,
`deny.toml`, and all other TOML files. Config in `taplo.toml`.

### [cargo-deny.md](./cargo-deny.md)
cargo-deny — license auditing, advisory database checking, crate bans,
and source verification. Config in `deny.toml`. Runs as part of the
`lint` task.

### [cargo-nextest.md](./cargo-nextest.md)
cargo-nextest — a next-generation test runner. Parallel test execution,
per-test timeout, JUnit XML output for CI, retry logic. Config in
`.config/nextest.toml`.

### [convco.md](./convco.md)
convco — conventional commit tooling. Interactive commit helper, commit
history validation, automatic changelog generation, semantic version
calculation. Config in `.convco`.

### [rustfmt-clippy.md](./rustfmt-clippy.md)
rustfmt and clippy — the standard Rust formatting and linting tools.
Config in `rustfmt.toml` and `Cargo.toml` `[lints]` section. Baseline
settings and any project-specific overrides.

## Related Sections

- [Pixi/tasks](../pixi/tasks.md) — how pixi invokes each tool
- [Pixi/conda-forge-packages](../pixi/conda-forge-packages.md) — which
  conda-forge packages provide these tools
- [CI/CD/github-actions](../cicd/github-actions.md) — how these tools
  run in CI
