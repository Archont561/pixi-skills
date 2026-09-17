# Knowledge Bundle Update Log

## 2026-09-17

- **Format**: Adopted [OKF v0.2](./conventions/knowledge-format.md) and declared the target version in the [root index](./index.md).
- **Navigation**: Renamed all ten `INDEX.md` files to the reserved lowercase `index.md`, removed index metadata except the root version, and made every section's context discoverable.
- **Metadata**: Added descriptive `type` and `description` fields to the fifty inherited concepts. Preserved local `section`, `kind`, and editorial date fields without inventing provenance or verification events.
- **Relationships**: Converted all 223 `relates_to` references into Markdown navigation and repaired the absent docs-site migration link in [skills.sh](./landscape/skills-sh.md).
- **Maintenance**: Added the [authoring and migration guide](./conventions/knowledge-format.md), this update log, structural validation, opt-in repository lint, regression tests, and a GitHub Actions check.
- **Scope**: Clarified that the bundle describes a planned product and that format validation is not a new factual review of its technical or ecosystem claims.
