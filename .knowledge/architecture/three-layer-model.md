---
title: "Three-Layer Task Model"
section: architecture
kind: detail
tags: [architecture, tasks, pixi, xtask, bun, automation, layers]
relates_to:
  - pixi/tasks
  - crates/xtask
  - docs-app/bun-setup
  - architecture/workspace-layout
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Three-Layer Task Model

All automation in pixi-skills is organized into three layers. Each
layer does what it is best at. No layer duplicates another's
responsibilities.

---

## The Layers

```
┌─────────────────────────────────────────────────────────┐
│                     LAYER 1: pixi tasks                 │
│              Orchestration + Glue + Entry Point         │
│                                                         │
│  "pixi run ci"                                          │
│  "pixi run fmt-all"                                     │
│  "pixi run docs-build"                                  │
│                                                         │
│  Responsibilities:                                      │
│  • Environment selection (which tools are available)    │
│  • Task dependency ordering (codegen before build)      │
│  • cwd routing (run bun commands in apps/docs/)         │
│  • Composite tasks (fmt-all = fmt-rust + fmt-toml +     │
│    fmt-ts)                                              │
│  • CI entrypoints (single command for entire pipeline)  │
├────────────────────┬────────────────────────────────────┤
│  LAYER 2a:         │  LAYER 2b:                         │
│  cargo xtask       │  bun run <script>                  │
│  (Rust automation) │  (JS/Astro automation)             │
│                    │                                    │
│  "cargo xtask      │  "bun run dev"                     │
│   cli-docs"        │  "bun run build"                   │
│  "cargo xtask      │  "bun run preview"                 │
│   release"         │  "bun run check"                   │
│                    │                                    │
│  Responsibilities: │  Responsibilities:                 │
│  • clap → MDX      │  • Astro dev server                │
│  • types → schema  │  • Astro static build              │
│  • version bumps   │  • Astro type checking             │
│  • workspace lint  │  • Astro preview server            │
│  • cross-compile   │                                    │
│  • completions     │  Knows nothing about Rust.         │
│                    │  Pure Astro/Starlight concerns.    │
│  Knows nothing     │                                    │
│  about JS/Astro.   │                                    │
│  Pure Rust         │                                    │
│  concerns.         │                                    │
├────────────────────┼────────────────────────────────────┤
│  LAYER 3a:         │  LAYER 3b:                         │
│  Rust toolchain    │  Bun + Node runtime                │
│                    │                                    │
│  rustc, cargo,     │  bun (from conda-forge)            │
│  rustfmt, clippy   │                                    │
│  (from conda-forge)│                                    │
├────────────────────┴────────────────────────────────────┤
│          LAYER 3c: Standalone CLI tools                  │
│                                                         │
│  taplo, biome, cargo-deny, cargo-nextest, convco        │
│  (all from conda-forge, invoked by pixi tasks)          │
└─────────────────────────────────────────────────────────┘
```

---

## Why Three Layers (Not Two, Not One)

### Why not just pixi tasks running shell commands?

Shell commands work for simple cases (`cargo build`, `taplo fmt`).
They break down for complex Rust-native automation:

| Task | Shell approach | xtask approach |
|---|---|---|
| Generate CLI docs | Parse `--help` output with sed/awk. Fragile, breaks on format changes. | Instantiate the real clap `Command`, walk the subcommand tree, call `.render_help()`. Cannot break. |
| Generate JSON schema | Write schema by hand. Drifts from Rust types immediately. | `#[derive(JsonSchema)]` on the real config structs. Schema and parser are the same code. |
| Bump versions | `find . -name Cargo.toml -exec sed ...` Misses edge cases, no validation. | `toml_edit` parses TOML, modifies the version field, preserves formatting and comments. |
| Cross-compile | Long shell script with platform detection, error handling. | Rust code using `xshell` — cross-platform, type-checked, testable. |

### Why not put everything in xtask?

xtask is Rust. The Astro toolchain expects a JS runtime. Running
`astro dev` from xtask would mean shelling out to bun — which is
exactly what a pixi task does, but with worse ergonomics.

**Rule**: if a task's implementation is "run one shell command," it
belongs in a pixi task. If a task requires programmatic logic in Rust,
it belongs in xtask. If a task is Astro/JS-native, it belongs in
package.json scripts.

### Why not just `make`?

- Make doesn't understand environments. Pixi knows which tools are
  available in which environment.
- Make doesn't install dependencies. Pixi provisions the entire
  toolchain.
- Make uses shell syntax that differs across platforms. Pixi tasks
  work on Linux, macOS, and Windows.
- Make has implicit rules and tab-sensitivity. Pixi tasks are explicit
  TOML declarations.

---

## Layer 1: pixi tasks — Detailed Responsibilities

### Environment selection
```toml
pixi run -e docs docs-dev     # Uses the docs environment (has bun)
pixi run -e release release   # Uses the release environment (has convco)
pixi run -e all ci            # Uses the all environment (has everything)
```

The developer doesn't need to know which tools are in which
environment — the task declarations bind tasks to features, and
features to environments.

### Task dependency ordering
```toml
docs-build = { depends-on = ["cli-docs", "schema", "docs-build-raw"] }
```

This ensures xtask generates CLI docs and schema JSON before Astro
tries to build. Without pixi, this ordering would be a shell script
with `&&` chains or a Makefile with phony targets.

### Composite tasks
```toml
fmt-all       = { depends-on = ["fmt", "fmt-ts"] }
lint-all      = { depends-on = ["lint", "lint-ts"] }
ci            = { depends-on = ["fmt-check-all", "lint-all", "test", ...] }
```

Single-command entry points that compose tools across language
boundaries. `fmt-all` runs rustfmt + taplo + biome — three different
tools, two different runtimes, one command.

### cwd routing
```toml
docs-dev = { cmd = "bun run dev", cwd = "apps/pixi-skills-docs" }
```

Bun scripts in `package.json` expect to run from the app directory.
Pixi handles the `cd` so the developer doesn't have to.

---

## Layer 2a: cargo xtask — Detailed Responsibilities

### Why xtask is Rust (not Python, not shell)

1. **Same language as the project.** Contributors already know Rust.
   No context-switching to Python or bash.

2. **Access to project types.** xtask can `use pixi_skills::cli`
   to get the real clap `Command` struct. No parsing `--help` output.

3. **Cross-platform.** xshell commands work on Windows, macOS, and
   Linux. Shell scripts don't.

4. **Compile-once, run fast.** After the first `cargo build`, xtask
   runs instantly. No interpreter startup, no JIT warmup.

5. **Testable.** xtask subcommands are functions that can be unit-
   tested. Shell scripts are tested by running them and hoping.

### xtask Subcommand Reference

| Subcommand | What it does | Key deps |
|---|---|---|
| `cli-docs` | Walks clap Command tree → writes one .mdx file per subcommand | `clap`, `pixi-skills` |
| `schema` | Derives JSON Schema from `skills-core` config types | `schemars`, `skills-core` |
| `completions` | Generates bash/zsh/fish/ps1 completions from clap | `clap_complete` |
| `lint` | Checks workspace consistency (editions, licenses, repo fields) | `toml_edit`, `glob` |
| `release` | Reads `convco version --bump`, updates all Cargo.toml, generates changelog, commits + tags | `toml_edit`, `xshell` |
| `dist` | Builds release binaries for target triples, creates tarballs, computes SHA256 | `xshell`, `flate2`, `sha2` |

### xtask Access Pattern

```
Developer types:        pixi run cli-docs
pixi.toml resolves to:  cargo xtask cli-docs --output apps/.../cli/
.cargo/config.toml:     xtask = "run --package xtask --"
cargo runs:             target/debug/xtask cli-docs --output apps/.../cli/
xtask:                  Instantiates pixi_skills::cli::build_command()
                        Walks subcommands recursively
                        Writes find.mdx, add.mdx, remove.mdx, ... to disk
```

---

## Layer 2b: bun scripts — Detailed Responsibilities

### What package.json scripts contain

```json
{
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check"
  }
}
```

Four commands. All Astro-native. No lint, no format — Biome runs via
pixi, not via bun.

### What bun scripts do NOT contain

- No `biome` invocation (biome is a pixi-managed conda-forge binary)
- No `eslint` or `prettier` (replaced by biome)
- No codegen scripts (that's xtask's job)
- No test scripts (no JS tests — all logic is in Rust)

### Why bun scripts exist at all

Without them, pixi tasks would directly invoke `astro dev`, which
requires knowing the exact astro CLI syntax and arguments. By
delegating to `bun run dev`, we:

1. Follow Astro's documented usage patterns
2. Allow `astro.config.mjs` to define dev server options
3. Keep the Astro-specific knowledge in the Astro project

---

## Layer 3: Standalone CLIs — Detailed Responsibilities

These tools are invoked directly by pixi tasks. They are not wrapped by
xtask or bun — pixi calls them as bare commands.

| Tool | pixi task | Command |
|---|---|---|
| `taplo` | `fmt-toml` | `taplo fmt` |
| `taplo` | `fmt-check-toml` | `taplo check` |
| `biome` | `fmt-ts` | `biome format --write .` (cwd: docs) |
| `biome` | `lint-ts` | `biome check .` (cwd: docs) |
| `cargo-deny` | `lint-deps` | `cargo deny check` |
| `cargo-nextest` | `test` | `cargo nextest run --workspace` |
| `convco` | `commit` | `convco commit` |
| `convco` | `check-commits` | `convco check` |
| `convco` | `changelog` | `convco changelog` |
| `convco` | `version-bump` | `convco version --bump` |

These tools follow the Unix philosophy: do one thing well. Pixi
composes them into workflows.

---

## Anti-Patterns (What We Avoid)

| Anti-pattern | Why it's bad | Our approach |
|---|---|---|
| Shell scripts in `scripts/` | Platform-dependent, untestable, drift | xtask for complex logic, pixi tasks for simple commands |
| `Makefile` | Tab-sensitive, implicit rules, no env management | pixi tasks |
| `npm run` for non-JS tasks | Forces npm/bun into Rust concerns | pixi tasks call cargo directly |
| `cargo xtask` calling `bun` | Leaks JS concerns into Rust automation | pixi tasks compose xtask + bun, neither calls the other |
| Global tool installs | "works on my machine," version drift | Everything from conda-forge via pixi |
