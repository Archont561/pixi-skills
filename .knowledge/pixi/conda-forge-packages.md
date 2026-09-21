---
type: Reference
title: "conda-forge Packages"
description: "Planned conda-forge toolchain packages, version constraints, and pinning strategy."
section: pixi
kind: detail
tags: [pixi, conda-forge, packages, dependencies, versions, pinning]
status: stable
created: "2025-01-01"
updated: "2026-09-21"
---

# conda-forge Packages

Every tool and runtime in the pixi-skills workspace is installed from
conda-forge. This page catalogs every package, why it's needed, and
the version pinning strategy.

---

## Package Catalog

> **Version snapshot verified 2026-09-17.** Latest-usable versions at
> review time: Rust 1.98.1, Bun 1.4.x, Node.js 24 (Active LTS),
> Biome 2.5.x, cargo-deny 0.20.2, cargo-nextest 0.9.143, taplo 0.9.x,
> convco 0.6.4 (crates.io only). Re-verify before each dependency
> refresh (`pixi update`).
>
> **Amended 2026-09-21:** those are *upstream* versions. What conda-forge
> actually ships can lag, and platform coverage can be narrower than the
> workspace's. `bun` is the live example — see
> [Windows and the docs feature](#windows-and-the-docs-feature).

### Runtime Toolchains

| Package | Feature | Version | Why |
|---|---|---|---|
| `rust` | `rust` | `>=1.85` | Rust compiler, cargo, rustfmt, clippy. The core language runtime. Floor raised from 1.80 → 1.85 (2026-09): Rust 2024 edition has been stable/default since 1.85; current stable is 1.98.1. |
| `bun` | `docs` (**scoped**, not win-64) | `>=1.2` | JavaScript runtime for the Astro docs site. Replaces Node.js + npm/pnpm. ⚠️ **No win-64 build on conda-forge** — verified 2026-09-21: v1.3.11 publishes `linux-64`, `linux-aarch64`, `osx-64`, `osx-arm64` only. Must be declared per target or the `docs` environment will not solve on Windows. conda-forge ships 1.3.11; the upstream 1.4.x line is still an open feedstock PR, so do not document 1.4-only behaviour. |
| `nodejs` | `docs` | `>=22` | Fallback runtime. Floor raised from 20 → 22 (2026-09): Astro 6 requires Node 22+; Node 24 is the Active LTS line. |

### Rust Development Tools

| Package | Feature | Version | Why |
|---|---|---|---|
| `cargo-nextest` | `lint` | `>=0.9` | Parallel test runner with per-test timeouts, retries, JUnit output. Still a rolling 0.9.x series (0.9.143 as of 2026-08). |
| `cargo-deny` | `lint` | `>=0.20` | License auditing, advisory checking, crate bans, source verification. Bumped from 0.16 (2026-09); 0.19/0.20 moved the project to Rust edition 2024 (source-build MSRV 1.88 — prebuilt conda-forge binaries are unaffected). |
| `taplo` | `lint` | `>=0.9` | TOML formatter and linter. Formats pixi.toml, Cargo.toml, etc. ⚠️ Upstream is low-activity since 2024 (still 0.9.x, TOML 1.1 support pending) — evaluate alternatives if it starts lagging on TOML 1.1 syntax. |

### JavaScript/TypeScript Tools

| Package | Feature | Version | Why |
|---|---|---|---|
| `biome` | `docs` | `>=2.3` | TS/JS/CSS linter and formatter. Installed from conda-forge (not npm) to keep package.json deps minimal. Bumped from 1.9 (2026-09): Biome 2.x has a new config format (`biome migrate --write`) and 2.3+ lints/formats TS & CSS *inside* `.astro` files. Latest is 2.5.x. |

### System Libraries

| Package | Feature | Version | Why |
|---|---|---|---|
| `openssl` | `rust` | `>=3` | TLS library required by `reqwest` (HTTP client) and `rattler_networking`. Without it, HTTP-based provider crates fail to compile. |
| `pkg-config` | `rust` | `>=0.29` | Helps Rust build scripts find `openssl` on Linux. Not needed on macOS (where `openssl` is in Homebrew/system) but required for portability. |
| `cmake` | `rust` | `>=3.28` | Required by `libgit2-sys` (dependency of convco's `git2` crate) and `zlib-ng-sys` (dependency of rattler for fast decompression). |

---

## Version Pinning Strategy

### Minimum version constraints

We use `>=X.Y` (minimum version) rather than `=X.Y.Z` (exact pin)
in `pixi.toml`:

```toml
rust = ">=1.85"       # Not "=1.98.1"
bun = ">=1.2"         # Not "=1.4.2"
biome = ">=2.3"       # Not "=2.5.11"
```

**Rationale**: `pixi.lock` handles exact pinning. The constraint in
`pixi.toml` is a compatibility floor — "we need at least this version."
The lockfile records the exact resolved version with content hashes.

### When to pin exactly

Use exact pins (`=X.Y.Z`) only when:
1. A specific version has a known regression (`bun = "=1.1.38"`)
2. A tool has breaking changes in minor versions (unusual for mature tools)
3. Reproducibility across lockfile updates is critical (pre-release)

### Updating dependencies

```bash
pixi update                    # Update all packages to latest matching constraints
pixi update rust               # Update just Rust
pixi update bun biome          # Update specific packages

# Always test after updating:
pixi run -e all ci             # Full CI pipeline
```

### Lock-only dependencies

Some packages are never specified in `pixi.toml` but appear in
`pixi.lock` as transitive dependencies. For example:
- `libgcc-ng` (Linux runtime)
- `libstdcxx-ng` (Linux C++ runtime)
- `ca-certificates` (TLS certificates)

These are resolved automatically by pixi's solver. We don't need
to manage them explicitly.

---

## Platform-Specific Packages

pixi resolves platform-specific packages automatically:

```toml
platforms = ["linux-64", "osx-arm64", "osx-64", "win-64"]
```

Some packages have platform-specific variants:
- `openssl`: different builds for Linux, macOS, Windows
- `rust`: includes platform-specific cross-compilation targets
- `cmake`: Windows builds use Visual Studio generators

pixi.lock records the resolved packages for each platform. A
single `pixi.lock` supports all four platforms — **but only if every
declared dependency exists on every declared platform.** One package
that is missing on one target makes that environment unsolvable there,
which is exactly the `bun` problem below.

---

## Windows and the docs feature

⚠️ **Design correction, 2026-09-21.** The workspace declares `win-64`
and the `docs` feature declares `bun`, but **conda-forge has no win-64
build of `bun`**. Verified against the conda-forge package listing on
2026-09-21: `bun` v1.3.11 publishes for `linux-64`, `linux-aarch64`,
`osx-64`, and `osx-arm64`. An unscoped declaration therefore fails to
solve on Windows with `No candidates were found for bun *`.

The sibling project
[pixi-sandbox](../landscape/pixi-sandbox.md) hit this same wall while
targeting `linux-64`/`osx-arm64`/`win-64`, and solved it by scoping the
dependency per target — keeping `win-64` in the workspace for the Rust
crates while the JS runtime stays on the platforms that have a build. Its
`biome` and `nodejs` dependencies remain unscoped and do solve on win-64,
which is the evidence that only `bun` needs the treatment:

```toml
# ✗ Unsolvable on win-64
[feature.docs.dependencies]
bun = ">=1.2"
biome = ">=2.3"
nodejs = ">=22"

# ✓ bun only where conda-forge ships it
[feature.docs.dependencies]
biome = ">=2.3"
nodejs = ">=22"

[feature.docs.target.linux-64.dependencies]
bun = ">=1.2"

[feature.docs.target.osx-arm64.dependencies]
bun = ">=1.2"

[feature.docs.target.osx-64.dependencies]
bun = ">=1.2"
```

### Consequences

- The docs site builds on Linux (CI) and macOS (by hand). A Windows
  contributor gets the Rust workspace, not `docs-dev`.
- Keep the `bun run` scripts Node-compatible so `nodejs` remains a
  working fallback for Windows docs contributors.
- `osx-64` does have a `bun` build, so scoping it as shown above is
  correct — but Intel macOS is not a CI target for this project, so
  dropping it from the platform list entirely is also defensible and
  cheapens every solve.
- Re-check when the
  [bun feedstock](https://github.com/conda-forge/bun-feedstock) adds a
  win-64 build or lands 1.4.x; until then this constraint is load-bearing.
- Add a CI gate on `pixi lock --check`. A single lock solve covers every
  declared platform, so it fails the moment any dependency goes missing
  on any target — which is how this `bun` problem would have been caught
  before it reached a Windows contributor.

---

## Verifying Installed Packages

```bash
# List all packages in an environment
pixi list                        # default environment
pixi list -e docs                # docs environment
pixi list -e all                 # all environment

# Check a specific package
pixi list | grep biome           # Version and build info

# Full package info
pixi info
```

---

## conda-forge Availability Check

Before adding a new tool, check if it's on conda-forge:

```bash
# Search conda-forge
pixi search <package-name>

# Or check the website
# https://prefix.dev/channels/conda-forge/packages/<package-name>
```

If a tool is NOT on conda-forge:
1. **Consider submitting a recipe** to conda-forge (most Rust binaries
   are straightforward to package)
2. **Use `cargo install`** as a fallback (e.g., convco)
3. **Build from source via xtask** (self-bootstrapping)

### Packages we'd like on conda-forge (not yet available)

| Package | Status | Workaround |
|---|---|---|
| `convco` | Still not on conda-forge (re-checked 2026-09); latest is 0.6.4 (2026-05) | `cargo install convco` or pre-built binary |

If you submit a conda-forge recipe for any of these, update this
document and switch the pixi.toml dependency.

---

## Security Considerations

### Package provenance

conda-forge packages are built by CI from reviewed recipes. The
supply chain is:
1. Recipe submitted as PR to `conda-forge/staged-recipes`
2. Reviewed by conda-forge maintainers
3. Built by CI (no local builds)
4. Signed and uploaded to `conda.anaconda.org/conda-forge`

### Hash verification

`pixi.lock` records content hashes (SHA-256) for every package.
When `pixi install` runs, it verifies the downloaded package matches
the expected hash. Tampered packages are rejected.

### Update auditing

When `pixi update` changes the lockfile, the diff shows exactly
which packages changed and to which versions. This diff should be
reviewed in PR review, especially for security-sensitive packages
(openssl, ca-certificates).

```bash
git diff pixi.lock    # Review package version changes
```

## Related Concepts

- [Pixi — Context](./CONTEXT.md)
- [Pixi Features](./features.md)
- [Pixi Environments](./environments.md)
- [Tooling — Context](../tooling/CONTEXT.md)
