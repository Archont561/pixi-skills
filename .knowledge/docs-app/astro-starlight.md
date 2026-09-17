---
title: "Astro Starlight"
section: docs-app
kind: detail
tags: [docs, astro, starlight, configuration, sidebar, search, dark-mode]
relates_to:
  - docs-app/CONTEXT
  - docs-app/content-structure
  - docs-app/bun-setup
  - pixi/tasks
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Astro Starlight

The documentation site is built with Astro and the Starlight theme.
This page covers the Astro/Starlight configuration, which features
we use, and how the site is structured at the framework level.

---

## Why Starlight

Starlight was chosen over alternatives (Docusaurus, VitePress, Nextra,
MkDocs) for these reasons:

| Criterion | Starlight | Docusaurus | VitePress | MkDocs |
|---|---|---|---|---|
| Runtime | Astro (static) | React (hydrated) | Vue (hydrated) | Python (static) |
| JS shipped to client | Near-zero | Large React bundle | Vue runtime | Zero |
| Built-in search | ✅ Pagefind | ✅ Algolia/local | ✅ local | ✅ mkdocs-search |
| Dark mode | ✅ built-in | ✅ built-in | ✅ built-in | ✅ via theme |
| i18n | ✅ built-in | ✅ built-in | ✅ built-in | ✅ plugin |
| MDX support | ✅ native | ✅ native | ❌ (md only) | ❌ (md only) |
| Sidebar autogenerate | ✅ from dirs | ❌ manual | ❌ manual | ✅ from dirs |
| Language | TS/Astro | React/TS | Vue/TS | Python |

Key advantages:
- **Near-zero client JS**: Starlight renders to static HTML. No React
  or Vue runtime shipped to the browser. Pages load instantly.
- **Pagefind search**: Client-side search indexed at build time. No
  external service (Algolia), no API keys, works offline.
- **Sidebar autogeneration**: `autogenerate: { directory: 'cli' }`
  means adding a new CLI subcommand page requires zero sidebar
  configuration.

---

## Configuration: `astro.config.mjs`

```javascript
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://pixi-skills.dev',       // Production URL
  integrations: [
    starlight({
      title: 'pixi-skills',
      logo: {
        src: './src/assets/logo.svg',
        replacesTitle: false,             // Show logo + text
      },

      // ── Social Links ──────────────────────────────────────────
      social: {
        github: 'https://github.com/yourorg/pixi-skills',
      },

      // ── Sidebar ───────────────────────────────────────────────
      sidebar: [
        {
          label: 'Getting Started',
          autogenerate: { directory: 'getting-started' },
        },
        {
          label: 'Concepts',
          autogenerate: { directory: 'concepts' },
        },
        {
          label: 'Guides',
          autogenerate: { directory: 'guides' },
        },
        {
          label: 'CLI Reference',
          autogenerate: { directory: 'cli' },
        },
        {
          label: 'Architecture',
          autogenerate: { directory: 'architecture' },
        },
        {
          label: 'Reference',
          autogenerate: { directory: 'reference' },
        },
      ],

      // ── Edit Link ─────────────────────────────────────────────
      editLink: {
        baseUrl: 'https://github.com/yourorg/pixi-skills/edit/main/apps/pixi-skills-docs/',
      },

      // ── Custom CSS ────────────────────────────────────────────
      customCss: ['./src/styles/custom.css'],

      // ── Head Tags ─────────────────────────────────────────────
      head: [
        {
          tag: 'meta',
          attrs: {
            property: 'og:image',
            content: 'https://pixi-skills.dev/og-image.png',
          },
        },
      ],

      // ── Pagination ────────────────────────────────────────────
      pagination: true,

      // ── Table of Contents ─────────────────────────────────────
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },

      // ── Last Updated ──────────────────────────────────────────
      lastUpdated: true,
    }),
  ],
});
```

---

## Starlight Features Used

### Pagefind Search

Pagefind is Starlight's built-in search engine. It runs at build
time, creating a search index from all rendered HTML pages. At
runtime, search is fully client-side — no server, no API, no
external dependency.

**Key behaviors**:
- Search covers all content including auto-generated CLI docs
- Search index is part of the static build output (`dist/`)
- Works offline (important for airgapped/enterprise environments)
- Keyboard shortcut: `Ctrl+K` / `Cmd+K`

No configuration needed — Pagefind is enabled by default.

### Dark Mode

Starlight ships dark mode out of the box. Users can toggle between
light, dark, and system-preference modes. The toggle is in the
top navigation bar.

Custom CSS variables in `custom.css` should define both light and
dark variants:

```css
/* src/styles/custom.css */
:root {
  --sl-color-accent-low: #1a2744;
  --sl-color-accent: #4a90d9;
  --sl-color-accent-high: #b3d4fc;
}
:root[data-theme='light'] {
  --sl-color-accent-low: #d4e6f9;
  --sl-color-accent: #2563eb;
  --sl-color-accent-high: #1e3a5f;
}
```

### Edit Links

Every page shows an "Edit this page" link that points to the
corresponding file on GitHub. This is configured via `editLink.baseUrl`.

For auto-generated CLI docs, the edit link points to the generated
`.mdx` file. A note in each generated file should direct contributors
to edit the clap definitions in Rust instead:

```mdx
{/* This file is auto-generated by `cargo xtask cli-docs`.
    Do not edit directly. Modify the clap definitions in
    crates/pixi-skills/src/cli.rs instead. */}
```

### Last Updated

`lastUpdated: true` shows the git commit date for each page. This
requires git history to be available at build time (which it is,
since CI uses `fetch-depth: 0` for convco).

### Table of Contents

Configured to show `h2` and `h3` headings in the right sidebar.
Deeper headings (`h4+`) are excluded to keep the TOC scannable.

---

## TypeScript Configuration

```jsonc
// apps/pixi-skills-docs/tsconfig.json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "astro"
  }
}
```

Astro's `strict` preset enables strict TypeScript checking for
component props and content collection schemas.

---

## Content Collections

Starlight uses Astro's content collections for type-safe content
management. The docs collection is configured in `src/content/config.ts`:

```typescript
// src/content/config.ts
import { defineCollection } from 'astro:content';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
  docs: defineCollection({ schema: docsSchema() }),
};
```

This gives us:
- Type-safe frontmatter (title, description, sidebar order, etc.)
- Build-time validation of all content files
- Auto-generated TypeScript types for content queries

---

## Static Assets

```
apps/pixi-skills-docs/
├── public/
│   ├── og-image.png                  # Open Graph social preview image
│   ├── favicon.svg                   # Site favicon
│   └── skills-schema.json           # Generated by xtask — served at /skills-schema.json
└── src/
    └── assets/
        └── logo.svg                  # Site logo (processed by Astro)
```

**`public/` vs `src/assets/`**:
- `public/` files are served as-is, no processing. Use for files that
  need stable URLs (schema, og-image).
- `src/assets/` files are processed by Astro (optimized, hashed). Use
  for images referenced in components.

---

## Build Output

```bash
bun run build
# Output: dist/

dist/
├── index.html
├── getting-started/
│   ├── installation/index.html
│   └── quickstart/index.html
├── cli/
│   ├── find/index.html
│   ├── add/index.html
│   └── ...
├── pagefind/                    # Search index
│   ├── pagefind.js
│   ├── pagefind-ui.js
│   └── pagefind-index-*.pf_meta
├── skills-schema.json           # From public/
└── _astro/                      # Hashed static assets
    ├── logo.abc123.svg
    └── custom.def456.css
```

All pages are pre-rendered to static HTML. No server-side rendering.
The entire `dist/` directory can be deployed to any static hosting.
