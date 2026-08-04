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

## Architecture

Accord has one executable implementation and one thin provider layer.

- `src/accord/` is the standalone Python package. It owns record storage,
  validation, mutation, context inspection, archive, and restore.
- `plugins/accord/` is the installable provider plugin. It contains only
  manifests, metadata, Markdown skills, creeds, templates, and guidance.
- Skills call the public `accord` CLI. They never invoke bundled scripts, edit
  JSONL directly, or search provider caches.
- The schema ships with the CLI. Existing schema-1 records use the same reader
  as new records and remain in place without migration.
- `.claude-plugin/` and `.agents/plugins/` are repository marketplace catalogs
  pointing to `./plugins/accord`.
- `tests/` contains focused contracts for the framework and standalone CLI.
- `~/.accord/` contains per-user records partitioned by project and remains
  outside project workspaces.

## Amendment discipline

- Creed improvements leave through plugin upgrades. Learning from particular
  work stays in its Accord record and learning notes.
- Changes made while work is active belong in its agreement. Lessons belong in
  learning notes. Only durable role responsibilities belong in the creed.
- Changes to event types, actors, or the shared vocabulary require human
  agreement. They are not incidental implementation decisions.
- Templates name what a conversation or record contains, never a required
  sequence of steps.
- The record describes what happened. Analytics over records remain descriptive
  and feed human judgment; they never generate rules, scores, or instructions
  that flow back to the agent.

## Verification

Run:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Build and install the wheel in isolation when changing packaging. Validate each
skill and the Codex plugin manifest when changing the provider layer. A passing
suite must contain no hidden skips.
