---
type: Comparative Analysis
title: "npm-skills"
description: "Overview of npm-distributed agent skills and their strengths and limitations."
section: landscape
kind: detail
tags: [landscape, npm-skills, npm, anthony-fu, competition]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# npm-skills

An approach to shipping AI agent skills inside npm packages. Primarily
associated with Anthony Fu's work. Skills are bundled as part of
regular npm packages and installed alongside other dependencies.

---

## How It Works

### Concept

Instead of a separate skills registry, skills are embedded in npm
packages. When you `npm install` a tool or library, its skills come
bundled:

```
node_modules/
└── some-library/
    ├── package.json
    ├── src/
    └── skills/                  # Skills bundled with the package
        └── usage-guide.md
```

A CLI tool discovers skill files inside `node_modules` and creates
symlinks or copies them into agent config directories.

### Discovery

The tool scans `node_modules` for packages that contain a `skills/`
directory or declare skills in their `package.json`:

```json
{
  "name": "some-library",
  "skills": {
    "directory": "skills/"
  }
}
```

### Installation

Skills are symlinked (or copied) from `node_modules` into the
agent config directories:

```
node_modules/some-library/skills/usage-guide.md
    → .claude/skills/some-library-usage-guide.md
    → .cursor/rules/some-library-usage-guide.md
```

---

## Strengths

| Strength | Detail |
|---|---|
| **Version pinning via package.json** | Skills version alongside their npm package. `npm install some-lib@1.2.3` pins the skill to that version. |
| **Dependency graph integration** | Skills are part of the npm dependency graph. `npm update` updates skills too. |
| **Private registry support** | Works with private npm registries (Artifactory, Verdaccio, GitHub Packages). |
| **Lockfile (package-lock.json)** | npm's lockfile covers skill-containing packages. Reproducible installs. |
| **Co-location** | Skills ship with the tools they describe. The Playwright npm package can include a Playwright skill. |

---

## Weaknesses

| Weakness | Detail | pixi-skills advantage |
|---|---|---|
| **npm-only** | Only works with npm packages. Not available for conda, pip, cargo, or non-JS ecosystems. | Provider-agnostic trait system |
| **Skills coupled to packages** | A skill can only be distributed as part of an npm package. Standalone skills require creating a dummy package. | Skills are first-class artifacts, not package attachments |
| **Node.js required** | Requires a Node.js runtime. Projects without JS dependencies must add one just for skills. | pixi-based — no JS required |
| **No skill-specific versioning** | Skill version = package version. Can't update a skill without updating the package (and potentially breaking API changes). | Independent skill versioning |
| **Limited adoption** | Relatively few npm packages ship skills today. Ecosystem is nascent. | GitHub provider gives instant access to existing skills |
| **symlink complexity** | Symlinks can break on Windows, in Docker, or in CI depending on permissions. | File copy with content hashing |

---

## Key Insight

The npm-skills approach is correct in principle: **skills should be
versioned and distributed through existing package infrastructure.**
The limitation is that it's locked to npm.

pixi-skills applies the same principle but generalizes it:
- conda packages can contain skills (same co-location benefit)
- GitHub repos can contain skills (same as skills.sh)
- PyPI packages can contain skills (future)
- Any provider can contain skills (trait-based extensibility)

The `skill-*` naming convention for conda packages is directly
inspired by the npm-skills `skills/` directory convention — but
as a first-class package type, not an add-on to existing packages.

## Related Concepts

- [Landscape — Context](./CONTEXT.md)
- [Differentiation](./differentiation.md)
- [skills.sh](./skills-sh.md)
