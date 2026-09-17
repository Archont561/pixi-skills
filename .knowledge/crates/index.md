# Crates — Index

This section documents every Rust crate in the workspace. Each crate
has its own detail page covering purpose, public API, key types,
dependencies, and implementation notes.

## Start Here

- [Context](./CONTEXT.md) — Planned Rust crate boundaries, provider isolation, and shared responsibilities.
- [Bundle index](../index.md) — Browse all knowledge sections.

## Core Library

### [skills-core.md](./skills-core.md)
The provider-agnostic foundation. Defines `SkillRegistry` trait, `Skill`
data model, `skills.toml` / `skills-lock.toml` manifest parsing, agent
detection, and the skill installer.

## Provider Crates

### [skills-provider-github.md](./skills-provider-github.md)
Implements `SkillRegistry` for GitHub repositories. Compatible with the
existing skills.sh ecosystem — fetches skill folders (agentskills.io
spec) from GitHub repos.

### [skills-provider-conda.md](./skills-provider-conda.md)
Implements `SkillRegistry` for conda channels. Uses `rattler` crates
for repodata fetching, package streaming, and version resolution.
The first-class provider.

### [skills-provider-prefix.md](./skills-provider-prefix.md)
Implements `SkillRegistry` for prefix.dev channels. May leverage OCI
registry protocol. Enterprise and private channel support.

### [skills-provider-pypi.md](./skills-provider-pypi.md)
Implements `SkillRegistry` for PyPI packages. Future provider — lowest
priority in the MVP roadmap.

## Binaries

### [pixi-skills-cli.md](./pixi-skills-cli.md)
The `pixi-skills` CLI binary. Built with clap v4. Functions as a pixi
extension — when installed, `pixi skills <subcommand>` dispatches to
this binary. Documents all subcommands: `find`, `add`, `remove`, `list`,
`update`, `lock`, `doctor`.

### [xtask.md](./xtask.md)
The build automation crate. Never published. Subcommands: `cli-docs`,
`schema`, `completions`, `lint`, `release`, `dist`. Why these tasks
are Rust (not shell scripts) and how they integrate with pixi tasks.

## Related Sections

- [Architecture/dependency-graph](../architecture/dependency-graph.md) —
  visualizes how these crates depend on each other
- [Tooling](../tooling/index.md) — the tools used to build, test, and
  lint these crates

## Related Concepts

- [Workspace Layout](../architecture/workspace-layout.md)
