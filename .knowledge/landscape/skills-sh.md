---
type: Comparative Analysis
title: "skills.sh"
description: "Overview of the skills.sh ecosystem, compatibility goals, and remaining product gaps."
section: landscape
kind: detail
tags: [landscape, skills-sh, competition, github, npm, npx, vercel]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# skills.sh

The incumbent skill manager, and the de-facto center of the open
agent-skills ecosystem. Published by **Vercel** — the CLI lives at
`vercel-labs/skills`, the directory at `skills.sh`. Invoked as
`npx skills` (or `bunx skills`).

> **Major update (2026-09-17):** this page was rewritten to reflect
> the ecosystem as it exists now. skills.sh **launched publicly on
> 2026-01-20** and grew extremely fast; several of our original
> "weakness" claims required revision — most notably, the CLI now
> writes a project-scoped `skills-lock.json` with content hashes, and
> the directory integrates **Snyk security scanning**. See the revised
> weaknesses table and `landscape/differentiation.md`.

---

## Ecosystem Snapshot (2026-09)

| Metric | Value |
|---|---|
| Launch | 2026-01-20 (20k installs within 6 hours; Stripe shipped skills same day) |
| Indexed skills | 83,000+ |
| Total installs | 8M+ |
| Supported agents | 70+ (OpenCode, Claude Code, Codex, Cursor, and ~69 more) |
| Security | Snyk scanning integrated into the directory (partnership) |
| Discovery | skills.sh leaderboard (ranked by total installs) |
| CLI | `npx skills` — TypeScript, `vercel-labs/skills` |

Context for scale: the wider ecosystem is estimated at ~490k SKILL.md
files overall (volume crawlers like SkillsMP index 400k+ with no
curation; OpenClaw's ClawHub ~10k — and was hit by the "ClawHavoc"
malware campaign). skills.sh is the **curated quality** play.

---

## How It Works

### Core commands

```bash
npx skills find [query] [--owner <org>]  # Search (or interactive)
npx skills add <source>                  # Install from many source formats
npx skills check                         # Check for skill updates
npx skills update                        # Update all installed skills
npx skills use <source>                  # Ephemeral: generate prompt, or pipe into an agent
npx skills init [name]                   # Scaffold a new skill
```

### Source formats

```bash
npx skills add vercel-labs/agent-skills                                        # GitHub shorthand
npx skills add https://github.com/vercel-labs/agent-skills                    # Full URL
npx skills add https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines  # Subpath
npx skills add vercel-labs/agent-skills@web-design-guidelines                 # @skill shorthand
npx skills add https://gitlab.com/org/repo                                    # GitLab
npx skills add git@github.com:org/repo.git                                    # Any git URL
npx skills add ./my-local-skills                                              # Local path
```

### Install scopes & flags

- Project scope by default; `-g` installs at user level (all projects)
- `-y` skips confirmation (enables agents to self-install mid-task)
- Writes matched skill files into **every detected agent's** skills
  directory (70+ agent paths auto-detected)

### Locking (new since our last analysis)

In project scope the CLI writes a **`skills-lock.json`** recording the
installed skills with a per-skill **content hash** (`computedHash`) —
used by `check`/`update` and increasingly by CI-style `verify`/frozen
install flows (command names still evolving upstream).

Third-party wrappers — community projects like **`skills-lock`** —
push further: they pin exact git **commit SHAs** plus a SHA-256 tree
hash of the skill directory, and offer `--frozen` CI installs. Their
existence is market validation for our core thesis (reproducible,
tamper-evident skill installs), delivered on top of plain git.

---

## Strengths

| Strength | Detail |
|---|---|
| **Huge curated ecosystem** | 83k+ skills, leaderboard-ranked, Snyk-scanned. The default discovery destination. |
| **Broadest agent support** | 70+ agents auto-detected — the industry's most complete agent-path map. |
| **Frictionless UX** | One command, any git URL or local path. Agents can even self-install mid-task (`-y`). |
| **npm ecosystem reach** | Available via npx/bunx to anyone with Node or Bun. |
| **Zero infrastructure** | GitHub (and now GitLab/any git) is the registry. |
| **Now has integrity hashes** | `skills-lock.json` detects content drift against install-time hashes. |

---

## Weaknesses — Revised (2026-09)

| Weakness | Status vs our original analysis | pixi-skills advantage |
|---|---|---|
| **No semantic versioning** | Still true. A branch/tag in a URL is not a version constraint; there is no `^1.2` resolution, no ranges, no solver. `update` jumps to latest — no "latest within a major" | `skills.toml` version reqs + `skills-lock.toml` resolution, exactly like cargo/pixi |
| **Hash-lock ≠ version management** | Partially mitigated by `skills-lock.json` (drift detection) — but the lock records *what you happened to install*, not *what you asked for*. No manifest/constraint separation | Manifest (`skills.toml`) and lockfile are distinct, first-class artifacts |
| **No private registries/channels** | Still true. Sources are git repos; private repos need git credentials, not registry authz; no org-scoped release management | Private conda channels, prefix.dev orgs, per-team ACLs |
| **No offline/airgap** | Still true. Every operation talks to git remotes | Conda packages + pixi-pack offline bundles; local channels |
| **npm/Node required** | Mostly true (`bunx` works too — but you still need a JS runtime). Not native to Rust/Python/Go dev environments | Standalone Rust binary via pixi/cargo; no JS runtime |
| **Skills vendored into agent dirs** | Still true — installed files are copied per-agent; no deduplication, no project cache | Skills referenced from a content-addressed store; installed agent files are derived artifacts |
| **Security posture** | **Improved** — Snyk scans the *directory*, but scanning is advisory metadata on a listing page, not enforcement at install time; lockfile lacks signatures/provenance. Ecosystem-wide incident rates are real (≈13% of sampled community skills with critical insecurities; ClawHub's ClawHavoc campaign) | Content hashes in lockfile, plan: signed conda packages + provenance attestations (`roadmap/improvement-proposals.md`) |
| **Single-source provider model** | Still true. Git is the only provider class; no conda, PyPI, OCI, or HTTP registry abstraction | `SkillRegistry` trait — providers are pluggable crates |

---

## What Changed for Our Positioning

1. **"No other skill manager has a lockfile" is dead.** skills.sh added
   `skills-lock.json`; community wrappers add SHA pinning + `--frozen`.
   Our reproducibility story must now emphasize **semantic version
   constraints** and **multi-provider resolution** — things a git-SHA
   hash-lock fundamentally cannot express.

2. **Security moved from "trusts arbitrary repos" to "scanned but
   advisory."** Directory-level Snyk scanning raises the bar but
   doesn't enforce installation policy. Enforcement (signed packages,
   hash-pinned lockfiles, org allow-lists) remains our enterprise lane.

3. **They validated agent self-installation** (`-y` flag +
   "find-skills" meta-skill). Any manager we ship should assume
   *agents*, not humans, are the primary installer persona.

4. **Compatibility surface grew.** Beyond GitHub: subpath skills,
   `@skill` names, GitLab, arbitrary git URLs, local paths. Our
   `skills-provider-github` compatibility target is now: *any source
   string `npx skills add` accepts*.

### Migration path for skills.sh users

```bash
# Before (skills.sh)
npx skills add vercel-labs/agent-skills@web-design-guidelines

# After (pixi-skills)
pixi skills add github:vercel-labs/agent-skills@skill:web-design-guidelines --ref tag:v1.0
```

The key difference: pixi-skills records a **version constraint plus
content hash** in `skills-lock.toml`. `@branch:main` remains possible
but discouraged (same drift problem as skills.sh — now they detect
drift; we prevent it silently becoming the new baseline).

The planned `migrating-from-skills-sh` guide is described in the
[documentation content plan](../docs-app/content-structure.md#section-3-guides).
The docs-site route does not exist in this bundle.

## Related Concepts

- [Landscape — Context](./CONTEXT.md)
- [Differentiation](./differentiation.md)
- [Agent Skills Open Standard](./agent-skills-standard.md)
- [skills-provider-github](../crates/skills-provider-github.md)
