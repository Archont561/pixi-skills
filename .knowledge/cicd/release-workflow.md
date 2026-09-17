---
title: "Release Workflow"
section: cicd
kind: detail
tags: [cicd, release, versioning, changelog, convco, xtask, publish]
relates_to:
  - cicd/CONTEXT
  - cicd/dist
  - crates/xtask
  - tooling/convco
  - conventions/commit-conventions
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Release Workflow

The full release pipeline: from conventional commits to published
artifacts. Releases are prepared locally by a maintainer, then
finalized by CI.

---

## Release Philosophy

### 1. Local preparation, CI finalization
The maintainer runs `pixi run -e release release` locally. This
bumps versions, generates the changelog, and creates a git tag.
The maintainer reviews the changes, then pushes. CI builds and
publishes the artifacts.

### 2. Reversible until push
Everything `xtask release` does is local. If something looks wrong,
`git reset --hard HEAD~1 && git tag -d v0.3.0` undoes everything.
Nothing is published until `git push && git push --tags`.

### 3. Conventional commits drive versioning
No manual version decisions. `convco version --bump` reads the
commit history and applies semver rules. The maintainer can override
with `--major`, `--minor`, or `--patch` if needed.

---

## Step-by-Step Release Process

### Prerequisites

```bash
# Ensure you're on main, up to date, with clean working tree
git checkout main
git pull origin main
git status    # Must be clean
```

### Step 1: Validate Commits

```bash
pixi run -e release check-commits
```

This runs `convco check` — validates that all commits since the last
tag follow the conventional format. If any commit is non-conventional,
fix it (interactive rebase) before proceeding.

### Step 2: Preview the Release

```bash
# What version will be released?
pixi run -e release version-bump
# Output: 0.3.0

# What will the changelog look like?
pixi run -e release changelog
# Output: markdown changelog preview
```

### Step 3: Execute the Release

```bash
pixi run -e release release
```

This runs `cargo xtask release`, which:

```
1. convco check
   └── Validates all commits since last tag

2. convco version --bump → "0.3.0"
   └── Calculates next version from commit types

3. Update Cargo.toml versions (toml_edit)
   ├── crates/skills-core/Cargo.toml          → version = "0.3.0"
   ├── crates/skills-provider-github/Cargo.toml → version = "0.3.0"
   ├── crates/skills-provider-conda/Cargo.toml  → version = "0.3.0"
   ├── crates/skills-provider-prefix/Cargo.toml → version = "0.3.0"
   ├── crates/skills-provider-pypi/Cargo.toml   → version = "0.3.0"
   ├── crates/pixi-skills/Cargo.toml            → version = "0.3.0"
   └── Workspace dependency versions updated too

4. convco changelog > CHANGELOG.md
   └── Generates full changelog from all tags

5. cargo xtask schema
   └── Regenerates JSON Schema (version embedded)

6. cargo xtask completions
   └── Regenerates shell completions (--version output)

7. git add -A
   git commit -m "chore(release): v0.3.0"

8. git tag v0.3.0
```

### Step 4: Review

```bash
# Review the release commit
git log --oneline -1
# chore(release): v0.3.0

# Review changed files
git diff HEAD~1 --stat
# CHANGELOG.md
# crates/*/Cargo.toml
# apps/.../public/skills-schema.json
# completions/*

# Review the tag
git tag -l 'v0.3.*'
# v0.3.0
```

### Step 5: Push

```bash
git push origin main
git push origin v0.3.0
```

This triggers CI, which will:
1. Run the full `ci` pipeline (tests, lints, docs build)
2. Build distribution artifacts (via the release workflow)
3. Create a GitHub Release with artifacts attached

---

## CI Release Workflow: `.github/workflows/release.yml`

```yaml
name: Release

on:
  push:
    tags: ['v*']

permissions:
  contents: write       # Create GitHub Release

jobs:
  build:
    name: Build (${{ matrix.target }})
    strategy:
      matrix:
        include:
          - target: x86_64-unknown-linux-gnu
            os: ubuntu-latest
          - target: aarch64-unknown-linux-gnu
            os: ubuntu-latest
          - target: x86_64-apple-darwin
            os: macos-latest
          - target: aarch64-apple-darwin
            os: macos-latest
          - target: x86_64-pc-windows-msvc
            os: windows-latest
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v5

      - uses: prefix-dev/setup-pixi@v0.10.2
        with:
          environments: release
          cache: true

      - name: Build distribution
        run: pixi run -e release dist -- --target ${{ matrix.target }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v5
        with:
          name: dist-${{ matrix.target }}
          path: dist/

  publish:
    name: Publish GitHub Release
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - name: Download all artifacts
        uses: actions/download-artifact@v5
        with:
          path: dist/
          merge-multiple: true

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          generate_release_notes: false
          body_path: CHANGELOG.md
          files: |
            dist/*.tar.gz
            dist/*.tar.gz.sha256
            dist/checksums.sha256

  publish-crates:
    name: Publish to crates.io
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5

      - uses: prefix-dev/setup-pixi@v0.10.2
        with:
          environments: release
          cache: true

      - name: Publish crates
        env:
          CARGO_REGISTRY_TOKEN: ${{ secrets.CARGO_REGISTRY_TOKEN }}
        run: |
          cargo publish -p skills-core
          sleep 30    # Wait for crates.io to index
          cargo publish -p skills-provider-github
          cargo publish -p skills-provider-conda
          cargo publish -p skills-provider-prefix
          cargo publish -p pixi-skills
```

### Crate Publish Order

Crates must be published in dependency order:

```
1. skills-core              (no workspace deps)
2. skills-provider-github   (depends on skills-core)
3. skills-provider-conda    (depends on skills-core)
4. skills-provider-prefix   (depends on skills-core)
5. skills-provider-pypi     (depends on skills-core)
6. pixi-skills              (depends on all above)
```

The `sleep 30` between publishes ensures crates.io indexes each
crate before the next one tries to resolve it as a dependency.

**Note**: `xtask` is never published (`publish = false`).

---

## Version Bump Rules

| Commits since last tag | Bump | Example |
|---|---|---|
| Only `fix:` commits | Patch | 0.2.0 → 0.2.1 |
| At least one `feat:` | Minor | 0.2.0 → 0.3.0 |
| Any `feat!:` or `BREAKING CHANGE:` | Major | 0.2.0 → 1.0.0 |
| Only `docs:`, `chore:`, `ci:`, etc. | No bump | — (release skipped) |

### Pre-1.0 behavior

While the version is `0.x.y`:
- Breaking changes bump **minor** (0.x.0), not major
- This follows the semver convention that 0.x versions make no
  stability guarantees
- Once we release 1.0.0, breaking changes bump major properly

### Override

```bash
pixi run -e release -- cargo xtask release --major    # Force major
pixi run -e release -- cargo xtask release --minor    # Force minor
pixi run -e release -- cargo xtask release --patch    # Force patch
```

---

## Dry Run

```bash
pixi run -e release -- cargo xtask release --dry-run
```

This runs through all release steps but:
- Does not modify any files
- Does not create git commits or tags
- Prints what it would do

Use this to verify the release will produce the expected version
and changelog before committing to it.

---

## Rollback

If something went wrong after `xtask release` but before `git push`:

```bash
# Undo the release commit and tag
git reset --hard HEAD~1
git tag -d v0.3.0

# You're back to the state before the release
```

If the push already happened:

```bash
# Delete the remote tag (stops the release workflow)
git push origin --delete v0.3.0

# Revert the release commit
git revert HEAD
git push origin main

# If a GitHub Release was created, delete it manually via the UI
```

If crates were published to crates.io, they **cannot** be unpublished
(only yanked). Yanking prevents new projects from depending on the
version but doesn't remove it from the registry:

```bash
cargo yank --version 0.3.0 skills-core
cargo yank --version 0.3.0 pixi-skills
# etc.
```

---

## Release Checklist (Summary)

```
□ On main branch, working tree clean
□ pixi run -e release check-commits        → all green
□ pixi run -e release version-bump          → expected version
□ pixi run -e release changelog             → looks correct
□ pixi run -e release release               → commit + tag created
□ Review: git log, git diff HEAD~1, git tag
□ pixi run -e all ci                        → full pipeline passes
□ git push origin main
□ git push origin v0.3.0
□ Monitor CI: release workflow builds + publishes
□ Verify GitHub Release has all artifacts
□ Verify crates.io has new versions
□ Announce release (if applicable)
```
