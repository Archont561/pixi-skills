---
type: Component Design
title: "pixi-skills CLI"
description: "Design of the pixi-skills CLI, subcommands, user experience, and provider composition."
section: crates
kind: detail
tags: [crates, cli, clap, pixi-extension, subcommands, ux]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# pixi-skills CLI

The `pixi-skills` binary crate. Built with clap v4. Functions as a
pixi extension — when named `pixi-skills` and placed on PATH, pixi
automatically discovers it and enables `pixi skills <subcommand>`.

---

## Crate Identity

```toml
[package]
name = "pixi-skills"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "pixi-skills"
path = "src/main.rs"

[dependencies]
skills-core = { path = "../skills-core" }
clap = { version = "4", features = ["derive", "env", "wrap_help"] }
tokio = { version = "1", features = ["full"] }
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }
console = "0.15"
indicatif = "0.17"
tabled = "0.16"
dialoguer = "0.11"

# Provider crates (feature-gated)
skills-provider-github = { path = "../skills-provider-github", optional = true }
skills-provider-conda  = { path = "../skills-provider-conda",  optional = true }
skills-provider-prefix = { path = "../skills-provider-prefix", optional = true }
skills-provider-pypi   = { path = "../skills-provider-pypi",   optional = true }

[features]
default = ["github", "conda"]
github  = ["dep:skills-provider-github"]
conda   = ["dep:skills-provider-conda"]
prefix  = ["dep:skills-provider-prefix"]
pypi    = ["dep:skills-provider-pypi"]
```

- **Published**: yes (to crates.io + conda-forge)
- **Dependents**: xtask (as library for clap introspection)
- **Dependencies on workspace crates**: skills-core + all providers
  (feature-gated)

---

## pixi Extension Model

pixi extensions follow a naming convention: an executable named
`pixi-{name}` on PATH is automatically invocable as `pixi {name}`.

```bash
# When pixi-skills is installed globally:
pixi skills find playwright
# pixi discovers `pixi-skills` on PATH, runs:
# pixi-skills find playwright

# Direct invocation also works:
pixi-skills find playwright
```

### Installation

```bash
# Via pixi global install (recommended)
pixi global install pixi-skills

# Via cargo install (from source)
cargo install pixi-skills

# Via conda-forge (when published)
pixi global install -c conda-forge pixi-skills
```

---

## Command Tree

```
pixi-skills (or pixi skills)
│
├── find <query>               Search for skills across all providers
├── add <source> [options]     Add a skill to the project
├── remove <skill-name>        Remove a skill from the project
├── list                       List installed skills
├── update [skill-name]        Update skills to latest matching version
├── lock                       Generate/update skills-lock.toml
├── doctor                     Diagnose issues
│
├── --version                  Print version
├── --help                     Print help
├── --verbose / -v             Increase log verbosity
└── --quiet / -q               Suppress non-essential output
```

---

## Subcommand Details

### `find <query>`

Search for skills across all enabled providers.

```
pixi skills find playwright

 Provider  Name              Version  Description
 ──────────────────────────────────────────────────────────
 🟢 conda  skill-playwright  1.2.3    Playwright testing patterns
 🟣 github anthropics/skill  main     Official Playwright skill
 🟠 pypi   skill-playwright  1.0.0    Playwright for Python agents
```

**Flags**:
- `--provider <name>` — filter to a specific provider
- `--limit <n>` — max results (default: 20)
- `--json` — output as JSON (for scripting)

### `add <source>`

Add a skill to the project. Updates `skills.toml` and installs the
skill into agent directories.

```bash
# From conda (preferred)
pixi skills add conda:conda-forge/skill-playwright@^1.0

# From GitHub
pixi skills add github:anthropics/skill-playwright@tag:v1.0

# From prefix.dev
pixi skills add prefix:my-org/skill-internal@>=2.0

# Interactive (no source specified)
pixi skills add playwright
# → Searches across providers, prompts user to select
```

**Flags**:
- `--agent <name>` — install only for a specific agent (default: all detected)
- `--version <constraint>` — version constraint (default: latest)
- `--no-lock` — skip lockfile update
- `--dry-run` — show what would happen without doing it

**Behavior**:
1. Resolve skill from provider
2. Append entry to `skills.toml`
3. Fetch skill content
4. Install into agent directories (via `SkillInstaller`)
5. Update `skills-lock.toml` (unless `--no-lock`)

### `remove <skill-name>`

Remove a skill from the project.

```bash
pixi skills remove playwright
```

**Behavior**:
1. Remove entry from `skills.toml`
2. Remove skill files from all agent directories
3. Update `skills-lock.toml`

### `list`

List all skills in the current project.

```bash
pixi skills list

 Name         Provider  Version  Agents          Locked
 ──────────────────────────────────────────────────────────
 playwright   conda     1.2.3    claude, cursor  ✅
 polars       github    v2.1.0   claude          ✅
 internal-api prefix    2.0.1    cursor          ⚠️ hash mismatch
```

**Flags**:
- `--json` — output as JSON
- `--outdated` — show only skills with available updates

### `update [skill-name]`

Update skills to the latest version matching the constraint in
`skills.toml`.

```bash
# Update all skills
pixi skills update

# Update a specific skill
pixi skills update playwright
```

**Behavior**:
1. For each skill (or specified skill):
   a. Query provider for latest version matching the constraint
   b. If newer than locked version: fetch, install, update lockfile
   c. If already at latest: skip
2. Report what was updated

### `lock`

Generate or update `skills-lock.toml` without changing installed files.

```bash
pixi skills lock
```

**Behavior**:
1. Read `skills.toml`
2. For each skill: resolve version, fetch content hash
3. Write `skills-lock.toml` with exact versions and hashes

This is the idempotent "resolve and record" step. It does not install
skills — that's `add`'s job.

### `doctor`

Diagnose issues with the skills setup.

```bash
pixi skills doctor

 ✅ skills.toml found
 ✅ skills-lock.toml found
 ⚠️  skills-lock.toml is stale (skills.toml has changed)
 ✅ Agent detected: Claude Code (.claude/skills/)
 ✅ Agent detected: Cursor (.cursor/rules/)
 ❌ Skill "playwright" installed but hash mismatch
 ✅ Skill "polars" installed and verified
 ✅ GitHub API: 4,832 requests remaining (authenticated)
 ⚠️  conda channel "my-company": authentication required
```

**Checks performed**:
- `skills.toml` exists and is valid
- `skills-lock.toml` exists, is valid, and matches `skills.toml`
- Installed skills match lockfile hashes
- Agent directories are detected and writable
- Provider connectivity and authentication status
- Rate limit status (GitHub)

---

## Architecture: The CLI Is Thin

The binary crate contains only:
1. **`main.rs`**: tokio runtime setup, tracing subscriber init,
   clap parsing, subcommand dispatch
2. **`cli.rs`**: clap `#[derive(Parser)]` structs for all subcommands

All business logic lives in `skills-core` and provider crates. The
CLI's role is:
- Parse user input (clap)
- Construct provider instances
- Call `skills-core` functions
- Format output for the terminal (console, tabled, indicatif)
- Map errors to user-friendly messages

```rust
// main.rs — simplified
#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    init_tracing(cli.verbose);

    let config = Config::load()?;
    let registry = build_registry(&config)?;
    let installer = SkillInstaller::new(&config);

    match cli.command {
        Command::Find(args) => cmd::find(&registry, args).await,
        Command::Add(args)  => cmd::add(&registry, &installer, args).await,
        Command::Remove(args) => cmd::remove(&installer, args).await,
        // ...
    }
}
```

### `build_registry()` — Provider Composition

```rust
fn build_registry(config: &Config) -> Result<MultiRegistry> {
    let mut registries: Vec<Box<dyn SkillRegistry>> = Vec::new();

    #[cfg(feature = "github")]
    registries.push(Box::new(GitHubRegistry::new(config)?));

    #[cfg(feature = "conda")]
    registries.push(Box::new(CondaRegistry::new(config)?));

    #[cfg(feature = "prefix")]
    registries.push(Box::new(PrefixRegistry::new(config)?));

    #[cfg(feature = "pypi")]
    registries.push(Box::new(PyPIRegistry::new(config)?));

    Ok(MultiRegistry::new(registries))
}
```

`MultiRegistry` wraps multiple providers and dispatches `search()`,
`list()`, and `fetch()` to the appropriate one based on `supports()`.

---

## Output Formatting

### Default: human-readable tables

Uses `tabled` for structured output and `console` for colors:
- 🟢 = conda
- 🟣 = GitHub
- 🔵 = prefix.dev
- 🟠 = PyPI

### `--json` flag: machine-readable

Every subcommand that produces output supports `--json` for scripting
and piping:

```bash
pixi skills list --json | jq '.[] | select(.provider == "conda")'
```

### Progress indicators

Uses `indicatif` for:
- Download progress bars (fetching packages)
- Spinners (resolving versions, searching)
- Multi-progress bars (updating multiple skills)

---

## Clap Configuration

```rust
#[derive(Parser)]
#[command(
    name = "pixi-skills",
    about = "Manage AI agent skills with version pinning and lockfiles",
    version,
    propagate_version = true,
    arg_required_else_help = true,
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Command,

    /// Increase log verbosity (-v, -vv, -vvv)
    #[arg(short, long, action = ArgAction::Count, global = true)]
    pub verbose: u8,

    /// Suppress non-essential output
    #[arg(short, long, global = true)]
    pub quiet: bool,
}
```

### Key clap Features Used

| Feature | Purpose |
|---|---|
| `derive` | Compile-time CLI definition from Rust structs |
| `env` | `#[arg(env = "PIXI_SKILLS_...")]` for env var fallbacks |
| `wrap_help` | Terminal-width-aware help text wrapping |
| `propagate_version` | `--version` works on all subcommands |
| `arg_required_else_help` | Show help when no subcommand given |

---

## How xtask Introspects This Crate

xtask imports this crate as a library to access the clap `Command`
struct:

```rust
// In pixi-skills/src/cli.rs, we expose:
pub fn build_command() -> clap::Command {
    Cli::command()
}

// In xtask/src/cli_docs.rs:
fn generate() {
    let cmd = pixi_skills::cli::build_command();
    for sub in cmd.get_subcommands() {
        let mdx = render_subcommand_to_mdx(sub);
        write_file(format!("cli/{}.mdx", sub.get_name()), &mdx);
    }
}
```

This is why xtask depends on `pixi-skills` — it needs compile-time
access to the real command tree, not parsed `--help` output.

## Related Concepts

- [skills-core](./skills-core.md)
- [xtask](./xtask.md)
- [Design Decisions](../architecture/design-decisions.md)
- [Pixi Tasks](../pixi/tasks.md)
