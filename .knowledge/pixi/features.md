---
type: Reference
title: "Pixi Features"
description: "Planned pixi feature definitions and their dependency and task composition."
section: pixi
kind: detail
tags: [pixi, features, composition, dependencies, tasks, modularity]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# Pixi Features

Pixi features are the composable building blocks that define what
tools and tasks are available. Environments combine features into
installable capability sets.

---

## Feature → Dependency → Task Mapping

### `rust` feature

The core Rust development feature. Every environment that builds
or tests Rust code includes this.

```toml
[dependencies]
rust = ">=1.85"          # 2024 edition stable since 1.85; current stable is 1.98.1 (Sep 2026)
openssl = ">=3"
pkg-config = ">=0.29"
cmake = ">=3.28"
```

> **Version snapshot (verified 2026-09-17):** Rust stable is 1.98.1;
> the 2024 edition has been the default since Rust 1.85. The floor is
> `>=1.85` (edition 2024) rather than the original `>=1.80`. Note that
> building modern companion tooling from source may require newer
> (e.g. cargo-deny 0.20 MSRV is Rust 1.88) — installing prebuilt
> binaries from conda-forge sidesteps that.

**Tasks owned**:
- `build`, `build-release`
- `fmt-rust`, `fmt-check-rust`
- `lint-rust`
- `fmt-toml`, `fmt-check-toml`, `lint-toml`
- `fmt`, `fmt-check`
- `xtask`, `cli-docs`, `schema`, `completions`, `lint-workspace`

**Why `openssl`, `pkg-config`, `cmake`?**
- `openssl`: required by `reqwest` (HTTP client used in providers)
  and `rattler_networking` (authentication middleware)
- `pkg-config`: helps the build system find `openssl` on Linux
- `cmake`: required by `libgit2-sys` (used by convco's git2 crate)
  and `zlib-ng` (used by rattler for decompression)

### `lint` feature

Additional linting tools beyond what ships with Rust.

```toml
[feature.lint.dependencies]
taplo = ">=0.9"            # 0.9.x line; upstream is low-activity, TOML 1.1 support pending
cargo-deny = ">=0.20"      # 0.20.2 (2026-07); note source-build MSRV Rust 1.88
cargo-nextest = ">=0.9"    # 0.9.x rolling series; latest 0.9.143 (2026-08)
```

**Tasks owned**:
- `test`, `test-doc`
- `lint-deps`

**Why separate from `rust`?**
These tools are not needed for `cargo build` or `cargo fmt`. Keeping
them in a separate feature means the `rust` feature resolves faster.
In practice, `lint` is always combined with `rust` (in `default`
and `all` environments), but the separation allows a hypothetical
"build-only" environment without testing/linting tools.

### `docs` feature

Everything needed for the documentation site.

```toml
[feature.docs.dependencies]
bun = ">=1.2"        # 1.4.x line current (2026); historical floor was 1.1
biome = ">=2.3"      # 2.3+ lints/formats TS *and* CSS inside .astro files; latest 2.5.x
```

> **Biome 2 note (2026):** Biome 2.0 landed mid-2025 with a new config
> format (`biome migrate --write` upgrades `biome.json`). 2.3 added
> full support for Astro/Vue/Svelte files, which is why the floor is
> `>=2.3` for a Starlight docs app.

**Tasks owned**:
- `docs-install`, `docs-dev`, `docs-build-raw`, `docs-preview`, `docs-check`
- `fmt-ts`, `lint-ts`, `fmt-check-ts`

**Why biome is here (not in `lint`)?**
Biome only lints TS/JS/CSS files in the docs app. Rust developers
who never touch the docs site don't need biome. By placing it in
the `docs` feature, the `default` environment stays smaller.

### `release` feature

Tools for cutting releases.

```toml
[feature.release.dependencies]
# convco — see note in tooling/convco.md about installation
```

**Tasks owned**:
- `commit`, `changelog`, `version`, `version-bump`, `check-commits`
- `release`, `dist`

**Why separate?**
Release tooling is used by maintainers only, and only during release
preparation. Most developers never need convco. Keeping it separate
reduces the default environment size.

### `all` feature

Cross-cutting tasks that span multiple features.

```toml
# No additional dependencies — this feature only defines composite tasks
```

**Tasks owned**:
- `fmt-all`, `fmt-check-all`, `lint-all`
- `docs-build` (the full codegen + Astro pipeline)
- `ci`, `pre-commit`

**Why a separate feature?**
The `all` feature defines tasks that depend on tasks from multiple
other features (e.g., `fmt-all` depends on `fmt` from `rust` and
`fmt-ts` from `docs`). These composite tasks can only exist in an
environment that includes all contributing features.

---

## Feature Composition Matrix

```
                    rust   lint   docs   release   all
                    ────   ────   ────   ───────   ───
default     env  =   ✅     ✅     ❌      ❌       ❌
docs        env  =   ❌     ❌     ✅      ❌       ❌
release     env  =   ✅     ✅     ❌      ✅       ❌
all         env  =   ✅     ✅     ✅      ✅       ✅
```

### Reading the matrix

- A developer in the `default` environment has Rust + lint tools
  but no bun, biome, or convco.
- A docs writer in the `docs` environment has bun + biome but no
  Rust compiler.
- The `all` environment has everything — used by CI and for full
  local builds.

---

## Adding a New Feature

### When to add a feature

Add a new feature when:
1. A workflow needs tools that not everyone needs
2. The tools have significant install size or resolve time
3. The tools have dependencies that conflict with other features
   (rare, but possible)

### Steps

1. Define the feature with its dependencies:
   ```toml
   [feature.bench.dependencies]
   hyperfine = ">=1.18"
   ```

2. Define tasks under the feature:
   ```toml
   [feature.bench.tasks]
   bench = "hyperfine --warmup 3 'target/release/pixi-skills find test'"
   ```

3. Create or update environments:
   ```toml
   [environments]
   bench = { features = ["rust", "bench"] }
   all = { features = ["rust", "lint", "docs", "release", "bench", "all"] }
   ```

4. Document in `.knowledge/pixi/features.md` (this file)

### Naming conventions

- Feature names are lowercase, single words: `rust`, `lint`, `docs`,
  `release`, `bench`
- Task names are `kebab-case`: `fmt-rust`, `lint-deps`, `docs-build`
- Tasks owned by a feature use a consistent prefix where appropriate:
  `docs-*` for docs tasks, `fmt-*` for format tasks

---

## Dependency Deduplication

When the same package appears in multiple features, pixi deduplicates
it. For example, if `rust` depends on `openssl >=3` and `docs` also
needs `openssl >=3`, pixi resolves it once.

This is automatic — no special handling needed. The `pixi.lock` file
records the single resolved version.

---

## Feature Isolation Guarantees

Features provide **additive** capabilities. They do not:
- Conflict with each other (pixi resolves dependencies across all
  features in an environment)
- Override each other's dependencies
- Hide each other's tasks

If two features define a task with the same name, pixi reports a
conflict. This shouldn't happen — each feature owns its tasks
exclusively.

## Related Concepts

- [Pixi — Context](./CONTEXT.md)
- [Pixi Environments](./environments.md)
- [Pixi Tasks](./tasks.md)
- [conda-forge Packages](./conda-forge-packages.md)
