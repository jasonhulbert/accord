# Project Context

This directory explores an expedition metaphor as a framework for human-in-the-loop AI work. Its premise is that clear roles, a shared "creed", and reliable communication can align a human and an AI agent while leaving the agent room to exercise judgment and capability. The narratives test whether this shared point of view can sustain trust and alignment without relying on prescriptive plans that manage the agent step by step.

Read the current narratives (in `plugin/creed/`) before proposing changes or additions. Treat them as the source of truth for the metaphor.

When contributing:

- Preserve the restrained, declarative tone of the existing narratives.
- Use the metaphor to clarify a meaningful idea about responsibility, authority, uncertainty, evidence, adaptation, or communication.
- Keep the framework useful across specific tools, models, and software methodologies.
- Identify contradictions or unclear role boundaries rather than silently resolving them.
- Do not introduce new lexicon terms or roles unless the existing vocabulary cannot express a distinct responsibility.

## Repository layout

- `plugin/` — the plugin root for both Claude Code and Codex; only this subtree is installed into consuming projects. Repo-root files (`AGENTS.md`, `FIELD_GUIDE.md`, `README.md`, `CLAUDE.md`) are contributor-facing and never ship.
  - `plugin/creed/` — the creed: `frontiersman.md`, `patron.md`, `scout.md`. Permanent, role-level, amended rarely. Narratives only; reference material belongs in `plugin/spec/`.
  - `plugin/templates/` — charter, dispatch, and journal-entry templates.
  - `plugin/hooks/` — shared, read-only Claude Code and Codex lifecycle hooks.
  - `plugin/spec/` — journey-state spec (`journey-state.md`), `journey.schema.json`, `examples/`, `analysis.md`.
  - `plugin/skills/` — the `expedition` and `expedition-missive` skills, shared by both harnesses. Each SKILL.md references `creed/`, `templates/`, and `spec/` at the plugin root; never vendor copies into skill folders.
  - `plugin/.claude-plugin/`, `plugin/.codex-plugin/` — plugin manifests.
  - `plugin/tools/` — `validate`, `render`.
- `.claude-plugin/marketplace.json`, `.agents/plugins/` — marketplace catalogs at the repo root, pointing at `./plugin`.
- `tests/` — contributor-facing behavior tests for shared plugin components.
- `.expeditions/` — journeys run *on this repo itself* (dogfooding). Excluded from git, like any project's expedition records. Charters and journals for other projects never live here.

## Amendment discipline

- Updates flow one way: creed improvements leave via package upgrade; project learnings stay home in that project's journal.
- Mid-task fixes go in that task's charter; lessons go in the journal as dated accounts; only role responsibilities go in the creed. Additions to the creed must be fought for; clarifications and removals are cheap.
- Adding, removing, or renaming any event type, actor, or lexicon term is a question for the patron, not an implementation choice — and only if the existing vocabulary cannot express a distinct responsibility.
- Templates name what a ceremony contains, never steps. A template that grows steps has failed.
- The journey log describes what happened; it never prescribes what must happen. Analytics over logs are descriptive only and feed the patron's judgment; they never generate rules, scores, or instructions that flow back to the agent.
