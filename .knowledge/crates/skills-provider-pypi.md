---
type: Component Design
title: "skills-provider-pypi"
description: "Proposed future PyPI provider and its packaging and dependency constraints."
section: crates
kind: detail
tags: [crates, provider, pypi, python, pip, uv, future]
status: draft
created: "2025-01-01"
updated: "2026-09-17"
---

# skills-provider-pypi

Implements `SkillRegistry` for PyPI (Python Package Index). This is a
**Phase 5 (future) provider** — lowest priority in the MVP roadmap.

---

## Crate Identity

```toml
[package]
name = "skills-provider-pypi"
version = "0.1.0"
edition = "2021"

[dependencies]
skills-core = { path = "../skills-core" }
reqwest = { version = "0.12", features = ["json"] }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
tracing = "0.1"
```

- **Published**: yes (eventually)
- **Dependents**: pixi-skills CLI (via feature flag `pypi`)
- **Dependencies on workspace crates**: `skills-core` only

---

## Concept

PyPI skill packages would follow a similar convention to conda:

- **Naming**: `skill-*` prefix (e.g., `skill-pandas` on PyPI)
- **Package structure**: skills stored in `skills/` directory inside
  the wheel/sdist
- **Version**: PEP 440 (mapped to `SkillVersion::PyPI`)

### Source Format

```toml
# skills.toml
[[skill]]
name = "pandas-guide"
source = "pypi"
package = "skill-pandas"
version = ">=1.0,<2.0"
index = "https://pypi.org/simple/"    # optional, defaults to PyPI
```

### Fetching Strategy

```
1. Query PyPI JSON API
   GET https://pypi.org/pypi/skill-pandas/json

2. Resolve version from available releases
   Apply PEP 440 version matching

3. Download wheel (.whl) — a zip file
   Extract the skills/<name>/ FOLDER tree from the wheel
   (ADR-008: SKILL.md + optional scripts/, references/, ...)

4. Parse SKILL.md (YAML frontmatter) + companion skill.toml,
   compute canonical tree hash

5. Return Skill struct (bundle)
```

---

## Why Lowest Priority

1. **Conda already covers Python packages.** Most Python skills can be
   published as conda noarch packages, which are better integrated
   with pixi.

2. **PyPI has no repodata equivalent.** Discovery requires querying
   the JSON API per-package — no bulk search like conda repodata.

3. **Wheel extraction is simpler than .conda** (just a zip file), but
   the tooling for building skill-only wheels doesn't exist yet.

4. **The audience overlap is smaller.** Users who want pixi-skills are
   already in the conda/pixi ecosystem, not pip-only workflows.

---

## Future Considerations

- **uv integration**: If uv (the fast Python package installer) gains
  a Rust library API, we could use it for version resolution instead
  of implementing PEP 440 matching ourselves.
- **Private PyPI**: Support for private indexes (Artifactory, DevPI,
  AWS CodeArtifact) via the `index` field.
- **Hybrid packages**: A single conda package could contain both a
  Python library and a skill — the conda provider would handle this
  case, not the PyPI provider.

---

## Implementation Status

**Not yet implemented.** This file documents the planned design.
Implementation begins in Phase 5 of the roadmap, after the lockfile
(Phase 4) is complete.

## Related Concepts

- [skills-core](./skills-core.md)
- [MVP Phases](../roadmap/mvp-phases.md)
