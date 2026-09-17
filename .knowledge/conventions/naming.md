---
title: "Naming Conventions"
section: conventions
kind: detail
tags: [conventions, naming, crates, packages, tasks, files, variables]
relates_to:
  - conventions/CONTEXT
  - crates/CONTEXT
  - pixi/tasks
  - architecture/design-decisions
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Naming Conventions

Consistent naming across all layers of the pixi-skills project.

---

## Rust Crate Names

| Pattern | Example | Rationale |
|---|---|---|
| `skills-core` | `skills-core` | Core library — no prefix/suffix needed |
| `skills-provider-{source}` | `skills-provider-github` | Provider crates follow `skills-provider-` prefix |
| `pixi-skills` | `pixi-skills` | CLI binary — matches pixi extension naming convention |
| `xtask` | `xtask` | Standard cargo-xtask convention |

### Rules

- Hyphens (not underscores) in crate names: `skills-core`, not
  `skills_core`
- Rust module names use underscores (automatic: `skills-core` →
  `skills_core` as module)
- Provider crates always use `skills-provider-{source}` pattern
- New providers must follow this pattern exactly

---

## Rust Type Names

| Category | Convention | Example |
|---|---|---|
| Traits | PascalCase, descriptive verb/noun | `SkillRegistry` |
| Structs | PascalCase | `Skill`, `SkillId`, `SkillSummary` |
| Enums | PascalCase | `ProviderKind`, `SkillVersion`, `AgentKind` |
| Enum variants | PascalCase | `ProviderKind::GitHub`, `ProviderKind::Conda` |
| Error types | PascalCase, `Error` suffix | `SkillsError` |
| Config types | PascalCase, `Config` suffix | `AgentConfig`, `ProjectConfig` |
| Builder types | PascalCase, `Builder` suffix | `SkillRegistryBuilder` |

---

## conda Package Names

| Pattern | Example | Description |
|---|---|---|
| `skill-{name}` | `skill-playwright` | A skill package on conda-forge |
| `pixi-skills` | `pixi-skills` | The CLI tool itself |

### Rules

- Always `skill-` prefix (not `pixi-skill-`, not `skills-`)
- Lowercase with hyphens
- Package suffix matches the **skill folder name**, which per the
  agentskills.io standard MUST equal the `name` field in the SKILL.md
  YAML frontmatter: `skill-playwright` ↔ `skills/playwright/` ↔
  `name: playwright` (updated 2026-09, ADR-008)
- Always `noarch` (skills are platform-independent folders of
  markdown/scripts)

---

## pixi Task Names

| Pattern | Example | Description |
|---|---|---|
| `{verb}` | `build`, `test` | Simple single-action tasks |
| `{verb}-{qualifier}` | `build-release`, `test-doc` | Qualified action tasks |
| `{verb}-{language}` | `fmt-rust`, `fmt-toml`, `fmt-ts` | Language-specific format/lint |
| `{verb}-{scope}` | `lint-deps`, `lint-workspace` | Scope-specific lint tasks |
| `{category}-{action}` | `docs-dev`, `docs-build`, `docs-preview` | App-specific tasks |
| `{verb}-all` | `fmt-all`, `lint-all` | Cross-cutting composite tasks |
| `{verb}-check` | `fmt-check`, `fmt-check-all` | CI check variants (no modification) |

### Rules

- kebab-case: `docs-build`, not `docsBuild` or `docs_build`
- Verb-first for actions: `fmt-rust`, not `rust-fmt`
- Category-first for app tasks: `docs-dev`, not `dev-docs`
- `-all` suffix for cross-cutting composites
- `-check` suffix for CI check variants
- No `run-` prefix (it's redundant: `pixi run run-tests`)

---

## File and Directory Names

| Category | Convention | Example |
|---|---|---|
| Rust source files | snake_case | `skill.rs`, `registry.rs` |
| Config files | Tool-standard naming | `pixi.toml`, `Cargo.toml`, `biome.json` |
| Skill folders | kebab-case, == frontmatter `name` | `playwright/`, `web-design-guidelines/` |
| Skill files | spec-standard inside the folder | `SKILL.md`, `skill.toml`, `scripts/*.sh`, `references/*.md` |
| Knowledge base | kebab-case | `workspace-layout.md`, `three-layer-model.md` |
| Directories | kebab-case | `skills-core/`, `pixi-skills-docs/` |
| Generated files | Tool-standard | `pixi-skills.bash`, `_pixi-skills.ps1` |
| CI workflows | kebab-case | `ci.yml`, `release.yml`, `deploy-docs.yml` |

---

## Environment Variable Names

| Pattern | Example | Description |
|---|---|---|
| `PIXI_SKILLS_{NAME}` | `PIXI_SKILLS_CACHE_DIR` | pixi-skills-specific variables |
| `GITHUB_TOKEN` | `GITHUB_TOKEN` | Standard GitHub token (not ours to name) |
| `PREFIX_DEV_TOKEN` | `PREFIX_DEV_TOKEN` | Standard prefix.dev token |
| `CONDA_TOKEN` | `CONDA_TOKEN` | Standard conda channel token |
| `CARGO_REGISTRY_TOKEN` | `CARGO_REGISTRY_TOKEN` | Standard cargo publish token |

### pixi-skills Variables

| Variable | Purpose | Default |
|---|---|---|
| `PIXI_SKILLS_CACHE_DIR` | Override cache directory | `~/.cache/pixi-skills` |
| `PIXI_SKILLS_CONFIG_DIR` | Override config directory | `~/.config/pixi-skills` |
| `PIXI_SKILLS_LOG` | Log level filter (tracing) | `info` |
| `PIXI_SKILLS_NO_COLOR` | Disable colored output | unset |

---

## Git Branch Names

| Pattern | Example | Description |
|---|---|---|
| `feat/{scope}/{description}` | `feat/core/add-registry-trait` | Feature branches |
| `fix/{scope}/{description}` | `fix/github/rate-limit-retry` | Bug fix branches |
| `docs/{description}` | `docs/installation-guide` | Documentation branches |
| `chore/{description}` | `chore/update-dependencies` | Maintenance branches |

Scope is optional for branch names (unlike commits, where it's
encouraged).

---

## Git Tag Names

| Pattern | Example | Description |
|---|---|---|
| `v{MAJOR}.{MINOR}.{PATCH}` | `v0.3.0` | Release tags |

Always prefixed with `v`. Always full semver (no `v0.3`, always
`v0.3.0`). No pre-release tags (e.g., `v0.3.0-beta.1`) until we
have a process for pre-releases.
