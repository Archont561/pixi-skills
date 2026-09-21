//! skills-core — provider-agnostic traits, data models, and utilities.
//!
//! The hub of the workspace: `Skill`, `SkillId`, `SkillSummary`, the
//! `SkillRegistry` trait, `skills.toml`/`skills-lock.toml` manifest parsing,
//! agent detection and the folder installer.
//!
//! See `.knowledge/crates/skills-core.md` for the full design.

#[cfg(test)]
mod tests {
    #[test]
    fn placeholder() {
        // Scaffold ships a single unit test so `cargo nextest run --workspace`
        // has something to run before the real model tests land (Phase 0).
    }
}
