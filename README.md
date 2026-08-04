# Accord

Accord is a narrative framework for substantial human-agent work.

The human holds the purpose. Within an accepted agreement, the agent holds the
work. Consequential choices return to the human while implementation remains
the agent's responsibility. An append-only record lets that understanding
survive changes of session.

Accord has two parts:

- a standalone `accord` CLI that owns records, storage, validation, and
  lifecycle operations;
- a thin provider plugin containing Markdown skills, creeds, templates, and
  guidance that teach agents how to use the CLI.

The plugin contains no executable runtime. The CLI contains no provider logic.

## Install

Install the CLI from this checkout:

```text
python3 -m pip install .
accord version
```

Install `plugins/accord/` through the Claude Code or Codex marketplace catalog
in this repository. The plugin requires a compatible standalone CLI and fails
loudly when it is missing.

The available skills are `accord`, `check-in`, and `visual-explanation`.

## Commands

The public CLI provides:

- `accord version` — report CLI and agent-protocol compatibility;
- `accord serve` — open the read-only terminal view of all projects;
- `accord location` — show the current project's record roots;
- `accord list` — list active and archived work without choosing an agreement;
- `accord context TASK` — read one explicitly named agreement and its record;
- `accord start`, `append`, `document`, and `amend` — validated mutations used
  by the skills;
- `accord validate TASK` — validate a stored record;
- `accord archive TASK` and `accord restore TASK` — move a complete task tree
  without rewriting it.

`accord serve` is global rather than project-scoped. It reads active and
archived work beneath `~/.accord`, and it never mutates records.

Machine-facing use should pass `--json` and require both a zero exit status and
the expected response shape.

## Records

Records stay outside project workspaces:

```text
~/.accord/projects/{project-key}/{task}/
  agreement.md
  record.jsonl
  reports/
  diagrams/
  learning-*.md
```

Archived work lives under
`~/.accord/archive/projects/{project-key}/{task}/` with the same internal
layout. Existing schema-1 records are read in place by the same code used for
new records. There is no migration or legacy reader.

`completion` and `end` close an agreement and record. Archival is a separate,
explicit change in visibility. Restoring work never reopens a closed agreement.

## Repository layout

```text
pyproject.toml                 standalone package metadata
src/accord/                    CLI, storage, record, and lifecycle code
plugins/accord/                Markdown-only provider plugin
  .claude-plugin/              Claude Code metadata
  .codex-plugin/               Codex metadata
  skills/                      agent instructions
  creed/                       durable role responsibilities
  templates/                   agreement, report, and learning-note contents
  spec/                        record meaning and check-in guidance
tests/                         focused framework and CLI contracts
GUIDE.md                       human-facing use
ACCORD_STYLE_GUIDE.md          maintainer writing standard
```

## Development

Run the focused suite:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Validate the Codex plugin and its skills with the repository's available plugin
and skill validators before shipping changes. The creed carries the point of
view. Code owns mechanics. Neither should compensate for the other by saying
everything twice.
