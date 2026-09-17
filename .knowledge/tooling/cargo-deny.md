---
type: Reference
title: "cargo-deny"
description: "Planned dependency auditing, license policy, advisory checks, and source restrictions."
section: tooling
kind: detail
tags: [tooling, cargo-deny, licenses, advisories, security, audit, dependencies]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# cargo-deny

A cargo plugin for linting your dependencies. Checks licenses,
detects known vulnerabilities (RustSec advisory database), bans
problematic crates, and verifies dependency sources.

---

## Installation

```toml
# pixi.toml
[feature.lint.dependencies]
cargo-deny = ">=0.20"
```

Installed via pixi from conda-forge. No `cargo install` needed.

> **Updated 2026-09-17:** floor raised from 0.16 → 0.20. The
> 0.19/0.20 lines (2026) moved the project to Rust edition 2024 with
> a source-build MSRV of Rust 1.88 — irrelevant for us because pixi
> installs prebuilt binaries. Latest release is 0.20.2 (2026-07).

---

## Configuration: `deny.toml`

```toml
# deny.toml (workspace root)

# ── Advisories ─────────────────────────────────────────────────────
# Check against the RustSec advisory database for known vulnerabilities.
[advisories]
db-path = "~/.cargo/advisory-db"
db-urls = ["https://github.com/rustsec/advisory-db"]
vulnerability = "deny"           # Deny any crate with a known vulnerability
unmaintained = "warn"            # Warn about unmaintained crates
yanked = "deny"                  # Deny yanked crate versions
notice = "warn"                  # Warn about informational notices
ignore = [
    # List specific advisory IDs to ignore (with justification):
    # "RUSTSEC-20XX-XXXX",  # Reason for ignoring
]

# ── Licenses ───────────────────────────────────────────────────────
# Enforce a license allowlist. All dependencies must use an approved
# license.
[licenses]
unlicensed = "deny"              # Deny crates with no license
copyleft = "deny"                # Deny copyleft licenses (GPL, AGPL)
allow = [
    "MIT",
    "Apache-2.0",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-3.0",
    "Unicode-DFS-2016",
    "Zlib",
    "BSL-1.0",                   # Boost
    "CC0-1.0",                   # Public domain equivalent
    "OpenSSL",
]
# Some crates have non-standard license expressions. Handle them:
exceptions = [
    # { name = "some-crate", allow = ["LGPL-2.1-only"] },
]

# Confidence threshold for license detection
confidence-threshold = 0.8

[licenses.private]
# Workspace crates don't need license checks
ignore = true

# ── Bans ───────────────────────────────────────────────────────────
# Ban specific crates or detect problematic dependency patterns.
[bans]
multiple-versions = "warn"       # Warn if multiple versions of a crate exist
wildcards = "deny"               # Deny wildcard version requirements
highlight = "all"                # Highlight all duplicated crate versions
allow = []
deny = [
    # Ban specific crates:
    # { name = "openssl", wrappers = ["openssl-sys"] },
]
skip = [
    # Allow specific crates to have multiple versions:
    # { name = "some-crate", version = "=1.0" },
]
skip-tree = [
    # Skip entire dependency trees for multi-version checks:
    # { name = "windows-sys" },
]

# ── Sources ────────────────────────────────────────────────────────
# Verify that all dependencies come from trusted sources.
[sources]
unknown-registry = "deny"        # Deny crates from unknown registries
unknown-git = "deny"             # Deny crates from unknown git repos
allow-registry = [
    "https://github.com/rust-lang/crates.io-index",
]
allow-git = []
```

---

## What cargo-deny Checks

### 1. Advisories (`cargo deny check advisories`)

Scans all dependencies against the RustSec advisory database:

| Severity | Action | Example |
|---|---|---|
| Vulnerability | **deny** (CI fails) | Memory safety bug, RCE |
| Unmaintained | **warn** (CI continues) | Crate abandoned by maintainer |
| Yanked | **deny** (CI fails) | Version recalled by author |
| Notice | **warn** (CI continues) | Informational (deprecation) |

The advisory DB is fetched fresh on each run. CI always checks
against the latest advisories.

### 2. Licenses (`cargo deny check licenses`)

Enforces a license allowlist:

- **Allowed**: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC,
  Unicode-3.0, Zlib, BSL-1.0, CC0-1.0
- **Denied**: GPL, AGPL, LGPL (copyleft), any unlicensed crate
- **Workspace crates**: excluded from checks (they're ours)

This prevents accidental introduction of copyleft dependencies that
would affect pixi-skills' licensing.

### 3. Bans (`cargo deny check bans`)

Detects problematic patterns:

- **Multiple versions**: warns when two versions of the same crate
  coexist in the dependency tree (binary bloat, potential confusion)
- **Wildcards**: denies `*` version requirements (non-reproducible)
- **Specific bans**: custom deny-list for known-bad crates

### 4. Sources (`cargo deny check sources`)

Verifies that all dependencies come from crates.io:

- **Unknown registries**: denied (no shadow registries)
- **Unknown git sources**: denied (no unvetted git deps)
- **Exceptions**: explicitly listed if needed

---

## pixi Task Integration

```toml
# pixi.toml
[feature.rust.tasks]
lint-deps = "cargo deny check"

# Part of the composite lint task
lint = { depends-on = ["lint-rust", "lint-toml", "lint-deps", "lint-workspace"] }
```

### Running Individual Checks

```bash
pixi run -- cargo deny check advisories    # Just vulnerability scan
pixi run -- cargo deny check licenses      # Just license audit
pixi run -- cargo deny check bans          # Just ban/duplication check
pixi run -- cargo deny check sources       # Just source verification
pixi run lint-deps                         # All checks at once
```

---

## CI Behavior

cargo-deny runs as part of the `lint-all` composite task in CI. If
any check fails with `deny` severity, CI fails immediately.

### Advisory DB Freshness

The advisory DB is fetched on each CI run. This means CI can fail
on a previously-passing commit if a new advisory is published.
This is intentional — we want to know about new vulnerabilities
immediately, even in unchanged code.

### Handling False Positives

If an advisory doesn't apply to our usage (e.g., we don't use the
affected feature), add it to the `ignore` list in `deny.toml` with
a comment explaining why:

```toml
[advisories]
ignore = [
    # RUSTSEC-2024-XXXX: affects feature X which we don't use.
    # Tracked in: https://github.com/our-org/pixi-skills/issues/123
    "RUSTSEC-2024-XXXX",
]
```

---

## Updating the Advisory Database

The advisory DB is cached at `~/.cargo/advisory-db`. To manually
refresh:

```bash
cargo deny fetch
```

In CI, the DB is always fresh (no cache between runs by default).
If CI caching is enabled for the cargo registry, ensure the advisory
DB cache is excluded or has a short TTL.

---

## When New Dependencies Are Added

After `cargo add <new-crate>`:

1. Run `pixi run lint-deps` to check the new dependency
2. If the license is not in the allowlist: either add it to `allow`
   (if acceptable) or find an alternative crate
3. If multiple-versions warnings appear: consider whether the
   duplication is acceptable or if version alignment is possible
4. Commit `deny.toml` changes alongside the dependency addition

---

## rattler-Specific Considerations

The `rattler_*` crates pull in a substantial dependency tree. Some
known patterns:

- **Multiple versions**: `windows-sys` often appears in multiple
  versions across the rattler dependency tree. This is typically
  acceptable — add to `skip-tree` if the warning is noisy.
- **OpenSSL**: rattler may depend on `openssl-sys`. The `openssl`
  crate is not banned because we need it for HTTPS. It's listed
  in `pixi.toml` dependencies to ensure the system library is
  available.
- **License edge cases**: some Unicode consortium crates use
  `Unicode-3.0` or `Unicode-DFS-2016` licenses — both are in
  our allowlist.

## Related Concepts

- [Tooling — Context](./CONTEXT.md)
- [Pixi Tasks](../pixi/tasks.md)
- [GitHub Actions](../cicd/github-actions.md)
- [Config Files](../conventions/config-files.md)
