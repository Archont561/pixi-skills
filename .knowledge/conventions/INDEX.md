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
updated: 2025-01-01
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
The `SKILL.md` specification: TOML frontmatter schema (metadata fields,
agent compatibility, version, dependencies on other skills), markdown
body format, and examples. The canonical reference for skill authors.

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
