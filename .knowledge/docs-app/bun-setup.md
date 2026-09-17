---
title: "Bun Setup"
section: docs-app
kind: detail
tags: [docs, bun, pixi, setup, gotchas, compatibility, node]
relates_to:
  - docs-app/CONTEXT
  - docs-app/astro-starlight
  - pixi/environments
  - pixi/conda-forge-packages
status: stable
created: 2025-01-01
updated: 2026-09-17
---

# Bun Setup

How bun and pixi coexist in the pixi-skills monorepo. Pixi installs
bun from conda-forge, bun runs Astro scripts, and pixi tasks
orchestrate everything.

---

## Installation Model

Bun is **not** installed globally on the system. It is a pixi
dependency:

```toml
# pixi.toml
[feature.docs.dependencies]
bun = ">=1.2"
```

This means:
- Bun is installed to `.pixi/envs/docs/bin/bun`
- Bun version is pinned in `pixi.lock`
- Every developer and CI runner uses the exact same bun version
- No `curl -fsSL https://bun.sh/install | bash` needed

> **Updated 2026-09-17:** floor raised from 1.1 → 1.2. The 1.4.x line
> is current as of mid-2026 and brings near-complete Node.js API
> compatibility (~99%+ of the top-1000 npm packages run on Bun), a
> faster test runner with parallel execution, and native Windows ARM64
> support. The locale/compat issues from the 1.1 era (see "Known
> Historical Gotchas" below) are long resolved.

### Accessing bun

```bash
# Via pixi (recommended)
pixi run -e docs -- bun --version

# Direct path (escape hatch)
.pixi/envs/docs/bin/bun --version

# Inside pixi shell
pixi shell -e docs
bun --version
```

---

## Package Management

Bun manages JS dependencies for the docs app via `package.json` and
`bun.lock`.

### Initial Setup

```bash
pixi run -e docs -- bun create astro --template starlight apps/pixi-skills-docs
```

Or if the project already exists:

```bash
pixi run -e docs docs-install    # runs: bun install --frozen-lockfile
```

### Adding Dependencies

```bash
pixi run -e docs -- bun add <package>          # production dep
pixi run -e docs -- bun add --dev <package>    # dev dep
```

### The `--frozen-lockfile` Flag

The `docs-install` pixi task uses `--frozen-lockfile`:

```toml
docs-install = { cmd = "bun install --frozen-lockfile", cwd = "apps/pixi-skills-docs" }
```

This ensures:
- CI never silently updates dependencies
- If `bun.lock` is out of sync with `package.json`, the install fails
- Developers must explicitly run `bun install` (without `--frozen`)
  and commit the updated `bun.lock`

---

## bun.lock Location

The `bun.lock` file lives inside the docs app directory:

```
apps/pixi-skills-docs/
├── package.json
├── bun.lock           # ← Here, not at workspace root
├── node_modules/      # ← Here, not at workspace root
└── ...
```

This is intentional — the docs app is the only JS workload. There
is no bun workspace at the root level. If future apps are added, each
gets its own `package.json` + `bun.lock` (or we add a root-level bun
workspace at that point).

---

## Node.js Compatibility

Some Astro dependencies may require Node.js APIs that bun doesn't
fully implement. Mitigation strategies:

### Strategy 1: pixi provides Node.js as a fallback

```toml
[feature.docs.dependencies]
bun = ">=1.2"
nodejs = ">=22"     # Fallback for compatibility. Floor raised 20 → 22 (2026-09):
                    # Astro 6 requires Node 22+; Node 24 is the Active LTS line.
```

Node.js is available in the docs environment but not used by default.
If bun hits a compatibility issue, the `docs-*` tasks can be switched
to use `node` / `npx`:

```toml
# Emergency fallback (only if bun breaks)
docs-dev-node = { cmd = "npx astro dev", cwd = "apps/pixi-skills-docs" }
```

### Strategy 2: Pin bun to a known-good version

If a specific bun version has a regression, pin it exactly:

```toml
bun = "=1.2.21"     # Pinned due to issue #XYZ (example — use the actual known-good version)
```

---

## Known Historical Gotchas

### Starlight v0.24.0 + bun locale issue (mid-2024)

**Issue**: Starlight v0.24.0 broke compatibility with bun due to
a locale-related runtime difference. v0.23.4 was the last working
version with that bun release.

**Status**: resolved long ago — Bun 1.2+ (and certainly the current
1.4.x line) no longer exhibits this. Kept for historical reference
only. If ever encountered, the fix is to update bun via pixi:

```bash
pixi update bun    # Update to latest bun on conda-forge
```

### astro-expressive-code Docker build failure (mid-2024)

**Issue**: The `astro-expressive-code` package failed during Docker
builds with bun due to a platform detection issue.

**Status**: likely resolved. If encountered in CI (which uses
containers), test with `nodejs` as the runtime:

```bash
pixi run -e docs -- node node_modules/.bin/astro build
```

### bun + sharp (image optimization)

**Issue**: Astro uses `sharp` for image optimization. Sharp has
native binaries that may not be available for all platforms in bun's
install mode.

**Solution**: pixi can provide `sharp` via conda-forge if needed:
```toml
[feature.docs.dependencies]
sharp = ">=0.33"
```

Or disable image optimization in `astro.config.mjs`:
```javascript
export default defineConfig({
  image: { service: { entrypoint: 'astro/assets/services/noop' } },
});
```

---

## pixi ↔ bun Interaction Model

```
┌──────────────────────────────────────────────────────────┐
│                      pixi.toml                           │
│                                                          │
│  [feature.docs.dependencies]                             │
│  bun = ">=1.1"              ←── pixi installs bun       │
│                                                          │
│  [feature.docs.tasks]                                    │
│  docs-install = "bun install --frozen-lockfile"           │
│  docs-dev     = "bun run dev"    ←── pixi runs bun      │
│  docs-build   = "bun run build"                          │
│                                                          │
│  Bun is just another tool in the pixi environment.       │
│  pixi doesn't know or care what bun does internally.     │
│  bun doesn't know it was installed by pixi.              │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│              apps/pixi-skills-docs/                       │
│                                                          │
│  package.json                                            │
│  ├── dependencies: astro, @astrojs/starlight             │
│  └── scripts: dev, build, preview, check                 │
│                                                          │
│  bun.lock ←── bun manages JS deps                        │
│  node_modules/ ←── bun installs JS deps here             │
│                                                          │
│  Bun manages its own dependency world.                   │
│  pixi manages bun itself.                                │
│  Two lockfiles, zero conflict.                           │
└──────────────────────────────────────────────────────────┘
```

### The Two-Lockfile Model

| Lockfile | Managed by | Contains | Scope |
|---|---|---|---|
| `pixi.lock` | pixi | Rust, bun, biome, taplo, cargo-deny, cargo-nextest, system libs | Entire workspace |
| `bun.lock` | bun | Astro, Starlight, @astrojs/check, Astro dependencies | Docs app only |

Both lockfiles are committed to git. Both must be kept in sync with
their respective manifest files (`pixi.toml` and `package.json`).

---

## Debugging bun Issues

### Check which bun pixi installed

```bash
pixi run -e docs -- bun --version
pixi run -e docs -- which bun
```

### Check if bun can resolve all dependencies

```bash
pixi run -e docs -- bun install --dry-run
```

### Check for bun-specific runtime errors

```bash
# Run with verbose logging
pixi run -e docs -- bun run build --verbose 2>&1 | tee build.log
```

### Fall back to Node.js for diagnosis

```bash
# If bun fails, test with node to isolate the issue
pixi run -e docs -- npx astro build
# If node works and bun doesn't → bun compatibility issue
# If both fail → Astro/Starlight issue
```

---

## Updating Dependencies

### Bun version (via pixi)

```bash
pixi update bun                  # Update bun to latest in conda-forge
pixi run -e docs -- bun --version  # Verify new version
pixi run -e docs docs-build      # Test the build
git add pixi.lock
git commit -m "chore(docs): update bun"
```

### JS dependencies (via bun)

```bash
pixi run -e docs -- bun update              # Update all JS deps
pixi run -e docs docs-build                 # Test the build
cd apps/pixi-skills-docs && git add bun.lock package.json
git commit -m "chore(docs): update JS dependencies"
```

### Astro major version upgrade

```bash
pixi run -e docs -- bun add astro@latest @astrojs/starlight@latest
pixi run -e docs docs-build                 # Test the build
# Review breaking changes in Astro/Starlight release notes
```
