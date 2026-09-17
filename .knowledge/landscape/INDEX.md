---
title: "Landscape — Index"
section: landscape
kind: index
tags: [landscape, index, navigation, competition, ecosystem]
relates_to:
  - roadmap/mvp-phases
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Landscape — Index

This section maps the competitive landscape and ecosystem context for
pixi-skills. Understanding what already exists — and where it falls
short — informs our design choices and positioning.

## Pages

### [skills-sh.md](./skills-sh.md)
The incumbent: `skills.sh` / `npx skills`. GitHub-as-registry model,
no version pinning, no lockfile. How it works, what it does well
(instant ecosystem, zero infra), and where it breaks down (vendored
skills, no reproducibility, npm-only).

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

- [Roadmap](../roadmap/INDEX.md) — the MVP plan informed by this
  landscape analysis
- [Architecture/design-decisions](../architecture/design-decisions.md) —
  decisions shaped by competitive gaps
