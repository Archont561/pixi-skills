---
title: "CI/CD — Index"
section: cicd
kind: index
tags: [cicd, index, navigation, github-actions, release, dist]
relates_to:
  - pixi/tasks
  - pixi/environments
  - crates/xtask
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# CI/CD — Index

This section documents the continuous integration and delivery pipeline.
All CI steps are executed through pixi — there are no shell scripts or
ad-hoc tool installations in CI.

## Pages

### [github-actions.md](./github-actions.md)
The CI workflow: `prefix-dev/setup-pixi` action, environment selection,
caching strategy, matrix builds (if any), and the single
`pixi run -e all ci` command that runs everything. Why `fetch-depth: 0`
is required for convco.

### [release-workflow.md](./release-workflow.md)
The full release pipeline: convco validates commits → convco calculates
next version → xtask bumps all Cargo.toml versions → convco generates
changelog → git commit + tag → (optional) GitHub Release. Manual vs.
automated triggering.

### [dist.md](./dist.md)
Cross-compilation targets, binary naming conventions, tarball structure,
SHA256 checksums, and how `cargo xtask dist` produces release artifacts.
Integration with GitHub Releases for binary distribution.

## Related Sections

- [Pixi/tasks](../pixi/tasks.md) — CI runs pixi tasks
- [Pixi/environments](../pixi/environments.md) — CI uses the `all`
  environment
- [Crates/xtask](../crates/xtask.md) — xtask handles release + dist
- [Tooling/convco](../tooling/convco.md) — convco drives the release
  version calculation
