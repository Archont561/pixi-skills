---
title: "Commit Conventions"
section: conventions
kind: detail
tags: [conventions, commits, conventional-commits, scopes, types, changelog]
relates_to:
  - conventions/CONTEXT
  - tooling/convco
  - cicd/release-workflow
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Commit Conventions

All commits follow the Conventional Commits specification. This
enables automatic changelog generation, semantic version calculation,
and structured git history.

---

## Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Examples

```
feat(core): add SkillRegistry trait definition

fix(github): handle rate limiting with exponential backoff

docs(docs): add installation guide for macOS

refactor(cli): extract provider composition into MultiRegistry

chore(release): v0.3.0
```

---

## Allowed Types

| Type | Description | Changelog section | Triggers bump? |
|---|---|---|---|
| `feat` | A new feature | Features | ✅ Minor |
| `fix` | A bug fix | Bug Fixes | ✅ Patch |
| `docs` | Documentation only changes | Documentation | ❌ |
| `refactor` | Code change that neither fixes a bug nor adds a feature | Refactoring | ❌ |
| `perf` | A code change that improves performance | Performance | ❌ |
| `test` | Adding or correcting tests | (hidden) | ❌ |
| `ci` | Changes to CI configuration | (hidden) | ❌ |
| `chore` | Other changes that don't modify src or test | (hidden) | ❌ |
| `build` | Changes to the build system or dependencies | (hidden) | ❌ |
| `style` | Formatting, whitespace, semicolons (no code change) | (hidden) | ❌ |

Hidden types don't appear in the changelog but are valid conventional
commits.

---

## Allowed Scopes

| Scope | Refers to |
|---|---|
| `core` | `skills-core` crate |
| `cli` | `pixi-skills` CLI crate |
| `github` | `skills-provider-github` crate |
| `conda` | `skills-provider-conda` crate |
| `prefix` | `skills-provider-prefix` crate |
| `pypi` | `skills-provider-pypi` crate |
| `docs` | The Astro Starlight docs site |
| `xtask` | The xtask automation crate |

Scopes are optional but strongly encouraged. They help filter the
changelog and make the git history scannable.

### Scope-less commits

Acceptable for cross-cutting changes:

```
chore: update pixi.lock
ci: add matrix build for macOS
build: bump rust edition to 2024
```

---

## Breaking Changes

### Using the `!` notation

```
feat!: redesign SkillRegistry trait to use associated types

The trait now uses associated types for error handling instead of
a shared SkillsError enum. All provider implementations must be
updated.
```

### Using the `BREAKING CHANGE` footer

```
feat(core): add provider-specific error types

BREAKING CHANGE: SkillsError is now an enum of provider-specific
error types. Downstream code matching on error variants must be
updated.
```

### Version impact

- Pre-1.0: breaking changes bump **minor** (0.x.0 → 0.(x+1).0)
- Post-1.0: breaking changes bump **major** (x.0.0 → (x+1).0.0)

---

## Multi-Line Commit Messages

### Body

Use the body for context that doesn't fit in the description:

```
feat(core): add agent detection for Windsurf

Windsurf stores rules in .windsurf/rules/. Detection checks for the
directory existence and the `windsurf` binary on PATH.

Closes #42
```

### Footers

Standard footers:

| Footer | Purpose |
|---|---|
| `BREAKING CHANGE: <description>` | Marks a breaking change |
| `Closes #N` | Links to a GitHub issue |
| `Refs #N` | References (but doesn't close) an issue |
| `Co-authored-by: Name <email>` | Credit co-authors |

---

## Enforcement

### Local: `convco commit`

```bash
pixi run -e release commit
```

Interactive prompt that guides you through creating a valid
conventional commit. You cannot accidentally create a non-conventional
commit.

### CI: `convco check`

```bash
pixi run -e release check-commits
```

Part of the `ci` pipeline. Validates all commits since the last tag.
Non-conventional commits fail the build.

### PR titles (GitHub)

If using squash merges, the PR title becomes the commit message.
Configure branch protection to require conventional PR titles:

1. Use a GitHub Action like `amannn/action-semantic-pull-request`
2. Or require reviewers to check the PR title format

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `Updated the README` | `docs: update README` or `docs(docs): update README` |
| `Fix bug in parser` | `fix(core): handle empty YAML frontmatter` |
| `WIP` | Don't commit WIP. Use draft PRs or `git stash`. If committed, interactive-rebase before merge. |
| `feat: add X and fix Y` | Split into two commits: `feat: add X` and `fix: fix Y` |
| `feat(Core): ...` (uppercase scope) | Use lowercase: `feat(core): ...` |
| Missing colon after type | `feat(core) description` → `feat(core): description` |
