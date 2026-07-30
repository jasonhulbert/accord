# Accord

A narrative framework for substantial human-in-the-loop AI work.

The human holds the purpose. The agent holds the work. They reach agreement on
the space between them before either mistakes motion for progress.

Accord gives a capable agent room to investigate, implement, verify, and adapt
without turning the human into a passive observer. The human keeps judgment over
purpose, consequential risk, resources, and the choices that should not be
delegated. Review happens while the work can still change.

Accord governs the work. The agreement gives trust a shape by recording the
work's accepted purpose, bounds, and division of authority. The record
preserves what happened.

New to the framework? Start with [GUIDE.md](GUIDE.md).

## The operating model

- **Creed** (`plugins/accord/creed/`) — the durable point of view for the human,
  agent, and supporting agent. It states responsibility and authority without
  prescribing implementation.
- **Agreement** — the understanding reached for one body of work before it
  begins: purpose, evidence of success, first approach, resources, risks, room
  to act, review points, and questions kept by the human.
- **Record** — an append-only factual account of what happened in the work,
  letting later sessions resume from evidence instead of memory.
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
ACCORD_STYLE_GUIDE.md          source-maintainer voice and writing standard
package.json                   contributor-only web build dependencies
web/                           web-view sources and build script
.claude-plugin/                Claude Code marketplace catalog
.agents/plugins/               Codex marketplace catalog
plugins/accord/                installable plugin root
  .claude-plugin/              Claude Code manifest
  .codex-plugin/               Codex manifest
  skills/
    accord/SKILL.md            begin or resume substantial work
    check-in/SKILL.md          consequential human input during active work
    visual-explanation/SKILL.md
                               visual accounts of cross-cutting work
  creed/                       agent.md, human.md, supporting-agent.md
  hooks/                       shared read-only lifecycle hooks
  templates/                   agreement, report, and learning-note templates
  spec/                        record and check-in specifications
  bin/                         stable user-facing command launcher
  tools/                       location, validate, render, serve, and install-launcher
tests/                         framework, hook, and tool behavior tests
```

## Adoption

**Claude Code.** Add this repository as a marketplace and install `accord`
(`/plugin marketplace add <repo>` then `/plugin install accord`), or load the
plugin directly during development with
`claude --plugin-dir <path-to-repo>/plugins/accord`. Its skills are
`/accord:accord`, `/accord:check-in`, and `/accord:visual-explanation`.

**Codex.** Add this repository as a plugin marketplace
(`codex plugin marketplace add <repo>`) and install `accord`.

The plugin needs no target-project configuration. Its records live in the
user's hidden home store, outside the target project. `tools/location` prints
the exact directory for a target project. After acceptance, the agent stores
the agreement and opens the work's record in a directory named by a technical
task ID:

```text
~/.accord/projects/{project-key}/{task}/
  agreement.md
  record.jsonl
  reports/
  diagrams/
```

The project key is derived from the project root, so two projects with the same
directory name keep separate records. The path stays stable while the project
remains at that root.

`plugins/accord/tools/validate` checks a record against the shared schema.
`plugins/accord/tools/render` creates an offline HTML timeline with a sibling
asset directory. Serve the generated directory locally rather than opening its
HTML through `file://`. Referenced visual explanations under `diagrams/` render
Mermaid blocks locally while keeping their source available for inspection.
`plugins/accord/bin/accord` is the stable user-facing launcher. Plugin hosts
that expose plugin `bin` commands make `accord` available after installation.
If your host does not expose it, install the launcher once from the installed
plugin directory with `tools/install-launcher`. From a source checkout, the
equivalent is:

```text
plugins/accord/tools/install-launcher
```

It places the launcher in the user-local executable directory and reports any
`PATH` setup still needed. From any target project root, run:

```text
accord serve
```

The command opens the record list in a browser. Use the explicit refresh action
when you want to see new events. Use `accord serve --task TASK` to open one
record directly by task ID, `accord serve --no-open` to print the URL without
opening a browser, and `Ctrl-C` to stop the server. The server reads records
but does not change them.
The bundled `tools/serve` remains available as the implementation entry point
for maintainers and direct plugin inspection.

The plugin bundles two read-only lifecycle hooks through
`plugins/accord/hooks/hooks.json`, shared by Claude Code and Codex.
`SessionStart` supplies a factual index of Accord records after startup, resume,
or compaction. `PostToolUse` validates records after a shell or file-editing tool
names a path in `~/.accord`. The hooks do not decide which agreement covers the
current work, infer events, or write to the record.

## Development

The installable plugin contains a generated web distribution and has no Node
runtime dependency. Contributors rebuild that distribution from the separate
HTML, CSS, and JavaScript sources with:

```text
npm ci
npm run build:web
```

`npm run check:web` fails when the checked-in distribution differs from its
sources or when the pinned Mermaid structure no longer supports Accord's
flowchart-and-sequence build.

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
