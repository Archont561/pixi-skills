---
title: "skills-provider-prefix"
section: crates
kind: detail
tags: [crates, provider, prefix, prefix-dev, oci, enterprise, private]
relates_to:
  - crates/skills-core
  - crates/skills-provider-conda
  - landscape/pixi-ecosystem
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# skills-provider-prefix

Implements `SkillRegistry` for prefix.dev channels. While prefix.dev
channels are technically conda channels, this provider adds
prefix.dev-specific features: organization management, API-driven
search, and tighter integration with the pixi ecosystem.

---

## Crate Identity

```toml
[package]
name = "skills-provider-prefix"
version = "0.1.0"
edition = "2021"

[dependencies]
skills-core = { path = "../skills-core" }
rattler_conda_types = "0.x"
reqwest = { version = "0.12", features = ["json"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
url = "2"
```

- **Published**: yes
- **Dependents**: pixi-skills CLI (via feature flag `prefix`)
- **Dependencies on workspace crates**: `skills-core` only

---

## Why a Separate Provider (Not Just Conda)?

The conda provider handles any conda channel, including prefix.dev
channels. The prefix provider adds value in three ways:

### 1. prefix.dev REST API
prefix.dev has a REST API that enables richer operations than raw
repodata parsing:
- Search by description, tags, and metadata (not just package name)
- List packages by organization
- Get download statistics and popularity signals
- Access package README and documentation

### 2. Organization-scoped discovery
```toml
[[skill]]
name = "internal-api"
source = "prefix"
channel = "my-company"        # Short name, not full URL
version = "^2.0"
```
The prefix provider resolves `"my-company"` to
`https://repo.prefix.dev/my-company` automatically.

### 3. Future OCI registry support
prefix.dev is exploring OCI-based package distribution. This provider
is the natural home for OCI integration when it becomes available.

---

## Relationship to Conda Provider

The prefix provider can delegate to the conda provider for actual
package fetching and extraction. It adds a layer on top:

```
User request → prefix provider
                  │
                  ├── Search: use prefix.dev REST API (richer results)
                  ├── List: use prefix.dev REST API (org-scoped)
                  └── Fetch: delegate to conda provider
                              (same repodata + package extraction)
```

This avoids duplicating rattler integration code while providing
prefix.dev-specific UX improvements.

---

## Configuration

```toml
# skills.toml
[[skill]]
name = "internal-skill"
source = "prefix"
channel = "my-org"               # Resolves to repo.prefix.dev/my-org
version = ">=1.0"

[[skill]]
name = "public-skill"
source = "prefix"
channel = "conda-forge"          # Also works for public channels
version = "^2.0"
```

### Authentication

prefix.dev authentication is handled via:
1. `PREFIX_DEV_TOKEN` environment variable
2. `pixi auth login` stored credentials (in rattler credential store)
3. Token passed in channel URL (not recommended)

---

## Testing Strategy

| Test type | What it covers |
|---|---|
| Unit tests | Channel URL resolution, org name → URL mapping |
| Integration (mocked) | REST API responses simulated with wiremock |
| Integration (live) | Gated behind `live-tests`, queries public prefix.dev channels |
