# The Accord record

Each active agreement keeps an append-only record at
`{store}/{task}/record.jsonl`, where `{store}` is the project directory printed
by `tools/location` under `~/.accord/projects/`. One JSON object occupies each
nonblank line.

The record describes what happened. It does not score the agent, prescribe the
next action, or turn earlier experience into a rule.

## Design

- **Append only.** Corrections are later events with references to what they
  correct. Previously valid lines do not change.
- **Readable alone.** Every event carries its task id, actor, time, type, and a
  plain summary. Records from several tasks can be combined without a join.
- **Narrative first.** Structured fields support validation and comparison.
  Context that does not need structure stays in `summary`.
- **Small vocabulary.** The event set covers the responsibilities in the creed.
  A material event that fits no specific type is a `note`.

## Envelope

Every event has:

| Field | Required | Meaning |
|---|---|---|
| `ts` | yes | ISO 8601 timestamp |
| `task` | yes | task id, matching `{task}` in `{store}/{task}/` |
| `schema` | yes | schema version, currently `"1"` |
| `type` | yes | one of the twelve event types below |
| `actor` | yes | `human`, `agent`, or `supporting-agent` |
| `summary` | yes | plain-language account of what happened |
| `refs` | no | task-relative paths or ids the event points to |

Three types require one additional field: `attempt.outcome`,
`question.subject`, and `direction.decision`. No other structured payload is
defined.

## Event types

| Type | Meaning |
|---|---|
| `start` | The human accepts the agreement and authorizes the work. |
| `investigation` | A bounded inquiry reports its evidence, inference, and limits. |
| `attempt` | An attempt at part of the work. `outcome` is `succeeded` or `failed`. |
| `review` | The work reaches a point where human judgment is reserved before it advances. |
| `report` | A reference event indexing a report in `refs`. |
| `question` | A consequential choice returns to the human. `subject` names the judgment sought. |
| `direction` | The human answers an open question. `decision` carries the answer. |
| `check-in` | The human speaks first during active work with a request, context, or proposed change. |
| `approach-change` | The approach changes while the purpose remains. |
| `completion` | The work satisfies the agreement's stated outcome and evidence. |
| `end` | The work ends without completion. |
| `note` | A factual event that fits no more specific type. |

Changing the event or actor set changes the shared record contract. It requires
human agreement, not an implementation choice made in passing.

Schema version `"1"` also accepts `investigator` so records written before the
supporting-agent role was adopted remain valid. New events use
`supporting-agent`; append-only history is not rewritten to adopt new
vocabulary.

## Documents and events

Agreements and reports are markdown-primary: the document carries the
conversation and its voice, while `start` and `report` events point to it.
Investigations, attempts, reviews, questions, directions, check-ins, approach
changes, completion, and endings are record-primary. A supporting agent records
the kind of work it did rather than receiving a separate event type merely
because the work was delegated.

Learning notes may be referenced by `note` events when the reference matters to
resumption.

## Validation

`tools/validate` checks each nonblank line against `spec/record.schema.json`.
Validation proves only that an event is well formed. It does not decide whether
the right events were recorded.
