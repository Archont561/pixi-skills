---
type: Component Design
title: "xtask"
description: "Design of Rust-native automation for code generation, linting, releases, and distribution."
section: crates
kind: detail
tags: [crates, xtask, automation, codegen, release, lint, dist]
status: stable
created: "2025-01-01"
updated: "2026-09-21"
---

# xtask

The build automation crate. A Rust binary with `publish = false` that
handles codegen, release management, workspace linting, distribution
builds, and shell completion generation.

---

## Crate Identity

```toml
[package]
name = "xtask"
version = "0.1.0"
edition = "2021"
publish = false

[dependencies]
clap = { version = "4", features = ["derive"] }
xshell = "0.2"
toml_edit = "0.25"
schemars = "1.2"
sha2 = "0.11"
flate2 = "0.2"
tar = "0.4"
glob = "0.3"
anyhow = "1"
chrono = "0.4"

# Workspace crates — for clap Command introspection
pixi-skills = { path = "../pixi-skills", default-features = false }
skills-core = { path = "../skills-core" }
```

- **Published**: never
- **Dependents**: none (terminal node)
- **Location**: `crates/xtask/` (a workspace member like the others; moved from the root 2026-09-21)

---

## Module Map

```
crates/xtask/src/
├── main.rs              # Clap dispatcher
├── cli_docs.rs          # Subcommand: generate CLI reference MDX
├── skill_schema.rs      # Subcommand: generate JSON Schema
├── completions.rs       # Subcommand: generate shell completions
├── lint.rs              # Subcommand: workspace consistency checks
├── release.rs           # Subcommand: version bump + changelog + tag
└── dist.rs              # Subcommand: cross-compile + tarball + checksums
```

---

## Subcommand: `cli-docs`

**Purpose**: Generate MDX documentation for every CLI subcommand from
the real clap `Command` struct.

**Invocation**:
```bash
cargo xtask cli-docs --output apps/pixi-skills-docs/src/content/docs/cli/
```

**How it works**:

```rust
fn cli_docs(output_dir: &Path) -> Result<()> {
    let cmd = pixi_skills::cli::build_command();

    for sub in cmd.get_subcommands() {
        let name = sub.get_name();
        let about = sub.get_about().unwrap_or_default();
        let long_about = sub.get_long_about().unwrap_or_default();

        let mut mdx = String::new();
        // YAML frontmatter
        writeln!(mdx, "---")?;
        writeln!(mdx, "title: \"pixi skills {}\"", name)?;
        writeln!(mdx, "description: \"{}\"", about)?;
        writeln!(mdx, "---")?;
        writeln!(mdx)?;

        // Description
        writeln!(mdx, "# `pixi skills {}`", name)?;
        writeln!(mdx)?;
        writeln!(mdx, "{}", long_about)?;
        writeln!(mdx)?;

        // Usage
        writeln!(mdx, "## Usage")?;
        writeln!(mdx)?;
        writeln!(mdx, "```bash")?;
        writeln!(mdx, "pixi skills {} [OPTIONS] [ARGS]", name)?;
        writeln!(mdx, "```")?;
        writeln!(mdx)?;

        // Arguments
        if sub.get_positionals().count() > 0 {
            writeln!(mdx, "## Arguments")?;
            for arg in sub.get_positionals() {
                render_arg(&mut mdx, arg)?;
            }
        }

        // Options/flags
        if sub.get_opts().count() > 0 {
            writeln!(mdx, "## Options")?;
            for opt in sub.get_opts() {
                render_option(&mut mdx, opt)?;
            }
        }

        let path = output_dir.join(format!("{}.mdx", name));
        std::fs::write(&path, &mdx)?;
    }
    Ok(())
}
```

**Key property**: the generated MDX is derived from the same Rust
structs that the CLI parser uses. If a flag is renamed, the docs
update automatically at next codegen run. They cannot drift.

---

## Subcommand: `schema`

**Purpose**: Generate a JSON Schema for `skills.toml` from the Rust
types that parse it.

**Invocation**:
```bash
cargo xtask schema --output apps/pixi-skills-docs/public/skills-schema.json
```

**How it works**:

```rust
fn schema(output: &Path) -> Result<()> {
    let schema = schemars::schema_for!(skills_core::manifest::SkillsManifest);
    let json = serde_json::to_string_pretty(&schema)?;
    std::fs::write(output, json)?;
    Ok(())
}
```

The `SkillsManifest` struct must derive `schemars::JsonSchema`:
```rust
// In skills-core/src/manifest.rs
#[derive(Deserialize, Serialize, JsonSchema)]
pub struct SkillsManifest { ... }
```

**Use cases**:
- Editor autocompletion when editing `skills.toml` (via JSON Schema
  association in VS Code / Zed)
- Validation in CI
- Documentation reference on the docs site

---

## Subcommand: `completions`

**Purpose**: Generate shell completion scripts for bash, zsh, fish,
and PowerShell.

**Invocation**:
```bash
cargo xtask completions --output completions/
```

**How it works**:

```rust
fn completions(output_dir: &Path) -> Result<()> {
    let mut cmd = pixi_skills::cli::build_command();

    for shell in [Shell::Bash, Shell::Zsh, Shell::Fish, Shell::PowerShell] {
        clap_complete::generate_to(shell, &mut cmd, "pixi-skills", output_dir)?;
    }
    Ok(())
}
```

---

## Subcommand: `lint`

**Purpose**: Check workspace-wide consistency that no single tool
catches.

**Invocation**:
```bash
cargo xtask lint
```

**Checks performed**:

| Check | What it verifies |
|---|---|
| **Edition consistency** | All Cargo.toml files use the same Rust edition |
| **License consistency** | All published crates use the same license field |
| **Repository field** | All Cargo.toml files have the same `repository` URL |
| **Version alignment** | All workspace crates are at the same version (or explicitly opted out) |
| **Publish flag** | xtask has `publish = false`; all other crates have `publish = true` (or unset) |
| **Feature flag naming** | Provider feature flags in pixi-skills match crate names |
| **pixi task references** | pixi.toml tasks reference valid cargo commands and existing crate names |

**Implementation**: uses `glob` to find all `Cargo.toml` files, parses
them with `toml_edit`, and validates cross-file invariants.

---

## Subcommand: `release`

**Purpose**: Orchestrate version bumps, changelog generation, and
git tagging for a release.

**Invocation**:
```bash
cargo xtask release              # Auto-detect bump level from commits
cargo xtask release --major      # Force major bump
cargo xtask release --dry-run    # Show what would happen
```

**Steps**:

```
1. Run `convco check` — validate all commits since last tag
   ↳ Fail if any commit doesn't follow conventional format

2. Determine next version
   ↳ Run `convco version --bump` to calculate (or use --major/--minor/--patch)
   ↳ e.g., "0.2.0" → "0.3.0" (feat commits → minor bump)

3. Update all Cargo.toml versions
   ↳ toml_edit: parse each Cargo.toml, set version, write back
   ↳ Preserve formatting, comments, and key ordering
   ↳ Also update workspace dependency versions

4. Generate changelog
   ↳ Run `convco changelog > CHANGELOG.md`

5. Regenerate version-stamped artifacts
   ↳ Run `cargo xtask schema` (version embedded in schema)
   ↳ Run `cargo xtask completions` (version in --version output)

6. Git commit
   ↳ `git add -A`
   ↳ `git commit -m "chore(release): v{version}"`

7. Git tag
   ↳ `git tag v{version}`

8. Print summary
   ↳ "Released v0.3.0. Push with: git push && git push --tags"
```

**Note**: the release subcommand does NOT push to remote or publish
to crates.io/conda-forge. Those are separate manual (or CI) steps.
This keeps the release process reversible until `git push`.

---

## Subcommand: `dist`

**Purpose**: Build release binaries, create tarballs, and compute
checksums for distribution.

**Invocation**:
```bash
cargo xtask dist                           # Build for current platform
cargo xtask dist --target x86_64-unknown-linux-gnu  # Cross-compile
cargo xtask dist --all-targets             # All supported targets
```

**Targets** (supported platforms):

| Target triple | OS | Arch |
|---|---|---|
| `x86_64-unknown-linux-gnu` | Linux | x86_64 |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 |
| `x86_64-apple-darwin` | macOS | Intel |
| `aarch64-apple-darwin` | macOS | Apple Silicon |
| `x86_64-pc-windows-msvc` | Windows | x86_64 |

**Output structure**:

```
dist/
├── pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz
├── pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256
├── pixi-skills-v0.3.0-aarch64-apple-darwin.tar.gz
├── pixi-skills-v0.3.0-aarch64-apple-darwin.tar.gz.sha256
└── checksums.sha256       # All checksums in one file
```

**Tarball contents**:
```
pixi-skills-v0.3.0-x86_64-unknown-linux-gnu/
├── pixi-skills              # The binary
├── LICENSE-MIT
├── LICENSE-APACHE
├── README.md
└── completions/
    ├── pixi-skills.bash
    ├── pixi-skills.zsh
    ├── pixi-skills.fish
    └── _pixi-skills.ps1
```

---

## Why Each Task Is in xtask (Summary)

| Task | Why not a shell script? | Why not a pixi task? |
|---|---|---|
| `cli-docs` | Needs clap `Command` introspection — impossible from shell | Needs Rust types — pixi can only run commands |
| `schema` | Needs `#[derive(JsonSchema)]` — impossible from shell | Needs Rust types |
| `completions` | Needs `clap_complete` — impossible from shell | Needs Rust types |
| `lint` | Multi-file TOML parsing with cross-validation — fragile in shell | Complex logic, not a single command |
| `release` | Multi-step with rollback, TOML editing — too complex for shell | Multi-step orchestration with error handling |
| `dist` | Platform detection, tarball creation, checksums — possible but fragile in shell | Complex logic, benefits from Rust's `sha2`/`tar`/`flate2` |

---

## Testing Strategy

| Subcommand | Test approach |
|---|---|
| `cli-docs` | Generate to temp dir, assert expected files exist, spot-check MDX frontmatter |
| `schema` | Generate, parse as JSON Schema, validate a known-good `skills.toml` against it |
| `completions` | Generate to temp dir, assert files exist for all 4 shells |
| `lint` | Create fixture workspace with known violations, assert lint catches them |
| `release` | Test version bumping logic with fixture Cargo.toml files (no git operations) |
| `dist` | Test tarball creation with temp directory, verify contents and checksums |

## Related Concepts

- [Three-Layer Task Model](../architecture/three-layer-model.md)
- [Dependency Graph](../architecture/dependency-graph.md)
- [pixi-skills CLI](./pixi-skills-cli.md)
- [Pixi Tasks](../pixi/tasks.md)
- [Release Workflow](../cicd/release-workflow.md)
- [convco](../tooling/convco.md)
