---
title: "Pixi Ecosystem"
section: landscape
kind: detail
tags: [landscape, pixi, rattler, conda, prefix-dev, pixi-pack, rattler-build]
relates_to:
  - landscape/CONTEXT
  - crates/skills-provider-conda
  - architecture/dependency-graph
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Pixi Ecosystem

The pixi/rattler/conda ecosystem that pixi-skills is built on. These
are not competitors — they are the foundation. pixi-skills extends
this ecosystem into the AI agent skills domain.

---

## Core Projects

### pixi

A cross-platform, multi-language package manager and workflow tool
built on the conda ecosystem. Provides developers with an experience
similar to cargo or yarn, but for any language.

**Version snapshot (2026-09-17):** latest release **v0.81.0**
(2026-09-15). Notable for us:
- **Lockfile v7** (since v0.68.0, 2026-05): more stable, portable
  (no machine-specific absolute paths), enables reproducible source
  builds. Requires collaborators/CI to run a recent pixi.
- `pixi build` is **deprecated → `pixi publish`** (relevant if we
  publish pixi-skills itself as a conda package).
- Multi-line tasks supported (v0.68+); `workspace = true` inheritance
  in environment dependency tables (v0.73+); better RISC-V defaults
  (v0.79+).

**Relevance to pixi-skills**:
- pixi-skills is a pixi extension (invoked as `pixi skills`)
- pixi provisions the pixi-skills development toolchain
- pixi's task system orchestrates the pixi-skills build pipeline
- pixi's lockfile model inspired `skills-lock.toml`

### rattler

A collection of Rust crates that implement the conda package
management specification. Unlike conda (Python), rattler is a
library designed for integration into other applications.

**Relevance to pixi-skills**:
- `skills-provider-conda` depends on rattler crates
- rattler provides repodata fetching, package extraction, version
  resolution, and authentication — all the heavy lifting for conda
  channel access

### Key rattler crates used

| Crate | pixi-skills usage |
|---|---|
| `rattler_conda_types` | Channel, PackageName, Version, MatchSpec, RepoDataRecord — core data types for conda operations |
| `rattler_repodata_gateway` | Fetching and caching repodata.json from conda channels. Handles HTTP, local, and OCI sources. |
| `rattler_package_streaming` | Extracting files from `.conda` (zstd) and `.tar.bz2` packages without full archive extraction |
| `rattler_lock` | Reading/writing conda lockfiles. Potential integration point with `pixi.lock`. |
| `rattler_networking` | Authentication middleware for private channels (prefix.dev tokens, conda tokens, keyring) |

### pixi-pack

Downloads `.conda` and `.tar.bz2` files from conda repositories to
create self-contained, offline-deployable environment bundles.

**Relevance to pixi-skills**:
- Skills installed from conda channels can be pixi-packed for offline
  use in airgapped environments
- This is a key enterprise differentiator — no other skill manager
  supports offline operation
- The conda provider works transparently with both online channels
  and local channels produced by pixi-pack

### rattler-build

A conda package build tool inspired by conda-build and boa. Produces
`.conda` packages installable by pixi, mamba, or conda.

**Relevance to pixi-skills**:
- Skill authors use rattler-build to create `skill-*` conda packages
- The "publishing-conda" guide on the docs site walks through using
  rattler-build to package a SKILL.md as a noarch conda package
- rattler-build has no dependency on Python or conda-build

---

## How pixi-skills Fits In

```
                    ┌─────────────────────┐
                    │    conda-forge      │
                    │  (package registry) │
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
        ┌───────────┐  ┌───────────┐  ┌─────────────────┐
        │   pixi    │  │ pixi-pack │  │  pixi-skills     │
        │ (env mgr) │  │ (bundler) │  │ (skills mgr)    │
        └─────┬─────┘  └───────────┘  └────────┬────────┘
              │                                 │
              │         ┌───────────────────────┘
              │         │
              ▼         ▼
        ┌───────────────────────┐
        │      rattler          │
        │   (Rust library)      │
        │                       │
        │  • conda_types        │
        │  • repodata_gateway   │
        │  • package_streaming  │
        │  • lock               │
        │  • networking         │
        └───────────────────────┘
```

pixi-skills is a **peer** of pixi and pixi-pack, not a child. All
three are independent applications built on the rattler library:
- pixi manages environments and packages
- pixi-pack bundles environments for offline use
- pixi-skills manages AI agent skills

They compose well: pixi installs pixi-skills, pixi-skills installs
skills from conda channels, pixi-pack bundles everything for offline.

---

## prefix.dev

The company behind pixi, rattler, and rattler-build. Also operates
a conda channel hosting service (prefix.dev) with:
- Organization management
- Private channels
- API access
- Package analytics

**Relevance to pixi-skills**:
- `skills-provider-prefix` uses the prefix.dev API for enhanced
  search and organization-scoped discovery
- prefix.dev is the recommended hosting for private/enterprise
  skill packages
- prefix.dev authentication integrates via `rattler_networking`

---

## Ecosystem Maturity (updated 2026-09-17)

| Project | Maturity | Current version | API stability |
|---|---|---|---|
| pixi | Production-ready, ~7k GitHub stars | v0.81.0 (2026-09) | Stable CLI, evolving config format |
| rattler | Production-ready | `rattler_conda_types` 0.50.0 (2026-09); py-rattler 0.25 (lockfile v7) | Crate APIs still evolving fast — minor bumps break; pin + test in CI |
| pixi-pack | Production-ready | — | Stable CLI |
| rattler-build | Production-ready | — | Stable CLI, recipe format evolving |
| prefix.dev | Production SaaS | — | Stable API |

### Implications for pixi-skills

- rattler crate API changes may require pixi-skills updates. We pin
  rattler to specific minor versions and test against them in CI.
  (Recent example of churn: lockfile v7 landed across pixi +
  py-rattler in 2026 — a breaking change requiring ecosystem-wide
  coordination. Expect similar waves; budget for them.)
- pixi's extension model is stable — our binary naming convention
  (`pixi-skills`) is a stable interface.
- conda package format is extremely stable (hasn't changed in years).
  Skills published as conda packages will remain installable long-term.
