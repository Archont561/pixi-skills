---
title: "Skill Format"
section: conventions
kind: detail
tags: [conventions, skill-format, SKILL.md, frontmatter, toml, markdown, spec]
relates_to:
  - conventions/CONTEXT
  - crates/skills-core
  - landscape/skills-sh
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Skill Format

The SKILL.md file format specification. This is the canonical reference
for skill authors.

---

## Overview

A skill is a markdown file (typically named `SKILL.md`) with optional
TOML frontmatter. The frontmatter contains metadata; the markdown body
contains the skill content that AI agents read.

```markdown
---
name = "playwright"
version = "1.0.0"
description = "Playwright testing patterns for browser automation"
agents = ["claude", "cursor"]
tags = ["testing", "browser", "e2e"]

[author]
name = "Your Name"
url = "https://github.com/yourname"
---

# Playwright Testing Patterns

When writing Playwright tests in this project, follow these patterns...
```

---

## TOML Frontmatter

### Delimiters

Frontmatter is delimited by `---` lines (matching the YAML convention
used by most static site generators). However, the content between
the delimiters is **TOML, not YAML**.

```
---                          ← opening delimiter
name = "example"             ← TOML content
version = "1.0.0"
---                          ← closing delimiter
```

### Why TOML (not YAML)?

- Consistent with the rest of the pixi-skills ecosystem (`pixi.toml`,
  `skills.toml`, `skills-lock.toml`, `Cargo.toml`)
- No implicit typing gotchas (YAML's `no` → `false`, `3.10` → `3.1`)
- Same parser already in the dependency tree (`toml` crate)

### Frontmatter is Optional

Skills without frontmatter are valid. They are treated as plain
markdown with no metadata:

```markdown
# My Skill

This is a valid skill with no frontmatter.
Just markdown content.
```

This ensures compatibility with existing skills.sh skills, which
are plain markdown files.

---

## Frontmatter Fields

### Required Fields (when frontmatter is present)

| Field | Type | Description |
|---|---|---|
| `name` | `string` | Machine-readable skill name (lowercase, hyphens). Must be unique within a project. |

### Recommended Fields

| Field | Type | Default | Description |
|---|---|---|---|
| `version` | `string` | `"0.0.0"` | Semver version of the skill content |
| `description` | `string` | `""` | One-line human-readable description |
| `agents` | `string[]` | `[]` (all agents) | Compatible agents. Empty = compatible with all. |
| `tags` | `string[]` | `[]` | Categorization tags for discovery |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `license` | `string` | SPDX license identifier (e.g., `"MIT"`) |
| `min_agent_version` | `table` | Minimum agent versions: `{ claude = "1.0", cursor = "0.50" }` |
| `depends_on` | `string[]` | Other skills this skill depends on (by name) |
| `conflicts_with` | `string[]` | Skills that conflict with this one |

### Author Section

```toml
[author]
name = "Your Name"
email = "you@example.com"    # optional
url = "https://github.com/you" # optional
```

---

## Markdown Body

The markdown body is the actual skill content. It is what the AI
agent reads and learns from.

### Content Guidelines

1. **Start with a heading**: `# Skill Name` — this serves as the
   title if no `name` field is in frontmatter.

2. **Be directive**: use imperative language. "Use X", "Always Y",
   "Never Z". Skills are instructions, not documentation.

3. **Include examples**: code blocks with concrete examples are more
   effective than abstract descriptions.

4. **Keep it focused**: one skill per file. If a skill covers multiple
   topics, consider splitting into multiple skills.

5. **Use standard markdown**: no framework-specific extensions (no
   MDX, no Astro components, no JSX). Skills must be readable by
   any agent.

### Markdown Features Supported

| Feature | Supported | Notes |
|---|---|---|
| Headings (`#`, `##`, etc.) | ✅ | Use for structure |
| Code blocks (fenced) | ✅ | Include language tag for highlighting |
| Lists (ordered, unordered) | ✅ | Use for rules and patterns |
| Bold, italic | ✅ | Use sparingly |
| Links | ✅ | Relative and absolute |
| Images | ⚠️ | Agents may not render images — use text descriptions |
| Tables | ✅ | Use for structured comparisons |
| HTML | ❌ | Not supported — agents parse markdown, not HTML |

---

## Agent-Specific Considerations

### Claude Code

- Reads from `.claude/skills/`
- Supports standard markdown
- Frontmatter is ignored by the agent but preserved by pixi-skills

### Cursor

- Reads from `.cursor/rules/`
- Uses `.mdc` file extension (markdown with Cursor metadata)
- pixi-skills' installer transforms SKILL.md to `.mdc` format when
  installing for Cursor

### GitHub Copilot

- Reads from `.github/copilot/skills/`
- Supports standard markdown
- No special format requirements

### Codex

- Reads from `.codex/`
- Supports standard markdown
- May expect specific file naming conventions

### Agent Transformations

The `SkillInstaller` in `skills-core` applies per-agent
transformations:

```
SKILL.md (canonical format)
    │
    ├── Claude:  .claude/skills/playwright.md (as-is)
    ├── Cursor:  .cursor/rules/playwright.mdc (transformed)
    ├── Copilot: .github/copilot/skills/playwright.md (as-is)
    └── Codex:   .codex/playwright.md (as-is)
```

The canonical SKILL.md is the source of truth. Per-agent files are
derived.

---

## Naming Convention

### Skill name (in frontmatter)

```toml
name = "playwright"          # ✅ lowercase, no spaces
name = "react-hooks"         # ✅ hyphens for multi-word
name = "Playwright"          # ❌ no uppercase
name = "react hooks"         # ❌ no spaces
name = "react_hooks"         # ❌ no underscores (use hyphens)
```

### File name

```
SKILL.md                     # ✅ default name (single skill per repo)
playwright.md                # ✅ named skill (multiple skills per repo)
skills/playwright.md         # ✅ in a skills/ directory (conda packages)
```

### conda package name

```
skill-playwright             # ✅ skill- prefix + skill name
pixi-skill-playwright        # ❌ redundant pixi- prefix
playwright-skill             # ❌ suffix, not prefix (not discoverable)
```

---

## Full Example

```markdown
---
name = "playwright"
version = "1.2.3"
description = "Playwright testing patterns for browser automation"
agents = ["claude", "cursor", "copilot"]
tags = ["testing", "browser", "e2e", "playwright"]
license = "MIT"

[author]
name = "Example Author"
url = "https://github.com/example"
---

# Playwright Testing Patterns

## Page Object Model

Always use the Page Object Model pattern for test organization:

- Create a class per page/component
- Encapsulate selectors as private properties
- Expose actions as public methods

```typescript
class LoginPage {
  private readonly page: Page;
  private readonly emailInput = this.page.locator('#email');
  private readonly passwordInput = this.page.locator('#password');
  private readonly submitButton = this.page.locator('button[type="submit"]');

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

## Assertions

Use web-first assertions that auto-retry:

```typescript
// ✅ Good — auto-retries until condition is met
await expect(page.locator('.status')).toHaveText('Success');

// ❌ Bad — no retry, flaky
const text = await page.locator('.status').textContent();
expect(text).toBe('Success');
```

## Test Isolation

Each test must be independent:

- Use `test.beforeEach` for setup, never shared mutable state
- Use unique test data (random emails, UUIDs)
- Clean up after tests that create persistent data
```
