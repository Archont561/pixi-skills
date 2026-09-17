---
title: "Landscape — Context"
section: landscape
kind: context
tags: [landscape, context, competition, skills, ecosystem, market]
relates_to:
  - landscape/skills-sh
  - landscape/npm-skills
  - landscape/pixi-ecosystem
  - landscape/differentiation
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Landscape — Context

## What This Section Covers

The competitive and ecosystem landscape around AI agent skills
management. This context informs every architectural decision in the
project.

## The Problem Space

AI coding agents (Claude Code, Cursor, GitHub Copilot, Codex, Windsurf,
etc.) use "skills" — markdown files that teach them domain-specific
knowledge. Skills are emerging as a new category of developer artifact,
analogous to packages, plugins, or configuration.

The problem: **skills have no proper package management.**

| Package type | Has package manager | Has lockfile | Has registry |
|---|---|---|---|
| Rust crates | ✅ cargo | ✅ Cargo.lock | ✅ crates.io |
| npm packages | ✅ npm/bun/pnpm | ✅ package-lock.json | ✅ npmjs.com |
| conda packages | ✅ pixi/conda | ✅ pixi.lock | ✅ conda-forge |
| AI agent skills | ⚠️ skills.sh (Vercel) — no semver, single-provider | ⚠️ hash-only `skills-lock.json` — no constraints | ⚠️ skills.sh directory — curated but centralized + git-only |

*(2026-09 update: the row above used to be all ❌. skills.sh filled
the naive versions of all three gaps in H1 2026. What remains unfilled
— and is pixi-skills' opening — is the **semantic, multi-provider,
enterprise-enforceable** version of each.)*

## The Current Landscape (Late 2026)

### Tier 1: Dedicated skill managers
- **skills.sh** (`npx skills`, Vercel; launched 2026-01-20) — the
  ecosystem gravity well: 83k+ skills, 8M+ installs, 70+ agent
  targets, Snyk directory scanning, project-scoped hash lockfile.
  Still git-only, no semver resolution, no private channels, no
  offline mode, JS runtime required.
- **skills-lock wrappers** (community, e.g. pcomans/skills-lock) —
  SHA pinning + integrity trees + `--frozen` CI on top of `npx
  skills`. Validation of the reproducibility thesis, delivered as glue.
- **npm-skills / paks** — skills shipped inside npm packages or a
  bespoke registry. Versioning via the host ecosystem; npm-only.

### Tier 2: Manual approaches
- **Blog-level solutions** (e.g., pavel.pink) — publishing skills as
  conda packages and managing with pixi. Correct idea but no reusable
  tooling — just a blog post describing the approach.
- **Git submodules** — some teams vendor skills as submodules. Painful
  updates, no version constraints, no discoverability.
- **Copy-paste** — the most common approach. Skills are copied into
  `.claude/skills/` or `.cursor/rules/` and committed. No updates,
  no provenance, git history pollution.

### Tier 3: Ecosystem enablers (not skill managers, but building blocks)
- **pixi** — cross-platform package manager built on conda. Provides
  the environment + task model we build on.
- **rattler** — Rust crates implementing conda spec. We use these for
  the conda provider.
- **pixi-pack** — offline bundling. Skills installed via conda can be
  pixi-packed for airgapped environments.

## The Gap pixi-skills Fills

Nobody has built a **general-purpose, provider-agnostic, lockfile-first
skills manager** with:
1. A trait-based provider system (not hardcoded to one registry)
2. A lockfile (exact versions + hashes, reproducible)
3. Conda-native support (not npm-only)
4. Enterprise features (private channels, offline support)
5. Proper CLI tooling as a pixi extension

pixi-skills is the first project to combine all five.

## Competitive Positioning

- **vs skills.sh**: we are the "cargo" to their "curl | sh". Same
  ecosystem access (GitHub provider), but with lockfiles, version
  pinning, and reproducibility.
- **vs npm-skills**: we are multi-language. They are npm-only. We
  support conda, GitHub, prefix.dev, and PyPI as sources.
- **vs manual approaches**: we are automation. They are copy-paste
  with extra steps.

## How This Informs Our Roadmap

The MVP starts with `skills-provider-github` for instant ecosystem
access (Phase 1), then layers conda-native support as the key
differentiator (Phase 3). This sequence gets us a working product
quickly while building toward the real value proposition.
