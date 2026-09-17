---
title: "Pixi Environments"
section: pixi
kind: detail
tags: [pixi, environments, features, default, docs, release, all]
relates_to:
  - pixi/CONTEXT
  - pixi/features
  - pixi/tasks
  - architecture/three-layer-model
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Pixi Environments

The four pixi environments define capability sets — each environment
provides the tools needed for a specific workflow.

---

## Environment Definitions

```toml
# pixi.toml
[environments]
default  = { features = ["rust", "lint"] }
docs     = { features = ["docs"] }
release  = { features = ["rust", "lint", "release"] }
all      = { features = ["rust", "lint", "docs", "release", "all"] }
```

---

## Environment Details

### `default` — Day-to-day Rust Development

**Features**: `rust`, `lint`

**Contains**:
- Rust toolchain (rustc, cargo, rustfmt, clippy)
- taplo (TOML formatting)
- cargo-deny (dependency auditing)
- cargo-nextest (test runner)

**Used for**:
```bash
pixi run build             # cargo build --workspace
pixi run test              # cargo nextest run --workspace
pixi run fmt               # cargo fmt + taplo fmt
pixi run lint              # clippy + taplo + cargo-deny + xtask lint
```

**Who uses it**: Rust developers working on crates. This is the
environment you live in 90% of the time.

**What it does NOT contain**: bun, biome, convco. You don't need
JS tooling or release tooling for Rust development.

### `docs` — Documentation Site Development

**Features**: `docs`

**Contains**:
- bun (JS runtime)
- biome (TS/JS lint + format)

**Used for**:
```bash
pixi run -e docs docs-dev      # Astro dev server
pixi run -e docs docs-build-raw  # Astro static build
pixi run -e docs fmt-ts        # biome format
pixi run -e docs lint-ts       # biome check
```

**Who uses it**: Documentation writers, designers, anyone working
on the docs site without touching Rust code.

**What it does NOT contain**: Rust toolchain, cargo-deny, nextest,
convco. A docs contributor doesn't need to compile Rust.

**Note**: `docs-build-raw` (just Astro) works in this environment.
`docs-build` (codegen + Astro) requires the `all` environment
because codegen needs Rust.

### `release` — Cutting Releases

**Features**: `rust`, `lint`, `release`

**Contains**:
- Everything in `default`
- convco (conventional commit tooling)

**Used for**:
```bash
pixi run -e release commit          # convco commit
pixi run -e release check-commits   # convco check
pixi run -e release changelog       # convco changelog
pixi run -e release release         # cargo xtask release
pixi run -e release dist            # cargo xtask dist
```

**Who uses it**: Maintainers preparing a release. This is an
infrequent workflow — most developers never need this environment.

**What it does NOT contain**: bun, biome. The release workflow
doesn't build the docs site (that's CI's job in the `all` env).

### `all` — CI / Full Builds

**Features**: `rust`, `lint`, `docs`, `release`, `all`

**Contains**: everything from all other environments plus cross-
cutting tasks.

**Used for**:
```bash
pixi run -e all ci              # Full CI pipeline
pixi run -e all docs-build      # Codegen + Astro build
pixi run -e all fmt-all         # Format everything
pixi run -e all lint-all        # Lint everything
```

**Who uses it**: CI, and developers who want to run everything
locally (e.g., before a big PR).

**Trade-off**: This environment is the slowest to resolve and
install because it contains every tool. That's why it's not the
default — day-to-day development uses smaller environments.

---

## Environment Selection

### Explicit: `-e <env>`

```bash
pixi run -e docs docs-dev
pixi run -e release release
pixi run -e all ci
```

### Implicit: tasks route to environments

When you run `pixi run <task>`, pixi checks which environments
contain that task and uses the appropriate one. If a task exists
in multiple environments, pixi uses the default environment (or
prompts for disambiguation).

In practice, task names are unique to features, so routing is
unambiguous:
- `docs-dev` → only in `docs` feature → `docs` or `all` env
- `commit` → only in `release` feature → `release` or `all` env
- `build` → in `rust` feature → `default` or `all` env

### Shell activation

For interactive work:
```bash
pixi shell -e docs       # Drop into a shell with bun available
bun --version            # Works — bun is on PATH
biome --version          # Works — biome is on PATH
cargo --version          # Does NOT work — not in docs env
```

---

## Environment Size Comparison

| Environment | Approx. packages | Approx. disk | Install time |
|---|---|---|---|
| `default` | ~50 | ~500 MB | ~15s (cached: 2s) |
| `docs` | ~20 | ~200 MB | ~10s (cached: 1s) |
| `release` | ~55 | ~550 MB | ~15s (cached: 2s) |
| `all` | ~70 | ~700 MB | ~20s (cached: 3s) |

These are rough estimates. Actual sizes depend on platform and
conda-forge package versions. The key point: smaller environments
are faster to resolve and install.

---

## Adding a New Environment

If a new workflow emerges (e.g., benchmarking), add a new feature
and environment:

```toml
[feature.bench.dependencies]
hyperfine = ">=1.18"
critcmp = ">=0.1"

[feature.bench.tasks]
bench = "cargo bench --workspace"
bench-compare = "critcmp target/criterion/baseline target/criterion/new"

[environments]
bench = { features = ["rust", "bench"] }
# Also add to 'all':
all = { features = ["rust", "lint", "docs", "release", "bench", "all"] }
```

The principle: environments are cheap. Add one whenever a workflow
needs a distinct set of tools.
