---
type: Reference
title: "convco"
description: "Planned conventional commit validation, changelog generation, and semantic versioning."
section: tooling
kind: detail
tags: [tooling, convco, conventional-commits, changelog, versioning, release]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# convco

A Conventional Commits CLI built in Rust. Provides tools for
creating, validating, and processing conventional commits: interactive
commit helper, commit history validation, automatic changelog
generation, and semantic version calculation.

---

## Installation

convco is not currently on conda-forge (as of mid-2025). Installation
options:

```bash
# Option 1: cargo install (requires Rust toolchain — already available via pixi)
cargo install convco

# Option 2: Pre-built binary in pixi task
# Download from GitHub releases and place in project .bin/

# Option 3: Build from source via xtask (self-bootstrapping)
# cargo xtask ensure-convco
```

**Preferred approach**: install via `cargo install` in the pixi
environment. The `release` pixi feature ensures convco is available
when needed for release tasks. If convco becomes available on
conda-forge, switch to `pixi add convco`.

> **Updated 2026-09-17:** latest convco is 0.6.4 (2026-05); still
> not packaged on conda-forge — the `cargo install convco` path
> remains the way to get it. The `.convco` config `"version": "0.6"`
> below stays valid for the whole 0.6.x line.

---

## Configuration: `.convco`

```json
{
  "version": "0.6",
  "types": [
    { "type": "feat",     "section": "Features",        "hidden": false },
    { "type": "fix",      "section": "Bug Fixes",       "hidden": false },
    { "type": "docs",     "section": "Documentation",   "hidden": false },
    { "type": "refactor", "section": "Refactoring",      "hidden": false },
    { "type": "perf",     "section": "Performance",      "hidden": false },
    { "type": "test",     "section": "Tests",            "hidden": true  },
    { "type": "ci",       "section": "CI",               "hidden": true  },
    { "type": "chore",    "section": "Miscellaneous",    "hidden": true  },
    { "type": "build",    "section": "Build System",     "hidden": true  },
    { "type": "style",    "section": "Style",            "hidden": true  }
  ],
  "scopes": [
    "core",
    "cli",
    "github",
    "conda",
    "prefix",
    "pypi",
    "docs",
    "xtask"
  ],
  "host": "https://github.com",
  "owner": "yourorg",
  "repository": "pixi-skills"
}
```

### Configuration Fields

| Field | Purpose |
|---|---|
| `types` | Allowed commit types and their changelog sections |
| `types[].hidden` | If `true`, commits of this type don't appear in the changelog |
| `scopes` | Allowed commit scopes (validated by `convco check`) |
| `host` / `owner` / `repository` | Used for generating commit links in the changelog |

---

## Core Commands

### `convco commit` — Interactive Commit Helper

Prompts the developer through the conventional commit format:

```
$ convco commit

? Select the type of change:
  feat     — A new feature
  fix      — A bug fix
  docs     — Documentation only changes
  refactor — A code change that neither fixes a bug nor adds a feature
  perf     — A code change that improves performance
  test     — Adding missing or correcting existing tests
  > feat

? Select the scope (optional):
  core | cli | github | conda | prefix | pypi | docs | xtask
  > core

? Write a short description: add SkillRegistry trait definition

? Write a longer description (optional):
  Defines the async trait that all provider crates must implement.
  Includes search, list, fetch, and supports methods.

? Are there any breaking changes? No

? Does this change affect any open issues? No

# Produces commit message:
# feat(core): add SkillRegistry trait definition
#
# Defines the async trait that all provider crates must implement.
# Includes search, list, fetch, and supports methods.
```

### `convco check` — Validate Commit History

Validates that all commits in a range follow the conventional format:

```bash
# Check all commits since the last tag
convco check

# Check commits in a specific range
convco check v0.1.0..HEAD

# Check only the last commit
convco check HEAD~1..HEAD
```

**Exit code**: 0 if all commits are valid, 1 if any violation is found.

**What it checks**:
- Commit message starts with a valid type (`feat`, `fix`, etc.)
- Scope (if present) is in the allowed list
- Description is present and not empty
- Breaking change notation is correctly formatted (`feat!:` or
  `BREAKING CHANGE:` footer)

### `convco changelog` — Generate Changelog

Generates a markdown changelog from conventional commits:

```bash
# Full changelog (all tags)
convco changelog

# Changelog since a specific version
convco changelog --from v0.2.0

# Write to file
convco changelog > CHANGELOG.md
```

**Output format**:

```markdown
## [0.3.0] - 2025-01-20

### Features
- **core**: add SkillRegistry trait definition (abc123)
- **cli**: implement `pixi skills find` subcommand (def456)

### Bug Fixes
- **github**: handle rate limiting with retry (789ghi)

### Documentation
- **docs**: add installation guide (jkl012)
```

**Grouping**: commits are grouped by type (Features, Bug Fixes, etc.)
and prefixed with their scope. Hidden types (`test`, `ci`, `chore`)
are excluded.

### `convco version` — Calculate Version

Determines the current version or calculates the next version based
on conventional commits:

```bash
# Current version (from latest git tag)
convco version
# Output: 0.2.0

# Next version (based on commits since last tag)
convco version --bump
# Output: 0.3.0  (feat commits → minor bump)

# Force a specific bump level
convco version --major   # 1.0.0
convco version --minor   # 0.3.0
convco version --patch   # 0.2.1
```

**Version calculation rules**:
| Commit type | Bump level |
|---|---|
| `fix:` | Patch (0.0.x) |
| `feat:` | Minor (0.x.0) |
| `feat!:` / `BREAKING CHANGE:` | Major (x.0.0) |
| `docs:`, `refactor:`, `chore:`, etc. | No bump |

**Pre-1.0 behavior**: When the current version is `0.x.y`, breaking
changes bump minor (not major), following the semver convention for
pre-release versions.

---

## pixi Task Integration

```toml
# pixi.toml
[feature.release.tasks]
commit        = "convco commit"
changelog     = "convco changelog"
version       = "convco version"
version-bump  = "convco version --bump"
check-commits = "convco check"
```

### How Developers Use It

```bash
# Stage changes, then create a conventional commit
git add -A
pixi run -e release commit         # Interactive prompt

# Before pushing: validate commit history
pixi run -e release check-commits  # Must pass before CI

# Preview the changelog
pixi run -e release changelog      # Print to stdout

# Check what the next version would be
pixi run -e release version-bump   # e.g., "0.3.0"
```

---

## Integration with xtask Release

The `cargo xtask release` command uses convco as a subprocess:

```
xtask release
  │
  ├── 1. xshell: `convco check`        → validate commit history
  ├── 2. xshell: `convco version --bump` → determine next version
  ├── 3. toml_edit: update Cargo.toml versions
  ├── 4. xshell: `convco changelog > CHANGELOG.md`
  ├── 5. xshell: `git add -A && git commit -m "chore(release): v{ver}"`
  └── 6. xshell: `git tag v{ver}`
```

xtask orchestrates convco — it doesn't reimplement conventional
commit parsing. convco is the source of truth for version calculation
and changelog format.

---

## CI Requirements

### Full Git History

convco needs the full git history to:
- Validate all commits since the last tag
- Count commits of each type for version calculation
- Generate the changelog

This requires `fetch-depth: 0` in the GitHub Actions checkout:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0    # convco needs full history
```

Without full history, `convco check` and `convco version --bump`
will produce incorrect results (they'll only see the last commit).

### Check on Every Push

The `check-commits` task runs on every CI run (part of the `ci`
composite task). This catches non-conventional commits before they're
merged to main. If a contributor forgets to use `convco commit`, the
CI will fail with a clear error message.

---

## Common Issues and Solutions

### Issue: "no tags found" on a fresh repository
**Solution**: Create an initial tag manually:
```bash
git tag v0.0.0
```
convco needs at least one tag to calculate the next version.

### Issue: Merge commits don't follow conventional format
**Solution**: Configure GitHub to use squash merges, where the PR
title becomes the commit message. Ensure PR titles follow conventional
format (enforce via GitHub branch protection rules or a PR title
linter).

### Issue: convco check fails on dependabot/renovate commits
**Solution**: These bots use their own commit formats. Options:
1. Configure the bot to use conventional commit format
2. Add a CI exception for bot commits
3. Use squash merge to override the bot's commit message

## Related Concepts

- [Tooling — Context](./CONTEXT.md)
- [Commit Conventions](../conventions/commit-conventions.md)
- [Release Workflow](../cicd/release-workflow.md)
- [xtask](../crates/xtask.md)
- [Pixi Tasks](../pixi/tasks.md)
