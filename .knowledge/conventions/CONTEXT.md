---
title: "Conventions — Context"
section: conventions
kind: context
tags: [conventions, context, consistency, naming, commits, format]
relates_to:
  - conventions/commit-conventions
  - conventions/skill-format
  - conventions/naming
  - conventions/config-files
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Conventions — Context

## What This Section Covers

Project-wide conventions that ensure consistency across all parts of the
monorepo. These conventions are enforced by tooling where possible
(convco for commits, xtask lint for workspace consistency, biome/taplo
for formatting).

## Why Conventions Matter Here

pixi-skills is a tool about package management — about bringing order
to skills that are currently copy-pasted and unversioned. The project
itself must demonstrate the discipline it advocates. If our commit
history is messy, our naming inconsistent, and our config files
scattered, we undermine our own value proposition.

## Convention Categories

### 1. Commit conventions (enforced by convco)
Every commit follows the Conventional Commits specification. This
enables:
- Automatic changelog generation (`convco changelog`)
- Automatic version calculation (`convco version --bump`)
- Meaningful git history that can be parsed by tools and humans

### 2. Skill format (defined by skills-core, documented here)
The skill **folder** — `SKILL.md` with YAML frontmatter per the
agentskills.io open standard, plus optional `scripts/`,
`references/`, `assets/`, and our companion `skill.toml` envelope —
is the unit of content that pixi-skills manages. The format must be:
- Simple enough that anyone can write a skill in a text editor
- 100% compliant with the open standard, so 26+ agents read it natively
- Structured enough that tools can parse metadata (version, agent
  compatibility, dependencies) from the companion envelope
- Backward-readable with pre-standard skills (bare markdown files)

*(Updated 2026-09-17 — previously described a single-file SKILL.md
with TOML frontmatter; superseded by ADR-008.)*

### 3. Naming conventions (enforced by xtask lint)
Consistent naming across crates, packages, tasks, and files reduces
cognitive load. When you see `skills-provider-github`, you know it
implements `SkillRegistry` for GitHub. When you see `skill-playwright`
on conda-forge, you know it's a skill package.

### 4. Config file placement (documented, not enforced)
Every config file has a canonical location. Root-level files configure
workspace-wide tools. Subdirectory files extend or override root config.
The config-files page is the single reference for "where does this
config live?"

## Enforcement Model

| Convention | Enforced by | When |
|---|---|---|
| Commit format | `convco check` | CI (`check-commits` task) |
| Crate naming | `cargo xtask lint` | CI (`lint-workspace` task) |
| Rust formatting | `rustfmt` | CI (`fmt-check-rust` task) |
| TOML formatting | `taplo check` | CI (`fmt-check-toml` task) |
| TS/JS formatting | `biome check` | CI (`fmt-check-ts` task) |
| Config placement | Documentation only | Code review |
| Skill format | `skills-core` parser | Runtime (when skills are installed) |
