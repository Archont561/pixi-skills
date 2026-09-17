---
title: "Agent Skills Open Standard"
section: landscape
kind: detail
tags: [landscape, agentskills, standard, SKILL.md, anthropic, spec]
relates_to:
  - landscape/CONTEXT
  - landscape/skills-sh
  - landscape/differentiation
  - conventions/skill-format
status: stable
created: 2026-09-17
updated: 2026-09-17
---

# Agent Skills Open Standard

On **2025-12-18**, Anthropic published **Agent Skills** as an open
standard at [agentskills.io](https://agentskills.io) — the same
playbook they used for MCP (solve a real interop problem, release the
spec, let adoption create network effects). Within months, **26+
platforms** adopted it: Claude (Code/Desktop/API), OpenAI Codex,
Gemini CLI, GitHub Copilot (announced Dec 2025), Cursor, VS Code,
OpenCode, and more. Partner skills from Atlassian, Canva, Figma,
Notion, Stripe, Zapier and others shipped at launch.

This page summarizes the spec as it affects pixi-skills. It is the
**single most important landscape document** for our format
decisions.

---

## Spec Essentials

### A skill is a directory, not a file

```
my-skill/
├── SKILL.md        # Required — YAML frontmatter + markdown body
├── scripts/        # Optional — executable code (Python, Bash, JS)
├── references/     # Optional — extra docs loaded on demand
├── assets/         # Optional — templates, images, data
└── agents/         # Optional — per-agent metadata (e.g. openai.yaml)
```

**Implication for us:** the unit of packaging is the **folder**.
A manager that only moves single SKILL.md files cannot represent
standard skills with scripts/references/assets.

### YAML frontmatter (not TOML)

```yaml
---
name: code-reviewer          # required; must match folder name
description: ...             # required; drives agent activation
license: MIT                 # optional
allowed-tools: [read_file]   # optional; enforced by some agents
context: fork                # optional; isolated subagent (Claude Code)
effort: high                 # optional; reasoning depth hint
---
```

Only `name` + `description` are required. Everything else is optional
and agent-dependent (`allowed-tools` is enforced by Claude Code and
OpenClaw, silently ignored elsewhere; `context: fork` is Claude-only;
`agents/openai.yaml` is Codex-CLI metadata ignored by others).

**Implication for us:** our original TOML-frontmatter design
(`conventions/skill-format.md`) diverges from the standard that the
entire industry converged on. See the compatibility strategy below.

### Progressive disclosure (context economics)

The standard formalizes a three-tier loading model:

| Tier | What loads | When | Budget guidance |
|---|---|---|---|
| 1 | `name` + `description` (~30–50 tokens/skill) | Session start, always | Keep descriptions tight |
| 2 | Full SKILL.md body | Task matches the description | ≤ ~5,000 tokens recommended |
| 3 | `references/`, `scripts/`, `assets/` | Only when needed during execution | ≤ ~500 lines per dir recommended |

**Implication for us:** skill *quality constraints* are now
spec-defined and **machine-checkable**. A manager can lint them
(`pixi skills lint` — see `roadmap/improvement-proposals.md`).

### Agent install paths (converging)

| Agent | Project-level skills path |
|---|---|
| Claude Code | `.claude/skills/` |
| OpenAI Codex | `.agents/skills/` (or `.codex/skills/`) |
| GitHub Copilot | `.github/skills/` (coding agent, CLI, VS Code agent mode) |
| Gemini CLI | `.gemini/skills/` |
| Cursor, VS Code, others | per-agent; the vercel-labs CLI maps 70+ |

**Implication for us:** update our agent-path table (our docs
referenced pre-standard paths like `.github/copilot/skills/` and
`.cursor/rules/` + `.mdc` transformation — superseded by native
SKILL.md support).

### Enterprise management

Anthropic shipped org-wide skill management alongside the standard:
admins can policy-control which skills are available, restrict
sensitive capabilities, and monitor usage. **Skills are becoming
IT-managed infrastructure.** This is exactly the audience for
signed, hash-pinned, channel-distributed skills.

---

## Compatibility Strategy for pixi-skills

> **✅ ADOPTED 2026-09-17 as ADR-008** (option applied: companion
> `skill.toml`, described as option (d) below). Normative spec:
> `conventions/skill-format.md`.

```
                        ┌──────────────────────────────┐
                        │  agentskills.io spec skill    │
                        │  (folder + YAML frontmatter)  │
                        └──────────────┬───────────────┘
                                       │
                read/write 100% compliant ──> NON-NEGOTIABLE
                                       │
        ┌──────────────────────────────┼──────────────────────────┐
        │                              │                          │
        ▼                              ▼                          ▼
┌───────────────┐            ┌──────────────────┐        ┌────────────────┐
│ Layer 0: spec │            │ Layer 1: pixi-skills       │        │ Layer 2: agent-│
│ fields        │            │ extensions       │        │ specific files │
│ name, desc,   │            │ version, source, │        │ agents/*.yaml  │
│ license...    │            │ hash, deps...    │        │ (pass-through) │
└───────────────┘            └──────────────────┘        └────────────────┘
     portable                     namespaced                  untouched
```

1. **Read**: accept any spec-compliant skill (YAML frontmatter,
   folder or bare file). Zero conversion.
2. **Extend, don't fork**: our extra metadata (semver `version`,
   provider `source`, dependency edges) lives in a **namespaced
   table/section** (e.g. `metadata: { pixi-skills: {...} }` or a
   companion `skill.toml` inside the folder) so standard agents
   ignore it safely.
3. **Migrate TOML frontmatter → YAML or companion file.** The ADR
   favoring TOML pre-dates the standard; keeping spec compliance is
   worth more than parser uniformity. (Revisit ADR in
   `architecture/design-decisions.md`.)
4. **Install = copy folder** into each detected agent path — no
   per-agent format transforms anymore (the `.mdc` era is over).

---

## Security Context (why enforcement matters)

- **ClawHavoc** (2026): malware campaign via a community skill hub
  (malicious SKILL.md instructions are prompt-injection at scale).
- Studies sampling community skills found **~13% with critical
  insecurities** (excessive permissions, credential-exfil patterns,
  unsafe tool use).
- Mitigations available today: curated registries w/ scanning
  (skills.sh+Snyk), `allowed-tools` restrictions, reading skills
  before install, periodic audits.
- Mitigations only a package manager can add: **signed artifacts,
  hash-pinned install enforcement, org allow-lists, offline-reviewed
  bundles**. That is pixi-skills' lane.

---

## Sources & Further Reading

- agentskills.io — the specification (canonical)
- github.com/anthropics/skills — reference skills
- Anthropic engineering posts on progressive disclosure
- skills.sh leaderboard — ecosystem gravity check
- `conventions/skill-format.md` — our format spec (to be reconciled)
- `roadmap/improvement-proposals.md` — proposals P1–P3 build directly
  on this document
