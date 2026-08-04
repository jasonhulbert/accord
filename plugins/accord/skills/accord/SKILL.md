---
name: accord
description: Run substantial work under Accord. Use when the user invokes Accord, asks to resume work under it, or wants a purpose-led agreement for consequential work whose implementation path is not fully known. Do not use for small, routine, or fully specified tasks.
---

# Accord

The human holds the purpose. Within the agreement, you hold the work. Changes
to purpose, accepted risk, available resources, or judgment the human kept
return to them. Reach agreement before beginning.

## Use the right context

Read `../../creed/agent.md`, `../../creed/human.md`, and
`../../creed/supporting-agent.md` before acting.

Run `accord version --json` before record work. This skill requires agent
protocol `"1"`. If the command is unavailable, its output is malformed, or the
protocol is incompatible, stop and tell the human that the standalone Accord
CLI must be installed or updated. Do not search plugin caches, invoke bundled
scripts, or write a record directly as a fallback.

Require a zero exit status and the expected JSON shape from every CLI command.
On failure, stop and surface the error. Do not act on partial output.

Run `accord list --json` in the target project. The result names active and
archived storage without deciding which agreement covers the request. Only work
with `storage: "active"` and `state: "open"` may cover current work. If one may
apply, run `accord context TASK --json`. When several may apply, ask the human
which work they mean. A `completion` or `end` event closes its agreement and
record; do not reopen or append to it. Reach a new agreement for later work.
History may inform counsel, but it does not lend authority to the new work.

Never inspect archived work speculatively. When the human explicitly asks to
inspect it, use `accord context TASK --archived --json`. If the human explicitly
resumes unclosed work, run `accord restore TASK --json`, then read it with
`accord context TASK --json`. Restoring completed or ended work does not reopen
its agreement.

On resumption, read it together with the record, reports, learning notes, and
actual work. Use the diagrams when they help explain what crosses those parts.
Wait on an open reserved question. Otherwise orient the human and resume the
work within the agreement. Read `../../spec/check-in.md` when the human speaks
first.

When the human asks to inspect work in progress under Accord, use the public
`accord serve` command when the standalone CLI is installed. It opens a
read-only terminal view of all active and archived projects, independent of
the directory from which it was launched. The human can refresh the view from
the terminal. A record or report can orient inspection; it cannot replace the
work.

## Reach agreement

If no active agreement covers the request, inspect enough of the project to
offer counsel. Draft from `../../templates/agreement.md`. Name material risks,
missing resources, unclear authority, and useful review points. Ask only for
consequential context and recommend where judgment is the human's.

Present the complete draft and counsel. Discuss and revise them until both
roles can stand behind the purpose, bounds, and division of responsibility.

### Acceptance

Invocation authorizes reaching agreement, not beginning work. Begin only after
a subsequent human message explicitly accepts the presented agreement.
Questions, revisions, and acknowledgments continue the dialogue.

After acceptance, place the accepted Markdown in a temporary file and run:

```text
accord start TASK --agreement FILE --actor human --summary SUMMARY --json
```

Remove the temporary file after the command succeeds. The CLI stores the
agreement and opens its record as one operation.

## Own the work

Within the agreement, choose and adapt the implementation. Follow evidence
rather than preserving the first approach. Record material events with:

```text
accord append TASK TYPE --actor ACTOR --summary SUMMARY [TYPE FIELDS] --json
```

Use `--outcome` for an `attempt`, `--subject` for a `question`, and
`--decision` for a `direction`. Use `--ref` for a stored document. The CLI
supplies time, task identity, schema version, validation, terminal-state checks,
locking, and the append. You decide what happened and whether it is material.
Read `../../spec/record.md` before the first append so each event retains its
meaning.

Look actively for bounded parts that supporting agents can carry when
delegation would improve the work. Give each one purpose, context, bounds, and
an expected return. Examine what comes back and keep responsibility for the
course, integration, and the completed work. Record the actor who carried the
work; do not delegate reserved decisions.

Bring a `question` to the human when a choice touches purpose, accepted risk,
resources, authority, or judgment the agreement kept human. Include evidence
and counsel. Do not return routine choices. Do not make or foreclose the
consequential choice before direction arrives.

When the human accepts changed terms, put the accepted amendment in a temporary
Markdown file and run `accord amend TASK --file FILE --json`. Remove the file
afterward. Record the event that explains what changed.

## Present work for review

At an agreed review point, or when the outcome and evidence appear to satisfy
the agreement, make the work available for inspection. Draft from
`../../templates/report.md`, then store the report through:

```text
accord document TASK report --file FILE --name report-DESCRIPTION.md --json
```

Use the returned `ref` when recording the `report` event. Record the `review`,
`report`, and `question`, then stop before making or foreclosing the human's
choice.

Tell the human which work is ready and ask the question kept human. More
evidence or a follow-up question is a `check-in`; the reserved judgment remains
open. A clear answer is `direction`; record it and resume. When correction is
requested, revise the work without acting beyond the unresolved judgment, then
report and ask again. Responsibility for implementation remains yours.

Do not name the review as though it were a phase, deliverable, or piece of work
for the human to approve.

An internal pause for testing or reflection is not a review. Authority returns
to the human where the agreement reserves it, the human requests review, a
consequential question exceeds the agreement, or the agent seeks judgment that
the work is complete.

## Keep the record

Use the CLI for every record event and durable document. Never rewrite valid
history.

Store learning notes with:

```text
accord document TASK learning-note --file FILE --name learning-DESCRIPTION.md --json
```

Reference them from a `note` event when that reference matters to resumption.
Learning notes inform judgment; they do not become rules.

The human's explicit direction that the work should be recorded as complete
allows a `completion` event. Evidence, confidence, silence, and earlier
authorization do not. Record `end` when the work stops without that approval.
Both events close the agreement and record.

Archival changes visibility, not state. Run `accord archive TASK --json` only
when the human explicitly asks. Do not archive automatically after a closing
event. Use `--force` for unclosed work only when the human explicitly directs
that override. Run `accord restore TASK --json` only for explicitly named
archived work; restoration never rewrites its contents.

When you believe the agreement has been satisfied, ask explicitly whether it
should be recorded as complete. After the human's `direction`, append the
`completion` event as the agent carrying the record.

Improve Accord at its source, not in an installed copy.
