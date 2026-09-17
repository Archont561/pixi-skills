---
type: Component Design
title: "skills-core"
description: "Design of shared skill models, registry traits, manifest parsing, and installation."
section: crates
kind: detail
tags: [crates, skills-core, traits, models, installer, agent, registry]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
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
├── skill.rs            # Skill data model + SkillMetadata (YAML frontmatter)
├── bundle.rs           # SkillBundle (folder tree) + TreeHash   [NEW — ADR-008]
├── companion.rs        # skill.toml envelope parsing            [NEW — ADR-008;
                        #   normative schema: conventions/skill-toml.md]
├── registry.rs         # SkillRegistry trait
├── manifest.rs         # skills.toml + skills-lock.toml parsing
├── installer.rs        # Install/uninstall skill folders into agent dirs
├── agent.rs            # Agent detection + configuration (data-driven)
└── config.rs           # User + project configuration
```

---

## Key Types (`skill.rs`)

> **Updated 2026-09-17 (ADR-008):** `Skill` now carries a **folder
> bundle**, not a single markdown string, matching the agentskills.io
> standard. The content hash is a canonical **tree hash**.

### `Skill`
The fully resolved skill — metadata plus its folder bundle. Returned
by `SkillRegistry::fetch()`.

```rust
pub struct Skill {
    pub id: SkillId,
    pub version: SkillVersion,
    pub source: SkillSource,
    pub metadata: SkillMetadata,   // YAML frontmatter (spec fields) + skill.toml envelope
    pub bundle: SkillBundle,       // The folder tree
    pub tree_hash: TreeHash,       // Canonical hash of the bundle
}
```

### `SkillBundle`
The folder-shaped artifact (ADR-008). `SKILL.md` at the root is
required; everything else is optional.

```rust
pub struct SkillBundle {
    /// Relative POSIX paths ("SKILL.md", "scripts/login.sh", ...)
    /// BTreeMap => deterministic iteration for hashing & diffing
    pub files: BTreeMap<RelativePath, FileEntry>,
}

pub struct FileEntry {
    pub contents: Vec<u8>,
    pub mode: FileMode,            // Regular | Executable (unix bit; fixed elsewhere)
}

impl SkillBundle {
    pub fn skill_md(&self) -> Result<&FileEntry>;   // required root SKILL.md
    pub fn parse_frontmatter(&self) -> Result<SkillMetadata>;  // YAML (serde_yaml)
    pub fn companion(&self) -> Option<&FileEntry>;  // skill.toml, if present
    pub fn tree_hash(&self) -> TreeHash;            // canonical, see below
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
contain the full bundle — only metadata for display.

```rust
pub struct SkillSummary {
    pub id: SkillId,
    pub version: SkillVersion,
    pub description: Option<String>,   // from YAML frontmatter (spec-required)
    pub agents: Vec<AgentKind>,        // compatible agents (hints)
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

### `TreeHash`
Canonical SHA-256 hash of the whole skill folder (ADR-008 §4). Used
in the lockfile for integrity verification.

```rust
pub struct TreeHash(pub [u8; 32]);

// Canonicalization:
//   for (path, entry) in bundle.files /* BTreeMap: sorted */:
//       h.update(path.as_posix()); h.update("\0");
//       h.update(mode_octet);      h.update("\0");
//       h.update(len_le);          h.update("\0");
//       h.update(lf_normalized_bytes);
// Deterministic across platforms: LF normalization; executable bit
// recorded on unix, synthesized as Regular on Windows.
//
// pub struct ContentHash(pub [u8; 32]);  // RETIRED 2026-09 (file hash)
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
# path = "skills/polars"          # optional; folder containing SKILL.md
                                  # (defaults per repo convention, see provider docs)

[[skill]]
name = "web-design-guidelines"
source = "github"
repo = "vercel-labs/agent-skills"
skill = "web-design-guidelines"    # multi-skill repo selector (@skill convention);
                                   # resolves to skills/<skill>/ or repo <skill>/
ref = "^1.4"                       # semver range over [v]X.Y.Z tags (ADR-004, amended)

[[skill]]
name = "internal-api"
source = "prefix"
channel = "my-company"
version = ">=1.0,<2.0"
```

### `skills-lock.toml` — The lockfile

Pins exact resolved versions with folder tree hashes.

```toml
# skills-lock.toml — DO NOT EDIT MANUALLY
# Generated by `pixi skills lock`

version = 2          # bumped 2026-09 (ADR-008): tree_hash replaces content_hash

[[skill]]
name = "playwright"
provider = "conda"
channel = "https://conda.anaconda.org/conda-forge"
package = "skill-playwright"
version = "1.2.3-h1234567_0"
tree_hash = "sha256:abcdef1234567890..."
file_count = 7
installed_at = "2026-09-15T10:30:00Z"

[[skill]]
name = "polars"
provider = "github"
repo = "user/polars-skill"
path = "skills/polars"
ref = "tag:v2.1.0"
commit = "abc123def456"
tree_hash = "sha256:fedcba0987654321..."
file_count = 3
installed_at = "2026-09-15T10:30:01Z"
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
    pub tree_hash: TreeHash,        // v2 (was: content_hash: ContentHash)
    pub file_count: u32,            // cheap drift signal + audit display
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
    /// Install a skill folder into all configured agent directories.
    /// Creates <agent-path>/<name>/ and copies the bundle tree,
    /// EXCLUDING the manager-only skill.toml (ADR-008 §5).
    pub async fn install(&self, skill: &Skill) -> Result<InstallReceipt>;

    /// Remove a skill folder from all agent directories.
    pub async fn uninstall(&self, skill_name: &str) -> Result<()>;

    /// Check if a skill is currently installed and return its status.
    pub async fn status(&self, skill_name: &str) -> Result<InstallStatus>;

    /// Verify the installed folder matches the lockfile tree hash.
    pub async fn verify(&self, locked: &LockedSkill) -> Result<VerifyResult>;
}
```

### Installation Strategy

1. **Verify** `skill.tree_hash()` against the lockfile entry (fail
   closed on mismatch)
2. **For each configured agent**:
   a. Determine the target folder (e.g., `.claude/skills/playwright/`)
   b. Replace the folder atomically (write to temp dir + rename)
   c. Copy every bundle file **except `skill.toml`**; preserve
      executable bits; pass `agents/*.yaml` through untouched
   d. Apply legacy transforms ONLY if a config-gated agent override
      requests them (ADR-003; default: none)
3. **Return an `InstallReceipt`** with folders written, file count,
   timestamps, and tree hash

### Agent-Specific Transformations

**Update 2026-09-17:** the agentskills.io standard made most
transforms unnecessary — 26+ agents now read folder-shaped SKILL.md
skills natively (Cursor no longer needs `.mdc`, Copilot/Codex have
standard skill dirs). Install = copy the folder, unchanged.

The transformation hook stays in the design for:
- Legacy/pre-standard agent layouts (config override per agent)
- Optional optimization passes (e.g. stripping `scripts/` when
  installing into a restricted sandbox agent)
- Faithful pass-through of per-agent `agents/*.yaml` metadata files

The `Skill` struct remains the canonical unit; the folder is its
serialized form. Canonical content + per-agent adaptation = config,
not code.

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
    GeminiCli,               // added 2026-09 (standard-era agents)
    Windsurf,
    Cline,
    Aider,
    Custom(String),          // data-driven: any entry in default_agents.toml
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

### Detection Heuristics (updated 2026-09)

| Agent | Project-level detection | System-level detection |
|---|---|---|
| Claude Code | `.claude/` directory exists | `claude` binary in PATH |
| Cursor | `.cursor/` directory exists | `cursor` binary in PATH |
| GitHub Copilot | `.github/skills/` (or legacy `.github/copilot/`) | — |
| Codex | `.agents/skills/` or `.codex/` exists | `codex` binary in PATH |
| Gemini CLI | `.gemini/` directory exists | `gemini` binary in PATH |
| Windsurf | `.windsurf/` directory exists | `windsurf` binary in PATH |
| Cline | `.cline/` directory exists | — |
| Aider | `.aider/` or `.aider.conf.yml` exists | `aider` binary in PATH |
| 70+ others | driven by `default_agents.toml` (data file; `agents --update`) | per data file |

The `AgentConfig.file_extension` field is retained **only** for
legacy per-agent overrides; conforming installs copy the folder
verbatim (ADR-008 §5).

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
        expected: TreeHash,
        actual: TreeHash,
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
    TomlParse(#[from] toml::de::Error),   // skill.toml, skills.toml, lockfile

    #[error("SKILL.md frontmatter error: {0}")]
    FrontmatterYaml(String),              // serde_yaml — ADR-008

    #[error("Skill bundle invalid: {0}")]
    InvalidBundle(String),                // missing SKILL.md, bad paths
}
```

---

## Testing Strategy

| Test type | What it covers | Location |
|---|---|---|
| Unit tests | Type parsing, version matching, hash computation | `src/*.rs` (`#[cfg(test)]`) |
| Integration tests | Manifest round-trip (parse → serialize → parse), agent detection with fixture dirs | `tests/` |
| Property tests | SkillVersion ordering, VersionReq matching, TreeHash determinism (path order, LF normalization) | Using `proptest` crate |

### Test Fixtures (folder-shaped, ADR-008)

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
│   ├── v2.toml               # Valid lockfile (tree_hash)
│   └── tampered.toml         # Tree hash mismatch
├── bundles/
│   ├── spec-full/            # SKILL.md + skill.toml + scripts/ + references/
│   ├── bare-markdown/        # legacy: SKILL.md, no frontmatter
│   └── invalid/
│       ├── no-skill-md/      # missing required SKILL.md
│       └── name-mismatch/    # folder name != frontmatter name
└── agents/
    ├── claude-project/       # .claude/skills/ directory
    ├── codex-project/        # .agents/skills/ directory
    ├── copilot-project/      # .github/skills/ directory
    └── multi-agent/          # .claude/ + .cursor/ + .agents/
```

## Related Concepts

- [Crates — Context](./CONTEXT.md)
- [skills-provider-github](./skills-provider-github.md)
- [skills-provider-conda](./skills-provider-conda.md)
- [pixi-skills CLI](./pixi-skills-cli.md)
- [Dependency Graph](../architecture/dependency-graph.md)
- [Skill Format](../conventions/skill-format.md)
