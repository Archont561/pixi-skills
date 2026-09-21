---
type: Reference
title: "pixi-sandbox — Offline Environment Transport"
description: "The sibling project Archont561/pixi-sandbox: git-native offline pixi environment packs, its measured numbers, and what pixi-skills can reuse."
section: landscape
kind: detail
tags: [landscape, pixi-sandbox, offline, airgap, pixi-pack, transport, tooling, p7]
status: stable
created: "2026-09-21"
updated: "2026-09-21"
sources:
  - id: pixi-sandbox-v020
    resource: https://github.com/Archont561/pixi-sandbox/tree/3d7a61825c165c161d4e13df78ee589d0eafc2f1
    title: "Archont561/pixi-sandbox at commit 3d7a618 (release v0.2.0)"
    last_modified: "2026-09-21T14:18:13Z"
  - id: conda-forge-bun
    resource: https://prefix.dev/channels/conda-forge/packages/bun
    title: "conda-forge bun package — published platform list"
---

# pixi-sandbox — Offline Environment Transport

[`Archont561/pixi-sandbox`](https://github.com/Archont561/pixi-sandbox)
is a sibling pixi extension that packs a project's **pixi environments**
into a Git orphan branch and restores them on a machine with no network
access. It is not a skills tool and not a competitor; it is the same
"reproducibility for airlocked machines" thesis that
[Differentiation](./differentiation.md) claims for pixi-skills, already
implemented and measured in Rust.[^pixi-sandbox-v020]

That makes it useful to this project in two distinct ways: as **evidence**
for claims the bundle currently makes without measurements, and as a
**source of hardened invariants** for the deferred
[P7 install-free evaluation proposal](../roadmap/improvement-proposals.md).

> **Verification note (2026-09-21).** Everything below was read from the
> repository at commit `3d7a618` / release `v0.2.0`, published 2026-09-21.
> The project is pre-1.0; re-verify before relying on any flag, schema,
> or size number. The `bun` platform finding was independently
> re-checked against conda-forge on the same date.[^conda-forge-bun]

---

## What It Does

```
connected build machine          orphan branch (Git)          airlocked machine
───────────────────────          ───────────────────          ─────────────────
 pixi.toml + pixi.lock   pack    sandbox/developer-linux-64    .pixi/envs/*
 Cargo.lock             ──────►   ├── pixi-sandbox    ──────►   vendor/
 .pixi/envs/{default,docs}        ├── restore.sh/.ps1           .pixi/tools/
                                  ├── .pixi-sandbox/            offline ✔
                                  │    ├── manifest.json
                                  │    ├── envs/<env>/pack/   (pixi-pack output)
                                  │    ├── tools/<platform>/  (static, sha256-pinned)
                                  │    └── vendor/            (cargo vendor)
                                  └── AGENTS.md
```

Seven verbs, all also reachable as `pixi sandbox <verb>` because pixi
discovers `pixi-<command>` executables on `$PATH`:

| Verb | Role |
|---|---|
| `plan` | Validate `.pixi-sandbox.toml` and emit a GitHub Actions matrix (one job per bundle × platform) |
| `pack` | Build the transport directory: conda payloads + vendored crates + pinned helper tools + a self-binary |
| `doctor` | Verify a transport or branch **without writing** — the CI gate; same code path as restore's preflight |
| `publish` | Force-push the transport as an orphan branch using Git plumbing only |
| `restore` | Verify, then materialize environments, tools, and vendor tree into a project directory |
| `unpack` | Single-environment primitive used by `restore` |
| `tools list` | Show the embedded sha256 pins for `pixi`, `pixi-pack`, `pixi-unpack` |

## Verified Facts (v0.2.0)

| Property | Value |
|---|---|
| Implementation | Pure Rust, static musl on Linux, native on macOS/Windows; no Python |
| License | MIT |
| Distribution | `cargo install pixi-sandbox`, checksum-verified release binaries + `SHA256SUMS`, GitHub Actions (`owner/repo@vX`, `/setup@vX`, `/publish@vX`), a `workflow_call`-reusable publish workflow. A conda package is buildable locally via `pixi publish`; **conda-forge is still planned** |
| Transport | Git orphan branch, whole files content-addressed; dedup comes free across environments and releases |
| Sharding | Files above 95 MiB split into `.partNNN` to stay under GitHub's 100 MiB blob limit. Shards are whole files — chunking would destroy dedup |
| Verification | sha256 checked before anything reaches the working tree; dynamically linked tools are rejected as a bug, not a warning; all failures are collected, not just the first |
| Offline proof | Restore verified inside `unshare -rn` — no conda channel or crates.io traffic |
| Helper pins | `pixi` 0.81.0, `pixi-pack` 0.7.11 (Quantco), `pixi-unpack`, sha256-pinned and compiled into the binary; `--tools-lock` overrides with reviewed data |

Measured on a small reference project (2 environments, 33 crates, linux-64):

| Part | Size |
|---|---|
| conda environments (`.conda`) | 133 MB |
| cargo vendor tree (loose) | 33 MB |
| bundled tools (`pixi`, `pixi-unpack`, self) | 96 MB |
| **transport directory** | **262 MB** |
| **orphan branch after Git dedup** | **~110 MB** |

Tools dominate small bundles. Budget accordingly: an airlock branch is
not a lightweight artifact, and a pixi-skills bundle would carry the
same ~96 MB tool floor before a single skill is added.

Measured on **this repository's** published branch
`sandbox/developer-linux-64` — `pixi-sandbox doctor --verify` on the
restored branch, 2026-09-21 (bundle `developer`, environments `dev` +
`docs`, linux-64, `cargo_vendor = true`):

| Part | Size |
|---|---|
| `dev` environment | 471.8 MiB packed → 1948.3 MiB unpacked (61 blobs) |
| `docs` environment | 85.4 MiB packed → 333.6 MiB unpacked (40 blobs) |
| helper tools (`pixi` 0.81.0, `pixi-unpack` 0.7.11, self 0.2.0) | 94.8 MiB |
| cargo vendor tree (loose, 267 crates) | 310.1 MiB — 32% of the payload |
| **payload total** | **962.1 MiB, 13 816 blobs, 0 verification failures** |

The Rust toolchain is what makes `dev` heavy; vendoring is a third of
the payload, so `cargo_vendor = false` is the lever if a bundle must
shrink. Upstream measured ~110 MB for a two-environment project with
33 crates, so the delta is almost entirely our 267-crate vendor tree.

> **Airlock proof (2026-09-21).** Restored via `scripts/restore.sh` into
> a scratch directory *outside* the workspace, with the project
> manifests copied in (the branch carries environments, not source):
> `pixi run --frozen --offline -e dev build` compiles the whole
> workspace in ~42 s with no package network, and `cargo` reports the
> expected future-incompatibility for `proc-macro-error2 v2.0.1` — the
> unmaintained advisory `deny.toml` ignores. `test` (nextest),
> `lint-rust` (clippy) and `lint-toml` (taplo) also pass from the
> restored tree. Two gates need something the branch does not carry,
> and the reason is not the package payload: `deny` git-clones
> `RustSec/advisory-db` when its per-`CARGO_HOME` cache is cold (a warm
> cache survives the airlock; the yanked check then degrades to a
> warning), and `lint-actions` (actionlint) wants a Git repository with
> `.github/workflows` in it. "Airlock" means no *package* network
> (conda + crates.io), not no network at all.

## Invariants Worth Stealing

These are the parts of the design that are expensive to rediscover, and
they transfer directly to any pixi-skills code that materializes files
into a user's working tree:

1. **Verify before write.** Nothing reaches the tree until its sha256
   matches the manifest; a partially written file is removed on mismatch.
2. **Treat the fetched source as read-only.** Stage elsewhere.
3. **Never use `/tmp` as a work directory.** `pixi-unpack` stages into
   `$TMPDIR`; a small tmpfs fails mid-restore. Default to
   `<project>/.pixi/.restore-work` and redirect `TMPDIR` for children.
4. **Nothing is downloaded at restore time.** The bundle is
   self-contained; CI fetches tools, the airlock never does.
5. **Isolate the side-effecting dependency.** All Git access goes
   through one `GitProtocol` trait with a real `ShellGit` and an
   in-memory `FakeGit`, so tests never shell out and `--dry-run` is not
   a second code path. This is the same argument
   [skills-core](../crates/skills-core.md) makes for `SkillRegistry`.
6. **Gate the config in CI.** A `lint-sandbox-plan` task re-validates
   `.pixi-sandbox.toml` against the embedded tool catalogue on every
   run, so the publish matrix cannot rot. The equivalent for us is a
   lint task that validates `skills.toml` examples against the real
   parser.

## Integration Levels for pixi-skills

Ranked by coupling. `pixi.toml` and `pixi.lock` landed with Phase 0, so
the gate on L0/L1 below is lifted; L2/L3 remain gated on the crate being
pre-1.0.

| Level | What | When | Verdict |
|---|---|---|---|
| **L0 — borrow invariants** | Copy the six rules above into the installer design; no dependency | Recorded above | ✅ Done |
| **L1 — dev/CI tooling** | Pack the `dev` + `docs` environments so airlocked contributors and offline CI can bootstrap the toolchain | Landed 2026-09-21 | ✅ Live |
| **L2 — crate dependency** | Depend on `pixi-sandbox-core` for `shard`/`verify`/`manifest` instead of writing our own | Phase 3–4 at the earliest | ⚠️ Re-evaluate; it is pre-1.0 with no stable-interface promise, and `manifest.json` has its own `SCHEMA_VERSION` |
| **L3 — product surface** | Use `unpack`/`restore` as the sandbox substrate for `pixi skills try` | [P7](../roadmap/improvement-proposals.md), currently "Could" in MoSCoW | ⚠️ Shelling out to `pixi sandbox` beats linking it; both need P7 to be promoted first |

> **Scaffolded, switched on, and measured 2026-09-21.** L0 is recorded
> above and L1 is live: `.pixi-sandbox.toml` declares the `developer`
> bundle (below), `scripts/restore.sh` is the airlock one-liner
> (defaulting to `sandbox/developer-linux-64`, the branch that plan
> produces), and `.github/workflows/publish-sandbox.yml` publishes from
> the pinned `7a2dcb1` (v0.2.0) release binary after `ci` is green on
> `main`. The measured payload of the published branch is in the table
> above.
>
> It consumes that release's **composite actions** but not its **reusable
> workflow**. Verified while wiring this up: the reusable publisher checks the
> project out into `project/` and then runs `prefix-dev/setup-pixi` without
> `working-directory: project`, so `pixi install` finds no manifest and the
> `plan` job dies before a matrix exists. Upstream's own last two
> publish-sandbox runs failed in ~10s at "Install Pixi (local mode)", and
> `Archont561/pixi-sandbox` has no `sandbox/*` branches — the transport works,
> the caller-facing job graph does not. Checking the project out at the
> workspace root and calling `setup-pixi-sandbox` / `publish-pixi-sandbox`
> directly keeps every upstream guarantee (immutable commit, SHA256SUMS
> verification, `doctor --verify`) without a fork.
>
> Release-binary mode remains the only workable mode: upstream *local* mode
> runs `cargo build -p pixi-sandbox` inside the project and calls
> `./project/.github/actions/publish-pixi-sandbox`, neither of which will ever
> exist here. Treat L2/L3 below as still gated on the crate being pre-1.0.

### L1 sketch

This is the file as actually committed. Environments are declared
explicitly — the tool refuses to infer them from `pixi.toml`, because
private test and bench environments should not be published. Only the
`developer` bundle is declared: `release` is not declared until a
release environment exists, and `ci` is deliberately absent (it exists
for the CI solve, and an airlock operator wants the developer surface,
not a union bundle):

```toml
schema = 1
branch_prefix = "sandbox"
cargo_vendor = true          # skills-core + rattler deps must build offline

[[bundle]]
name = "developer"
environments = ["dev", "docs"]
platforms = ["linux-64"]     # the only target it has validated
```

## A Finding That Changes Our Design

`pixi-sandbox` targets `linux-64`, `osx-arm64`, and `win-64`, and records
that **`bun` has no win-64 build on conda-forge** — `pixi lock` fails with
"No candidates were found for bun \*". Its fix scopes `bun` per target so
the Rust workspace keeps win-64 while the docs environment does not.

Re-checked independently against conda-forge on 2026-09-21: `bun` v1.3.11
publishes for `linux-64`, `linux-aarch64`, `osx-64`, and `osx-arm64` —
**no `win-64`**.[^conda-forge-bun] Two consequences for us:

1. The planned platform list plus a `bun` dependency in the `docs`
   feature does not solve on Windows. Corrected in
   [conda-forge Packages](../pixi/conda-forge-packages.md).
2. conda-forge's `bun` is **1.3.11**, not the 1.4.x line that upstream
   Bun ships; the 1.4.x feedstock updates are still open pull requests.
   A `>=1.2` floor is fine, but docs must not promise 1.4 behaviour on a
   conda-provisioned toolchain.

## Caveats

- **Pre-1.0 and moving.** Flags, the `.pixi-sandbox.toml` schema, and
  `manifest.json` are all subject to change. Do not encode them in
  pixi-skills interfaces.
- **linux-64 is the only validated target** in its own reviewed config;
  other platforms have embedded tool pins but no published airlock proof.
- **It is not pixi-pack.** `pixi-pack` (Quantco) produces the
  environment archive; `pixi-sandbox` wraps it with Git transport,
  verification, vendoring, and restore orchestration. Our
  [Pixi Ecosystem](./pixi-ecosystem.md) claims are about pixi-pack and
  remain accurate — this project is one layer above.
- **Not on conda-forge yet,** so a conda-native install path for it is
  not available; that matters if we ever want `pixi-skills` itself to
  provision it declaratively.
- **Weight.** A published branch is ~110 MB for a small project — and
  962.1 MiB for this repository's (measured, table above). It is a
  delivery mechanism for airlocked teams, not a casual artifact.

## Related Concepts

- [Pixi Ecosystem](./pixi-ecosystem.md) — pixi-pack and the layer this project wraps.
- [Differentiation](./differentiation.md) — the offline/airgap advantage this makes measurable.
- [Improvement Proposals](../roadmap/improvement-proposals.md) — P7, the `pixi skills try` substrate question.
- [conda-forge Packages](../pixi/conda-forge-packages.md) — the corrected `bun` platform scoping.
- [skills-provider-conda](../crates/skills-provider-conda.md) — offline channel strategy this validates.
- [skills-core](../crates/skills-core.md) — the same trait-isolation argument as `GitProtocol`.

[^pixi-sandbox-v020]: Repository contents, README, CLI and configuration reference docs, `pixi.toml`, `.pixi-sandbox.toml`, `AGENTS.md`, and `crates/pixi-sandbox-core/assets/tools.lock.json` at the pinned commit in `sources`. Sizes and the `unshare -rn` offline proof are the project's own measurements, not ours.

[^conda-forge-bun]: Platform list and latest version read from the conda-forge `bun` package page in `sources` on 2026-09-21; corroborated by the win-64 solve failure recorded in the pinned `pixi-sandbox` checkout.
