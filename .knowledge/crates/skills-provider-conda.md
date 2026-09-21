---
type: Component Design
title: "skills-provider-conda"
description: "Design of conda-channel skill discovery and installation using rattler."
section: crates
kind: detail
tags: [crates, provider, conda, rattler, channels, packages, noarch]
status: stable
created: "2025-01-01"
updated: "2026-09-21"
---

# skills-provider-conda

Implements `SkillRegistry` for conda channels. This is the **first-class
provider** — the one that delivers pixi-skills' key differentiators:
version pinning, lockfile integrity, private channels, and offline
bundling (via pixi-pack).

---

## Crate Identity

```toml
[package]
name = "skills-provider-conda"
version = "0.1.0"
edition = "2021"

[dependencies]
skills-core = { path = "../skills-core" }
rattler_conda_types = "0.x"
rattler_repodata_gateway = "0.x"
rattler_package_streaming = "0.x"
rattler_lock = "0.x"
rattler_networking = "0.x"
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
url = "2"
```

- **Published**: yes
- **Dependents**: pixi-skills CLI (via feature flag `conda`)
- **Dependencies on workspace crates**: `skills-core` only

---

## How It Works

### Skill Package Convention (updated 2026-09, ADR-002 amended + ADR-008)

Skills are published as `noarch` conda packages with the `skill-*`
naming prefix. The payload is a **folder tree** per the agentskills.io
standard:

```
Package: skill-playwright
Version: 1.2.3
Build: 0
Subdir: noarch
Files:
  skills/
    └── playwright/               # folder name == frontmatter name
        ├── SKILL.md              # required (YAML frontmatter, spec)
        ├── skill.toml            # optional manager envelope
        ├── scripts/              # optional
        │   └── login-flow.sh
        ├── references/           # optional
        └── assets/               # optional
  info/
    ├── index.json
    ├── about.json            # tags: ["agent-skill", "pixi-skill"]
    └── paths.json
```

Package `version` is authoritative; `skill.toml [package].version`
should mirror it (lint warns on divergence).

### Discovery via Repodata

```
1. Fetch repodata for the channel
   rattler_repodata_gateway::fetch(channel, "noarch")

2. Filter packages by name prefix
   packages.filter(|p| p.name.starts_with("skill-"))

3. Optionally filter by metadata label
   packages.filter(|p| p.about.tags.contains("pixi-skill"))

4. Return SkillSummary list with version info
```

### Fetching Strategy

```
1. Resolve version constraint → specific RepoDataRecord
   rattler_conda_types::MatchSpec + solver

2. Download the .conda package
   rattler_repodata_gateway::download(record)

3. Extract the skill FOLDER from the package
   rattler_package_streaming::extract("skills/<name>/**")
   (single-skill packages; reject ambiguous multi-skill payloads)

4. Parse SKILL.md (YAML frontmatter) + companion skill.toml,
   compute canonical tree hash over the folder

5. Return Skill struct (bundle)
```

### Version Resolution

Conda version resolution is handled by the rattler solver. The
provider translates `VersionReq::Semver("^1.0")` into a conda
`MatchSpec` and lets the solver find the best matching version.

```rust
// Translate VersionReq to MatchSpec
fn to_match_spec(name: &str, req: &VersionReq) -> MatchSpec {
    match req {
        VersionReq::Semver(range) => {
            // Convert semver range to conda version spec
            // "^1.0" → ">=1.0,<2.0"
            MatchSpec::from_str(&format!("{}={}", name, range))
        }
        VersionReq::Exact(ver) => {
            MatchSpec::from_str(&format!("{}=={}", name, ver))
        }
        VersionReq::Latest => {
            MatchSpec::from_str(name)
        }
        _ => unreachable!("Git refs not supported for conda"),
    }
}
```

---

## rattler Crate Integration

### Which rattler crates and why

| Crate | Purpose in this provider |
|---|---|
| `rattler_conda_types` | `Channel`, `PackageName`, `Version`, `MatchSpec`, `RepoDataRecord`, `Platform` — all the core conda data types |
| `rattler_repodata_gateway` | Fetching, caching, and parsing `repodata.json` from conda channels. Handles HTTP, local files, OCI. Manages the repodata cache (`~/.cache/rattler/`). |
| `rattler_package_streaming` | Extracting files from `.conda` (zstd-compressed) and `.tar.bz2` packages without extracting the entire archive. We extract only `skills/<name>/**`. |
| `rattler_lock` | Reading and writing conda-style lockfiles. We use this for potential integration with `pixi.lock`, though our primary lockfile is `skills-lock.toml`. |
| `rattler_networking` | Authentication middleware — handles tokens for private channels (prefix.dev, Artifactory, etc.) |

### rattler Version Pinning

rattler crates are actively developed and APIs change. We pin to a
specific minor version range and test against it in CI. The
`pixi.lock` ensures all developers use the same rattler version
through the Rust toolchain.

---

## SkillRegistry Implementation

```rust
pub struct CondaRegistry {
    channels: Vec<Channel>,
    cache_dir: PathBuf,
    auth_middleware: Option<AuthenticationMiddleware>,
}

#[async_trait]
impl SkillRegistry for CondaRegistry {
    fn supports(&self, source: &SkillSource) -> bool {
        matches!(source, SkillSource::Conda { .. })
    }

    fn provider_kind(&self) -> ProviderKind {
        ProviderKind::Conda
    }

    async fn search(&self, query: &str) -> Result<Vec<SkillSummary>> {
        // Fetch repodata for all configured channels
        // Filter by "skill-*" prefix AND query match
        // Return sorted by relevance
    }

    async fn list(&self, source: &SkillSource) -> Result<Vec<SkillSummary>> {
        // Fetch repodata for the specified channel
        // Filter by "skill-*" prefix
        // Return all skill packages with version info
    }

    async fn fetch(
        &self,
        id: &SkillId,
        version: &VersionReq,
    ) -> Result<Skill> {
        // Resolve version via MatchSpec
        // Download .conda package
        // Extract the skills/<name>/** folder tree
        // Parse (YAML + companion) + tree-hash + return bundle
    }
}
```

---

## Private Channel Support

One of pixi-skills' key enterprise differentiators. Private conda
channels (prefix.dev organizations, Artifactory, local channels)
work transparently:

```toml
# skills.toml
[[skill]]
name = "internal-api"
source = "conda"
channel = "https://repo.prefix.dev/my-company-skills"
version = "^2.0"
```

Authentication is handled by `rattler_networking`, which reads
credentials from:
1. Environment variables (`CONDA_TOKEN`, `PREFIX_DEV_TOKEN`)
2. `~/.rattler/credentials.json`
3. Keyring integration (platform-specific)

---

## Offline Support (pixi-pack Integration)

Skills installed from conda channels can be bundled for offline use
with pixi-pack. The workflow:

```bash
# Online machine: pack all skills
pixi pack --environment skills-env --output skills-bundle.tar.zst

# Offline machine: unpack
pixi unpack skills-bundle.tar.zst
# Skills are now available locally, no network needed
```

This is possible because conda packages are self-contained archives.
The conda provider works with both online channels and local
directory channels (from pixi-pack output).

> **Measured precedent (2026-09-21).** The sibling project
> [pixi-sandbox](../landscape/pixi-sandbox.md) implements this exact
> transport in Rust: `pixi-pack` output plus a sha256 manifest published
> to a Git orphan branch, restored with zero network and proven inside
> `unshare -rn`. Two details worth copying for the offline test fixtures
> above — it publishes `.conda` files as whole, content-addressed blobs
> (files above 95 MiB are split into `.partNNN` and rejoined after
> verification), and it rejects dynamically linked tools outright. Its
> measured payload for a small two-environment project was 262 MB of
> transport, ~110 MB after Git dedup.

---

## Testing Strategy

| Test type | What it covers |
|---|---|
| Unit tests | MatchSpec construction, version translation, package name filtering |
| Integration tests (mocked) | Repodata parsing with fixture data, package extraction from test `.conda` files |
| Integration tests (live) | Gated behind `live-tests` feature, fetches from conda-forge |

### Building Test `.conda` Packages

Test fixtures include minimal `.conda` packages built with
`rattler-build`:

```
skills-provider-conda/tests/fixtures/
├── repodata/
│   └── noarch/
│       └── repodata.json         # Fixture repodata with skill-* packages
├── packages/
│   ├── skill-test-1.0.0-0.conda  # Minimal skill package
│   └── skill-test-2.0.0-0.conda  # Updated version for upgrade tests
└── channels/
    └── local/                     # Local channel directory for offline tests
```

## Related Concepts

- [skills-core](./skills-core.md)
- [pixi-skills CLI](./pixi-skills-cli.md)
- [Pixi Ecosystem](../landscape/pixi-ecosystem.md)
- [Design Decisions](../architecture/design-decisions.md)
