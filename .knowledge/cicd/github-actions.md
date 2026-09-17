---
type: Reference
title: "GitHub Actions"
description: "Planned pixi-based GitHub Actions workflows, caching, and environment selection."
section: cicd
kind: detail
tags: [cicd, github-actions, ci, setup-pixi, caching, workflows]
status: stable
created: "2025-01-01"
updated: "2026-09-17"
---

# GitHub Actions

> **Current checkout:** `.github/workflows/knowledge.yml` is the
> documentation-only validation workflow. It runs the Python validator
> and regression tests described in [Knowledge Format](../conventions/knowledge-format.md).
> The product workflows and version notes below are retained design
> examples, not installed workflows or a new verification of action versions.

In the planned product pipeline, all CI runs through pixi. The GitHub
Actions workflows use `prefix-dev/setup-pixi` to provision the toolchain
from conda-forge, without separate Rust or Bun setup actions.

> **Action versions (verified 2026-09-17):**
>
> | Action | Pinned to | Notes |
> |---|---|---|
> | `actions/checkout` | `v5` | Node-24 runner migration; v4 is legacy |
> | `prefix-dev/setup-pixi` | `v0.10.2` | Pin the **full** version — the action's API can change between minors (official guidance). Pairs with pixi `v0.81.0` |
> | `actions/upload-pages-artifact` | `v5` | v5.x requires `deploy-pages` v4+ |
> | `actions/deploy-pages` | `v5` | Current major |
> | `actions/upload-artifact` / `download-artifact` | `v5` | Artifact actions ship new majors frequently (v7+ adds `archive: false` single-file uploads) — re-check at upgrade time |
> | `EnricoMi/publish-unit-test-result-action` | `v2` | Still the current major (v2.24.x) |
> | `softprops/action-gh-release` | `v2` | Still the current major |

---

## CI Workflow: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  ci:
    name: CI Pipeline
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v5
        with:
          fetch-depth: 0          # Full history for convco

      - name: Setup pixi
        uses: prefix-dev/setup-pixi@v0.10.2
        with:
          environments: all
          cache: true
          cache-key: pixi-${{ hashFiles('pixi.lock') }}

      - name: Run CI
        run: pixi run -e all ci

      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v2
        if: always()
        with:
          files: target/nextest/ci/junit.xml
          check_name: Test Results

      - name: Upload docs artifact
        if: github.ref == 'refs/heads/main'
        uses: actions/upload-pages-artifact@v5
        with:
          path: apps/pixi-skills-docs/dist/
```

### Key Configuration Decisions

#### `fetch-depth: 0`

Full git history is required because:
1. `convco check` validates all commits since the last tag
2. `convco version --bump` counts commit types for version calculation
3. Starlight's `lastUpdated` reads git commit dates per file

Without full history, convco produces incorrect results and
Starlight shows wrong "last updated" dates.

#### `concurrency` with `cancel-in-progress`

If a new commit is pushed while CI is running for the same branch,
the in-progress run is cancelled. This saves runner minutes and
prevents stale results from being reported.

#### `cache: true`

The `setup-pixi` action caches the resolved pixi environment. The
cache key is derived from `pixi.lock` — when dependencies change,
the cache is invalidated. Subsequent runs with the same lockfile
skip the entire dependency installation step.

**Cache savings**: initial environment install takes ~20–30s. Cached
restore takes ~3s.

---

## Docs Deployment: `.github/workflows/deploy-docs.yml`

```yaml
name: Deploy Docs

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: deploy-docs
  cancel-in-progress: true

jobs:
  build:
    name: Build Docs
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - uses: prefix-dev/setup-pixi@v0.10.2
        with:
          environments: all
          cache: true

      - name: Build docs
        run: pixi run -e all docs-build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v5
        with:
          path: apps/pixi-skills-docs/dist/

  deploy:
    name: Deploy to GitHub Pages
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v5
```

### Deployment Flow

```
Push to main
  → Build job: pixi run -e all docs-build
    → cli-docs (cargo xtask) → generates MDX
    → schema (cargo xtask) → generates JSON Schema
    → docs-build-raw (bun run build) → generates dist/
  → Upload dist/ as pages artifact
  → Deploy job: deploy to GitHub Pages
```

### Alternative: Cloudflare Pages

If deploying to Cloudflare Pages instead of GitHub Pages:

```yaml
- name: Deploy to Cloudflare Pages
  uses: cloudflare/pages-action@v1
  with:
    apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
    accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
    projectName: pixi-skills-docs
    directory: apps/pixi-skills-docs/dist/
```

---

## Matrix Builds (Optional)

For cross-platform testing, add a matrix strategy:

```yaml
jobs:
  ci:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
      - uses: prefix-dev/setup-pixi@v0.10.2
        with:
          environments: all
          cache: true
      - run: pixi run -e all ci
```

**When to enable matrix builds**:
- After MVP, when cross-platform correctness matters
- Focus on `ubuntu-latest` for MVP to keep CI fast and cheap

---

## CI Performance Optimization

### Parallelism via separate jobs

For large projects, split CI into parallel jobs:

```yaml
jobs:
  fmt:
    runs-on: ubuntu-latest
    steps: [checkout, setup-pixi, pixi run -e all fmt-check-all]

  lint:
    runs-on: ubuntu-latest
    steps: [checkout, setup-pixi, pixi run -e all lint-all]

  test:
    runs-on: ubuntu-latest
    steps: [checkout, setup-pixi, pixi run test, pixi run test-doc]

  docs:
    runs-on: ubuntu-latest
    needs: [lint]    # docs-build needs xtask which needs Rust to compile
    steps: [checkout, setup-pixi, pixi run -e all docs-build]
```

**Trade-off**: parallel jobs start faster but each needs its own
pixi install (even if cached, it's ~3s per job). For a small project,
a single job is simpler and often faster overall.

**Recommendation for MVP**: single job. Split when CI exceeds 5 minutes.

---

## Secrets and Tokens

| Secret | Purpose | Required? |
|---|---|---|
| `GITHUB_TOKEN` | Automatic — used for checkout, pages deploy, API requests | Auto-provided |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Pages deployment | Only if using CF |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Pages deployment | Only if using CF |
| `CARGO_REGISTRY_TOKEN` | Publishing to crates.io | Only for release workflow |
| `PREFIX_DEV_TOKEN` | Publishing to prefix.dev channels | Only for release workflow |

---

## Debugging CI Failures

### Reproduce locally

```bash
# Run the exact same command CI runs:
pixi run -e all ci

# If that passes locally but fails in CI, check:
# 1. git history (local may have more commits than CI)
# 2. pixi.lock (local may be newer than pushed)
# 3. bun.lock (same concern)
```

### CI-specific issues

| Symptom | Likely cause | Fix |
|---|---|---|
| `convco check` fails | Shallow clone | Ensure `fetch-depth: 0` |
| `bun install` fails | `bun.lock` out of sync | Run `bun install` locally, commit `bun.lock` |
| `cargo deny` fails on new advisory | New RustSec advisory published | Evaluate advisory, ignore if not applicable |
| Pixi cache miss on every run | `pixi.lock` changed | Expected — cache rebuilds after lockfile changes |
| Timeout | Large dependency tree, slow conda-forge mirror | Increase timeout, check conda-forge status |

### Viewing CI logs

The `pixi run -e all ci` command runs all tasks in dependency order.
If a step fails, the log shows which specific task failed:

```
✅ fmt-check-rust
✅ fmt-check-toml
✅ fmt-check-ts
✅ lint-rust
❌ lint-deps        ← cargo deny found advisory RUSTSEC-2025-XXXX
```

The JUnit XML output (from nextest) provides per-test results
rendered as PR annotations via `publish-unit-test-result-action`.

## Related Concepts

- [CI/CD — Context](./CONTEXT.md)
- [Release Workflow](./release-workflow.md)
- [Pixi Tasks](../pixi/tasks.md)
- [Pixi Environments](../pixi/environments.md)
