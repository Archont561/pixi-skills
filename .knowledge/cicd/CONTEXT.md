---
type: Overview
title: "CI/CD — Context"
description: "Principles for the planned reproducible CI, release, and distribution pipeline."
section: cicd
kind: context
tags: [cicd, context, github-actions, release, reproducibility]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# CI/CD — Context

## What This Section Covers

The continuous integration and delivery infrastructure for pixi-skills.
All CI/CD runs through pixi, ensuring that what runs in CI is identical
to what runs on a developer's machine.

## Core CI Principle: One Command

The entire CI pipeline is a single command:
```bash
pixi run -e all ci
```

This runs (in dependency order):
1. `fmt-check-all` — rustfmt + taplo + biome format checks
2. `lint-all` — clippy + taplo check + cargo-deny + xtask lint + biome
3. `test` — cargo nextest run
4. `test-doc` — cargo test --doc
5. `check-commits` — convco check
6. `docs-build` — cli-docs + schema + astro build

If any step fails, the pipeline fails. No partial successes.

## Why pixi in CI?

### Reproducibility
`pixi.lock` pins exact package builds with content hashes. CI installs
the same bytes as every developer machine. No version skew between
"local clippy says OK" and "CI clippy says error."

### Single setup step
The `prefix-dev/setup-pixi` GitHub Action installs pixi and resolves
the specified environment. One action replaces:
- `actions/setup-rust` (rustup + toolchain + components)
- `actions/setup-node` or `oven-sh/setup-bun`
- Manual `cargo install` for cargo-deny, cargo-nextest, taplo, etc.

### Caching
`setup-pixi` has built-in caching (`cache: true`). The pixi environment
is cached by the hash of `pixi.lock`. Subsequent runs skip dependency
installation entirely.

## Release Model

Releases follow semantic versioning calculated from conventional commits:
- `feat:` → minor bump
- `fix:` → patch bump
- `feat!:` or `BREAKING CHANGE:` → major bump

The release workflow is triggered manually (workflow_dispatch) or by
pushing a tag. The `xtask release` command handles all version bumping,
changelog generation, and tagging locally. CI then builds distribution
artifacts with `xtask dist`.

## Security Considerations

- `cargo-deny` checks for known vulnerabilities (RustSec advisory DB)
  on every CI run.
- `cargo-deny` enforces a license allowlist — no copyleft dependencies
  can enter the tree without explicit approval.
- `convco check` ensures all commits follow conventional format,
  preventing untraceable changes in the changelog.
- `fetch-depth: 0` is required so convco has full git history for
  commit validation and version calculation.

## Related Concepts

- [GitHub Actions](./github-actions.md)
- [Release Workflow](./release-workflow.md)
- [Distribution Artifacts](./dist.md)
- [Pixi Tasks](../pixi/tasks.md)
- [Pixi Environments](../pixi/environments.md)
