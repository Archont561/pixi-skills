---
title: "cargo-nextest"
section: tooling
kind: detail
tags: [tooling, cargo-nextest, testing, parallel, junit, ci]
relates_to:
  - tooling/CONTEXT
  - pixi/tasks
  - cicd/github-actions
  - conventions/config-files
status: stable
created: 2025-01-01
updated: 2025-01-01
---

# cargo-nextest

A next-generation test runner for Rust. Runs each test in its own
process, enabling true parallelism, per-test timeouts, retries,
and JUnit XML output for CI integration.

---

## Installation

```toml
# pixi.toml
[feature.lint.dependencies]
cargo-nextest = ">=0.9"
```

Installed via pixi from conda-forge. Replaces `cargo test` for
all workspace test execution.

---

## Configuration: `.config/nextest.toml`

```toml
# .config/nextest.toml

[store]
# Directory for nextest's internal state
dir = "target/nextest"

# ── Default Profile ────────────────────────────────────────────────
[profile.default]
# Run tests with moderate parallelism
test-threads = "num-cpus"

# Per-test timeout — prevents hung tests from blocking CI
slow-timeout = { period = "30s", terminate-after = 2 }

# Fail fast — stop on first failure during local development
fail-fast = true

# Status level — show pass/fail/skip for each test
status-level = "pass"

# Final status — show summary at the end
final-status-level = "fail"

# ── CI Profile ─────────────────────────────────────────────────────
[profile.ci]
# Run all tests even after failures — collect full failure report
fail-fast = false

# Stricter timeout in CI
slow-timeout = { period = "20s", terminate-after = 2 }

# JUnit XML output for CI test reporting
junit = { path = "target/nextest/ci/junit.xml" }

# Retry flaky tests up to 2 times
retries = 2

# Status level — show only failures (less noise in CI logs)
status-level = "fail"
final-status-level = "all"

# ── Live Test Profile ──────────────────────────────────────────────
# For integration tests that hit real external services
[profile.live]
# Override filter to include live-tests feature
default-filter = "not test(/^ignored/)"

# Longer timeout for network operations
slow-timeout = { period = "120s", terminate-after = 1 }

# No retries — live tests should be deterministic
retries = 0

# Sequential — avoid overwhelming external APIs
test-threads = 1
```

---

## Why nextest Over `cargo test`

| Feature | `cargo test` | `cargo nextest run` |
|---|---|---|
| Execution model | Tests in same process | Each test in its own process |
| Parallelism | Thread-based (shared state risks) | Process-based (true isolation) |
| Per-test timeout | ❌ Not supported | ✅ `slow-timeout` with auto-terminate |
| Retry flaky tests | ❌ Not supported | ✅ `retries = N` |
| JUnit XML output | ❌ Requires external tools | ✅ Built-in `junit` option |
| Fail-fast control | ❌ Limited | ✅ Per-profile `fail-fast` |
| Test filtering | `--test`, `--lib`, name filter | All of those + regex, partition |
| Output | Text only | Text + JUnit XML + custom reporters |
| Speed | Sequential by default | Parallel by default, optimized scheduling |

The key benefit for pixi-skills: **per-test timeouts prevent CI hangs.**
Integration tests (especially those involving network or file I/O) can
hang indefinitely. nextest's `slow-timeout` with `terminate-after`
kills stuck tests after a grace period.

---

## pixi Task Integration

```toml
# pixi.toml
[feature.rust.tasks]
test     = "cargo nextest run --workspace"
test-doc = "cargo test --workspace --doc"
```

**Note**: `cargo nextest` does not support doc tests. Doc tests
(`/// ``` ... ````) still run via `cargo test --doc`. This is a
known nextest limitation. We have two separate test tasks.

### Profile Selection

```bash
# Local development (default profile: fail-fast)
pixi run test

# CI (ci profile: no fail-fast, JUnit output, retries)
pixi run -- cargo nextest run --workspace --profile ci

# Live integration tests
pixi run -- cargo nextest run --workspace --profile live --features live-tests
```

---

## Test Partitioning (Future)

nextest supports test partitioning for parallel CI jobs:

```bash
# Job 1 of 3
cargo nextest run --partition count:1/3

# Job 2 of 3
cargo nextest run --partition count:2/3

# Job 3 of 3
cargo nextest run --partition count:3/3
```

This is not needed at the MVP stage but becomes valuable if the test
suite grows large. Each CI job runs a different partition, reducing
total CI time.

---

## JUnit XML Integration

The CI profile generates `target/nextest/ci/junit.xml`. This file
can be consumed by GitHub Actions for test reporting:

```yaml
# .github/workflows/ci.yml
- name: Test
  run: pixi run -- cargo nextest run --workspace --profile ci

- name: Publish Test Results
  uses: EnricoMi/publish-unit-test-result-action@v2
  if: always()
  with:
    files: target/nextest/ci/junit.xml
```

This renders test results as annotations on the PR, with expandable
failure details.

---

## Common Patterns

### Running tests for a specific crate

```bash
pixi run -- cargo nextest run -p skills-core
pixi run -- cargo nextest run -p skills-provider-github
```

### Running a specific test by name

```bash
pixi run -- cargo nextest run -E 'test(manifest::parse)'
```

### Running only tests that changed

nextest doesn't have built-in change detection, but you can combine
it with `cargo nextest list` and external filtering. In practice,
`cargo nextest run --workspace` is fast enough for the full suite.

### Archiving and replaying test runs

```bash
# Archive test results for later analysis
cargo nextest run --workspace --archive-file tests.tar.zst

# Replay on another machine (no compilation needed)
cargo nextest run --archive-file tests.tar.zst
```

This is useful for reproducing CI failures locally without
recompiling.
