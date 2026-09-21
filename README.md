# pixi-skills

Design and knowledge for a provider-agnostic, reproducible skills manager
for AI coding agents — and, since Phase 0, the workspace that tooling will
grow into.

| Layer | State |
|---|---|
| [Knowledge bundle](#knowledge-bundle) | Design, ADRs, roadmap, ecosystem research — complete and maintained |
| Rust workspace | **Phase 0 scaffold**: seven crates compile, one placeholder test runs, CI is green. The real model lands with [Phase 0](.knowledge/roadmap/mvp-phases.md) |
| pixi workspace | Live: `pixi.toml` + `pixi.lock` for `linux-64`, `osx-arm64`, `win-64` |
| Docs site (`apps/pixi-skills-docs`) | Planned with Phase 4; its CI gates are guarded until it exists |

## Quickstart

```sh
pixi run -e dev build        # cargo build --workspace
pixi run -e dev test         # cargo nextest run --workspace
pixi run -e dev lint         # fmt · clippy · cargo-deny · actionlint · taplo
```

Every command CI runs is one of these tasks, so the authoritative list is
`[tasks]` in [`pixi.toml`](pixi.toml) and the CI job is twelve lines of
`pixi run -e dev <task>`. See [Pixi Tasks](.knowledge/pixi/tasks.md).

The crate layout is `skills-core` (model, traits, installer) plus four
provider crates and the `pixi-skills` CLI; the CLI is also a pixi extension,
so `pixi skills …` is the intended entry point. Design:
[Crates](.knowledge/crates/index.md),
[Dependency graph](.knowledge/architecture/dependency-graph.md).

## Knowledge bundle

Start at **[.knowledge/index.md](.knowledge/index.md)**. The directory is an
[Open Knowledge Format (OKF) v0.2](.knowledge/conventions/knowledge-format.md)
Knowledge Bundle: linked Markdown concepts with YAML frontmatter,
progressive-disclosure indexes, and an [update log](.knowledge/log.md).

- [Project context](.knowledge/CONTEXT.md)
- [Architecture](.knowledge/architecture/index.md)
- [Roadmap](.knowledge/roadmap/index.md)
- [Authoring rules and migration audit](.knowledge/conventions/knowledge-format.md)

The bundle is prose and frontmatter only — there is no Python validator in
this repository any more, so nothing needs installing to read or edit it.
Changes are reviewed like any other Markdown; the [update log](.knowledge/log.md)
is the place to record substantive ones.

## Continuous integration

| Path | Role |
|---|---|
| `.github/workflows/ci.yml` | Single entry point: `fmt-check` → `lint-rust` → `deny` → `lint-actions` → `lint-toml` → (`lint-docs`) → `test` → `test-doc` → `coverage` → (`docs-build`) |
| `.github/workflows/publish-sandbox.yml` | After `ci` is green on `main`: packs the pixi environments into an orphan branch |
| `.pixi-sandbox.toml` | Reviewed publish plan: which environments become which sandbox branch |
| `.github/dependabot.yml` | Keeps the SHA-pinned actions and the Cargo workspace current |
| `scripts/restore.sh` | Airlock one-liner: fetch → verify → restore → wire PATH |

### Sandbox (airlock) branches

`.pixi-sandbox.toml` declares one bundle — `developer`, holding the `dev` and
`docs` pixi environments for `linux-64` — so a green `main` publishes
`sandbox/developer-linux-64`. Restore it on a machine with no network:

```sh
bash scripts/restore.sh                       # defaults to sandbox/developer-linux-64
bash scripts/restore.sh sandbox/developer-linux-64 ./airlock
```

`publish-sandbox.yml` consumes the sha256-verified `pixi-sandbox` v0.2.0
release binary and the pinned composite actions from
[Archont561/pixi-sandbox](https://github.com/Archont561/pixi-sandbox); it does
not call that repository's *reusable* workflow, whose job graph cannot see a
`pixi.toml` checked out into a subdirectory. Background and measured payload
sizes: [pixi-sandbox](.knowledge/landscape/pixi-sandbox.md),
[GitHub Actions](.knowledge/cicd/github-actions.md).
