# Pixi — Index

This section documents the `pixi.toml` configuration — the single file
that defines all environments, dependencies, and tasks for the entire
monorepo.

## Start Here

- [Context](./CONTEXT.md) — Role of pixi in the planned workspace, dependency provisioning, and task orchestration.
- [Bundle index](../index.md) — Browse all knowledge sections.

## Pages

### [environments.md](./environments.md)
The four pixi environments (`default`, `docs`, `release`, `all`): what
each contains, when to use which, and how they map to development
workflows and CI jobs.

### [tasks.md](./tasks.md)
The full task catalog. Every `pixi run` command, its underlying command,
`depends-on` chains, `cwd` overrides, and which environment it belongs
to. The canonical reference for "how do I do X in this repo?"

### [features.md](./features.md)
Pixi features (`rust`, `lint`, `docs`, `release`, `all`) and how they
compose into environments. The mapping from feature → dependencies →
tasks.

### [conda-forge-packages.md](./conda-forge-packages.md)
Every conda-forge package we depend on and why. Rust, bun, biome, taplo,
cargo-deny, cargo-nextest, and supporting libraries (openssl, pkg-config,
cmake). Version constraints and pinning strategy.

## Related Sections

- [Architecture/three-layer-model](../architecture/three-layer-model.md) —
  pixi is the top layer of this model
- [Tooling](../tooling/index.md) — the tools pixi provisions and
  orchestrates
- [CI/CD](../cicd/index.md) — CI runs everything through pixi
