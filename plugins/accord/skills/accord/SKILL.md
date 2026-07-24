---
name: accord
description: Run substantial human-agent work under Accord. Use when the user invokes Accord by name, asks to start or resume an Accord, or wants a purpose-led working agreement for consequential work whose implementation path is not fully known. Do not use for small, routine, or completely specified tasks. Establishes the human, agent, and investigator roles; reaches agreement through dialogue before work begins; and keeps an append-only record under .accord/.
---

# Accord

The human holds the purpose. You hold the work. Reach agreement on the space
between them before beginning.

The framework files are at the plugin root, two directories above this file.
Read `creed/agent.md`, `creed/human.md`, and `creed/investigator.md` before
acting. Do not delegate these readings. The creed carries the point of view;
this skill carries only what is needed to work under it.

## Reach agreement

Look for `.accord/` in the target project. If an existing agreement covers the
request, resume from it. Read its agreement, record, reports, learning notes,
and actual work. If a review or question is open, wait for human direction.
Otherwise orient the human to the current state and continue within the
agreement.

If no agreement covers the work, inspect enough of the project and request to
offer informed counsel. Draft an agreement from `templates/agreement.md`. Name
material risks, missing resources, unclear authority, bounds that leave too
little or too much room, and review points where human judgment would still
have leverage. Ask only for context that would change the agreement
consequentially. Make recommendations where judgment is yours.

Present the complete draft and counsel to the human. Discuss and revise them
until both roles can stand behind the purpose, bounds, and division of
responsibility.

### Acceptance

The message that invokes Accord authorizes reaching agreement, even when it
also says “start,” “proceed,” or “go ahead.” It does not accept an agreement the
human has not yet seen.

Begin the work only after a subsequent human message explicitly accepts the
presented agreement. A question, revision, or acknowledgment continues the
dialogue. If intent is unclear, ask whether the agreement is accepted and the
work should begin.

After acceptance, create:

```text
.accord/{task}/
  agreement.md
  record.jsonl
```

Write the accepted agreement and open the record with a `start` event that
references it. The record, not session memory, carries the work forward.

## Own the work

Within the agreement, choose and adapt the implementation. Follow evidence
rather than preserving the first approach. Record an `approach-change` when the
change is material.

Use investigators for bounded questions that are cheaper to answer before the
work commits. Give the investigator the question and relevant context. Keep
responsibility for interpreting the report and deciding what follows.

Bring a `question` to the human when a choice touches purpose, accepted risk,
resources, authority, or judgment the agreement kept human. Include evidence
and counsel. Do not send routine implementation choices back merely because
they are difficult. Do not make or foreclose the consequential choice before
direction arrives.

## Meet at reviews

At an agreed review point, make the work itself available for inspection. Write
a report from `templates/report.md` that names the judgment sought, choices
still open, what will grow harder to change, and the agent's counsel. Append
`review`, `report`, and `question` events, then stop. Do not advance beyond the
review in the same run.

Read later human messages against the open question. A request for more evidence
or a follow-up question is a `check-in`; the review remains open. A clear answer
is `direction`; record it and resume accordingly.

Direction may continue, request another pass over the reviewed work, change the
approach, amend the agreement, or end the work. When correction is requested,
revise the reviewed work without advancing beyond the review, then report and
ask again. Human judgment shapes the outcome; responsibility for implementation
remains yours.

An internal pause for testing or reflection is not a review. Authority returns
to the human only where the agreement reserves it, where the human requests a
review, or where a consequential question exceeds the agreement.

## Keep the record

Read `spec/record.md` before writing the first event. Append material events to
`.accord/{task}/record.jsonl`; never rewrite valid history. The twelve types are
`start`, `investigation`, `attempt`, `review`, `report`, `question`,
`direction`, `check-in`, `approach-change`, `completion`, `end`, and `note`.
Use `note` when no more specific type fits. The record describes what happened;
it does not require an event for every phase or tool call.

Write reports as durable markdown documents under `.accord/{task}/reports/` and
index them with `report` events. Use `templates/learning-note.md` when another
session would otherwise have to rediscover an important lesson. Learning notes
inform later judgment; they do not become rules.

Receive a human-initiated message during active work according to
`spec/check-in.md`. The `check-in` skill is the explicit channel, but the
responsibility applies whenever the human speaks first.

Record `completion` when the agreement's outcome and evidence are satisfied and
no reserved completion judgment remains. If the agreement keeps that judgment
human, bring it to review as a question. Record `end` when the work stops
without completion. Preserve unresolved facts plainly in either case.

This skill ships with Accord. Improve the source framework rather than editing
an installed copy.
