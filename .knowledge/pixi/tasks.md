---
title: "Pixi Tasks"
section: pixi
kind: detail
tags: [pixi, tasks, commands, depends-on, workflows, ci]
relates_to:
  - pixi/CONTEXT
  - pixi/environments
  - pixi/features
  - architecture/three-layer-model
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Pixi Tasks

The full catalog of pixi tasks. Every `pixi run` command, its
underlying command, dependency chain, and which feature it belongs to.

---

## Task Catalog

### Build Tasks (`rust` feature)

| Task | Command | Description |
|---|---|---|
| `build` | `cargo build --workspace` | Build all crates (debug) |
| `build-release` | `cargo build --workspace --release` | Build all crates (release) |

### Test Tasks (`rust` / `lint` feature)

| Task | Command | Description |
|---|---|---|
| `test` | `cargo nextest run --workspace` | Run all tests (parallel, per-process) |
| `test-doc` | `cargo test --workspace --doc` | Run doc tests (nextest can't do these) |

### Format Tasks

| Task | Command | Feature | Description |
|---|---|---|---|
| `fmt-rust` | `cargo fmt --all` | `rust` | Format Rust source |
| `fmt-toml` | `taplo fmt` | `rust` | Format TOML files |
| `fmt-ts` | `biome format --write .` (cwd: docs) | `docs` | Format TS/JS/CSS |
| `fmt` | depends-on: `fmt-rust`, `fmt-toml` | `rust` | Format Rust + TOML |
| `fmt-all` | depends-on: `fmt`, `fmt-ts` | `all` | Format everything |

### Format Check Tasks (CI)

| Task | Command | Feature | Description |
|---|---|---|---|
| `fmt-check-rust` | `cargo fmt --all -- --check` | `rust` | Check Rust formatting |
| `fmt-check-toml` | `taplo check` | `rust` | Check TOML formatting |
| `fmt-check-ts` | `biome check .` (cwd: docs) | `docs` | Check TS/JS/CSS |
| `fmt-check` | depends-on: `fmt-check-rust`, `fmt-check-toml` | `rust` | Check Rust + TOML |
| `fmt-check-all` | depends-on: `fmt-check`, `fmt-check-ts` | `all` | Check everything |

### Lint Tasks

| Task | Command | Feature | Description |
|---|---|---|---|
| `lint-rust` | `cargo clippy --workspace --all-targets -- -D warnings` | `rust` | Rust linting |
| `lint-toml` | `taplo check` | `rust` | TOML validation |
| `lint-deps` | `cargo deny check` | `lint` | License + advisory audit |
| `lint-workspace` | `cargo xtask lint` | `rust` | Workspace consistency |
| `lint-ts` | `biome check .` (cwd: docs) | `docs` | TS/JS/CSS linting |
| `lint` | depends-on: `lint-rust`, `lint-toml`, `lint-deps`, `lint-workspace` | `rust` | All Rust-side linting |
| `lint-all` | depends-on: `lint`, `lint-ts` | `all` | Lint everything |

### Xtask Tasks (`rust` feature)

| Task | Command | Description |
|---|---|---|
| `xtask` | `cargo xtask` | Run xtask with custom args |
| `cli-docs` | `cargo xtask cli-docs --output apps/.../cli/` | Generate CLI reference MDX |
| `schema` | `cargo xtask schema --output apps/.../skills-schema.json` | Generate JSON Schema |
| `completions` | `cargo xtask completions --output completions/` | Generate shell completions |
| `lint-workspace` | `cargo xtask lint` | Workspace consistency checks |

### Docs Tasks (`docs` feature)

| Task | Command | cwd | Description |
|---|---|---|---|
| `docs-install` | `bun install --frozen-lockfile` | `apps/pixi-skills-docs` | Install JS deps |
| `docs-dev` | `bun run dev` | `apps/pixi-skills-docs` | Start Astro dev server |
| `docs-build-raw` | `bun run build` | `apps/pixi-skills-docs` | Build Astro site (no codegen) |
| `docs-preview` | `bun run preview` | `apps/pixi-skills-docs` | Preview built site |
| `docs-check` | `bun run check` | `apps/pixi-skills-docs` | Astro type checking |

### Release Tasks (`release` feature)

| Task | Command | Description |
|---|---|---|
| `commit` | `convco commit` | Interactive conventional commit |
| `changelog` | `convco changelog` | Generate/preview changelog |
| `version` | `convco version` | Show current version |
| `version-bump` | `convco version --bump` | Calculate next version |
| `check-commits` | `convco check` | Validate commit history |
| `release` | `cargo xtask release` | Full release flow |
| `dist` | `cargo xtask dist` | Build distribution artifacts |

### Cross-Cutting Tasks (`all` feature)

| Task | depends-on | Description |
|---|---|---|
| `fmt-all` | `fmt`, `fmt-ts` | Format all languages |
| `fmt-check-all` | `fmt-check`, `fmt-check-ts` | Check all formatting |
| `lint-all` | `lint`, `lint-ts` | Lint all languages |
| `docs-build` | `cli-docs`, `schema`, `docs-build-raw` | Full docs build (codegen + Astro) |
| `ci` | `fmt-check-all`, `lint-all`, `test`, `test-doc`, `check-commits`, `docs-build` | Full CI pipeline |
| `pre-commit` | `fmt-check-all`, `lint-all`, `test` | Fast local pre-commit check |

---

## Dependency Graph (Key Composite Tasks)

### `ci` (the full pipeline)

```
ci
├── fmt-check-all
│   ├── fmt-check
│   │   ├── fmt-check-rust        cargo fmt --all -- --check
│   │   └── fmt-check-toml        taplo check
│   └── fmt-check-ts              biome check . (cwd: docs)
├── lint-all
│   ├── lint
│   │   ├── lint-rust             cargo clippy ... -D warnings
│   │   ├── lint-toml             taplo check
│   │   ├── lint-deps             cargo deny check
│   │   └── lint-workspace        cargo xtask lint
│   └── lint-ts                   biome check . (cwd: docs)
├── test                          cargo nextest run --workspace
├── test-doc                      cargo test --workspace --doc
├── check-commits                 convco check
└── docs-build
    ├── cli-docs                  cargo xtask cli-docs --output ...
    ├── schema                    cargo xtask schema --output ...
    └── docs-build-raw            bun run build (cwd: docs)
        └── docs-install          bun install --frozen-lockfile
```

### `docs-build` (codegen → Astro)

```
docs-build
├── cli-docs         cargo xtask cli-docs   → writes .mdx to cli/
├── schema           cargo xtask schema     → writes .json to public/
└── docs-build-raw   bun run build          → reads .mdx + .json → dist/
    └── docs-install bun install --frozen-lockfile
```

### `release` (version bump → tag)

```
release              cargo xtask release
├── test             cargo nextest run (prerequisite)
├── lint             clippy + taplo + deny + xtask lint (prerequisite)
└── check-commits    convco check (prerequisite)
```

---

## Task Design Principles

### 1. Leaf tasks are single commands
Every leaf task (no `depends-on`) is a single, simple command.
This makes each task debuggable in isolation:
```bash
pixi run fmt-rust            # Just cargo fmt — nothing else
pixi run lint-deps           # Just cargo deny check — nothing else
```

### 2. Composite tasks compose via depends-on
Higher-level tasks compose leaf tasks via `depends-on`. They never
contain commands themselves — they are pure orchestration.

### 3. Tasks are idempotent
Running any task twice produces the same result. `fmt` formats
already-formatted code (no-op). `test` runs all tests (same results).
`docs-build` regenerates the same output.

### 4. CI is a single task
`pixi run -e all ci` runs everything. No multi-step CI scripts.
If it passes locally, it passes in CI.

### 5. Escape hatches exist
Every pixi task delegates to a real tool. If pixi tasks break, the
underlying commands still work:
```bash
cargo fmt --all                  # Instead of pixi run fmt-rust
cargo clippy --workspace         # Instead of pixi run lint-rust
cd apps/pixi-skills-docs && bun run dev  # Instead of pixi run docs-dev
```

---

## Adding a New Task

### Checklist

1. **Decide which feature it belongs to** (rust, lint, docs, release)
2. **Write the leaf task** with a single command
3. **Add to appropriate composite tasks** if needed
4. **Test in isolation**: `pixi run <task>`
5. **Test in CI composite**: `pixi run -e all ci`
6. **Document in this file** (update the tables above)
7. **Update `.knowledge/pixi/tasks.md`** (this file)

### Example: adding a `bench` task

```toml
# pixi.toml
[feature.rust.tasks]
bench = "cargo bench --workspace"

# If it should be part of CI:
[feature.all.tasks]
ci = { depends-on = [..., "bench"] }
```
