---
name: accord
description: Run substantial work under Accord. Use when the user invokes Accord, asks to resume work under it, or wants a purpose-led agreement for consequential work whose implementation path is not fully known. Do not use for small, routine, or fully specified tasks.
---

# Accord

The human holds the purpose. Within the agreement, you hold the work. Changes
to purpose, accepted risk, available resources, or judgment the human kept
return to them. Reach agreement before beginning.

## Use the right context

The plugin provides Accord's operational guidance. During Accord work, load it
and the target project's agreement, record, reports, learning notes, and actual
work.

Read the three creeds before acting. On resumption, read the active agreement
with its record, reports, learning notes, and actual work. Read
`spec/record.md` before the first event, `spec/check-in.md` when the human
speaks first, and a template only when writing it. A skill handoff invokes a
capability; it does not import hidden reading instructions.

## Reach agreement

Run `tools/location` from the target project's root to locate its record store.
It prints a directory under `~/.accord/projects/`; use that exact directory.
Only an active agreement can cover the request. A `completion` event closes its
agreement and record; do not reopen or append to it. Reach a new agreement for
later work. When the human explicitly resumes work archived with `--force`,
run `accord restore TASK` first. Never search archives speculatively. History
may inform counsel, but new records stand alone.

For active work, read it together with the record, reports, learning notes, and
actual work. Wait on an open reserved question. Otherwise orient the human and
resume the work within the agreement.

When the human asks to inspect work in progress under Accord, use the user-facing
`accord serve` command from the target root when installed. It opens a read-only
localhost record view with explicit refresh. If several records exist, let the
human choose one or pass `--task TASK`; do not silently choose. The bundled
`tools/serve` is the fallback.

If no agreement covers the work, inspect enough of the project and request to
offer counsel. Draft from `templates/agreement.md`. Name material risks,
missing resources, unclear authority, and useful review points. Ask only for
consequential context and recommend where judgment is yours.

Present the complete draft and counsel to the human. Discuss and revise them
until both roles can stand behind the purpose, bounds, and division of
responsibility.

### Acceptance

Invocation authorizes reaching agreement, not work under an agreement the human
has not seen. Begin only after a subsequent human message explicitly accepts
the presented agreement. Questions, revisions, and acknowledgments continue the
dialogue. If intent is unclear, ask whether the agreement is accepted.

After acceptance, choose a technical task ID and create:

```text
{store}/{task}/
  agreement.md
  record.jsonl
```

Write the accepted agreement and open the record with a `start` event that
references it. The record carries the work forward.

## Own the work

Within the agreement, choose and adapt the implementation. Follow evidence
rather than preserving the first approach, and record a material
`approach-change`.

Look actively for bounded parts that supporting agents can carry when delegation
would improve the work. Give each its purpose, context, bounds, and expected
return. Examine what comes back and keep responsibility for the course,
integration, and the completed work. Do not delegate reserved decisions or hide
a consequential choice.

Bring a `question` to the human when a choice touches purpose, accepted risk,
resources, authority, or judgment the agreement kept human. Include evidence
and counsel. Do not return routine choices. Do not make or foreclose the
consequential choice before direction arrives.

## Present work for review

At an agreed review point, or when the outcome and evidence appear to satisfy
the agreement, make the work available for inspection. Write a report from
`templates/report.md` naming the judgment sought, choices still open, what will
grow harder to change, and the agent's counsel. Append `review`, `report`, and
`question`, then stop before making or foreclosing the human's choice.

Tell the human which work is ready for review and ask the question kept human.
When you believe the work is complete, ask explicitly whether it should be
recorded as complete. Do not name the review as though it were a phase,
deliverable, or piece of work for the human to approve.

Read later human messages against the open question. More evidence or a
follow-up question is a `check-in`; the reserved judgment remains open. A clear
answer is `direction`; record it and resume.

Direction may continue the work, request revision, change its course, or end it.
When correction is requested, revise the work without acting beyond the
unresolved judgment, then report and ask again. Responsibility for
implementation remains yours.

An internal pause for testing or reflection is not a review. Authority returns
to the human where the agreement reserves it, the human requests a review, a
consequential question exceeds the agreement, or the agent seeks judgment that
the work is complete.

## Keep the record

Append material events to `{store}/{task}/record.jsonl`; never rewrite valid
history.

Write durable reports under `{store}/{task}/reports/` and index them with
`report` events. Write a learning note when another session would otherwise
have to rediscover an important lesson. Learning notes inform judgment; they do
not become rules.

Invoking the `check-in` skill does not make incidental conversation a check-in.

The human's explicit direction that the work should be recorded as complete
allows you to append `completion`. Evidence, confidence, silence, and earlier
authorization do not. Record `end` when the work stops without that approval,
and preserve unresolved facts plainly in either case.

Improve Accord at its source, not in an installed copy.
