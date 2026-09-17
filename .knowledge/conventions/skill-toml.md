---
type: Convention
title: "skill.toml — Manager Envelope Schema"
description: "Manager-owned skill.toml envelope schema, validation rules, and evolution policy."
section: conventions
kind: detail
tags: [conventions, skill-toml, companion, envelope, schema, versioning, ADR-008]
status: stable
created: "2026-09-17"
updated: "2026-09-17"
---

# skill.toml — Manager Envelope Schema (v1, open schema)

The normative specification for the `skill.toml` companion file
introduced by **ADR-008**. `skill.toml` lives **next to SKILL.md**
inside the skill folder and carries the manager-owned metadata that
must never enter agent-visible context.

> **Stability model: v1 — open schema (2026-09-17).** This schema is
> **defined but deliberately unfrozen**: it ships with a formal
> evolution policy (§7) instead of a compatibility freeze. Extensions
> arrive as tolerated-unknown fields; breaking changes arrive only
> via an explicit `schema` bump. Do not wait for a "final" schema —
> there isn't one, by design.

---

## 1. Role: One of Three TOMLs

pixi-skills has three TOML artifacts with disjoint lifecycles.
Confusing them is the #1 schema-design failure mode — this diagram
is the default answer to "where does field X live?"

```
┌────────────────────────────────────────────────────────────────┐
│ skill.toml          skills.toml            skills-lock.toml     │
│ ───────────         ───────────            ───────────────      │
│ THE ARTIFACT        THE PROJECT            THE SOLVED STATE     │
│ "what am I?"        "what do I need?"      "what exactly        │
│                                              did you get?"      │
│                                                                  │
│ travels WITH the    lives at project root  lives at project     │
│ skill (git repo,    (user-authored)        root (generated,     │
│ conda pkg, wheel)                          committed)           │
│                                                                  │
│ author: skill       author: project user   author: resolver     │
│         publisher                            (pixi skills lock) │
│                                                                  │
│ read by: pixi-      read by: resolver      read by: installer,  │
│ skills (manager)                           doctor, audit, CI    │
│ NEVER by agents                            NEVER by agents      │
│ NEVER installed to                          enforcement input   │
│ agent dirs (ADR-008 §5)                                           │
└────────────────────────────────────────────────────────────────┘
```

A skill is fully valid **without** `skill.toml` (spec-pure, per
ADR-008) — the file only upgrades a skill from "anonymous artifact"
to "managed, versioned, publishable artifact".

---

## 2. Placement & Lifecycle Rules

| Rule | Statement |
|---|---|
| R1 Placement | Exactly one `skill.toml`, at the skill folder root, sibling of `SKILL.md` |
| R2 Travels | Included in every distribution shape: git repos, `skill-*` conda payloads, PyPI wheels, tarballs, the pixi-skills content-addressed cache |
| R3 Never agent-visible | The installer MUST NOT copy it into agent skill dirs (ADR-008 §5) |
| R4 Never parsed by agents | Conforming agents don't know it exists; we never reference it from SKILL.md content |
| R5 Optional | Absence is legal (`InvalidCompanion` never fires on missing file) |
| R6 Rewrite-safe | Tools rewriting the file MUST preserve unknown fields/tables verbatim (order may normalize; values/comments may not silently drop) |

---

## 3. Schema v1

```toml
# skill.toml — pixi-skills manager envelope
schema = 1                          # optional; reserved; MUST be 1 if present

[package]
version = "1.2.3"                   # semver string

[author]
name = "Example Author"             # REQUIRED if this table is present
url = "https://github.com/example"  # optional
email = "you@example.com"           # optional

[relations]
depends_on = ["git-workflows"]      # skill names; resolved in project context
conflicts_with = ["legacy-e2e"]

[hints]
agents = ["claude", "cursor", "codex"]   # empty/absent = all agents
tags = ["testing", "browser", "e2e"]

[lint]
disable = ["body-token-budget"]     # rule ids to skip for THIS skill
```

### 3.1 Top level

| Key | Type | Required | Semantics |
|---|---|---|---|
| `schema` | integer | ➖ reserved | Envelope schema revision. Only `1` is defined. If present and > 1, parsers MUST refuse with "upgrade pixi-skills" (hard gate, see §7) |

### 3.2 `[package]`

| Key | Type | Required | Semantics |
|---|---|---|---|
| `version` | semver string | ➖ (see rule PKG1) | The skill artifact's own version. Drives lockfile resolution, `check`/`update`, and changelogs |

Rules:

- **PKG1**: `version` is REQUIRED for `pixi skills publish` (any
  provider) and RECOMMENDED otherwise. Absence ≠ error; the resolver
  falls back to provider-native identity (git tag/SHA, conda build).
- **PKG2**: when packaged as `skill-<name>` on conda, the package
  version SHOULD equal `[package].version` (lint warning on skew;
  the package record is authoritative at install time).
- **ENV1 (identity rule)**: `skill.toml` MUST NOT contain `name`,
  `display_name`, or `title` anywhere. Identity derives from the
  *folder name*, which per spec equals the SKILL.md `name`. One
  source of truth; `lint` errors on violation.

### 3.3 `[author]`

| Key | Type | Required | Semantics |
|---|---|---|---|
| `name` | string | ✅ if table present | Display/attribution name |
| `url` | URL string | ➖ | Canonical profile/ homepage |
| `email` | string | ➖ | Contact; discouraged in public skills (spam) — lint nudges to `url` |

### 3.4 `[relations]`

Edges consumed by the resolver (proposal P2) and the audit pipeline
(proposal P3).

| Key | Type | Required | Semantics |
|---|---|---|---|
| `depends_on` | string[] | ➖ | Skill **names** (identity-form, same rule as 3.2-ENV1). The resolver looks each name up in the project's `skills.toml` / provider context; unknown names are warnings at lint time, errors at install time |
| `conflicts_with` | string[] | ➖ | Skill names that must not co-install; the resolver refuses lockfiles violating this |

v1 scope note: names only, no version qualifiers. `@version` edge
syntax is an open question (§8, Q1).

### 3.5 `[hints]`

Non-binding metadata. Hints inform search/display/defaults; they
never gate installation.

| Key | Type | Required | Semantics |
|---|---|---|---|
| `agents` | string[] | ➖ | Agent ids this skill was authored/tested for (e.g. `claude`, `cursor`, `codex`, `copilot`, `gemini`). Absent/empty = all agents. Unknown ids: lint warning (data file is the registry) |
| `tags` | string[] | ➖ | Free-form discovery tags; powers `find` ranking and channel browsing |

### 3.6 `[lint]`

Per-skill escape hatches for `pixi skills lint`.

| Key | Type | Required | Semantics |
|---|---|---|---|
| `disable` | string[] | ➖ | Rule ids to skip for this skill (e.g. `body-token-budget`, `scripts-executable`). Skipping a *spec-compliance* rule is ignored with a warning — budgets may flex, the standard may not |

### 3.7 Everything else: tolerated-unknown

Any key/table not listed here is **reserved-or-unknown**: parsers
MUST warn once per key and otherwise tolerate, and rewriters MUST
preserve (R6). Known future reservations: `[publish]`
(per-provider packaging overrides), `[provenance]` (signing/
attestation hooks for proposal P3).

---

## 4. Validation Rules (pseudocode)

```pseudo
rule-ids  = ENV1, ENV2, REL1, REL2, AUTH1, PKG1, PKG2, FM1, SC1

fn validate_companion(file?, folder) -> [Finding]:
    if file is missing:            return []          # R5
    t = parse_toml(file)
    if t.schema present and t.schema != 1:
        fail(SC1, "unsupported schema; upgrade pixi-skills")
    if tree_contains(t, ["name", "display_name", "title"]):
        fail(ENV1, "identity lives in folder name + SKILL.md `name`")
    if version = t.package?.version:
        require_semver(version, ENV2)
    for r in t.relations?.depends_on ++ conflicts_with:
        require_identity_form(r, REL1)                 # kebab-case name
        warn_unless_known_or_manifested(r, REL2)
    if t.author present: require(t.author.name, AUTH1)
    if folder.packaged_as_conda:
        warn_if(t.package?.version != pkg.version, PKG2)
    publish_gate: require(t.package?.version, PKG1)    # only on publish
    frontmatter_match(folder.FM1):                     # name == folder-ish
        # (FM1 formally: SKILL.md `name` == folder name)
    return findings
```

Exit semantics: spec-compliance failures (`FM1`, `SC1`, `ENV1`)
are hard errors — always; everything else defaults to warning;
`[lint].disable` can mute warnings, never hard errors (§3.6).

---

## 5. Duplication Matrix — Each Datum Has ONE Home

| Datum | Home | NOT in |
|---|---|---|
| Skill identity (`name`) | SKILL.md frontmatter + folder name | skill.toml (ENV1), lockfile keeps resolved identity |
| What the skill does (`description`) | SKILL.md frontmatter (tier-1 context) | skill.toml |
| Skill's own `version` | `[package].version` | frontmatter (spec has no version field) |
| Agent permissions (`allowed-tools`) | SKILL.md frontmatter (spec, agent-enforced) | skill.toml (managers audit it, never override it) |
| Dependency/conflict edges | `[relations]` | frontmatter |
| Author | `[author]` | frontmatter `metadata` (avoid; tolerated) |
| Required versions of THIS skill per project | skills.toml (`version`/`ref`) | skill.toml, lockfile holds the resolution |
| Exact resolved version + tree hash + provenance | skills-lock.toml v2 | skill.toml, skills.toml |
| Install targets (agent paths) | `default_agents.toml` + project overrides | skill.toml |

---

## 6. Examples

### 6.1 Minimal valid companion (managed, unremarkable)

```toml
[package]
version = "1.0.0"
```

### 6.2 Typical published skill

```toml
schema = 1

[package]
version = "1.2.3"

[author]
name = "Example Author"
url = "https://github.com/example"

[relations]
depends_on = ["git-workflows"]

[hints]
agents = ["claude", "cursor", "codex"]
tags = ["testing", "browser", "e2e"]
```

### 6.3 Budget-exception skill (docs-heavy reference skill)

```toml
[package]
version = "0.4.0"

[lint]
disable = ["body-token-budget"]   # intentionally reference-dense;
                                  # tier-3 files carry the depth
```

### 6.4 Migration mapping (pre-ADR-008 TOML frontmatter → today)

| Old (TOML frontmatter) | New home |
|---|---|
| `name = "playwright"` | SKILL.md YAML `name:` (= folder name) |
| `version = "1.2.3"` | `skill.toml [package].version` |
| `description = "..."` | SKILL.md YAML `description:` |
| `agents = [...]` | `skill.toml [hints].agents` |
| `tags = [...]` | `skill.toml [hints].tags` |
| `license = "MIT"` | SKILL.md YAML `license:` |
| `depends_on = [...]` | `skill.toml [relations].depends_on` |
| `conflicts_with = [...]` | `skill.toml [relations].conflicts_with` |
| `[author]` table | `skill.toml [author]` |
| `min_agent_version` table | dropped (open question §8/Q4) |

`pixi skills lint --fix` performs this migration mechanically.

---

## 7. Evolution Policy (the "open schema" contract)

1. **Additive evolution is always allowed** in v1: new optional
   fields/tables. Old parsers tolerate (§3.7) → files stay usable.
2. **Never tighten requirement levels in v1**: optional never becomes
   required (the only quasi-exception is context gates like PKG1,
   which exist at tool-behavior level, not schema level).
3. **Breaking changes** (rename, type change, semantic reversal)
   require `schema = 2`; parsers refuse unknown higher revisions
   (SC1) with a clear upgrade instruction.
4. **Rewrite discipline (R6)** preserves what's tolerated — a v1
   tool must never silently strip a v2 field it doesn't understand.
5. The lockfile (`skills-lock.toml` v2) has its own, stricter
   versioning; envelope evolution does NOT imply lockfile evolution.

---

## 8. Open Questions (deferred, with triggers)

| # | Question | Deferred until |
|---|---|---|
| Q1 | Version-qualified edges: `depends_on = ["git-workflows@^2"]`? | First real multi-skill ecosystem conflict (resolver P2 lands) |
| Q2 | `[publish]` table — per-provider packaging overrides | First author needing non-derived conda metadata |
| Q3 | `[provenance]` — signatures/attestation fields (sigstore on `skill-*`) | Proposal P3 (trust pipeline) implementation |
| Q4 | Agent-version floors (`min_agent_version` revival) | First agent that versions its skill loader breaking-ly |
| Q5 | Multiple authors/maintainers (`[authors]` array + `maintainers`) | First org-scale skill needing it |

Each answer lands as an additive v1 extension until/unless it forces
a §7 rule-3 break.

## Related Concepts

- [Skill Format](./skill-format.md)
- [Conventions — Context](./CONTEXT.md)
- [skills-core](../crates/skills-core.md)
- [Design Decisions](../architecture/design-decisions.md)
