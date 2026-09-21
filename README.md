# pixi-skills

Design and knowledge for a provider-agnostic, reproducible skills manager
for AI coding agents.

This checkout currently contains documentation and its validation tooling,
not yet the Rust CLI, pixi workspace, or Astro application described in
the design.

## Knowledge bundle

Start at **[.knowledge/index.md](.knowledge/index.md)**. The directory is an
[Open Knowledge Format (OKF) v0.2](.knowledge/conventions/knowledge-format.md)
Knowledge Bundle: linked Markdown concepts with YAML frontmatter,
progressive-disclosure indexes, and an [update log](.knowledge/log.md).

- [Project context](.knowledge/CONTEXT.md)
- [Architecture](.knowledge/architecture/index.md)
- [Roadmap](.knowledge/roadmap/index.md)
- [Authoring rules and migration audit](.knowledge/conventions/knowledge-format.md)

## Validate changes

Python 3.11 or newer is needed only for validation, not to read the bundle.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-knowledge.txt
.venv/bin/python scripts/check_knowledge.py --lint
.venv/bin/python -m unittest discover -s tests -v
```

Without `--lint`, the checker tests required OKF document structure only.
With it, the repository also requires descriptive metadata, complete
indexes, and working in-bundle file links. It does not verify factual
claims, external URLs, fragment anchors, or attested computations.

The same tests and linted validation run in the `knowledge` job of
[the ci workflow](.github/workflows/ci.yml).

## Continuous integration

`.github/` mirrors the layout of
[Archont561/pixi-sandbox](https://github.com/Archont561/pixi-sandbox) at
v0.2.0, so the pipeline is already shaped for the workspace this bundle
designs:

| Path | Role |
|---|---|
| `.github/workflows/ci.yml` | Single CI entry point: `probe` → `knowledge` (runs today) → `workspace` (skipped until `pixi.toml` + `pixi.lock` exist) |
| `.github/workflows/publish-sandbox.yml` | Thin caller of the upstream reusable publisher, in release-binary mode, pinned by commit SHA |
| `.pixi-sandbox.toml` | Reviewed publish plan: which pixi environments become airlock branches |
| `.github/dependabot.yml` | Keeps the SHA-pinned actions current |
| `scripts/restore.sh` | Airlock one-liner: fetch → verify → restore → wire PATH |

Nothing in that layout executes until the pixi workspace exists — every
gate probes for it and skips rather than fails. See
[pixi-sandbox](.knowledge/landscape/pixi-sandbox.md) for why it is worth
having, and [GitHub Actions](.knowledge/cicd/github-actions.md) for the
pipeline design.
