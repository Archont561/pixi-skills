---
okf_version: "0.2"
---

# pixi-skills — Knowledge Bundle

An Open Knowledge Format (OKF) v0.2 bundle describing the design,
architecture, tooling, and conventions of `pixi-skills`, for AI coding
agents, contributors, and maintainers.

> **Scope:** this repository currently contains the knowledge bundle and
> its validation tooling. The Rust workspace, CLI, docs application, and
> pixi tasks described here are design targets, not an implementation
> included in this checkout. Format validation does not verify product
> claims or third-party version information.

## Start Here

- [Project Context](./CONTEXT.md) — Mission, scope, and intended technology stack of the pixi-skills design.
- [Knowledge Format](./conventions/knowledge-format.md) — OKF v0.2 authoring rules, local extensions, validation, and migration notes for this bundle.
- [Update Log](./log.md) — Chronological history of bundle maintenance.

Each section has an `index.md` for navigation and a `CONTEXT.md` concept
for framing. Detail concepts contain the actual design and reference
material. Follow Markdown links to explore related concepts.

## Sections

- [Architecture](./architecture/index.md) — Workspace layout, the three-layer task model (pixi → xtask/Bun → toolchains), dependency graphs, and design decisions.
- [Crates](./crates/index.md) — Designs for `skills-core`, provider crates, the `pixi-skills` CLI, and `xtask` automation.
- [Docs App](./docs-app/index.md) — The planned Astro Starlight site, content structure, custom components, and Bun integration.
- [Tooling](./tooling/index.md) — Biome, Taplo, cargo-deny, cargo-nextest, convco, rustfmt, and clippy configuration and workflows.
- [Pixi](./pixi/index.md) — Planned environments, features, dependencies, and task orchestration in `pixi.toml`.
- [CI/CD](./cicd/index.md) — Planned GitHub Actions integration, releases, cross-compilation, and distribution artifacts.
- [Landscape](./landscape/index.md) — Agent Skills, skills.sh, npm-skills, the pixi ecosystem, and product differentiation.
- [Conventions](./conventions/index.md) — Commit and naming conventions, configuration locations, Agent Skills folders, `skill.toml`, and this bundle's OKF profile.
- [Roadmap](./roadmap/index.md) — MVP phases, milestones, product proposals, and priority ordering.

## Quick Navigation by Role

**Writing Rust code?** Start with [Crates Context](./crates/CONTEXT.md),
then the [Dependency Graph](./architecture/dependency-graph.md).

**Working on the docs site?** Start with [Docs App Context](./docs-app/CONTEXT.md),
then [Content Structure](./docs-app/content-structure.md).

**Setting up tooling or CI?** Start with [Pixi Context](./pixi/CONTEXT.md),
then [Tooling Context](./tooling/CONTEXT.md).

**Planning a release?** Read the [Release Workflow](./cicd/release-workflow.md)
and [Commit Conventions](./conventions/commit-conventions.md).

**Evaluating the project?** Read [Differentiation](./landscape/differentiation.md)
and the [MVP Phases](./roadmap/mvp-phases.md).

**Maintaining this bundle?** Read [Knowledge Format](./conventions/knowledge-format.md).

## Document Roles

| File or field | Role |
|---|---|
| `index.md` | Reserved directory listing, not a concept; only the root may declare `okf_version` |
| `log.md` | Reserved date-grouped update history, not a concept |
| `CONTEXT.md` | Ordinary concept with `type: Overview`, giving scope and principles |
| Other `.md` files | Concepts with YAML frontmatter and a descriptive `type` |
| `kind`, `section`, `created`, `updated` | Preserved local extensions, not OKF trust or provenance fields |
