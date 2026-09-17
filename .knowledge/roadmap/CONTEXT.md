---
type: Overview
title: "Roadmap — Context"
description: "Roadmap principles, phase dependencies, and success criteria for the proposed product."
section: roadmap
kind: context
tags: [roadmap, context, strategy, mvp, phasing, priorities]
status: stable
created: "2025-01-01"
updated: "2025-01-01"
---

# Roadmap — Context

## What This Section Covers

The development plan for pixi-skills, from initial prototype to
feature-complete tool. The roadmap is informed by the competitive
landscape analysis and optimized for fastest path to a usable product.

## Roadmap Philosophy

### 1. Ship usability before purity
Phase 1 implements `skills-provider-github` — compatibility with the
existing skills.sh ecosystem. This gives pixi-skills immediate access
to every skill already published on GitHub, even though GitHub is not
the "ideal" provider (conda is). Instant ecosystem > architectural
purity.

### 2. The lockfile is the moat
Phase 4 (`skills-lock.toml`) is the real differentiator. No existing
tool has a lockfile for skills. Once users depend on reproducible skill
installation, switching costs are high. This must ship before we
invest in polish or additional providers.

### 3. Core library first, CLI second
Phase 0 builds `skills-core` as a library before any CLI exists. This
ensures the API is clean and testable independent of CLI concerns. The
CLI (Phase 2) is a thin wrapper over the library.

### 4. One provider at a time
Each provider crate is a phase. This keeps each phase small, shippable,
and testable. It also lets us validate the `SkillRegistry` trait design
with GitHub (simple) before tackling conda (complex, rattler integration).

## Phase Dependencies

```
Phase 0 (skills-core)
    │
    ├──→ Phase 1 (provider-github)
    │         │
    │         └──→ Phase 2 (CLI)
    │                  │
    │                  ├──→ Phase 3 (provider-conda)
    │                  │
    │                  └──→ Phase 4 (lockfile)
    │                            │
    │                            └──→ Phase 5 (more providers)
    │
    └──→ Phase 3 can also start after Phase 0 if the trait is stable
```

Phases 3 and 4 can be developed in parallel once the CLI exists.
Phase 5 is open-ended — new providers can be added indefinitely.

## Success Metrics

| Phase | Success = |
|---|---|
| Phase 0 | `skills-core` compiles, trait is defined, unit tests pass |
| Phase 1 | Can fetch any skill from a skills.sh-compatible GitHub repo |
| Phase 2 | `pixi skills add <github-url>` works end-to-end |
| Phase 3 | Can install a skill from a conda channel |
| Phase 4 | `pixi skills lock` generates reproducible lockfile |
| Phase 5 | At least one additional provider works (PyPI or prefix.dev) |

## Timeline Expectations

This is an open-source side project. No fixed deadlines. Phases are
ordered by priority, not by calendar. The roadmap is a sequencing plan,
not a schedule.

## Related Concepts

- [MVP Phases](./mvp-phases.md)
- [Differentiation](../landscape/differentiation.md)
- [skills.sh](../landscape/skills-sh.md)
