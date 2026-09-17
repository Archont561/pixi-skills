---
title: "Improvement Proposals — 2026-09 Strategy Review"
section: roadmap
kind: detail
tags: [roadmap, proposals, strategy, differentiation, standard, security]
relates_to:
  - roadmap/mvp-phases
  - landscape/agent-skills-standard
  - landscape/skills-sh
  - landscape/differentiation
  - conventions/skill-format
status: draft
created: 2026-09-17
updated: 2026-09-17
---

# Improvement Proposals — 2026-09 Strategy Review

Eight product proposals, drafted after the 2026-09-17 knowledge-base
refresh. Each is presented as a **mental model**, not an
implementation — graphs and pseudocode only. Sequencing guidance maps
onto the existing [MVP phases](./mvp-phases.md).

> **✅ Adoption status (2026-09-17): P0, P1 and P4 are ACCEPTED** —
> **P0/P4 → ADR-008**, **P1 → ADR-009** (index search folded into
> `skills-provider-github`; separate provider crate rejected).
> **P2 and P3 remain the open proposals** (P5/P6/P7 deferred with
> their phase gates). Content below is design rationale.

### Trigger: what changed in the world

```
2025-H2                         2026
────────────────────────────────┼───────────────────────────────────
 skills = single SKILL.md       │  Dec 18  agentskills.io open standard
 files, per-agent dialects      │           (26+ platforms adopt)
                                │  Jan 20  skills.sh launches → 83k skills,
 our thesis: "nobody has        │           8M installs, Snyk scan, 70+ agents
 a lockfile"  ── invalidated ──>│  Feb–Jun skills-lock wrappers: SHA pins,
                                │           --frozen CI, integrity trees (
                                │           our differentiator, done as glue)
 security = theoretical concern │  ClawHavoc malware via skill hub;
                                │  ~13% of sampled skills critically
                                │  insecure → enterprise fear is REAL
────────────────────────────────┴───────────────────────────────────
Conclusion: keep the mission, re-aim the differentiators.
```

---

## Proposals at a glance

| # | Proposal | Type | Impact | Effort | Phase fit | Status |
|---|---|---|---|---|---|---|
| P0 | Folder-shaped, spec-native skill packaging (agentskills.io) | Format foundation | 🔥🔥🔥 | M | Phase 0 | ✅ **ADR-008** |
| P1 | skills.sh as a *provider* (`@skill` sources, their index) — meet users where they are | Adoption | 🔥🔥🔥 | S | Phase 1+ | ✅ **ADR-009** |
| P2 | Manifest/lock split with **semantic** version resolution | Core differentiator | 🔥🔥🔥 | M | Phase 4 | ⏳ proposal |
| P3 | Skill trust pipeline: lint → verify → policy (`skills audit`) | Security moat | 🔥🔥🔥 | M | Phase 4+ | ⏳ proposal |
| P4 | Provider trait v2: versions(), folder bundles, content hashes | Enabler | 🔥🔥 | S | Phase 0/1 | ✅ **ADR-008** |
| P5 | `pixi skills init` + first-party authoring toolchain | Supply side | 🔥🔥 | S | Phase 2 | ⏳ proposal |
| P6 | Agent-capability graph beyond skills (MCP, hooks, rules) | Expansion | 🔥🔥 | L | Phase 5+ | ⏳ proposal |
| P7 | Install-free evaluation (`pixi skills try`) via pixi sandboxes | UX edge | 🔥 | M | Phase 3+ | ⏳ proposal |

> **Non-goals for 2026:** building a public skills portal/leaderboard
> (skills.sh owns discovery — integrate, don't fight), and a hosted
> "skills registry SaaS" before the CLI proves pull.
>
> Background docs: format & landscape evidence →
> `landscape/agent-skills-standard.md`, `landscape/skills-sh.md`,
> `landscape/differentiation.md` (all updated today).

---

## P0 — Skill folder + spec-native format (foundation)

**Status: ✅ ACCEPTED 2026-09-17 as ADR-008.** The "envelope, not
owner" model below was adopted verbatim; companion `skill.toml` is
the chosen extension mechanism (option d). See
`conventions/skill-format.md` for the normative spec.

**Mental model — "envelope, not owner":** pixi-skills manages the
*lifecycle envelope* around a standard artifact; the artifact's
content remains 100% agentskills.io-compliant.

```
        ┌───────────────────────────────────────────────┐
        │ skill folder (standard, portable, agent-owned) │
        │  SKILL.md  scripts/  references/  assets/      │
        ├───────────────────────────────────────────────┤
        │ envelope (manager-owned):                      │
        │  companion skill.toml / lock entry:            │
        │  source, resolved-ref, hashes, deps, policy    │
        └───────────────────────────────────────────────┘
```

**Why:** folders are the spec unit; managing single files would
exclude every real skill (Anthropic's doc skills ship scripts).
Companion metadata keeps spec purity → zero risk of breaking 26+
agent loaders. Conda provider already wins here: an unpacked
`.conda` *is* a directory tree — folder skills map 1:1.

---

## P2 — Manifest/lock split with semantic resolution (core)

Differentiate above SHA-pinners (`skills-lock` wrappers) which record
*what you got*, not *what you asked*.

**Mental model:** cargo/pixi semantics applied to a heterogeneous
provider world — constraints are user intent; the lockfile is a
solved, hashed artifact; drift is impossible by construction.

```toml
# skills.toml  (intent)
[skills]
web-design = { github = "vercel-labs/agent-skills", skill = "web-design-guidelines", ref = "~1.4" }
pdf        = { conda  = "skill-pdf", version = ">=1,<3" }
```

**Resolution pseudocode:**

```pseudo
fn solve(manifest, providers, old_lock?) -> lockfile:
    for req in manifest.skills:
        provider  = providers[req.source_kind]
        universe  = provider.versions(req.name)            # tags | repodata
        matching  = filter(universe, satisfies(req.constraint))
        pick      = policy(matching, prefer: old_lock.pin) # minimal-change
        hash      = provider.content_hash(pick)            # deterministic
        lock.record(req, pick, hash, provider_attestation)
    verify_disjoint_install_paths(lock)       # no two skills → same name
    return lock                                            # deterministic TOML
```

Upgrade policy is the alpha: `update` moves **inside declared
constraints only**. `check` (skills.sh parity) comes free as
`solve()` with `dry_run`.

---

## P4 — Provider trait v2 changes implied by P0–P2

Minimal trait deltas, pseudocode-level:

```pseudo
trait SkillRegistry:
    search(query) -> [SkillSummary]                       # unchanged
    versions(name) -> [Version]                                       # NEW
    fetch(name, version) -> SkillBundle                 # dir,  was: file
    content_hash(bundle) -> Hash  -- canonical: walk dir, sort paths,
                                     sha256(path‖mode‖blob) per file # NEW
```

Consequence: `skills-provider-github` resolves tag→SHA **and**
surfaces tag *names* as the version axis (semver-looking tags get
ranges; non-semver tags stay exact-pins with a warning).

---

## P3 — Trust pipeline: `pixi skills audit` (security moat, big)

skills.sh scans its *directory* (Snyk) — advisory, pre-install,
opt-out. Nothing enforces **at install**, **per project**, with an
**audit trail**. That's the enterprise-will-pay lane.

**Mental model — staged trust funnel:**

```
   untrusted ecosystem                    your repo
 ┌────────────────────┐            ┌──────────────────────┐
 │ 83k skills, ~13%    │  lint     │ policy file           │  lock
 │ critically insecure │──────────>│ .pixi/skill-policy.   │──────> CI
 └────────────────────┘  (static   │ toml: allow/deny,     │  --frozen
                        analysis)  │ max-permissions,      │  (enforce)
                                   │ trusted-publishers    │
                                   └──────────────────────┘
```

`pixi skills audit` checks, layered:

1. **Static**: YAML frontmatter sanity; `allowed-tools` over-broad?
   shell-out patterns / network exfil markers in `scripts/`; prompt-
   injection signatures in body (imperative redirects, base64 blobs).
2. **Provenance**: lockfile hash ✓; source repo signals (stars,
   publisher identity); conda: package signed channel? (future:
   sigstore attestation on `skill-*` repodata).
3. **Policy**: org-defined rules; `deny on new-permissions-diff` —
   a skill update that widens `allowed-tools` fails CI loudly.

**Pseudocode:**

```pseudo
fn audit(skill, lock, policy) -> Verdict:
    findings  = static_scan(skill.bundle)            # layer 1
    findings += provenance_check(skill, lock)        # layer 2
    verdict   = policy.evaluate(findings, delta_of(
                    old = lock.prev(skill), new = skill))
    emit(verdict, format: human | sarif)             # GitHub code-
    exit(verdict.ok ? 0 : 1)                         # scanning ready
```

SARIF output ~= free PR annotations; "ClawHavoc would have failed
here" is the launch-story headline.

---

## P1 — skills.sh as a *provider*: adopt, don't fight

**Status: ✅ ACCEPTED 2026-09-17 as ADR-009.** Design refinement from
the accepted decision: the index search folds **into
`skills-provider-github`** (no separate crate — the trait seam is
the search index, not the transport), with graceful degradation to
GitHub-native search on index outage. Public portal stays a 2026
non-goal. Original rationale below.

They own discovery (83k skills, the leaderboard). We own
lifecycle. A `skills-provider-skillssh` crate wraps their public
index + git backend: users get `pixi skills find` across their corpus
with *our* lockfile, *our* audit, *our* installs. Transforms the
competitive frame from "rival CLI" to "the enterprise shell around
the ecosystem."

**Mental model:** Homebrew vs Casks — the formula index is public,
the value is the manager.

---

## P5 — `pixi skills init` + authoring toolchain (supply side)

Distribution needs supply. Scaffolding + validation in one command:

```pseudo
init(name):
    scaffold dir: SKILL.md (valid YAML, description-template),
                  references/, skill.toml
    lint --fix; suggest stronger description (activation quality)
publish-flow: conda recipe codegen (rattler-build, noarch)
              → channel publish → "now findable via pixi skills find"
```

Dogfood: ship our `.knowledge/` as `skill-pixi-skills-devdocs` —
an installable "how this repo works" skill (meta-proof the format).

---

## P6 — Agent-capability graph (expansion, post-MVP)

Skills are one node type in what agents load. The emerging graph:

```
        ┌────────┐   configures   ┌─────────┐
        │ skills │───────────────>│  agents  │┐
        └────────┘                └─────────┘│ installs into 70+
 ┌──────┴───────┐                    ▲   ▲   │ agent × project
 │ MCP servers  │──provides tools───┘   │   │ matrix
 ├──────────────┤                       │
 │ hooks/rules/ │──behavior─────────────┘
 │ agents.md    │
 └──────────────┘
```

Lockfile-scoped MCP server configs (pixi already solves *their*
binaries!) is the adjacent wedge: `skills.toml` could declare
`[mcp] playwright = { pkg = "mcp-playwright" }` and pixi provisions
the binary deterministically. Vision: **one manifest for everything
an agent consumes**. (Post-MVP; sec-risk research needed.)

---

## P7 — `pixi skills try` (install-free evaluation)

pixi's unique UX wedge: `pixi exec`-style ephemeral env per skill.

```
pixi skills try github:anthropics/skills@pdf
  → resolve+fetch to content-addressed store
  → mount into a throwaway sandbox (cwd copy or worktree)
  → generate temp agent config pointing only at this skill
  → spawn agent / print prompt; discard on exit
```

Evaluating a skill stops mutating the repo — security and hygiene in
one move. No competitor can do this without an environment manager;
we're built on one.

---

## Sequencing (merges into MVP phases)

```
Phase 0  skills-core          + folder model (P0), trait v2 (P4)
Phase 1  provider-github      + skills.sh index source (P1-lite)
Phase 2  CLI                  + init (P5), try (P7 if cheap)
Phase 3  provider-conda       + folder extraction ✓ native
Phase 4  lockfile             + audit/policy (P3)  ← THE release
Phase 5  providers            + MCP manifest reading (P6 spike)
```

**Release narrative:** v0.x = "reproducible skills"; v1.0 =
"the enterprise skill supply chain: lock + audit + policy + private
channels". Skills lock-in fear + ClawHavoc anxiety are the storm;
we ship the lighthouse.

### MoSCoW

- **Must**: P0, P2, P4 (deltas), P3-static-scan
- **Should**: P1, P5, audit SARIF/policy
- **Could**: P7, provenance/sigstore spike
- **Won't (yet)**: P6 full, public portal, hosted registry SaaS
