---
title: "skills.sh"
section: landscape
kind: detail
tags: [landscape, skills-sh, competition, github, npm, npx]
relates_to:
  - landscape/CONTEXT
  - landscape/differentiation
  - crates/skills-provider-github
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# skills.sh

The most widely known skill management tool as of mid-2025. Published
by Vercel Labs. Invoked as `npx skills` or installed globally via npm.

---

## How It Works

### Registry model

skills.sh uses **GitHub repositories as its registry**. There is no
central database — skills are discovered by convention:

1. A skill is a GitHub repository containing a `SKILL.md` file
2. Discovery happens via GitHub topic search (`pixi-skill` topic)
   or curated lists
3. Installation fetches the file from the repo's default branch

### Core commands

```bash
npx skills find <query>     # Search for skills on GitHub
npx skills add <repo>       # Fetch SKILL.md from a GitHub repo
npx skills list             # List installed skills
npx skills remove <name>    # Remove an installed skill
```

### Installation behavior

When `npx skills add user/repo` is run:
1. Fetches `SKILL.md` from `https://raw.githubusercontent.com/user/repo/main/SKILL.md`
2. Writes the content to the appropriate agent config directory
   (e.g., `.claude/skills/`, `.cursor/rules/`)
3. Supports 16+ agent config paths (auto-detected)

### Agent support

skills.sh supports a wide range of agent config paths and auto-detects
which agents are present in the project. This is a strong feature —
broad agent compatibility was a key design goal.

---

## Strengths

| Strength | Detail |
|---|---|
| **Instant ecosystem** | Any GitHub repo with a SKILL.md is a skill. Zero publishing ceremony. |
| **Zero infrastructure** | No registry to maintain. GitHub is the registry. |
| **Broad agent support** | Detects and installs into 16+ agent config directories. |
| **Simple mental model** | `npx skills add user/repo` — one command, instantly understood. |
| **npm ecosystem reach** | Available via npx — any developer with Node.js can use it. |

---

## Weaknesses

| Weakness | Detail | pixi-skills advantage |
|---|---|---|
| **No version pinning** | Always fetches from `main` branch. No way to pin `v1.2.3`. | `skills-lock.toml` with exact versions |
| **No lockfile** | No record of what was installed, at what version, with what hash. | Content-hashed lockfile |
| **No reproducibility** | Two developers running `npx skills add` at different times get different content. | Lockfile guarantees identical installs |
| **Skills are vendored** | Content is copied into the repo. Updates mean committing markdown diffs. | Skills are referenced, not vendored. Updates are `pixi skills update`. |
| **Git history pollution** | Every skill update creates a diff in the repo. Git history fills with markdown changes you didn't write. | Skills are not in git — they're installed from the lockfile |
| **npm-only** | Requires Node.js / npm. Not available to Rust, Python, Go, etc. developers without Node. | pixi-based — works with any language |
| **No private source support** | Only public GitHub repos. No enterprise/private skill sources. | Private conda channels, prefix.dev orgs |
| **No offline support** | Always fetches from GitHub. Doesn't work offline or in airgapped environments. | pixi-pack offline bundles |
| **No supply chain security** | Trusts arbitrary GitHub repos. No signing, no integrity verification. | Content hashes in lockfile, conda signing (future) |

---

## Compatibility Strategy

pixi-skills' `skills-provider-github` is designed to be **compatible
with the existing skills.sh ecosystem**. Any GitHub repo that works
with `npx skills add` should work with `pixi skills add github:user/repo`.

This gives pixi-skills instant access to every skill already published,
while adding version pinning and lockfile integrity on top.

### Migration path for skills.sh users

```bash
# Before (skills.sh)
npx skills add user/playwright-skill

# After (pixi-skills)
pixi skills add github:user/playwright-skill@tag:v1.0
```

The key difference: pixi-skills requires (or strongly encourages) a
version ref. `@tag:v1.0` pins to a specific tag. `@branch:main` is
supported but discouraged (same problem as skills.sh).

See the [migrating-from-skills-sh](/guides/migrating-from-skills-sh/)
guide on the docs site.
