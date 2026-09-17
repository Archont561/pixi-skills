---
title: "conda-forge Packages"
section: pixi
kind: detail
tags: [pixi, conda-forge, packages, dependencies, versions, pinning]
relates_to:
  - pixi/CONTEXT
  - pixi/features
  - pixi/environments
  - tooling/CONTEXT
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# conda-forge Packages

Every tool and runtime in the pixi-skills workspace is installed from
conda-forge. This page catalogs every package, why it's needed, and
the version pinning strategy.

---

## Package Catalog

### Runtime Toolchains

| Package | Feature | Version | Why |
|---|---|---|---|
| `rust` | `rust` | `>=1.80` | Rust compiler, cargo, rustfmt, clippy. The core language runtime. Must be 1.80+ for workspace lint inheritance and recent async trait improvements. |
| `bun` | `docs` | `>=1.1` | JavaScript runtime for the Astro docs site. Replaces Node.js + npm/pnpm. |
| `nodejs` | `docs` | `>=20` | Fallback runtime. Some Astro dependencies may need Node.js APIs not yet in bun. LTS version for stability. |

### Rust Development Tools

| Package | Feature | Version | Why |
|---|---|---|---|
| `cargo-nextest` | `lint` | `>=0.9` | Parallel test runner with per-test timeouts, retries, JUnit output. |
| `cargo-deny` | `lint` | `>=0.16` | License auditing, advisory checking, crate bans, source verification. |
| `taplo` | `lint` | `>=0.9` | TOML formatter and linter. Formats pixi.toml, Cargo.toml, etc. |

### JavaScript/TypeScript Tools

| Package | Feature | Version | Why |
|---|---|---|---|
| `biome` | `docs` | `>=1.9` | TS/JS/CSS linter and formatter. Installed from conda-forge (not npm) to keep package.json deps minimal. |

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
rust = ">=1.80"      # Not "=1.80.1"
bun = ">=1.1"        # Not "=1.1.38"
biome = ">=1.9"      # Not "=1.9.4"
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
single `pixi.lock` supports all four platforms.

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
| `convco` | Not on conda-forge | `cargo install convco` or pre-built binary |

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
