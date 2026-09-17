---
title: "skills-provider-github"
section: crates
kind: detail
tags: [crates, provider, github, registry, skills-sh, compatibility]
relates_to:
  - crates/skills-core
  - crates/pixi-skills-cli
  - landscape/skills-sh
  - roadmap/mvp-phases
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# skills-provider-github

Implements `SkillRegistry` for GitHub repositories. This is the
**Phase 1 provider** — it exists to give pixi-skills instant access
to the existing skills.sh ecosystem on day one.

---

## Crate Identity

```toml
[package]
name = "skills-provider-github"
version = "0.1.0"
edition = "2021"

[dependencies]
skills-core = { path = "../skills-core" }
reqwest = { version = "0.12", features = ["json"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tracing = "0.1"
```

- **Published**: yes (alongside skills-core)
- **Dependents**: pixi-skills CLI (via feature flag `github`)
- **Dependencies on workspace crates**: `skills-core` only

---

## How It Works

### Source Format

GitHub skills are referenced by repository:

```toml
# skills.toml
[[skill]]
name = "playwright"
source = "github"
repo = "anthropics/skill-playwright"
ref = "tag:v1.0.0"                    # or "branch:main", "commit:abc123"
path = "SKILL.md"                     # optional, defaults to SKILL.md
```

### Fetching Strategy

```
1. Resolve ref → commit SHA
   GET /repos/{owner}/{repo}/git/ref/tags/{tag}
   or
   GET /repos/{owner}/{repo}/branches/{branch}

2. Fetch file content
   GET /repos/{owner}/{repo}/contents/{path}?ref={sha}
   (Returns base64-encoded content via GitHub API)
   or
   GET https://raw.githubusercontent.com/{owner}/{repo}/{sha}/{path}
   (Raw content, no API rate limit for public repos)

3. Parse SKILL.md
   Extract TOML frontmatter (if present)
   Compute content hash (SHA-256 of the raw content)

4. Return Skill struct
```

### skills.sh Compatibility

skills.sh publishes skills as GitHub repos following a loose convention.
This provider is compatible with those repos:

| skills.sh convention | Our handling |
|---|---|
| Skill content in `SKILL.md` at repo root | Default path is `SKILL.md` |
| No version tags | `ref: "branch:main"` works, `Latest` works |
| Multiple skills per repo (subdirectories) | `path` field supports subdirectories |
| No TOML frontmatter | Frontmatter is optional — plain markdown works |

### Search Implementation

GitHub search has limitations for skill discovery:

```rust
async fn search(&self, query: &str) -> Result<Vec<SkillSummary>> {
    // Strategy 1: GitHub code search for SKILL.md files
    // GET /search/code?q={query}+filename:SKILL.md
    //
    // Strategy 2: GitHub topic search
    // GET /search/repositories?q=topic:pixi-skill+{query}
    //
    // Strategy 3: Curated registry (future)
    // Fetch a known index repo that lists skill repos
}
```

Search is best-effort for GitHub. The conda provider will have much
better search via repodata.

### Rate Limiting

- **Unauthenticated**: 60 requests/hour (GitHub API limit)
- **Authenticated**: 5,000 requests/hour (with `GITHUB_TOKEN`)
- **Raw content**: no rate limit for public repos

The provider checks for `GITHUB_TOKEN` in the environment and
includes it in API requests if present. The `pixi skills doctor`
command reports the current rate limit status.

### Caching

Fetched skills are cached locally to avoid repeated API calls:

```
~/.cache/pixi-skills/github/
├── {owner}/{repo}/{commit_sha}/
│   └── SKILL.md
└── rate-limit.json        # Cached rate limit status
```

Cache invalidation: content is keyed by commit SHA. If the ref
resolves to a new SHA, the old cache entry is stale but not deleted
(it may be useful for rollback).

---

## SkillRegistry Implementation

```rust
pub struct GitHubRegistry {
    client: reqwest::Client,
    cache_dir: PathBuf,
    token: Option<String>,
}

#[async_trait]
impl SkillRegistry for GitHubRegistry {
    fn supports(&self, source: &SkillSource) -> bool {
        matches!(source, SkillSource::GitHub { .. })
    }

    fn provider_kind(&self) -> ProviderKind {
        ProviderKind::GitHub
    }

    async fn search(&self, query: &str) -> Result<Vec<SkillSummary>> {
        // GitHub code search + topic search
    }

    async fn list(&self, source: &SkillSource) -> Result<Vec<SkillSummary>> {
        // List SKILL.md files in the repo (tree API)
    }

    async fn fetch(
        &self,
        id: &SkillId,
        version: &VersionReq,
    ) -> Result<Skill> {
        // Resolve ref → SHA → fetch content → parse → return Skill
    }
}
```

---

## Testing Strategy

| Test type | What it covers |
|---|---|
| Unit tests | URL construction, ref parsing, SKILL.md frontmatter extraction |
| Integration tests (mocked) | Full fetch flow with `wiremock` or `mockito` simulating GitHub API |
| Integration tests (live) | Optional, gated behind `#[cfg(feature = "live-tests")]`, hitting real GitHub repos |

### Test Fixtures

```
skills-provider-github/tests/fixtures/
├── api-responses/
│   ├── contents-skill-md.json       # GitHub Contents API response
│   ├── ref-tag-v1.json              # Git ref resolution response
│   ├── search-code.json             # Code search response
│   └── rate-limit-exceeded.json     # 403 rate limit response
└── skills/
    ├── plain-markdown.md            # SKILL.md without frontmatter
    ├── with-frontmatter.md          # SKILL.md with TOML frontmatter
    └── nested/
        └── SKILL.md                 # Skill in a subdirectory
```
