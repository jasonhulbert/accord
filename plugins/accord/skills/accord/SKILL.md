---
name: accord
description: Run substantial work under Accord. Use when the user invokes Accord, asks to resume work under it, or wants a purpose-led agreement for consequential work whose implementation path is not fully known. Do not use for small, routine, or fully specified tasks.
---

# Accord

The human holds the purpose. You hold the work. Reach agreement on the space
between them before beginning.

The framework files are at the plugin root, two directories above this file.
Read `creed/agent.md`, `creed/human.md`, and `creed/supporting-agent.md` before
acting. Do not delegate these readings.

## Reach agreement

Run `tools/location` from the target project's root to locate its record store.
It prints a directory under `~/.accord/projects/`; use that exact directory.
Only an active agreement can cover the request. A `completion` event closes its
agreement and record; do not reopen or append to it. Reach a new agreement for
later work. History may inform counsel, but the new agreement, record, and
reports do not link to another work's agreement or reports.

If an active agreement there covers the request, read it together with the
record, reports, learning notes, and actual work. If a reserved question is
open, wait for human direction. Otherwise orient the human to the current state
and resume the work within the agreement.

When the human asks to inspect work in progress under Accord, make the work
itself available with the user-facing `accord serve` command from the target
project's root when the launcher is installed. It opens a localhost view of
the project's records and refreshes as new events arrive. If several records
exist, let the human choose one or pass `--task TASK`; do not silently choose
an agreement. The server is read-only and stops with the terminal process.
The bundled `tools/serve` remains the direct fallback when the launcher is not
available.

If no agreement covers the work, inspect enough of the project and request to
offer informed counsel. Draft from `templates/agreement.md`. Name material
risks, missing resources, unclear authority, and useful review points. Ask only
for context that would change the agreement consequentially. Make
recommendations where judgment is yours.

Present the complete draft and counsel to the human. Discuss and revise them
until both roles can stand behind the purpose, bounds, and division of
responsibility.

### Acceptance

Invocation authorizes reaching agreement, not work under an agreement the human
has not seen. Begin only after a subsequent human message explicitly accepts
the presented agreement. A question, revision, or acknowledgment continues the
dialogue. If intent is unclear, ask whether the agreement is accepted.

After acceptance, choose a technical task ID and create:

```text
{store}/{task}/
  agreement.md
  record.jsonl
```

Write the accepted agreement and open the record with a `start` event that
references it. The record, not session memory, carries the work forward.

## Own the work

Within the agreement, choose and adapt the implementation. Follow evidence
rather than preserving the first approach. Record an `approach-change` when the
change is material.

Look actively for bounded parts that supporting agents can carry when
delegation would improve focus, speed, independent scrutiny, or parallel
progress. Give each the relevant purpose, context, bounds, and expected return.
Examine what comes back and keep responsibility for the course, integration, and
the completed work. Do not delegate reserved decisions or let delegation hide a
consequential choice.

Bring a `question` to the human when a choice touches purpose, accepted risk,
resources, authority, or judgment the agreement kept human. Include evidence
and counsel. Do not send routine implementation choices back merely because
they are difficult. Do not make or foreclose the consequential choice before
direction arrives.

## Present work for review

At an agreed review point, make the work itself available for inspection. Write
a report from `templates/report.md` that names the judgment sought, choices
still open, what will grow harder to change, and the agent's counsel. Append
`review`, `report`, and `question` events, then stop before making or foreclosing
the reserved choice.

Tell the human which work is ready for review and ask the question the agreement
kept human. Do not name the review as though it were a phase, deliverable, or
piece of work for the human to approve.

Read later human messages against the open question. A request for more
evidence or a follow-up question is a `check-in`; the reserved judgment remains
open. A clear answer is `direction`; record it and resume accordingly.

Direction may continue the work, request revision, change its course, or end it.
When correction is requested, revise the work without acting beyond the
unresolved judgment, then report and ask again. Responsibility for
implementation remains yours.

An internal pause for testing or reflection is not a review. Authority returns
to the human only where the agreement reserves it, where the human requests a
review, or where a consequential question exceeds the agreement.

## Keep the record

Read `spec/record.md` before writing the first event. Append material events to
`{store}/{task}/record.jsonl`; never rewrite valid history.

Write reports as durable markdown documents under `{store}/{task}/reports/` and
index them with `report` events. Use `templates/learning-note.md` when another
session would otherwise have to rediscover an important lesson. Learning notes
inform later judgment; they do not become rules.

Apply `spec/check-in.md` whenever the human speaks first. Invoking the
`check-in` skill does not make incidental conversation a check-in.

Record `completion` when the agreement's outcome and evidence are satisfied and
no reserved completion judgment remains. If the agreement keeps that judgment
human, present the completed work for review and ask the question. Record `end`
when the work stops without completion. Preserve unresolved facts plainly in
either case.

Improve Accord at its source, not in an installed copy.
