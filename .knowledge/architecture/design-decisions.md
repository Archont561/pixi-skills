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
  - landscape/agent-skills-standard
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Design Decisions

Architecture Decision Records (ADRs) for key choices in the
pixi-skills project. Each decision documents the context, options
considered, choice made, and consequences.

> ## 📋 Decision Review — 2026-09 (agentskills.io adoption)
>
> The publication of the Agent Skills open standard (2025-12-18, see
> [`landscape/agent-skills-standard.md`](../landscape/agent-skills-standard.md))
> triggered a full review of every standing ADR:
>
> | ADR | Subject | Verdict (2026-09-17) |
> |---|---|---|
> | ADR-001 | Lockfile format: TOML | ✅ **Re-affirmed** — lockfile is manager-owned; spec doesn't govern it |
> | ADR-002 | Conda `skill-*` prefix | 🔄 **Amended** — package payload is now a skill *folder*, not a single `.md` |
> | ADR-003 | Configurable agent paths | ✅ **Validated** — 70+ agents proved configurability right; default map is now data-driven |
> | ADR-004 | Provider-native versions | 🔄 **Amended** — content hash is now a *tree* hash; semver-parsable Git tags unlock ranges on GitHub |
> | ADR-005 | Biome | ✅ Unaffected (see tooling notes: Biome ≥2.3 covers `.astro`) |
> | ADR-006 | xtask | ✅ Unaffected |
> | ADR-007 | pixi extension | ✅ Unaffected |
> | *(not an ADR)* | TOML frontmatter inside SKILL.md | ❌ **Superseded by ADR-008** — was never an ADR, lived only in conventions/skill-format.md |
> | **ADR-008** | Adopt agentskills.io as the artifact format | 🆕 **Accepted 2026-09-17** |
>
> Rule going forward: **the skill artifact is owned by the standard;
> the manager envelope is owned by us.** Any future decision that
> changes bytes inside `SKILL.md` requires exceptional justification.

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

> **Amended 2026-09-17 (ADR-008):** the package payload convention
> changed with the standard adoption. Originally `skills/<name>.md`
> (single file); now `skills/<name>/` — a **folder** containing
> `SKILL.md` plus optional `scripts/`, `references/`, `assets/`,
> `agents/` per the agentskills.io spec, and our companion
> `skill.toml` (manager metadata). noarch remains correct —
> folders of markdown/scripts are platform-independent.

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

### Known Agent Paths (updated 2026-09-17)

The agentskills.io standard (2025-12-18) converged most major agents
onto native SKILL.md directories:

| Agent | Skills directory |
|---|---|
| Claude Code | `.claude/skills/` |
| OpenAI Codex | `.agents/skills/` (or `.codex/skills/`) |
| GitHub Copilot | `.github/skills/` (was `.github/copilot/skills/` pre-standard) |
| Cursor | `.cursor/skills/` (was `.cursor/rules/` + `.mdc` pre-standard) |
| Gemini CLI | `.gemini/skills/` |
| Windsurf | `.windsurf/rules/` |
| Cline | `.cline/rules/` |
| Aider | `.aider/` |
| …70+ total | the vercel-labs/skills CLI maintains the fullest public map; ours must be data-driven (see below) |

> **2026 note:** the count went from ~7 known agents to 70+. This
> *validates* the configurability decision below — and pushes it
> further: ship the default map as a data file (`default_agents.toml`)
> that `pixi skills` can self-update (`agents --update`) without a
> CLI release. Also: per-agent **format transforms are nearly dead** —
> native SKILL.md support means install = copy folder. (Former table
> kept in git history.)

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

> **Amended 2026-09-17 (ADR-008):** two refinements:
> 1. **Semver-parsable Git tags unlock ranges.** The skills.sh-era
>    ecosystem (vercel-labs/agent-skills, anthropics/skills) uses
>    release tags. When a tag matches `[v]X.Y.Z`, the GitHub provider
>    exposes it as a semver version, so `ref = "^1.4"` ranges work on
>    GitHub — not just exact pins. Non-semver tags/branches remain
>    exact-pin or floating-with-warning.
> 2. **Content hash is a canonical tree hash** (folder → sorted-path
>    SHA-256), not a file hash. See ADR-008 consequences.

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

## ADR-008: Adopt agentskills.io as the Skill Artifact Format

**Status**: Accepted (2026-09-17) — supersedes the TOML-frontmatter
format previously documented in `conventions/skill-format.md`.

### Context

Until 2026, "a skill" had no cross-vendor definition. We designed our
own: a single `SKILL.md` file with optional **TOML** frontmatter.
On 2025-12-18 Anthropic published **Agent Skills as an open standard**
(agentskills.io); within months 26+ platforms (Claude, Codex, Copilot,
Cursor, Gemini CLI, VS Code, …) adopted it, and the skills.sh
ecosystem (83k+ skills) writes to it. The standard's format differs
from ours on the three fundamentals: **unit** (folder, not file),
**frontmatter** (YAML, not TOML), and **context model** (progressive
disclosure budgets).

Staying on a private format would make every ecosystem skill
unreadable-or-lossy for us, and every skill we produce second-class
for 26+ agents.

### Options Considered

| Option | Pros | Cons |
|---|---|---|
| **(a) Keep TOML-frontmatter SKILL.md** | No rework; parser uniformity | Non-compliant: ecosystem skills unreadable, our skills invisible to standard agents. Existential. |
| **(b) Pure spec, drop our metadata** | Zero extension surface | Loses semver `version`, dependency edges, author table — the manager features that justify existing |
| **(c) Spec YAML + namespaced `metadata:` in frontmatter** | Single file | Risk of collision with future spec fields; some agent linters reject unknown keys; bloats Tier-1 token budget |
| **(d) Spec YAML frontmatter + companion `skill.toml` in the folder** | Spec-pure SKILL.md; keeps TOML parser reuse (ADR-001 spirit); managers ignore artifacts safely, agents ignore sidecars safely; mirrors `Cargo.toml`-next-to-`src/` pattern | Two files to author (mitigated: `pixi skills init` scaffolds both) |

### Decision

**(d) — Full agentskills.io adoption with a companion envelope:**

1. **Unit of management = the skill folder** (`SKILL.md` + optional
   `scripts/` `references/` `assets/` `agents/`).
2. **SKILL.md frontmatter is YAML**, containing *only* spec fields
   (`name`, `description` required; `license`, `compatibility`,
   `allowed-tools`, `metadata` optional). Unknown fields are
   preserved on copy, never required.
3. **Manager metadata lives in `skill.toml`** alongside SKILL.md:
   semver `version`, author table, dependency edges
   (`depends_on`/`conflicts_with`), agent hints. Everything
   install-critical stays derivable without it (a missing
   `skill.toml` must never make a skill uninstallable).
   *(Normative schema specified 2026-09-17 in
   [`conventions/skill-toml.md`](../conventions/skill-toml.md) —
   v1, open schema with a formal evolution policy.)*
4. **Integrity = canonical tree hash** over the folder: sort by
   relative path, SHA-256 of `path‖mode‖size‖bytes` per file.
   Deterministic across platforms (LF normalization, exec-bit aware
   on unix, fixed mode on Windows).
5. **Install = copy the folder tree** into each agent's skills dir.
   No format transforms. `skill.toml` is NOT copied (manager-only);
   `agents/*.yaml` pass through untouched.
6. **Legacy reading is supported, never emitted**: bare-markdown
   SKILL.md (no frontmatter) and pre-standard single-file skills are
   read as folder-shaped bundles of one file, hash included. New
   skills (`pixi skills init`) are always spec folders.

### Consequences

- `skills-core`: `Skill.content: String` → `SkillBundle` (file map);
  frontmatter parser swaps TOML→YAML (`serde_yaml`); companion
  `skill.toml` parser added; tree hash replaces file hash.
- Providers fetch folders: GitHub via Trees-API/tarball; conda
  package layout `skills/<name>/...`; PyPI wheels `skills/<name>/...`.
- Agent transforms are dead codepaths by default (kept only as
  config-gated legacy overrides — see ADR-003).
- `conventions/skill-format.md` rewritten as the adopted spec.
- Quality budgets from the spec (≤~5k tokens body, ≤~500 lines per
  dir) become machine-checkable lint rules (proposal P5).
- The `.convco`/`skill-format` knowledge in older docs may reference
  the TOML design — superseded passages are marked inline.

---

## Decision Log (Summary)

| ADR | Decision | Status |
|---|---|---|
| ADR-001 | Lockfile format: TOML | Accepted (re-affirmed 2026-09) |
| ADR-002 | Conda skill naming: `skill-*` prefix | Accepted, **amended 2026-09** (folder payload) |
| ADR-003 | Agent paths: configurable with defaults | Accepted, **validated 2026-09** (data-driven map) |
| ADR-004 | Version resolution: provider-native + semver common language | Accepted, **amended 2026-09** (semver tags, tree hash) |
| ADR-005 | Biome over ESLint + Prettier | Accepted (Biome ≥2.3) |
| ADR-006 | xtask over shell scripts | Accepted |
| ADR-007 | pixi extension model | Accepted |
| — | TOML frontmatter in SKILL.md | **Superseded by ADR-008** (2026-09) |
| ADR-008 | Adopt agentskills.io format (folder unit, YAML frontmatter, companion `skill.toml`, tree hash) | **Accepted 2026-09-17** |
