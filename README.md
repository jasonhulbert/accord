# The Expedition Framework

A narrative role framework for human-in-the-loop AI work. It aligns a human (the patron) and an AI agent (the frontiersman) through shared roles, a common creed, and reliable ceremonies of communication — leaving the agent room to exercise judgment instead of managing it step by step.

The creed shapes the traveler, never the trail: it prepares whoever journeys under it to meet terrain it cannot predict. The framework prescribes that its ceremonies exist, never their choreography.

## The layers

The framework separates what is permanent from what is disposable, and keeps learning where it belongs.

- **Creed** (`creed/`) — the frontiersman's, patron's, and scout's narratives. Permanent and role-level, amended rarely. Ships with the package.
- **Charter** — per-expedition and disposable. Because it expires with the task, it is allowed to be specific: purpose, destination, first approach, provisions, accepted dangers, arrival criteria, and which questions require a rider home. Templates ship with the framework; charters never live in the framework repo.
- **Journal** — per-project and accumulating. Maps, not mandates: entries inform future judgment, never bind it. Journals never travel back into the framework repo.

Updates flow one way. Creed improvements reach projects through package upgrades; project learnings stay home in that project's journal.

## Repository layout

```
creed/                      the creed (frontiersman.md, patron.md, scout.md)
templates/                  charter, dispatch, and journal-entry templates
spec/                       journey-state spec, JSON Schema, examples, analysis notes
adapters/
  claude/                   self-contained Claude skill (vendored creed + templates + spec)
  codex/expedition/         self-contained Codex skill (metadata + vendored framework)
  project-snippet.md        fallback for tools without a skill mechanism
tools/                      validate, render, and skill-build scripts
```

## Adoption

Run `tools/build-skill` before installing either adapter. It vendors the current creed, templates, and spec essentials into both skill folders and builds the Claude package.

**Codex.** Install `adapters/codex/expedition/` as a user skill at `~/.agents/skills/expedition/`, or as a repository skill at `.agents/skills/expedition/`. Codex supports copied or symlinked skill folders. Invoke it as `$expedition`; Codex may also select it when a request matches its description.

**Claude.** Install the generated `expedition.skill` per-user.

Both adapters travel across projects and need no target-project configuration. On invocation they establish the roles, draft a charter with the patron, and create `expeditions/{name}/` in the target project. If an `expeditions/` charter already exists for the work at hand, they resume under that charter. The `expeditions/` directory is the persistence mechanism.

**Fallback.** For tools without a skill mechanism, paste `adapters/project-snippet.md` into the project's AGENTS.md or CLAUDE.md.

Each expedition keeps an append-only log, `expeditions/{name}/journey.jsonl`, described in `spec/journey-state.md`. Validate a log with `tools/validate`; render it into a visual journey with `tools/render`.

## Amendment discipline

- The creed records role responsibilities only. Additions must be fought for; clarifications and removals are cheap.
- Mid-task fixes belong in that task's charter. Lessons belong in the journal as dated accounts. Only role responsibilities belong in the creed.
- New lexicon terms, roles, actors, or event types are admitted only when the existing vocabulary cannot express a distinct responsibility — and admitting one is a rider to the patron, not an implementation choice.
- Templates name what a ceremony contains, never steps. A template that grows steps has failed.
- The log describes what happened; it never prescribes what must happen. Analytics over logs are descriptive only, feeding the patron's judgment — they never generate rules, scores, or instructions that flow back to the agent.
