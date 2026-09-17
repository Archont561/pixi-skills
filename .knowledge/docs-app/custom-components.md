---
title: "Custom Components"
section: docs-app
kind: detail
tags: [docs, components, astro, mdx, SkillCard, ProviderBadge, CLIDemo]
relates_to:
  - docs-app/astro-starlight
  - docs-app/content-structure
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Custom Components

Custom Astro components that extend Starlight's built-in capabilities.
These are `.astro` files in `src/components/` that can be imported
into any MDX page.

---

## Component Inventory

```
src/components/
├── SkillCard.astro              # Renders a skill preview card
├── ProviderBadge.astro          # Visual provider indicator
├── CLIDemo.astro                # Terminal demo / command example
├── ComparisonTable.astro        # Interactive feature comparison
└── SkillFormatPreview.astro     # Live SKILL.md format preview
```

---

## `<SkillCard />`

Renders a card-style preview of a skill — used on catalog/discovery
pages and in the Getting Started guide.

### Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | ✅ | Skill display name |
| `provider` | `'conda' \| 'github' \| 'prefix' \| 'pypi'` | ✅ | Provider type (determines badge color) |
| `version` | `string` | ✅ | Current version |
| `description` | `string` | ✅ | One-line description |
| `url` | `string` | ❌ | Link to skill source |
| `agents` | `string[]` | ❌ | Compatible agents (shown as small icons) |

### Usage

```mdx
import SkillCard from '../../components/SkillCard.astro';

<SkillCard
  name="playwright"
  provider="conda"
  version="1.2.3"
  description="Playwright testing patterns for browser automation"
  agents={['claude', 'cursor']}
/>
```

### Rendering

```
┌─────────────────────────────────────────────────┐
│ 🟢 conda                              v1.2.3   │
│                                                 │
│ playwright                                      │
│ Playwright testing patterns for browser         │
│ automation                                      │
│                                                 │
│ 🤖 Claude  🖱️ Cursor                            │
└─────────────────────────────────────────────────┘
```

---

## `<ProviderBadge />`

A small inline badge indicating the provider. Used within tables,
lists, and `<SkillCard>`.

### Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `provider` | `'conda' \| 'github' \| 'prefix' \| 'pypi'` | ✅ | Provider type |
| `size` | `'sm' \| 'md'` | ❌ | Badge size (default: `md`) |

### Color Mapping

| Provider | Emoji | Color | CSS variable |
|---|---|---|---|
| conda | 🟢 | Green | `--provider-conda: #4caf50` |
| github | 🟣 | Purple | `--provider-github: #9c27b0` |
| prefix | 🔵 | Blue | `--provider-prefix: #2196f3` |
| pypi | 🟠 | Orange | `--provider-pypi: #ff9800` |

### Usage

```mdx
import ProviderBadge from '../../components/ProviderBadge.astro';

Available from <ProviderBadge provider="conda" /> and
<ProviderBadge provider="github" />.
```

---

## `<CLIDemo />`

Renders a terminal-style code block with command + output, styled to
look like a real terminal session. Built on top of Astro Expressive
Code.

### Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `command` | `string` | ✅ | The command being demonstrated |
| `output` | `string` | ✅ | The command's output |
| `title` | `string` | ❌ | Terminal window title (default: `Terminal`) |
| `prompt` | `string` | ❌ | Prompt symbol (default: `$`) |

### Usage

```mdx
import CLIDemo from '../../components/CLIDemo.astro';

<CLIDemo
  command="pixi skills find playwright"
  output={`
 Provider  Name              Version  Description
 ──────────────────────────────────────────────────────────
 🟢 conda  skill-playwright  1.2.3    Playwright testing patterns
 🟣 github anthropics/skill  main     Official Playwright skill
`}
  title="Search for skills"
/>
```

### Design Considerations

- Uses monospace font and dark background to match terminal UX
- Command line is highlighted (bold/different color) to distinguish
  from output
- Copy button on the command line (not the output)
- Responsive — wraps gracefully on mobile

### Alternative: Asciinema Embeds

For more complex demos (multi-step interactions), consider embedding
Asciinema recordings:

```mdx
<script id="asciicast-XXXXX"
  src="https://asciinema.org/a/XXXXX.js"
  async
  data-rows="20">
</script>
```

This is heavier (external JS) but shows real terminal interaction
including timing, colors, and interactive prompts.

---

## `<ComparisonTable />`

An interactive feature comparison table between pixi-skills and
alternatives (skills.sh, npm-skills, manual approaches).

### Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `tools` | `Tool[]` | ✅ | Array of tools to compare |
| `features` | `Feature[]` | ✅ | Array of features to compare against |

### Type Definitions

```typescript
interface Tool {
  name: string;
  url?: string;
}

interface Feature {
  name: string;
  description: string;
  values: Record<string, 'yes' | 'no' | 'partial' | string>;
}
```

### Usage

```mdx
import ComparisonTable from '../../components/ComparisonTable.astro';

<ComparisonTable
  tools={[
    { name: 'pixi-skills', url: '/' },
    { name: 'skills.sh', url: 'https://skills.sh' },
    { name: 'npm-skills' },
  ]}
  features={[
    {
      name: 'Version pinning',
      description: 'Lock skill versions for reproducibility',
      values: { 'pixi-skills': 'yes', 'skills.sh': 'no', 'npm-skills': 'partial' },
    },
    {
      name: 'Lockfile',
      description: 'Deterministic lockfile with content hashes',
      values: { 'pixi-skills': 'yes', 'skills.sh': 'no', 'npm-skills': 'no' },
    },
    // ...
  ]}
/>
```

### Rendering

Renders as a table with ✅ / ❌ / ⚠️ icons:

```
Feature           pixi-skills   skills.sh   npm-skills
───────────────────────────────────────────────────────
Version pinning   ✅            ❌          ⚠️
Lockfile          ✅            ❌          ❌
Multi-language    ✅            ❌          ❌
Private channels  ✅            ❌          ❌
Offline support   ✅            ❌          ❌
```

---

## `<SkillFormatPreview />`

Shows a SKILL.md file with TOML frontmatter, with annotations
explaining each section. Used on the `skill-md-format` reference page.

### Props

| Prop | Type | Required | Description |
|---|---|---|---|
| `content` | `string` | ✅ | Raw SKILL.md content |
| `annotations` | `Annotation[]` | ❌ | Line annotations |

### Usage

```mdx
import SkillFormatPreview from '../../components/SkillFormatPreview.astro';

<SkillFormatPreview
  content={`---
name = "playwright"
version = "1.0.0"
agents = ["claude", "cursor"]
tags = ["testing", "browser"]
---

# Playwright Testing Patterns

When writing Playwright tests, always use...
`}
  annotations={[
    { lines: '1-5', label: 'TOML frontmatter (optional)' },
    { lines: '7-9', label: 'Markdown body (the skill content)' },
  ]}
/>
```

### Rendering

Shows the skill file with highlighted sections and callout labels,
similar to annotated code examples in Stripe or Vercel documentation.

---

## Component Development Guidelines

### File naming
- PascalCase: `SkillCard.astro`, not `skill-card.astro`
- One component per file

### Props
- Always define a TypeScript interface for props
- Use required/optional distinction explicitly
- Provide sensible defaults for optional props

### Styling
- Use Starlight's CSS variables where possible (for theme consistency)
- Scoped styles (Astro's default) — no global CSS leaks
- Support both light and dark mode

### Testing
- No unit tests for Astro components (Astro doesn't have a component
  testing story yet)
- Visual testing via the dev server: create a test page at
  `src/content/docs/_test/components.mdx` that renders every component
  with sample data. Exclude from sidebar with `sidebar: { hidden: true }`.

### Importing in MDX

```mdx
---
title: Some Page
---

import SkillCard from '../../components/SkillCard.astro';
import ProviderBadge from '../../components/ProviderBadge.astro';

Regular markdown content here.

<SkillCard name="example" provider="conda" version="1.0" description="Example skill" />

More markdown after the component.
```

Import paths are relative to the MDX file. Components are imported
at the top of the MDX body (after frontmatter, before content).
