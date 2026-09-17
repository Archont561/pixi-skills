---
title: "Skill Format"
section: conventions
kind: detail
tags: [conventions, skill-format, SKILL.md, folder, yaml, companion, skill-toml, agentskills, spec]
relates_to:
  - conventions/CONTEXT
  - crates/skills-core
  - landscape/skills-sh
  - landscape/agent-skills-standard
  - architecture/design-decisions
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Skill Format

The skill format specification. This is the canonical reference
for skill authors.

> **Current spec (ADOPTED 2026-09-17, ADR-008):** pixi-skills uses
> the **agentskills.io open standard** as the artifact format, plus
> one manager-owned companion file (`skill.toml`). The earlier
> TOML-frontmatter single-file design is **superseded** — older
> revisions of this page are kept in git history only.

---

## 1. The Unit: A Folder, Not a File

A skill is a **directory**. Only `SKILL.md` is required.

```
playwright/                     ← folder name MUST equal frontmatter `name`
├── SKILL.md                    ← required: YAML frontmatter + markdown body
├── skill.toml                  ← optional: pixi-skills manager envelope (§4)
├── scripts/                    ← optional: executable code (py/bash/js)
│   └── login-flow.sh
├── references/                 ← optional: loaded on demand by the agent
│   └── selectors-cheatsheet.md
├── assets/                     ← optional: templates, images, data
└── agents/                     ← optional: per-agent metadata
    └── openai.yaml             ← Codex-CLI-specific; ignored by others
```

**Why folders:** the standard's progressive-disclosure model (§5)
needs somewhere to put tier-3 content. Conda packages, git repos,
and wheels all carry directory trees natively — the folder is the
common denominator of every provider.

---

## 2. SKILL.md — YAML Frontmatter (Spec Fields Only)

```markdown
---
name: playwright
description: Browser automation patterns for Playwright. Use when
  writing, debugging, or refactoring end-to-end browser tests.
license: MIT
compatibility: Requires playwright >= 1.40 available in the project.
allowed-tools:
  - read_file
  - run_tests
metadata:
  homepage: https://playwright.dev
---

# Playwright Testing Patterns

When writing Playwright tests in this project, follow these patterns...
```

| Field | Required | Notes |
|---|---|---|
| `name` | ✅ | Lowercase-hyphen; **must equal the folder name** |
| `description` | ✅ | Drives agent activation — the most important field; write it as "what + when to use" |
| `license` | ➖ | SPDX identifier |
| `compatibility` | ➖ | Free-text environment requirements |
| `allowed-tools` | ➖ | Tool allow-list; enforced by some agents (Claude Code, OpenClaw), ignored by others |
| `metadata` | ➖ | Small key-value escape hatch; **do not** rely on it for manager data (use `skill.toml`) |

Rules enforced by `pixi skills lint`:
- Only spec fields in frontmatter (unknown fields: warning, preserved)
- Frontmatter is YAML — **never TOML, never JSON**
- `name` matches folder name
- Body starts with a top-level heading

> ⚠️ **Never put manager data in frontmatter.** Version, source,
> dependency edges, hashes — none of these belong in agent-visible
> context. They live in `skill.toml` (§4) or the lockfile.

---

## 3. Markdown Body

1. **Be directive**: imperative language. "Use X", "Always Y",
   "Never Z". Skills are instructions, not documentation.
2. **Include examples**: fenced code blocks with language tags.
3. **Keep it focused**: one skill per folder. Split multi-topic
   skills.
4. **Standard markdown only**: no MDX/JSX/Astro components, no raw
   HTML. Images allowed but agents may not render them — prefer
   text descriptions.
5. **Move depth into `references/`**: the body is tier-2 context;
   details belong in tier-3 files the agent loads only when needed.

---

## 4. Companion `skill.toml` (pixi-skills Envelope)

Manager-owned metadata, living **next to** SKILL.md. Agents never
read it; `pixi skills` never installs it (see §7). Optional — a
skill without it is fully valid (spec-pure), just unmanaged.

> 📐 **Normative schema (v1, open schema) →
> [`conventions/skill-toml.md`](./skill-toml.md)** — every field,
> type, requirement level, validation rule, the duplication matrix
> (what lives where vs frontmatter/manifest/lockfile), and the
> evolution policy. Summary below; the linked page wins on conflict.

```toml
# skill.toml — pixi-skills manager envelope
schema = 1                          # optional; reserved

[package]
version = "1.2.3"                    # semver; the skill's own version

[author]
name = "Example Author"
url = "https://github.com/example"

[relations]
depends_on = ["git-workflows"]       # other skills, by name
conflicts_with = ["legacy-e2e"]

[hints]
agents = ["claude", "cursor", "codex"]   # empty/absent = all agents
tags = ["testing", "browser", "e2e"]
```

| Section | Purpose |
|---|---|
| `[package]` | The skill's own semver version — feeds lockfile resolution & changelogs. **No `name` here (ENV1 identity rule)** |
| `[author]` | Attribution |
| `[relations]` | Dependency/conflict edges consumed by the resolver (proposal P2) |
| `[hints]` | Non-binding discovery/metadata (search, display) |
| `[lint]` | Per-skill lint escape hatches (budget rules only) |

Why a companion file (ADR-008 option d): SKILL.md stays 100%
spec-compliant → 26+ agents + all ecosystem tools read it with zero
risk; our TOML tooling (`toml_edit`, taplo) stays; and agent-visible
context never carries manager bytes.

---

## 5. Progressive Disclosure Budgets (Spec)

| Tier | What loads | When | Budget (lint-enforced) |
|---|---|---|---|
| 1 | `name` + `description` | Session start, always | ~30–50 tokens per skill |
| 2 | SKILL.md body | Task matches description | ≤ ~5,000 tokens |
| 3 | `references/`, `scripts/`, `assets/` | On demand during execution | ≤ ~500 lines per directory |

`pixi skills lint` measures tiers (tokenizer for the body) and fails
CI on budget violations. `pixi skills doctor` reports total tier-1
cost of all installed skills (context hygiene at a glance).

---

## 6. Distribution Shapes

| Channel | Shape |
|---|---|
| Git repo (GitHub/GitLab/any git) | Skill folder anywhere in the repo; multi-skill repos use `skills/<name>/` per skills.sh-era convention |
| conda package (`skill-<name>`, noarch) | `skills/<name>/` tree inside the package payload (ADR-002, amended) |
| PyPI wheel (`skill-*`) | `skills/<name>/` inside the wheel |
| Local | Path to a skill folder |

Naming (`conventions/naming.md`): folder name == frontmatter `name`
== conda package suffix (`skill-playwright` ↔ `playwright/`).

---

## 7. Install Semantics

```
resolve + fetch skill folder
  → verify canonical tree hash vs skills-lock.toml
  → for each detected agent:
        copy folder tree → <agent-skills-path>/<name>/
        EXCLUDE: skill.toml (manager-only)
        PASS THROUGH: SKILL.md, scripts/, references/, assets/, agents/
  → record InstallReceipt (paths, tree hash, timestamp)
```

- **No format transforms.** Every conforming agent reads the folder
  as-is (ADR-008 §5). The transform hook survives only as a
  config-gated legacy override (ADR-003).
- **Verification is by tree hash** (ADR-008 §4): sort by relative
  path; SHA-256 over `path‖mode‖size‖bytes`; LF-normalized;
  exec-bit-aware on unix, fixed mode on Windows.

### Agent paths (post-standard, from ADR-003 — data file authoritative)

| Agent | Installs to |
|---|---|
| Claude Code | `.claude/skills/<name>/` |
| OpenAI Codex | `.agents/skills/<name>/` (or `.codex/skills/<name>/`) |
| GitHub Copilot | `.github/skills/<name>/` |
| Cursor | `.cursor/skills/<name>/` |
| Gemini CLI | `.gemini/skills/<name>/` |
| 70+ others | `default_agents.toml` (self-updatable via `pixi skills agents --update`) |

---

## 8. Legacy Compatibility (Read-Only)

Older artifacts are accepted on **read**, never **emitted**:

| Legacy shape | Handling |
|---|---|
| Bare markdown SKILL.md (no frontmatter) | Read as a one-file bundle; `name` from H1/folder; hash normally |
| Pre-standard single-file skills | Wrapped as a one-file folder bundle upstream of install |
| TOML frontmatter (our pre-ADR-008 design) | `pixi skills lint` offers `--fix` migration to YAML + `skill.toml` |
| Pre-standard agent paths (`.cursor/rules/*.mdc`, `.github/copilot/skills/`) | Detected by `doctor`; `pixi skills migrate-agents` moves installs to standard paths |

---

## 9. Full Example

```
playwright/
├── SKILL.md
├── skill.toml
└── references/
    └── selector-strategies.md
```

`SKILL.md`:

```markdown
---
name: playwright
description: Playwright testing patterns for browser automation.
  Use when writing, debugging, or reviewing end-to-end tests.
license: MIT
---

# Playwright Testing Patterns

## Page Object Model

Always use the Page Object Model pattern for test organization...

```typescript
class LoginPage {
  async login(email: string, password: string) { /* ... */ }
}
```

## Further Reading

See `references/selector-strategies.md` for the full selector guide.
```

`skill.toml`:

```toml
[package]
version = "1.2.3"

[author]
name = "Example Author"
url = "https://github.com/example"

[relations]
depends_on = ["git-workflows"]

[hints]
agents = ["claude", "cursor", "codex"]
tags = ["testing", "browser", "e2e", "playwright"]
```
