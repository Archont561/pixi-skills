---
title: "Roadmap — Index"
section: roadmap
kind: index
tags: [roadmap, index, navigation, mvp, phases, milestones]
relates_to:
  - landscape/differentiation
  - crates/INDEX
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Roadmap — Index

This section documents the development roadmap for pixi-skills: what
gets built, in what order, and why.

## Pages

### [mvp-phases.md](./mvp-phases.md)
The six-phase MVP plan:
- **Phase 0**: `skills-core` — traits, models, agent detection, installer
- **Phase 1**: `skills-provider-github` — instant ecosystem access
- **Phase 2**: `pixi-skills` CLI — clap binary, pixi extension
- **Phase 3**: `skills-provider-conda` — first-class conda integration
- **Phase 4**: `skills-lock.toml` — the real differentiator
- **Phase 5**: Additional providers (PyPI, OCI, local paths)

Each phase includes: deliverables, definition of done, key risks,
and dependency on prior phases.

### [improvement-proposals.md](./improvement-proposals.md)
**2026-09 strategy review** (P0–P7): spec-native folder skills,
skills.sh-as-provider, semantic manifest/lock resolution, the
`skills audit` trust pipeline, authoring toolchain, agent-capability
graph, and sandboxed `skills try`. Mental models, graphs, and
pseudocode — sequenced against the MVP phases with MoSCoW priorities.

## Related Sections

- [Landscape/differentiation](../landscape/differentiation.md) —
  competitive analysis that informed phase ordering
- [Crates](../crates/INDEX.md) — the crates built in each phase
- [Architecture/design-decisions](../architecture/design-decisions.md) —
  decisions that affect roadmap sequencing
