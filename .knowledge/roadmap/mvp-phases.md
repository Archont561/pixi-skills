---
type: Roadmap
title: "MVP Phases"
description: "MVP phases, deliverables, completion criteria, risks, and dependencies."
section: roadmap
kind: detail
tags: [roadmap, mvp, phases, milestones, priorities, deliverables]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# MVP Phases

The six-phase development plan for pixi-skills. Each phase is a
shippable increment with clear deliverables, definition of done,
and dependency on prior phases.

---

## Phase Overview

```
Phase 0 ──→ Phase 1 ──→ Phase 2 ──┬──→ Phase 3
  (core)     (github)    (CLI)     │     (conda)
                                   │
                                   └──→ Phase 4
                                         (lockfile)
                                           │
                                           └──→ Phase 5
                                                 (more providers)
```

---

## Phase 0: `skills-core` Foundation

### Goal
Build the core library with all shared types, traits, and logic.
No providers, no CLI — just the library.

### Deliverables

- [ ] `Skill`, `SkillId`, `SkillSummary`, `SkillSource` types
- [ ] `SkillVersion`, `VersionReq`, `TreeHash` types
- [ ] **`SkillBundle` folder model** (BTreeMap file tree) + canonical
  tree-hash computation *(ADR-008, adopted 2026-09)*
- [ ] **`SkillMetadata` = YAML frontmatter parser** (spec fields,
  unknown preserved) + **companion `skill.toml` envelope parser**
- [ ] `SkillRegistry` trait definition (returns bundles, not files)
- [ ] `SkillsManifest` (skills.toml) parser — incl. `skill=` selector
  and semver-range refs
- [ ] `SkillsLockfile` (skills-lock.toml) parser — format v2 (tree_hash)
- [ ] `SkillInstaller` — install/uninstall skill **folders** to agent
  directories (exclude `skill.toml`, pass `agents/*.yaml` through)
- [ ] `AgentDetector` — detect installed agents; post-standard paths
  (`.agents/skills/`, `.github/skills/`, ...) via data-driven
  `default_agents.toml`
- [ ] `Config` — layered configuration loading
- [ ] `SkillsError` — error type hierarchy (YAML + bundle variants)
- [ ] Unit tests for all types and parsing
- [ ] Integration tests with fixture directories (folder bundles)
- [ ] Crate documentation (`///` doc comments)

### Definition of Done

- `cargo test -p skills-core` passes
- `cargo doc -p skills-core` generates clean documentation
- `SkillRegistry` trait compiles and can be implemented by downstream crates
- Fixture-based tests cover valid and invalid manifests

### Key Risks

- **Trait design**: `SkillRegistry` must be general enough for all
  providers. Risk of redesign when the second provider is implemented.
  Mitigation: implement a mock provider in tests. *(2026-09: risk
  partially retired — trait v2 bundle/hash surface now designed in
  `roadmap/improvement-proposals.md` P4 and ADR-008 consequences.)*
- **Agent path churn**: agent config directories change frequently.
  Mitigation: paths configurable + data-driven map
  (`default_agents.toml`, self-updatable). *Validated 2026-09: the
  standard converged paths, but the 70+ agent long tail keeps this
  risk alive.*

### Dependencies

None — this is the starting point.

### Estimated Effort

Medium. The types are well-defined from the design phase. The trait
interface may require iteration.

---

## Phase 1: `skills-provider-github`

### Goal
Implement the GitHub provider for instant access to the existing
skills.sh ecosystem.

### Deliverables

- [ ] `GitHubRegistry` implementing `SkillRegistry`
- [ ] Ref resolution (branch → SHA, tag → SHA, **semver range → tag**)
- [ ] **Folder tree fetching** (Git Trees API recursive, or codeload
  tarball subtree) for the skill folder
- [ ] `@skill` multi-skill repo selector (`skills/<name>/` probing)
- [ ] SKILL.md **YAML frontmatter** parsing (spec fields)
- [ ] Canonical **tree hash** computation
- [ ] Search via **skills.sh public index (ADR-009, normative)** —
  graceful degradation to GitHub code/topic search on index outage
- [ ] Rate limit handling (with/without `GITHUB_TOKEN`)
- [ ] Local caching keyed by commit SHA + skill path
- [ ] Unit tests with mocked API responses
- [ ] Integration test with a real public skill repo (gated)
- [ ] Compatibility test with 3+ skills.sh-era spec repos
  (e.g. vercel-labs/agent-skills, anthropics/skills) covering
  folder skills incl. `scripts/`/`references/`

### Definition of Done

- Can fetch any skill **folder** from a public GitHub repo
- Can resolve tags and branches to commit SHAs; semver ranges resolve
  over `[v]X.Y.Z` tags
- Works with and without `GITHUB_TOKEN`
- Handles rate limiting gracefully
- Passes compatibility tests with skills.sh ecosystem repos (ADR-008)
- **Index outage degrades search gracefully — `add`/`lock`/`install`
  never depend on the skills.sh index (ADR-009)**

### Key Risks

- **GitHub API rate limits**: 60 req/hour unauthenticated.
  Mitigation: encourage `GITHUB_TOKEN`, implement caching.
- **API changes**: GitHub may change API responses.
  Mitigation: test with mocked AND live responses.

### Dependencies

Phase 0 (skills-core) must be complete.

### Estimated Effort

Small-Medium. GitHub API is well-documented. Main complexity is
rate limiting and caching.

---

## Phase 2: `pixi-skills` CLI

### Goal
Build the CLI binary that wires together the core library and
provider(s) into a usable tool.

### Deliverables

- [ ] `pixi-skills` binary crate with clap v4
- [ ] `find` subcommand — search across providers
- [ ] `add` subcommand — add a skill to the project
- [ ] `remove` subcommand — remove a skill
- [ ] `list` subcommand — list installed skills
- [ ] `doctor` subcommand — diagnose issues
- [ ] `--json` output for all subcommands
- [ ] Progress indicators (indicatif)
- [ ] Colored output (console)
- [ ] `--verbose` / `--quiet` flags
- [ ] pixi extension naming (`pixi-skills` binary name)
- [ ] `build_command()` export for xtask introspection
- [ ] End-to-end test: `pixi skills add github:user/repo`

### Definition of Done

- `pixi skills add github:user/repo` installs a skill into detected
  agent directories
- `pixi skills list` shows installed skills
- `pixi skills find <query>` returns search results
- `pixi skills doctor` reports agent detection and connectivity
- `pixi skills --help` shows all subcommands with descriptions
- Works as a standalone binary AND as a pixi extension

### Key Risks

- **UX design**: CLI UX is hard to change after release. Risk of
  regret on subcommand naming/flags.
  Mitigation: study cargo, pixi, skills.sh CLI patterns.
- **Error messages**: unhelpful errors ruin user experience.
  Mitigation: invest in error message quality (context, suggestions).

### Dependencies

Phase 0 + Phase 1 (at least one provider to be useful).

### Estimated Effort

Medium. clap scaffolding is fast. UX polish takes time.

---

## Phase 3: `skills-provider-conda`

### Goal
Implement the conda provider — the first-class provider that
delivers pixi-skills' key differentiators.

### Deliverables

- [ ] `CondaRegistry` implementing `SkillRegistry`
- [ ] Repodata fetching via `rattler_repodata_gateway`
- [ ] Package name filtering (`skill-*` prefix)
- [ ] Version resolution via `MatchSpec`
- [ ] Package download and extraction via `rattler_package_streaming`
- [ ] Skill **folder** extraction (`skills/<name>/**`) from package
  archives *(ADR-002 amended: folder payload)*
- [ ] Private channel support via `rattler_networking`
- [ ] Search across multiple channels
- [ ] Unit tests with fixture repodata and `.conda` packages
- [ ] Integration test with conda-forge (gated)
- [ ] Document the `skill-*` package format for authors
  (folder tree + `skill.toml` envelope conventions)
- [ ] Create one example skill package with rattler-build — a
  spec-compliant folder skill incl. `scripts/` + `references/` *(ADR-008)*

### Definition of Done

- Can install a `skill-*` package from conda-forge
- Can install from private channels with authentication
- Version constraints work (`^1.0`, `>=2,<3`)
- Search returns results filtered by `skill-*` prefix
- Example skill package builds with rattler-build

### Key Risks

- **rattler API stability**: rattler crates may change.
  Mitigation: pin rattler versions, test in CI.
- **Package format**: the `skill-*` convention needs ecosystem buy-in.
  Mitigation: publish a few example packages, document the format.

### Dependencies

Phase 0 (skills-core). Can start in parallel with Phase 2 if the
SkillRegistry trait is stable.

### Estimated Effort

Large. rattler integration is substantial. Understanding the conda
package format and repodata schema requires investment.

---

## Phase 4: Lockfile (`skills-lock.toml`)

### Goal
Implement the lockfile — the core differentiator. `pixi skills lock`
resolves all skills to exact versions with content hashes.

### Deliverables

- [ ] `lock` subcommand — generate/update `skills-lock.toml` (format v2)
- [ ] `update` subcommand — update skills to latest matching versions
- [ ] `check` subcommand — report available updates without applying
  (skills.sh parity; = dry-run solve)
- [ ] Lockfile generation from `skills.toml` manifest
- [ ] **Tree hash** verification on install
- [ ] Stale lockfile detection (`doctor` enhancement)
- [ ] Lockfile diff-friendly output (deterministic TOML serialization)
- [ ] `--frozen` flag — fail if lockfile doesn't exist or is stale
- [ ] Integration test: lock → install → modify → detect stale

### Definition of Done

- `pixi skills lock` produces a deterministic `skills-lock.toml`
- `pixi skills add` updates the lockfile
- `pixi skills update` resolves to newer versions within constraints
- `pixi skills doctor` detects stale lockfiles, tree-hash mismatches,
  AND pre-standard legacy installs (offers migration)
- Two fresh clones with the same lockfile produce identical skill
  installations (byte-identical folder trees)

### Key Risks

- **Deterministic serialization**: TOML output must be identical
  across runs and platforms. Non-deterministic output → noisy diffs.
  Mitigation: use `toml_edit` with explicit key ordering.
- **Multi-provider resolution**: resolving skills from different
  providers in a single lockfile is novel. Edge cases likely.
  Mitigation: extensive integration tests.

### Dependencies

Phase 2 (CLI) + at least one provider. Phase 3 (conda) is desirable
but not required — lockfile works with GitHub provider too.

### Estimated Effort

Medium. The lockfile model is well-designed from the planning phase.
Deterministic serialization and multi-provider edge cases are the
main challenges.

---

## Phase 5: Additional Providers

### Goal
Add more providers and polish the ecosystem.

### Deliverables (pick as needed)

- [ ] `skills-provider-prefix` — prefix.dev REST API, org-scoped
  discovery
- [ ] `skills-provider-pypi` — PyPI JSON API, wheel extraction
- [ ] Local filesystem provider — `source = "local"`, path reference
- [ ] OCI registry provider — pull skills from container registries

### Definition of Done

Per-provider: implements `SkillRegistry`, passes integration tests,
documented in docs site.

### Key Risks

- **Scope creep**: many providers, each with unique edge cases.
  Mitigation: implement one at a time, only when there's user demand.
- **Maintenance burden**: each provider must be kept working as
  upstream APIs change.
  Mitigation: gated live tests, clear provider ownership.

### Dependencies

Phase 0 (skills-core) + Phase 2 (CLI).

### Estimated Effort

Small per provider (prefix reuses conda infrastructure, PyPI is
simple HTTP + zip). But cumulative effort grows with each provider.

---

## Phase Sequencing Rationale

| Decision | Rationale |
|---|---|
| **Phase 0 first** | Everything depends on the core library. Trait design must be stable before providers. |
| **Phase 1 (GitHub) before Phase 3 (conda)** | Instant ecosystem access. Users can adopt pixi-skills on day one with existing skills. |
| **Phase 2 (CLI) before Phase 4 (lockfile)** | A working CLI without a lockfile is useful. A lockfile without a CLI is not. |
| **Phase 3 (conda) before Phase 5 (others)** | Conda is the key differentiator. It must work well before we spread to other providers. |
| **Phase 4 (lockfile) after at least two providers** | Lockfile design benefits from seeing two providers' versioning schemes in practice. |

---

## Success Criteria (Project-Level)

| Milestone | Metric |
|---|---|
| **First usable release** | Phase 2 complete. A user can `pixi skills add github:...` and it works. |
| **Differentiation proven** | Phase 4 complete. Lockfile works, reproducibility demonstrated. |
| **Ecosystem traction** | 10+ skill packages on conda-forge. 5+ GitHub repos tagged `pixi-skill`. |
| **Community adoption** | 100+ stars. 10+ contributors. Mentioned in AI agent tool discussions. |
| **Enterprise readiness** | Private channels work. Offline support via pixi-pack verified. |

## Related Concepts

- [Roadmap — Context](./CONTEXT.md)
- [Crates — Index](../crates/index.md)
- [Differentiation](../landscape/differentiation.md)
- [Dependency Graph](../architecture/dependency-graph.md)
