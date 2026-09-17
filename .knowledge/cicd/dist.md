---
title: "Distribution Artifacts"
section: cicd
kind: detail
tags: [cicd, dist, cross-compilation, tarball, checksums, binary, release]
relates_to:
  - cicd/release-workflow
  - crates/xtask
  - crates/pixi-skills-cli
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Distribution Artifacts

How `cargo xtask dist` builds release binaries, creates tarballs,
and computes checksums for distribution.

---

## Supported Targets

| Target Triple | OS | Architecture | Runner |
|---|---|---|---|
| `x86_64-unknown-linux-gnu` | Linux | x86_64 (Intel/AMD) | `ubuntu-latest` |
| `aarch64-unknown-linux-gnu` | Linux | ARM64 | `ubuntu-latest` (cross) |
| `x86_64-apple-darwin` | macOS | Intel | `macos-latest` |
| `aarch64-apple-darwin` | macOS | Apple Silicon | `macos-latest` |
| `x86_64-pc-windows-msvc` | Windows | x86_64 | `windows-latest` |

### Cross-Compilation

Most targets are compiled on their native runner. The exception is
`aarch64-unknown-linux-gnu`, which is cross-compiled on `ubuntu-latest`
using the `cross` tool or Rust's built-in cross-compilation with
appropriate linker configuration.

```bash
# Native build
cargo build --release --target x86_64-unknown-linux-gnu

# Cross-compile (via xtask, which configures the linker)
cargo xtask dist --target aarch64-unknown-linux-gnu
```

---

## Output Structure

```
dist/
├── pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz
├── pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256
├── pixi-skills-v0.3.0-aarch64-unknown-linux-gnu.tar.gz
├── pixi-skills-v0.3.0-aarch64-unknown-linux-gnu.tar.gz.sha256
├── pixi-skills-v0.3.0-x86_64-apple-darwin.tar.gz
├── pixi-skills-v0.3.0-x86_64-apple-darwin.tar.gz.sha256
├── pixi-skills-v0.3.0-aarch64-apple-darwin.tar.gz
├── pixi-skills-v0.3.0-aarch64-apple-darwin.tar.gz.sha256
├── pixi-skills-v0.3.0-x86_64-pc-windows-msvc.zip
├── pixi-skills-v0.3.0-x86_64-pc-windows-msvc.zip.sha256
└── checksums.sha256
```

### Naming Convention

```
pixi-skills-v{VERSION}-{TARGET}.{EXT}
```

- **VERSION**: from git tag (e.g., `0.3.0`)
- **TARGET**: Rust target triple
- **EXT**: `.tar.gz` for Unix, `.zip` for Windows

### Tarball Contents

```
pixi-skills-v0.3.0-x86_64-unknown-linux-gnu/
├── pixi-skills                 # The binary (or pixi-skills.exe on Windows)
├── LICENSE-MIT
├── LICENSE-APACHE
├── README.md
└── completions/
    ├── pixi-skills.bash
    ├── pixi-skills.zsh
    ├── pixi-skills.fish
    └── _pixi-skills.ps1
```

Completions are included so users can source them immediately after
extracting, without running a separate `pixi-skills completions`
command.

---

## Checksum Files

### Per-artifact checksums

Each tarball has a corresponding `.sha256` file:

```
$ cat pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256
a1b2c3d4e5f6...  pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz
```

### Combined checksums file

`checksums.sha256` contains all checksums in a single file, suitable
for `sha256sum -c`:

```
a1b2c3d4e5f6...  pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz
f6e5d4c3b2a1...  pixi-skills-v0.3.0-aarch64-apple-darwin.tar.gz
...
```

### Verification

```bash
# Download the tarball and checksum
curl -LO https://github.com/.../pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz
curl -LO https://github.com/.../pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256

# Verify
sha256sum -c pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256
# pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz: OK
```

---

## Binary Stripping and Optimization

### Release build profile

```toml
# Cargo.toml (workspace root)
[profile.release]
lto = "thin"              # Link-Time Optimization (balance of speed vs size)
strip = true              # Strip debug symbols
codegen-units = 1         # Maximize optimization (slower compile)
panic = "abort"           # Smaller binary (no unwinding)
opt-level = 3             # Maximum optimization
```

### Expected binary sizes

| Target | Approximate size (stripped) |
|---|---|
| Linux x86_64 | ~10–15 MB |
| macOS ARM64 | ~10–15 MB |
| Windows x86_64 | ~12–18 MB |

These are estimates. Actual sizes depend on which provider features
are compiled in. The `default` feature set (github + conda) produces
the largest binary due to rattler dependencies.

### Feature-minimized builds

For smaller binaries, compile with fewer providers:

```bash
# GitHub-only build (~5 MB smaller)
cargo build --release --no-default-features --features github

# Minimal build (no providers — useful for testing)
cargo build --release --no-default-features
```

---

## xtask dist Implementation

```rust
fn dist(targets: &[String]) -> Result<()> {
    let version = get_version_from_tag()?;     // Read from git tag or Cargo.toml
    let dist_dir = Path::new("dist");
    fs::create_dir_all(dist_dir)?;

    for target in targets {
        // 1. Build release binary
        cmd!(sh, "cargo build --release --target {target}").run()?;

        // 2. Determine binary name and extension
        let bin_name = if target.contains("windows") {
            "pixi-skills.exe"
        } else {
            "pixi-skills"
        };
        let ext = if target.contains("windows") { "zip" } else { "tar.gz" };

        // 3. Create archive name
        let archive_name = format!("pixi-skills-v{version}-{target}.{ext}");
        let archive_dir = format!("pixi-skills-v{version}-{target}");

        // 4. Stage files
        let stage = dist_dir.join(&archive_dir);
        fs::create_dir_all(&stage)?;
        fs::copy(
            format!("target/{target}/release/{bin_name}"),
            stage.join(bin_name),
        )?;
        fs::copy("LICENSE-MIT", stage.join("LICENSE-MIT"))?;
        fs::copy("LICENSE-APACHE", stage.join("LICENSE-APACHE"))?;
        fs::copy("README.md", stage.join("README.md"))?;
        copy_dir("completions", &stage.join("completions"))?;

        // 5. Create archive
        if target.contains("windows") {
            create_zip(&stage, &dist_dir.join(&archive_name))?;
        } else {
            create_tar_gz(&stage, &dist_dir.join(&archive_name))?;
        }

        // 6. Compute checksum
        let hash = sha256_file(&dist_dir.join(&archive_name))?;
        fs::write(
            dist_dir.join(format!("{archive_name}.sha256")),
            format!("{hash}  {archive_name}\n"),
        )?;

        // 7. Clean up staging directory
        fs::remove_dir_all(&stage)?;
    }

    // 8. Generate combined checksums file
    generate_combined_checksums(dist_dir)?;

    Ok(())
}
```

---

## Installation from Release Artifacts

### Linux / macOS

```bash
# Download
curl -LO https://github.com/yourorg/pixi-skills/releases/latest/download/pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz

# Verify
curl -LO https://github.com/yourorg/pixi-skills/releases/latest/download/pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256
sha256sum -c pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz.sha256

# Extract
tar xzf pixi-skills-v0.3.0-x86_64-unknown-linux-gnu.tar.gz

# Install
sudo cp pixi-skills-v0.3.0-x86_64-unknown-linux-gnu/pixi-skills /usr/local/bin/

# Shell completions (bash example)
cp pixi-skills-v0.3.0-x86_64-unknown-linux-gnu/completions/pixi-skills.bash \
   ~/.local/share/bash-completion/completions/pixi-skills
```

### Recommended: `pixi global install`

```bash
# This is the preferred installation method — no manual download
pixi global install pixi-skills
```

This installs from conda-forge (when published), which handles
PATH setup and shell completions automatically.
