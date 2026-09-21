---
type: Reference
title: "Config Files"
description: "Target configuration-file locations and the tools each file configures."
section: conventions
kind: detail
tags: [conventions, config, files, locations, tools, map]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Config Files

The definitive map of every configuration file in the workspace:
what tool it configures, where it lives, and its documentation link.

---

## Root-Level Config Files

| File | Tool | Purpose | Docs |
|---|---|---|---|
| `pixi.toml` | pixi | Environments, dependencies, tasks | [pixi docs](https://pixi.sh/latest/) |
| `pixi.lock` | pixi | Locked dependency versions + hashes | Auto-generated |
| `Cargo.toml` | cargo | Rust workspace: members, shared deps, workspace lints | [cargo reference](https://doc.rust-lang.org/cargo/reference/manifest.html) |
| `Cargo.lock` | cargo | Locked Rust dependency versions | Auto-generated |
| `biome.json` | biome | TS/JS/CSS lint + format rules (root) | [biome docs](https://biomejs.dev/reference/configuration/) |
| `deny.toml` | cargo-deny | License policy, advisories, bans, sources | [cargo-deny docs](https://embarkstudios.github.io/cargo-deny/) |
| `taplo.toml` | taplo | TOML formatting rules | [taplo docs](https://taplo.tamasfe.dev/configuration/) |
| `rustfmt.toml` | rustfmt | Rust formatting rules | [rustfmt docs](https://rust-lang.github.io/rustfmt/) |
| `.convco` | convco | Commit types, scopes, repo info | [convco docs](https://convco.github.io/) |
| `CHANGELOG.md` | convco / xtask | Generated changelog | Auto-generated |

## Nested Config Files

| File | Tool | Purpose |
|---|---|---|
| `.cargo/config.toml` | cargo | Aliases (`xtask = "run --package xtask --"`) |
| `.config/nextest.toml` | cargo-nextest | Test profiles, timeouts, retries |
| `apps/pixi-skills-docs/biome.json` | biome | Docs-specific lint overrides (extends root) |
| `apps/pixi-skills-docs/package.json` | bun | JS dependencies and scripts |
| `apps/pixi-skills-docs/bun.lock` | bun | Locked JS dependency versions |
| `apps/pixi-skills-docs/astro.config.mjs` | astro | Starlight config, sidebar, integrations |
| `apps/pixi-skills-docs/tsconfig.json` | typescript | TS config for Astro components |

## Per-Crate Config Files

| File | Tool | Purpose |
|---|---|---|
| `crates/*/Cargo.toml` | cargo | Crate-specific deps, features, metadata |
| `crates/xtask/Cargo.toml` | cargo | xtask deps, `publish = false` |

## Generated Artifacts (Not Config, but Tracked)

| File | Generator | Purpose |
|---|---|---|
| `completions/pixi-skills.bash` | xtask | Bash shell completions |
| `completions/pixi-skills.zsh` | xtask | Zsh shell completions |
| `completions/pixi-skills.fish` | xtask | Fish shell completions |
| `completions/_pixi-skills.ps1` | xtask | PowerShell completions |
| `apps/.../public/skills-schema.json` | xtask | JSON Schema for skills.toml |
| `apps/.../src/content/docs/cli/*.mdx` | xtask | CLI reference documentation |

## User-Level Config (Not in Repo)

| File | Tool | Purpose |
|---|---|---|
| `~/.config/pixi-skills/config.toml` | pixi-skills | User-level default settings |
| `~/.rattler/credentials.json` | rattler | Channel authentication tokens |
| `~/.cargo/advisory-db/` | cargo-deny | Cached RustSec advisory database |

---

## Config File Precedence

When multiple config files exist for the same tool, the precedence
is typically:

```
Most specific wins:
  1. Per-crate / per-app config (e.g., apps/.../biome.json)
  2. Workspace root config (e.g., biome.json)
  3. User-level config (e.g., ~/.config/...)
  4. Tool defaults
```

Exceptions:
- `pixi.toml` has no per-crate overrides — it's workspace-only
- `deny.toml` has no per-crate overrides — it's workspace-only
- `taplo.toml` uses `[[rule]]` sections for per-path overrides
  within a single file

---

## Adding a New Tool

When adding a new tool to the project:

1. **Check if it's on conda-forge**: `pixi search <tool>`
2. **Add to the appropriate pixi feature**: `[feature.X.dependencies]`
3. **Create its config file** at the workspace root (unless it's
   app-specific)
4. **Add pixi tasks** for common invocations
5. **Update this document** with the new config file
6. **Update `.knowledge/tooling/`** with a detail page for the tool
7. **Add to `.gitignore`** if the tool generates cache/output files
8. **Add to `taplo.toml` exclude** if the tool generates TOML files

---

## .gitignore Relevance

Config files that are generated or contain secrets should be in
`.gitignore`:

```gitignore
# pixi environments (installed packages)
.pixi/

# Rust build output
target/

# JS dependencies
node_modules/

# Build output
dist/

# pixi-skills cache (runtime)
.skills-cache/
```

Config files that are NOT in `.gitignore` (committed to git):
- All files listed in the tables above
- `pixi.lock`, `Cargo.lock`, `bun.lock` (lockfiles)
- `CHANGELOG.md` (generated but committed)
- `completions/*` (generated but committed)
- Generated CLI docs and schema (committed for non-Rust contributors)

## Related Concepts

- [Conventions — Context](./CONTEXT.md)
- [Workspace Layout](../architecture/workspace-layout.md)
- [Tooling — Context](../tooling/CONTEXT.md)
