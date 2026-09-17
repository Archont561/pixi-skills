---
title: "skills-core"
section: crates
kind: detail
tags: [crates, skills-core, traits, models, installer, agent, registry]
relates_to:
  - crates/CONTEXT
  - crates/skills-provider-github
  - crates/skills-provider-conda
  - crates/pixi-skills-cli
  - architecture/dependency-graph
  - conventions/skill-format
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# skills-core

The provider-agnostic foundation crate. Defines all shared types,
traits, and logic that provider crates and the CLI depend on.
This crate has **zero provider-specific code** and **zero network I/O**.

---

## Crate Identity

```toml
[package]
name = "skills-core"
version = "0.1.0"
edition = "2021"
license = "MIT OR Apache-2.0"
description = "Core types and traits for AI agent skills management"
```

- **Published**: yes (to crates.io, eventually)
- **Dependents**: all provider crates, pixi-skills CLI, xtask
- **Dependencies on workspace crates**: none (leaf crate)

---

## Module Map

```
skills-core/src/
├── lib.rs              # Public API re-exports
├── skill.rs            # Skill data model
├── registry.rs         # SkillRegistry trait
├── manifest.rs         # skills.toml + skills-lock.toml parsing
├── installer.rs        # Install/uninstall/symlink skills into agent dirs
├── agent.rs            # Agent detection + configuration
└── config.rs           # User + project configuration
```

---

## Key Types (`skill.rs`)

### `Skill`
The fully resolved skill — metadata plus content. Returned by
`SkillRegistry::fetch()`.

```rust
pub struct Skill {
    pub id: SkillId,
    pub version: SkillVersion,
    pub source: SkillSource,
    pub metadata: SkillMetadata,
    pub content: String,          // The markdown body
    pub content_hash: ContentHash, // SHA-256 of content
}
```

### `SkillId`
A globally unique identifier for a skill. Composed of provider +
namespace + name.

```rust
pub struct SkillId {
    pub provider: ProviderKind,   // GitHub, Conda, Prefix, PyPI
    pub namespace: String,        // "conda-forge", "github:user/repo"
    pub name: String,             // "playwright", "polars"
}
```

### `SkillSummary`
A lightweight summary returned by `search()` and `list()`. Does not
contain the full content — only metadata for display.

```rust
pub struct SkillSummary {
    pub id: SkillId,
    pub version: SkillVersion,
    pub description: Option<String>,
    pub agents: Vec<AgentKind>,   // Compatible agents
    pub tags: Vec<String>,
}
```

### `SkillSource`
Where a skill comes from. Used to route to the correct provider.

```rust
pub enum SkillSource {
    GitHub { owner: String, repo: String, path: Option<String> },
    Conda { channel: Url, package: String },
    Prefix { channel: String, package: String },
    PyPI { package: String, index: Option<Url> },
    Local { path: PathBuf },
}
```

### `SkillVersion`
A provider-native version representation.

```rust
pub enum SkillVersion {
    Semver(semver::Version),
    Conda(String),                // "1.2.3-hdeadbeef_0"
    GitRef(GitRef),               // Branch, Tag, or Commit
    PyPI(String),                 // PEP 440
}
```

### `VersionReq`
A version constraint (for skills.toml manifests).

```rust
pub enum VersionReq {
    Semver(semver::VersionReq),   // "^1.0", "~1.2", ">=1,<2"
    Exact(SkillVersion),          // "=1.2.3"
    GitRef(GitRef),               // "branch:main", "tag:v1.0"
    Latest,                       // "*"
}
```

### `ContentHash`
A SHA-256 hash of the skill's content. Used in the lockfile for
integrity verification.

```rust
pub struct ContentHash(pub [u8; 32]);
```

---

## The SkillRegistry Trait (`registry.rs`)

The primary extension point. Every provider crate implements this trait.

```rust
#[async_trait]
pub trait SkillRegistry: Send + Sync {
    /// Search for skills matching a query string.
    /// Returns summaries (no full content).
    async fn search(&self, query: &str) -> Result<Vec<SkillSummary>>;

    /// List all skills from a specific source.
    async fn list(&self, source: &SkillSource) -> Result<Vec<SkillSummary>>;

    /// Fetch a specific skill by ID, resolved to a version matching
    /// the given constraint.
    async fn fetch(
        &self,
        id: &SkillId,
        version: &VersionReq,
    ) -> Result<Skill>;

    /// Check if this registry handles the given source.
    /// Used for routing: the CLI iterates providers and calls
    /// the first one that returns true.
    fn supports(&self, source: &SkillSource) -> bool;

    /// Return the provider kind this registry implements.
    fn provider_kind(&self) -> ProviderKind;
}
```

### Design Notes

- **`async_trait`**: all methods are async because provider operations
  involve network I/O (except `supports()` and `provider_kind()`).

- **`Send + Sync`**: providers must be safe to use from async runtimes
  with work-stealing (tokio).

- **Error type**: `Result<T>` uses a crate-level `SkillsError` enum
  with variants for network errors, version resolution failures,
  skill-not-found, parse errors, etc.

- **No `&mut self`**: the trait uses shared references. Providers
  that need interior mutability (e.g., caching) use `RwLock` or
  `DashMap` internally.

---

## Manifest Parsing (`manifest.rs`)

### `skills.toml` — The project manifest

Declares which skills a project needs and where to get them.

```toml
# skills.toml
[project]
name = "my-project"
agents = ["claude", "cursor"]    # Target agents

[[skill]]
name = "playwright"
source = "conda"
channel = "conda-forge"
version = "^1.0"

[[skill]]
name = "polars"
source = "github"
repo = "user/polars-skill"
ref = "tag:v2.1.0"

[[skill]]
name = "internal-api"
source = "prefix"
channel = "my-company"
version = ">=1.0,<2.0"
```

### `skills-lock.toml` — The lockfile

Pins exact resolved versions with content hashes.

```toml
# skills-lock.toml — DO NOT EDIT MANUALLY
# Generated by `pixi skills lock`

version = 1

[[skill]]
name = "playwright"
provider = "conda"
channel = "https://conda.anaconda.org/conda-forge"
package = "skill-playwright"
version = "1.2.3-h1234567_0"
content_hash = "sha256:abcdef1234567890..."
installed_at = "2025-01-15T10:30:00Z"

[[skill]]
name = "polars"
provider = "github"
repo = "user/polars-skill"
ref = "tag:v2.1.0"
commit = "abc123def456"
content_hash = "sha256:fedcba0987654321..."
installed_at = "2025-01-15T10:30:01Z"
```

### Rust Types

```rust
pub struct SkillsManifest {
    pub project: ProjectConfig,
    pub skills: Vec<SkillRequirement>,
}

pub struct SkillsLockfile {
    pub version: u32,
    pub skills: Vec<LockedSkill>,
}

pub struct LockedSkill {
    pub name: String,
    pub provider: ProviderKind,
    pub source_details: SkillSource,
    pub version: SkillVersion,
    pub content_hash: ContentHash,
    pub installed_at: DateTime<Utc>,
}
```

---

## Installer (`installer.rs`)

Handles installing, uninstalling, and updating skills in agent
configuration directories.

### Core Operations

```rust
pub struct SkillInstaller {
    agents: Vec<AgentConfig>,
}

impl SkillInstaller {
    /// Install a skill into all configured agent directories.
    /// Creates the target directory if it doesn't exist.
    /// Writes SKILL.md (or the agent-specific equivalent).
    pub async fn install(&self, skill: &Skill) -> Result<InstallReceipt>;

    /// Remove a skill from all agent directories.
    pub async fn uninstall(&self, skill_name: &str) -> Result<()>;

    /// Check if a skill is currently installed and return its status.
    pub async fn status(&self, skill_name: &str) -> Result<InstallStatus>;

    /// Verify installed skill content matches the lockfile hash.
    pub async fn verify(&self, locked: &LockedSkill) -> Result<VerifyResult>;
}
```

### Installation Strategy

1. **Read skill content** (from the `Skill` struct, already fetched)
2. **For each configured agent**:
   a. Determine the target path (e.g., `.claude/skills/playwright.md`)
   b. Create parent directories if needed
   c. Write the skill content
   d. Optionally transform format (some agents expect different
      frontmatter or file naming)
3. **Return an `InstallReceipt`** with paths written, timestamps,
   and content hash

### Agent-Specific Transformations

Different agents may expect different file formats:
- Claude Code: `SKILL.md` with any frontmatter
- Cursor: `.mdc` files with specific metadata format
- Others: plain markdown

The installer applies per-agent transformations defined in
`AgentConfig`. The `Skill` struct contains the canonical content;
the installer adapts it per agent.

---

## Agent Detection (`agent.rs`)

Detects which AI coding agents are present in the current project
and/or system.

```rust
pub enum AgentKind {
    ClaudeCode,
    Cursor,
    GitHubCopilot,
    Codex,
    Windsurf,
    Cline,
    Aider,
    Custom(String),
}

pub struct AgentConfig {
    pub kind: AgentKind,
    pub skills_path: PathBuf,     // e.g., ".claude/skills/"
    pub file_extension: String,   // e.g., "md", "mdc"
    pub detected: bool,           // Is this agent present in the project?
}

pub struct AgentDetector;

impl AgentDetector {
    /// Scan the current project directory for known agent config dirs.
    /// Returns all detected agents with their config.
    pub fn detect(project_root: &Path) -> Vec<AgentConfig>;

    /// Scan the system for globally installed agents.
    /// Checks $PATH for agent binaries (claude, cursor, etc.).
    pub fn detect_global() -> Vec<AgentConfig>;

    /// Merge detected agents with user-configured agents from
    /// skills.toml, preferring user config where specified.
    pub fn merge(
        detected: Vec<AgentConfig>,
        configured: &[AgentConfigOverride],
    ) -> Vec<AgentConfig>;
}
```

### Detection Heuristics

| Agent | Project-level detection | System-level detection |
|---|---|---|
| Claude Code | `.claude/` directory exists | `claude` binary in PATH |
| Cursor | `.cursor/` directory exists | `cursor` binary in PATH |
| GitHub Copilot | `.github/copilot/` exists | — |
| Codex | `.codex/` directory exists | `codex` binary in PATH |
| Windsurf | `.windsurf/` directory exists | `windsurf` binary in PATH |
| Cline | `.cline/` directory exists | — |
| Aider | `.aider/` or `.aider.conf.yml` exists | `aider` binary in PATH |

---

## Configuration (`config.rs`)

Layered configuration with cascading precedence.

```rust
pub struct Config {
    pub default_agents: Vec<AgentKind>,
    pub default_provider: ProviderKind,
    pub cache_dir: PathBuf,
    pub global_skills_dir: PathBuf,
}
```

### Precedence (highest to lowest)

1. **CLI flags**: `--agent claude`, `--provider conda`
2. **Environment variables**: `PIXI_SKILLS_CACHE_DIR`, etc.
3. **Project config**: `skills.toml` in the current project
4. **User config**: `~/.config/pixi-skills/config.toml`
5. **Built-in defaults**: compiled into the binary

```rust
impl Config {
    pub fn load() -> Result<Self> {
        let defaults = Config::builtin_defaults();
        let user = Config::load_user_config()?;
        let project = Config::load_project_config()?;
        let env = Config::from_environment()?;
        // Merge with precedence
        defaults.merge(user).merge(project).merge(env)
    }
}
```

---

## Error Types

```rust
#[derive(Debug, thiserror::Error)]
pub enum SkillsError {
    #[error("Skill not found: {0}")]
    NotFound(SkillId),

    #[error("Version resolution failed: {0}")]
    VersionResolution(String),

    #[error("Network error: {0}")]
    Network(#[from] reqwest::Error),

    #[error("Parse error in {file}: {message}")]
    Parse { file: PathBuf, message: String },

    #[error("Install error: {0}")]
    Install(String),

    #[error("Lockfile integrity violation: expected {expected}, got {actual}")]
    IntegrityViolation {
        skill: String,
        expected: ContentHash,
        actual: ContentHash,
    },

    #[error("Provider {provider} does not support source {source}")]
    UnsupportedSource {
        provider: ProviderKind,
        source: String,
    },

    #[error("Agent not detected: {0}")]
    AgentNotDetected(AgentKind),

    #[error(transparent)]
    Io(#[from] std::io::Error),

    #[error(transparent)]
    TomlParse(#[from] toml::de::Error),
}
```

---

## Testing Strategy

| Test type | What it covers | Location |
|---|---|---|
| Unit tests | Type parsing, version matching, hash computation | `src/*.rs` (`#[cfg(test)]`) |
| Integration tests | Manifest round-trip (parse → serialize → parse), agent detection with fixture dirs | `tests/` |
| Property tests | SkillVersion ordering, VersionReq matching, ContentHash determinism | Using `proptest` crate |

### Test Fixtures

```
skills-core/tests/fixtures/
├── manifests/
│   ├── minimal.toml          # Smallest valid skills.toml
│   ├── full.toml             # All fields populated
│   ├── multi-provider.toml   # Mixed GitHub + conda + prefix
│   └── invalid/
│       ├── missing-name.toml
│       └── bad-version.toml
├── lockfiles/
│   ├── v1.toml               # Valid lockfile
│   └── tampered.toml         # Content hash mismatch
└── agents/
    ├── claude-project/        # .claude/skills/ directory
    ├── cursor-project/        # .cursor/rules/ directory
    └── multi-agent/           # Both .claude/ and .cursor/
```
