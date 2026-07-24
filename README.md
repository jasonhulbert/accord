# The Expedition Framework

A narrative role framework for human-in-the-loop AI work. It aligns a human (the patron) and an AI agent (the frontiersman) through shared roles, a common creed, and reliable ceremonies of communication — leaving the agent room to exercise judgment instead of managing it step by step.

The creed shapes the traveler, never the trail: it prepares whoever journeys under it to meet terrain it cannot predict. The framework prescribes that its ceremonies exist, never their choreography.

New to the workflow? Start with [FIELD_GUIDE.md](FIELD_GUIDE.md) — how a journey runs, common pitfalls, and what is expected of the patron.

## The layers

The framework separates what is permanent from what is disposable, and keeps learning where it belongs.

- **Creed** (`plugin/creed/`) — the frontiersman's, patron's, and scout's narratives. Permanent and role-level, amended rarely. Ships with the package.
- **Charter** — per-expedition and disposable. Because it expires with the task, it is allowed to be specific: purpose, destination, first approach, provisions, accepted dangers, arrival criteria, and which questions require a rider home. Templates ship with the framework; charters never live in the framework repo.
- **Journal** — per-project and accumulating. Maps, not mandates: entries inform future judgment, never bind it. Journals never travel back into the framework repo.

Updates flow one way. Creed improvements reach projects through package upgrades; project learnings stay home in that project's journal.

## Repository layout

The `plugin/` subtree is the plugin for both Claude Code and Codex: one shared tree of framework resources, with both skills referencing it — nothing is vendored or duplicated. Only `plugin/` is installed into consuming projects; repo-root docs (this README, FIELD_GUIDE.md, AGENTS.md, CLAUDE.md) stay behind.

```
FIELD_GUIDE.md              user-facing guide: the workflow, pitfalls, the patron's part
.claude-plugin/             marketplace catalog (points at ./plugin)
.agents/plugins/            Codex marketplace catalog (points at ./plugin)
plugin/                     the plugin root — the only tree that installs
  .claude-plugin/           Claude Code plugin manifest
  .codex-plugin/            Codex plugin manifest
  skills/
    expedition/SKILL.md     the expedition skill (shared by both harnesses)
    expedition-missive/SKILL.md
  creed/                    the creed (frontiersman.md, patron.md, scout.md)
  hooks/                    shared Claude Code and Codex lifecycle hooks
  templates/                charter, dispatch, and journal-entry templates
  spec/                     journey-state spec, JSON Schema, examples, analysis notes
  tools/                    validate and render scripts
tests/
  test_framework_contract.py  role and authority contract tests
  test_hooks.py               cross-harness hook behavior tests
```

## Adoption

**Claude Code.** Add this repository as a marketplace and install the plugin (`/plugin marketplace add <repo>` then `/plugin install expedition`), or load it directly for development with `claude --plugin-dir <path-to-repo>/plugin`. Skills are namespaced: `/expedition:expedition`, `/expedition:expedition-missive`. Run `claude plugin validate ./plugin` after changes.

**Codex.** Add this repository as a plugin marketplace (`codex plugin marketplace add <repo>`) and install the `expedition` plugin; both skills come with it.

The plugin travels across projects and needs no target-project configuration. On invocation the skills establish the roles, draft a charter with the patron, and create `.expeditions/{name}/` in the target project. If an `.expeditions/` charter already exists for the work at hand, they resume under that charter. The `.expeditions/` directory is the persistence mechanism.

Each expedition keeps an append-only log, `.expeditions/{name}/journey.jsonl`, described in `plugin/spec/journey-state.md`. Validate a log with `plugin/tools/validate`; render it into a visual journey with `plugin/tools/render`.

The plugin bundles two read-only lifecycle hooks through `plugin/hooks/hooks.json`, discovered by both harnesses. `SessionStart` supplies a factual index of expedition records on startup, resume, and compaction. `PostToolUse` validates journey logs after a shell or file-editing tool explicitly names `.expeditions` or `journey.jsonl`. The hooks never choose an active charter, infer an event, or write to the expedition record.

Run the hook behavior tests with `python3 -m unittest discover -s tests -v`.

## Amendment discipline

- The creed records role responsibilities only. Additions must be fought for; clarifications and removals are cheap.
- Mid-task fixes belong in that task's charter. Lessons belong in the journal as dated accounts. Only role responsibilities belong in the creed.
- New lexicon terms, roles, actors, or event types are admitted only when the existing vocabulary cannot express a distinct responsibility — and admitting one is a rider to the patron, not an implementation choice.
- Templates name what a ceremony contains, never steps. A template that grows steps has failed.
- The log describes what happened; it never prescribes what must happen. Analytics over logs are descriptive only, feeding the patron's judgment — they never generate rules, scores, or instructions that flow back to the agent.
