---
title: "Conventions — Index"
section: conventions
kind: index
tags: [conventions, index, navigation, commits, naming, format]
relates_to:
  - tooling/convco
  - crates/CONTEXT
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Conventions — Index

This section documents all project-wide conventions: how we commit, how
we name things, how skills are formatted, and where config files live.

## Pages

### [commit-conventions.md](./commit-conventions.md)
Conventional commit format, allowed types (`feat`, `fix`, `docs`,
`refactor`, `perf`, `test`, `ci`, `chore`), allowed scopes (`core`,
`cli`, `github`, `conda`, `prefix`, `pypi`, `docs`, `xtask`), breaking
change notation, and how convco enforces these rules.

### [skill-format.md](./skill-format.md)
The skill specification (agentskills.io open standard, ADR-008):
skill **folder** anatomy, `SKILL.md` with YAML frontmatter (spec
fields), progressive-disclosure budgets, the companion `skill.toml`
manager envelope (version, relations, hints), install semantics, and
legacy compatibility. The canonical reference for skill authors.

### [skill-toml.md](./skill-toml.md)
**Normative `skill.toml` schema (v1, open schema).** The manager
envelope: every table/field with types and requirement levels, the
three-TOMLs role diagram (envelope vs manifest vs lockfile),
duplication matrix, validation rules (ENV1 identity rule, PKG/AUTH/
REL gates), evolution policy, and open deferred questions.

### [naming.md](./naming.md)
Naming conventions for crates (`skills-provider-*`), conda packages
(`skill-*` noarch packages), CLI subcommands, pixi tasks, file names,
and environment variables.

### [config-files.md](./config-files.md)
The config file map: which file configures which tool, where each file
lives, and the schema/documentation link for each. A single page to
answer "where do I configure X?"

## Related Sections

- [Tooling/convco](../tooling/convco.md) — enforces commit conventions
- [Crates](../crates/INDEX.md) — follows crate naming conventions
- [Pixi](../pixi/INDEX.md) — follows task naming conventions
