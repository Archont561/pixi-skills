---
type: Convention
title: "Knowledge Format"
description: "OKF v0.2 authoring rules, local extensions, validation, and migration notes for this bundle."
section: conventions
kind: detail
tags: [conventions, knowledge, okf, metadata, navigation, validation]
status: stable
created: "2026-09-17"
updated: "2026-09-21"
sources:
  - id: okf-v02
    resource: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/62432a095456147ee71e70ac6e4dc0d2dea3ac30/okf/SPEC.md
    title: Open Knowledge Format v0.2 specification
---

# Knowledge Format

## Scope and Specification

`.knowledge/` is an **Open Knowledge Format (OKF) v0.2 Knowledge Bundle**.
The conformance target is the official specification at revision
`62432a095456147ee71e70ac6e4dc0d2dea3ac30`, checked on 2026-09-17.
The pinned source makes this migration reproducible even if the upstream
specification changes.[^okf-v02]

This convention governs knowledge documents, **not** the `SKILL.md`
frontmatter or `skill.toml` used by the product. Those follow the separate
[Skill Format](./skill-format.md) and [Manager Envelope](./skill-toml.md)
contracts; do not add OKF fields to skill examples merely to satisfy this
bundle's validator.

## OKF Requirements

The specification deliberately has a small interoperability surface:[^okf-v02]

1. Every non-reserved `.md` file is a UTF-8 concept document with a leading
   YAML block delimited by `---` and a Markdown body. Its `type` must be a
   non-empty string. Unknown types and extension keys are allowed.
2. `index.md` and `log.md` are reserved at **every directory level** and
   must not be used as concept documents.
   - An index groups navigation entries under headings. It has **no
     frontmatter**, except that the bundle-root index may contain
     `okf_version: "0.2"` alone.
   - A log is a flat list of entries grouped under `YYYY-MM-DD` headings,
     newest first. It is not a concept and carries no concept frontmatter.
3. Indexes, logs, descriptions, tags, and the provenance/trust/lifecycle
   families are optional in OKF. Consumers must tolerate missing optional
   metadata, unknown types/fields, missing indexes, and broken cross-links.

No JSON manifest, embeddings, SDK, or runtime is required. The directory
can be copied, archived, or distributed as part of a Git repository.

## Local Authoring Profile

We use a stricter authoring profile to make this particular bundle easy
to browse. These are **repository lint rules**, not additional OKF
conformance requirements.

### Concept metadata

Every concept in this repository has a descriptive `type`, a `title`, a
single-line `description`, and a non-empty list of string `tags`.
For example:

```markdown
---
type: Reference
title: Example Concept
description: A short summary of the knowledge on this page.
tags: [example, reference]
status: draft
---

# Example Concept

Explain the concept and link to related knowledge in the body.
```

Types describe content, not file roles. This bundle uses `Overview` for
context pages and types such as `Architecture`, `Decision Record`,
`Component Design`, `Convention`, `Reference`, `Playbook`, `Roadmap`,
`Proposal`, and `Comparative Analysis` for detail pages. This is **not** a
closed taxonomy; choose another descriptive type when appropriate.

These existing fields remain permitted local extensions:

| Field | Local meaning |
|---|---|
| `section` | Topic grouping, usually the containing directory or `root` |
| `kind` | Legacy reading role: `context` or `detail`; does not replace `type` |
| `created`, `updated` | Legacy editorial date strings; not standardized OKF timestamps, provenance, or verification events |

### Paths and navigation

- Concept identity is the bundle-relative file path **without `.md`**.
  Case matters. The existing `CONTEXT.md` names are retained as ordinary
  concepts; only `index.md` and `log.md` are reserved.
- Every directory containing knowledge has a lowercase `index.md`.
  It lists its direct concepts (including `CONTEXT.md`), its log if any,
  and child sections via their indexes. Summarize each linked page;
  reuse its frontmatter description when adding an entry.
- Root `index.md` declares `okf_version: "0.2"`. Section indexes contain
  no frontmatter, including no `type`, `kind`, or `title` keys.
- Express relationships using standard **Markdown body links**, not the
  former `relates_to` extension. Reference-style Markdown links are also
  supported. Labels and surrounding prose explain the relationship.
- Both `/crates/skills-core.md` (bundle-relative) and
  `../crates/skills-core.md` (relative) are OKF paths. A leading `/` means
  the **bundle root**, not the repository root or a website route.
  We generally use relative paths so navigation also works on GitHub.
- Keep local links inside the bundle and point them at existing targets.
  Link to an existing design page when an implementation or docs-site
  route does not exist yet. Plain code examples are not graph edges.
- Record meaningful maintenance in [the root log](../log.md), using real
  calendar dates and newest-first ordering. Do not invent earlier events.

### Trust and freshness

This migration is **structural**, not a new factual review of the product
or ecosystem. Existing architecture and tool configuration describe the
planned product; they are not evidence that the implementation exists.
`status: stable` means the document is ready for consumption, not that
its software is shipped or its assertions are verified.

The inherited `created` and `updated` dates were retained and quoted as
local strings. Their historical accuracy was not re-established. In
particular, the old `2025-01-01` values are **not** converted into invented
`generated.at` or verification timestamps.

For future content maintenance, the optional OKF v0.2 families are
available:[^okf-v02]

- `sources` records known provenance. Each entry needs a `resource`;
  give it a stable `id` when attributing a claim with a matching Markdown
  footnote, as this page does with `okf-v02`.
- `generated` records the real producer (`by`) and, when known, the last
  meaningful content change (`at`).
- `verified` records actual confirmation **against the content's sources
  or resource**, not a successful format or link check. Do not fabricate
  a `human:` reviewer or mark these concepts verified just because CI passes.
  Without `verified`, a concept is unverified but still conformant.
- Standard timestamp-valued fields such as `generated.at`, `verified.at`,
  `stale_after`, and `sources[].last_modified` use ISO 8601 datetimes with
  explicit offsets, for example `2026-09-17T12:00:00Z`, not date-only values.

Optional families are not necessary to make these design documents
conformant. Omit facts about authorship, freshness, or trust that are not
known rather than manufacturing metadata.

## Validation

> **Status (2026-09-21): no validator is installed.** The commands below
> describe the Python checker that used to live here. `scripts/check_knowledge.py`,
> `requirements-knowledge.txt` and `tests/` have since been removed from the
> repository, the `knowledge` job is gone from `.github/workflows/ci.yml`, and
> the Dependabot `pip` entry that tracked the requirements file with it. The
> format rules above are still the bundle's contract — they are just enforced
> by review and by the [update log](../log.md) now, not by a script. Keep this
> section as the record of what the tool checked in case it is restored.

From the repository root, with Python 3.11 or newer:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-knowledge.txt

# Required document structure and reserved-file rules only:
.venv/bin/python scripts/check_knowledge.py

# Also enforce this repository's metadata and navigation profile:
.venv/bin/python scripts/check_knowledge.py --lint

# Regression tests for the validator:
.venv/bin/python -m unittest discover -s tests -v
```

The checker accepts an optional bundle directory argument. It parses
YAML safely and uses a CommonMark parser for links, excluding fenced and
indented code and inline-code examples. The default structural checks do
not reject unknown types, extensions, absent optional metadata/indexes,
or broken links. `--lint` additionally checks recommended metadata,
reserved-name casing, the declared version, complete directory indexes,
and existing local file targets that stay inside the bundle.

**Limits:** it does not fetch external URLs, check fragment anchors,
verify factual claims, or validate all optional provenance/computation
contracts or attestations. Passing it is not a trust or security verdict.

The `knowledge` job of `.github/workflows/ci.yml` used to run the tests and
linted validation for pull requests and changes to `main`; it had replaced
the former `knowledge.yml` when the CI layout was unified, and it was removed
with the checker in Phase 0. That job was also the only reason the checkout
needed Python at all: no tooling is required to read or distribute the bundle,
and the workspace it used to defer to now exists, so `ci` is a single pixi job
with no Python in it.

## Migration Audit — 2026-09-17

| Area | Before | After |
|---|---|---|
| Concept typing | None of 60 Markdown files had `type` | 50 inherited concepts have descriptive types; this convention adds one more |
| Indexes | 10 uppercase `INDEX.md` files with concept-like metadata | 10 lowercase reserved `index.md` files; only root has version frontmatter |
| Descriptions | No concept descriptions in frontmatter | One-line descriptions on every concept |
| Relationships | 223 entries in a custom `relates_to` field | All those edges preserved in Markdown navigation |
| Link integrity | One link to an absent docs-site route | Link points to the existing documentation content plan |
| Maintenance | No reserved update log or executable format checks | Root log, authoring guide, validator, regression tests, and CI |

Substantive design content is retained. Apart from index renames, existing
concept IDs are unchanged. The old uppercase index paths are intentionally
not kept as duplicate concept documents; all in-bundle references were
updated to the reserved lowercase names. Git retains their history.

## Related Concepts

- [Project Context](../CONTEXT.md) — Scope and intended product architecture.
- [Conventions Context](./CONTEXT.md) — Other project-wide conventions.
- [Bundle Index](../index.md) — Start browsing the knowledge bundle.

[^okf-v02]: Open Knowledge Format v0.2 specification, pinned revision linked in `sources`; particularly §§3–9 and §§11–13.
