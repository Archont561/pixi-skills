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
updated: 2026-09-17
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

### Source Format (updated 2026-09, ADR-008)

GitHub skills are referenced by repository; the unit is the **skill
folder** (agentskills.io standard):

```toml
# skills.toml
[[skill]]
name = "playwright"
source = "github"
repo = "anthropics/skills"
ref = "tag:v1.0.0"                    # or "branch:main", "commit:abc123",
                                      # or "^1.4" (semver range over [v]X.Y.Z tags)
path = "skills/playwright"            # folder containing SKILL.md
                                      # (default: repo convention probes below)

[[skill]]                             # Multi-skill repo, @skill convention:
name = "web-design-guidelines"        #   pixi skills add github:vercel-labs/agent-skills@web-design-guidelines
source = "github"
repo = "vercel-labs/agent-skills"
skill = "web-design-guidelines"       # resolves to skills/<skill>/ or <skill>/
ref = "^1.4"
```

**Folder resolution order** (first hit wins): explicit `path=` →
`skill=` selector (`skills/<skill>/`, then `<skill>/`) → repo root
(single-skill repo with root SKILL.md).

### Fetching Strategy

```
1. Resolve ref → commit SHA
   GET /repos/{owner}/{repo}/git/ref/tags/{tag}
   or
   GET /repos/{owner}/{repo}/branches/{branch}
   (for semver ranges: list tags, filter [v]X.Y.Z, pick max satisfying)

2. Fetch the skill FOLDER as a tree
   Preferred: GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1
     → filter entries under the skill path → fetch blobs
   Alternative (fewer calls): codeload tarball
     GET /repos/{owner}/{repo}/tarball/{sha} → extract subtree

3. Parse + hash
   YAML frontmatter of SKILL.md (spec fields; unknown preserved)
   companion skill.toml if present (manager envelope)
   Canonical TREE hash over the folder (ADR-008 §4)

4. Return Skill struct (bundle)
```

### skills.sh Compatibility (standard era)

The skills.sh ecosystem now publishes **spec-compliant folders**
(`vercel-labs/agent-skills`, `anthropics/skills`). Compatibility
target: *every source string `npx skills add` accepts* (see
`landscape/skills-sh.md` for the full source-format list).

| skills.sh convention | Our handling |
|---|---|
| Skill folder at repo root (single-skill repo) | Default probe finds root SKILL.md |
| `skills/<name>/` multi-skill layout | `skill = "<name>"` selector (== `@skill` UX) |
| YAML frontmatter (spec) | Parsed natively; unknown fields preserved |
| `scripts/`, `references/`, `assets/`, `agents/` | Fetched & installed as part of the bundle |
| Bare markdown, no frontmatter (legacy) | Read-only support: one-file bundle, name from H1/folder |
| No version tags | `ref: "branch:main"` works, `Latest` works (lint warns) |
| Semver-looking tags (`v1.4.0`) | Exposed as semver → ranges supported (ADR-004, amended) |

### Search Implementation

GitHub search has limitations for skill discovery:

```rust
async fn search(&self, query: &str) -> Result<Vec<SkillSummary>> {
    // Strategy 1: skills.sh public index (83k+ skills, leaderboard
    //   signals) — the normative search backend (ADR-009), with
    //   graceful degradation to strategies 2-3 on outage
    //
    // Strategy 2: GitHub code search for SKILL.md files
    // GET /search/code?q={query}+filename:SKILL.md
    //
    // Strategy 3: GitHub topic search
    // GET /search/repositories?q=topic:agent-skill+{query}
}
```

Search is best-effort for GitHub proper; the skills.sh index gives
ranked ecosystem coverage, and the conda provider gives exact
repodata search.

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
├── {owner}/{repo}/{commit_sha}/{skill_path}/
│   ├── SKILL.md
│   ├── skill.toml            # if present upstream
│   └── ...                   # scripts/, references/, ... (whole bundle)
└── rate-limit.json           # Cached rate limit status
```

Cache invalidation: bundles are keyed by commit SHA + skill path. If
the ref resolves to a new SHA, the old cache entry is stale but not
deleted (it may be useful for rollback). The cache doubles as the
content-addressed store — installs only ever copy from cache.

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
│   ├── trees-recursive.json         # Git Trees API (recursive) response
│   ├── ref-tag-v1.json              # Git ref resolution response
│   ├── tags-list.json               # Tag listing (semver range tests)
│   ├── search-code.json             # Code search response
│   └── rate-limit-exceeded.json     # 403 rate limit response
└── skills/
    ├── spec-folder/                 # SKILL.md (YAML) + skill.toml + scripts/
    ├── bare-markdown/               # legacy: plain SKILL.md, no frontmatter
    └── nested/skills/playwright/    # multi-skill repo layout (skills/<name>/)
```
