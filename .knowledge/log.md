# Knowledge Bundle Update Log

## 2026-09-21

- **Landscape**: Added [pixi-sandbox](./landscape/pixi-sandbox.md), a reference page on the sibling project `Archont561/pixi-sandbox` v0.2.0 — git-native offline pixi environment transport, verified against the repository at commit `3d7a618`, with its measured payload sizes, restore invariants, and four ranked integration levels gated on the workspace existing.
- **Correction**: Recorded that conda-forge has no `win-64` build of `bun` (independently re-verified: v1.3.11 ships `linux-64`, `linux-aarch64`, `osx-64`, `osx-arm64`), so the planned four-platform workspace with an unscoped `bun` dependency would not solve on Windows. [conda-forge Packages](./pixi/conda-forge-packages.md) now prescribes per-target scoping, notes that conda-forge lags upstream Bun 1.4.x, and proposes a per-platform solve gate in CI.
- **Evidence**: Turned the previously unmeasured offline/airgap differentiator into a cited one in [Differentiation](./landscape/differentiation.md), [Pixi Ecosystem](./landscape/pixi-ecosystem.md), and the offline section of [skills-provider-conda](./crates/skills-provider-conda.md).
- **Roadmap**: Named `pixi-sandbox` as a candidate sandbox substrate for the deferred P7 `pixi skills try` proposal in [Improvement Proposals](./roadmap/improvement-proposals.md), recommending invariant reuse over a crate dependency while the upstream project is pre-1.0.
- **CI**: Replaced `.github/workflows/knowledge.yml` with a single `.github/workflows/ci.yml` copying the `Archont561/pixi-sandbox@7a2dcb1` layout. A `probe` job gates every pixi and Cargo step on `pixi.toml` plus `pixi.lock` existing, so the file merges before Phase 0 without going red; OKF validation moved in as the `knowledge` job that runs today. Recorded in [GitHub Actions](./cicd/github-actions.md).
- **Sandbox publishing**: Added `.github/workflows/publish-sandbox.yml` as a thin caller of the upstream reusable publisher in release-binary mode, pinned to commit `7a2dcb1` (v0.2.0) and passing only inputs that workflow declares; `.pixi-sandbox.toml` declaring the `developer` and `release` bundles for `linux-64`; `scripts/restore.sh` for airlock reconstruction; `.github/dependabot.yml` to maintain the SHA pins; and `.gitignore` entries for generated transport weight. Documented in [pixi-sandbox](./landscape/pixi-sandbox.md).

## 2026-09-17

- **Format**: Adopted [OKF v0.2](./conventions/knowledge-format.md) and declared the target version in the [root index](./index.md).
- **Navigation**: Renamed all ten `INDEX.md` files to the reserved lowercase `index.md`, removed index metadata except the root version, and made every section's context discoverable.
- **Metadata**: Added descriptive `type` and `description` fields to the fifty inherited concepts. Preserved local `section`, `kind`, and editorial date fields without inventing provenance or verification events.
- **Relationships**: Converted all 223 `relates_to` references into Markdown navigation and repaired the absent docs-site migration link in [skills.sh](./landscape/skills-sh.md).
- **Maintenance**: Added the [authoring and migration guide](./conventions/knowledge-format.md), this update log, structural validation, opt-in repository lint, regression tests, and a GitHub Actions check.
- **Scope**: Clarified that the bundle describes a planned product and that format validation is not a new factual review of its technical or ecosystem claims.
