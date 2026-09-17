---
title: "Docs App — Index"
section: docs-app
kind: index
tags: [docs, astro, starlight, bun, index, navigation]
relates_to:
  - pixi/tasks
  - tooling/biome
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# Docs App — Index

This section documents the `apps/pixi-skills-docs/` Astro Starlight
documentation site. It is a static site built with bun, deployed to
GitHub Pages or Cloudflare Pages.

## Pages

### [astro-starlight.md](./astro-starlight.md)
Starlight configuration: `astro.config.mjs` setup, sidebar definition,
social links, edit links, custom CSS, and which Starlight features we
use (Pagefind search, dark mode, i18n-ready structure).

### [content-structure.md](./content-structure.md)
The information architecture of the docs site. Section breakdown:
Getting Started, Concepts, Guides, CLI Reference, Architecture,
Reference. What each page covers and why it is ordered that way.

### [custom-components.md](./custom-components.md)
Custom Astro/MDX components: `<SkillCard>`, `<ProviderBadge>`,
`<CLIDemo>`, `<ComparisonTable>`, `<SkillFormatPreview>`. Their props,
usage patterns, and where they appear in the docs.

### [bun-setup.md](./bun-setup.md)
How bun and pixi coexist. Pixi installs bun from conda-forge. Bun runs
Astro scripts. Known historical gotchas (Starlight v0.24.0 locale bug,
Docker build issues). How to diagnose bun-specific build failures.

## Related Sections

- [Tooling/biome](../tooling/biome.md) — Biome lints/formats the TS/JS
  files in this app
- [Pixi/tasks](../pixi/tasks.md) — the `docs-*` pixi tasks that
  orchestrate this app
- [Crates/xtask](../crates/xtask.md) — xtask generates CLI docs and
  JSON schema consumed by this app
