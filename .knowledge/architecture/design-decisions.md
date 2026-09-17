---
title: "Design Decisions"
section: architecture
kind: detail
tags: [architecture, decisions, adr, trade-offs, rationale]
relates_to:
  - architecture/workspace-layout
  - architecture/three-layer-model
  - conventions/skill-format
  - conventions/naming
  - landscape/differentiation
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Design Decisions

Architecture Decision Records (ADRs) for key choices in the
pixi-skills project. Each decision documents the context, options
considered, choice made, and consequences.

---

## ADR-001: Lockfile Format — TOML

### Context
pixi-skills needs a lockfile to pin exact skill versions and hashes.
The lockfile must be human-readable (for code review), diffable (for
git), and parseable (for tooling).

### Options Considered

| Option | Pros | Cons |
|---|---|---|
| **JSON** (`skills-lock.json`) | Universal parser support. skills.sh uses this. | Noisy diffs (trailing commas, brackets). Not human-friendly for large files. |
| **TOML** (`skills-lock.toml`) | Idiomatic in the pixi/Rust ecosystem. Clean diffs. Human-readable. Comments allowed. | Less universal than JSON. Slightly more complex parser. |
| **Extend pixi.lock** | No additional file. Skills are just "packages." | pixi.lock is conda-specific. Not all skill sources are conda. Would couple skill management to conda. |
| **YAML** | Human-readable. Common in DevOps tooling. | Indentation-sensitive. Implicit typing gotchas. Not idiomatic in Rust ecosystem. |

### Decision
**TOML** (`skills-lock.toml`).

### Rationale
- pixi.toml, Cargo.toml, Cargo.lock (TOML-ish) — the ecosystem is
  TOML-native. Adding another TOML file is consistent.
- TOML supports comments, which lockfiles benefit from (e.g., noting
  why a version is pinned).
- Clean line-based diffs in git — each skill is a `[[skill]]` block.
- `toml` and `toml_edit` crates are already in our dependency tree.

### Consequences
- We need a TOML serializer that produces deterministic output (sorted
  keys, consistent formatting) to avoid noisy diffs.
- Tools outside the Rust ecosystem that want to read the lockfile need
  a TOML parser (available in every major language).

---

## ADR-002: Skill Packaging Convention for Conda

### Context
Skills published as conda packages need a discoverable naming convention
so `pixi skills find` can locate them in conda channels.

### Options Considered

| Option | Pros | Cons |
|---|---|---|
| **(a) `skill-*` prefix** | Simple, discoverable. `skill-playwright`, `skill-polars`. | Occupies namespace on conda-forge. Requires coordination. |
| **(b) Arbitrary packages with `skills/` dir** | Any package can contain skills. No naming constraint. | No discoverability. Can't search for "all skill packages." |
| **(c) Package metadata label** | Flexible. `about.tags: ["pixi-skill"]`. | Requires repodata parsing for discovery. Slower search. |

### Decision
**(a) `skill-*` naming convention** as the primary mechanism, with
**(c) metadata labels** as a secondary signal for discovery.

### Rationale
- Convention-based discovery is fast — filter repodata package names
  by prefix. No need to fetch and parse every package's metadata.
- The `skill-*` prefix is self-documenting — a user browsing
  conda-forge immediately knows what these packages are.
- Metadata labels serve as a fallback — a package that doesn't follow
  the naming convention can still be discovered if it has the right
  label.

### Consequences
- We need to document the `skill-*` convention clearly for skill
  authors.
- We should register the convention with conda-forge (issue/RFC) to
  prevent namespace squatting.
- The conda provider implements a two-pass search: name-prefix first,
  then metadata-label fallback.

---

## ADR-003: Agent Target Directories

### Context
Different AI agents store their skills/rules in different directories.
pixi-skills must know where to install skills for each agent.

### Known Agent Paths (as of mid-2025)

| Agent | Skills directory |
|---|---|
| Claude Code | `.claude/skills/` |
| Cursor | `.cursor/rules/` |
| GitHub Copilot | `.github/copilot/skills/` |
| Codex | `.codex/` |
| Windsurf | `.windsurf/rules/` |
| Cline | `.cline/rules/` |
| Aider | `.aider/` |

### Decision
**Configurable with sensible defaults.** Agent paths are defined in
a default configuration that ships with `skills-core`, but can be
overridden in `skills.toml`:

```toml
# skills.toml
[agents.claude]
path = ".claude/skills/"

[agents.cursor]
path = ".cursor/rules/"

# Custom agent
[agents.my-agent]
path = ".my-agent/prompts/"
```

### Rationale
- Agent config paths change frequently (new agents, new versions).
  Hardcoding would require a pixi-skills release for every agent
  update.
- The default set covers all known agents. Users only need to
  configure if they use a custom or very new agent.
- Agent detection (`skills-core::agent`) probes the filesystem for
  known paths and reports which agents are present.

### Consequences
- `skills-core` ships a `default_agents.toml` or equivalent
  compiled-in configuration.
- The `pixi skills doctor` command reports detected agents and their
  configured paths.
- New agents can be supported without code changes — just config.

---

## ADR-004: Version Resolution Strategy

### Context
Skills can come from different providers, each with its own versioning
scheme. We need a unified version resolution strategy.

### Options Considered

| Provider | Native versioning |
|---|---|
| GitHub | Git refs (branches, tags, commits) |
| conda | conda version spec (PEP 440-ish) |
| prefix.dev | Same as conda |
| PyPI | PEP 440 (semver-ish) |

### Decision
**Provider-native versions with semver as the common language.**

- Each provider uses its native versioning scheme internally.
- `skills-core` defines a `VersionReq` enum that can represent:
  - Semver range (`^1.0`, `~1.2`, `>=1.0,<2.0`)
  - Exact version (`=1.2.3`)
  - Git ref (`branch:main`, `tag:v1.0.0`, `commit:abc123`)
  - Latest (`*`)
- The lockfile records the resolved exact version in the provider's
  native format plus a content hash.

### Rationale
- Forcing semver on all providers would lose information (conda
  versions have epochs, PyPI has post-releases).
- Git refs are not versions at all — they're references. Forcing them
  into semver would be lossy and confusing.
- The lockfile resolves all ambiguity — once locked, the exact version
  is recorded regardless of the constraint format.

### Consequences
- `VersionReq` is a tagged enum, not a simple string. Each variant
  has provider-specific parsing.
- The `pixi skills update` command must understand each variant to
  determine "is there a newer version?"
- Display formatting differs per variant: `^1.0` for semver,
  `main` for git branch, `1.2.3-hdeadbeef_0` for conda.

---

## ADR-005: Biome Over ESLint + Prettier

### Context
The docs app contains TypeScript and Astro files that need linting
and formatting.

### Decision
**Biome** replaces both ESLint and Prettier.

### Rationale
- Biome is a single binary that handles both linting and formatting.
  One tool, one config file, one invocation.
- Biome is written in Rust — consistent with our "prefer Rust tools"
  principle.
- Biome is available on conda-forge — pixi provisions it alongside
  other tools. No `bun add --dev @biomejs/biome` needed.
- Biome is significantly faster than ESLint + Prettier (no Node.js
  startup, no plugin resolution).
- Biome's monorepo support (config inheritance via `extends`) works
  well with our workspace layout.

### Consequences
- Some ESLint rules have no Biome equivalent. We accept this trade-off
  — Biome covers 500+ rules, which is sufficient.
- Astro `.astro` file support in Biome may be limited. We lint the
  `<script>` and `<style>` portions; template HTML is not linted by
  Biome.
- No Prettier plugins (e.g., Astro Prettier plugin). Formatting of
  Astro template syntax relies on Astro's own formatter via
  `astro check`.

---

## ADR-006: xtask Over Shell Scripts

### Context
The project needs build automation for codegen, release management,
and workspace linting.

### Decision
**cargo xtask** (a Rust crate with `publish = false`).

### Rationale
See [three-layer-model.md](./three-layer-model.md) for the full
argument. Summary:
- Shell scripts don't have access to Rust types.
- Shell scripts aren't cross-platform.
- Shell scripts aren't testable.
- xtask is compiled Rust — same language, same toolchain, same CI.

### Consequences
- First-time `cargo xtask` invocation compiles the xtask crate (~5s).
  Subsequent runs are instant.
- xtask depends on `pixi-skills` as a library. Changes to the CLI
  struct trigger xtask recompilation. This is intentional — it ensures
  codegen stays in sync.
- Contributors must know Rust to modify build automation. This is
  acceptable — the project is a Rust project.

---

## ADR-007: pixi Extension Model (Not Plugin)

### Context
pixi-skills needs to integrate with pixi so users can type
`pixi skills <subcommand>`.

### Decision
**pixi extension** (standalone binary named `pixi-skills`), not a
compiled pixi plugin.

### Rationale
- pixi extensions are simply executables that follow the naming
  convention `pixi-{name}`. When you run `pixi {name}`, pixi
  discovers and executes the binary. Zero coupling to pixi internals.
- No need to link against pixi's Rust API or match its Rust version.
- The extension can be installed via `pixi global install pixi-skills`
  or via conda channel.
- Extensions can be developed and released independently of pixi's
  release cycle.

### Consequences
- The CLI cannot access pixi's internal state (e.g., resolved
  environments) directly. It must read `pixi.toml` / `pixi.lock`
  from disk if needed.
- The CLI is a standalone binary — it works without pixi installed
  (users can run `pixi-skills` directly, though the pixi integration
  is the intended UX).

---

## Decision Log (Summary)

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Lockfile format: TOML | Accepted |
| ADR-002 | Conda skill naming: `skill-*` prefix | Accepted |
| ADR-003 | Agent paths: configurable with defaults | Accepted |
| ADR-004 | Version resolution: provider-native + semver common language | Accepted |
| ADR-005 | Biome over ESLint + Prettier | Accepted |
| ADR-006 | xtask over shell scripts | Accepted |
| ADR-007 | pixi extension model | Accepted |
