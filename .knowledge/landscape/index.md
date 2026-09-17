# Landscape — Index

This section maps the competitive landscape and ecosystem context for
pixi-skills. Understanding what already exists — and where it falls
short — informs our design choices and positioning.

## Start Here

- [Context](./CONTEXT.md) — Market context and competitive positioning that inform the pixi-skills design.
- [Bundle index](../index.md) — Browse all knowledge sections.

## Pages

### [agent-skills-standard.md](./agent-skills-standard.md)
**Read first.** The agentskills.io open standard (2025-12-18):
folder-shaped skills, YAML frontmatter, progressive disclosure,
converged agent paths, and the security context. 26+ platforms
conform. Drives our format decisions.

### [skills-sh.md](./skills-sh.md)
The incumbent: `skills.sh` / `npx skills` by Vercel (launched
2026-01-20). 83k+ skills, 70+ agents, Snyk directory scanning,
project-scoped `skills-lock.json`. How it works, what it does well,
and the weaknesses that remain (no semver resolution, git-only
provider, no private channels, npm/Node required).

### [npm-skills.md](./npm-skills.md)
Anthony Fu's `npm-skills` approach: shipping agent skills inside npm
packages. Skills version alongside npm dependencies. Strengths (version
pinning via package.json) and limitations (npm-only, no conda/pixi).

### [pixi-ecosystem.md](./pixi-ecosystem.md)
The pixi/rattler/conda ecosystem that pixi-skills builds on: pixi
(package manager + workflow tool), rattler (Rust conda implementation),
pixi-pack (offline bundles), rattler-build (package building). How
pixi-skills fits into this ecosystem.

### [differentiation.md](./differentiation.md)
Our competitive advantages: lockfile-first reproducibility, provider
extensibility via traits, conda-native packaging, enterprise readiness
(private channels, airgapped support, supply chain security). The
comparison table: pixi-skills vs skills.sh vs npm-skills.

## Related Sections

- [Roadmap](../roadmap/index.md) — the MVP plan informed by this
  landscape analysis
- [Architecture/design-decisions](../architecture/design-decisions.md) —
  decisions shaped by competitive gaps

## Related Concepts

- [MVP Phases](../roadmap/mvp-phases.md)
