# Project context

This repository develops Accord, a narrative framework for substantial
human-in-the-loop AI work. Its premise is that clear roles, a shared creed, and
reliable communication can align a human and an AI agent while leaving the agent
room to exercise judgment.

The roles and responsibilities are literal. The writing remains narrative:
warm, declarative, and attentive to pressure, consequence, and the division of
authority.

Read `ACCORD_STYLE_GUIDE.md` and every current creed in
`plugins/accord/creed/` before proposing changes. Together they are the source
of truth for the framework's point of view.

When contributing:

- Preserve the restrained, declarative voice defined in the style guide.
- Clarify responsibility, authority, uncertainty, evidence, adaptation, or
  communication without prescribing implementation step by step.
- Keep the framework independent of specific tools, models, and software
  methodologies.
- Identify contradictions or unclear role boundaries rather than silently
  resolving them.
- Do not introduce a new term or role when ordinary language or the existing
  vocabulary already expresses the responsibility.
- Keep the human and agent capable. Do not reduce either to an input source,
  approval mechanism, executor, or tool.

## Repository layout

- `plugins/accord/` — the installable plugin root for Claude Code and Codex.
  Only this subtree ships to consuming projects.
  - `creed/` — `agent.md`, `human.md`, `investigator.md`. Permanent,
    role-level, and amended rarely.
  - `skills/` — `accord` and `check-in`. Both reference shared plugin-root
    resources; never vendor copies into skill folders.
  - `templates/` — agreement, report, and learning-note contents. Templates
    name substance, not choreography.
  - `spec/` — record schema, event example, check-in semantics, and descriptive
    analysis boundary.
  - `hooks/` — shared, read-only Claude Code and Codex lifecycle hooks.
  - `tools/` — record validation and rendering.
- `.claude-plugin/`, `.agents/plugins/` — repository marketplace catalogs
  pointing to `./plugins/accord`.
- `tests/` — contributor-facing contract, hook, and tool behavior tests.
- `ACCORD_STYLE_GUIDE.md` — accepted voice and style authority.
- `~/.accord/` — per-user Accord records, partitioned by project and kept
  outside project workspaces.

## Amendment discipline

- Creed improvements leave through plugin upgrades. Project learning stays in
  that project's Accord record and learning notes.
- Mid-task changes belong in the task's agreement. Lessons belong in learning
  notes. Only durable role responsibilities belong in the creed.
- Changes to event types, actors, or the shared vocabulary require human
  agreement. They are not incidental implementation decisions.
- Templates name what a conversation or record contains, never a required
  sequence of steps.
- The record describes what happened. Analytics over records remain
  descriptive and feed human judgment; they never generate rules, scores, or
  instructions that flow back to the agent.
