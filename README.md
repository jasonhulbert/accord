# Accord

A narrative framework for substantial human-in-the-loop AI work.

The human holds the purpose. The agent holds the work. They reach agreement on
the space between them before either mistakes motion for progress.

Accord gives a capable agent room to investigate, implement, verify, and adapt
without turning the human into a passive observer. The human keeps judgment over
purpose, consequential risk, resources, and the choices that should not be
delegated. Review happens while the work can still change.

New to the framework? Start with [GUIDE.md](GUIDE.md).

## The operating model

- **Creed** (`plugins/accord/creed/`) — the durable point of view for the human,
  agent, and supporting agent. It states responsibility and authority without
  prescribing implementation.
- **Agreement** — the understanding reached for one task before work begins:
  purpose, evidence of success, first approach, resources, risks, room to act,
  review points, and questions kept by the human.
- **Record** — an append-only factual account that lets later sessions resume
  from evidence instead of memory.
- **Reports** — durable orientation to work, evidence, failure, uncertainty, and
  counsel. A report points to the work; it never substitutes for inspection.
- **Learning notes** — context that may help later judgment. Evidence, not
  mandates.

The agreement is not handed down. The agent inspects what is known and counsels
on cost, risk, missing context, unclear authority, and useful review points. The
human and agent discuss and revise the draft. Work begins only after the human
has seen and explicitly accepted the agreement.

## Repository layout

Only `plugins/accord/` is installed into consuming projects. The documents at
the repository root are contributor-facing.

```text
GUIDE.md                       practical human-facing guide
ACCORD_STYLE_GUIDE.md          voice and writing standard
.claude-plugin/                Claude Code marketplace catalog
.agents/plugins/               Codex marketplace catalog
plugins/accord/                installable plugin root
  .claude-plugin/              Claude Code manifest
  .codex-plugin/               Codex manifest
  skills/
    accord/SKILL.md            begin or resume substantial work
    check-in/SKILL.md          human-initiated communication during active work
  creed/                       agent.md, human.md, supporting-agent.md
  hooks/                       shared read-only lifecycle hooks
  templates/                   agreement, report, and learning-note templates
  spec/                        record and check-in specifications
  tools/                       location, validate, render, and serve
tests/                         framework, hook, and tool behavior tests
```

## Adoption

**Claude Code.** Add this repository as a marketplace and install `accord`
(`/plugin marketplace add <repo>` then `/plugin install accord`), or load the
plugin directly during development with
`claude --plugin-dir <path-to-repo>/plugins/accord`. Its skills are
`/accord:accord` and `/accord:check-in`.

**Codex.** Add this repository as a plugin marketplace
(`codex plugin marketplace add <repo>`) and install `accord`.

The plugin needs no target-project configuration. Its records live in the
user's hidden home store, outside the target project. `tools/location` prints
the exact directory for a target project. An accepted agreement creates:

```text
~/.accord/projects/{project-key}/{task}/
  agreement.md
  record.jsonl
  reports/
```

The project key is derived from the project root, so two projects with the same
directory name keep separate records. The path stays stable while the project
remains at that root.

`plugins/accord/tools/validate` checks a record against the shared schema.
`plugins/accord/tools/render` creates a self-contained HTML timeline.
`plugins/accord/tools/serve` starts a live, localhost-only view of the current
project's records. From the project root, run:

```text
plugins/accord/tools/serve
```

It opens the record list in a browser and refreshes while work continues. Use
`--task TASK` to open one record directly, `--no-open` to print the URL without
opening a browser, and `Ctrl-C` to stop the server. The server reads records but
does not change them.

The plugin bundles two read-only lifecycle hooks through
`plugins/accord/hooks/hooks.json`, shared by Claude Code and Codex.
`SessionStart` supplies a factual index of Accord records after startup, resume,
or compaction. `PostToolUse` validates records after a shell or file-editing tool
names a path in `~/.accord`. The hooks do not choose an active agreement, infer
events, or write to the record.

## Development

Run the full behavior suite:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Validate the Claude Code manifest:

```text
claude plugin validate ./plugins/accord
```

The creed carries the point of view. Skills should remain concise. Templates
name what a conversation or record contains, not a sequence of steps.
Specifications define structure. Analytics over records remain descriptive and
must never generate rules, scores, or instructions that flow back to the agent.
