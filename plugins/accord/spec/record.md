# The Accord record

Each body of work has an append-only `record.jsonl` stored with its agreement
and durable documents. The standalone CLI resolves the project location,
validates every event, and performs every mutation. `accord start` stores an
accepted agreement and opens its record as one operation.

The record describes what happened. It does not score the agent, prescribe the
next action, or turn earlier experience into a rule.

## Keep evidence readable

- **Append only.** Corrections follow the events they correct. Valid history is
  never rewritten.
- **Readable alone.** Every event carries its task ID, actor, time, type, and a
  plain summary.
- **Narrative first.** Structured fields support validation and comparison.
  Context that needs no structure stays in the summary.
- **Language is evidence.** Words in a record show what was said and done. They
  do not define Accord's vocabulary or create authority.
- **Small vocabulary.** A material event that fits no specific type is a
  `note`.

## Name what happened

Every event names an actor: `human`, `agent`, or `supporting-agent`.
`investigator` remains valid in stored schema-1 history. New events use the
current actor names; existing records are not rewritten.

The event types mean:

| Type | Meaning |
|---|---|
| `start` | The human accepts the agreement and authorizes the work. |
| `investigation` | A bounded inquiry reports evidence, inference, and limits. |
| `attempt` | An attempt succeeds or fails. |
| `review` | Work reaches a point where human judgment is reserved before it advances. |
| `report` | A reference indexes a durable report. |
| `question` | A consequential choice returns to the human. |
| `direction` | The human answers an open question. |
| `check-in` | Human input meets the boundary in `check-in.md`. |
| `approach-change` | The approach changes while the purpose remains. |
| `completion` | The human approves recording the work as complete. |
| `end` | The work ends without completion. |
| `note` | A factual event fits no more specific type. |

An `attempt` records whether it succeeded or failed. A `question` names the
judgment sought. A `direction` carries the human's answer. The CLI validates
these fields; the agent remains responsible for choosing the event whose
meaning matches what happened.

Changing the event or actor set changes the shared record contract. It requires
human agreement, not an implementation choice made in passing.

## Let closure remain closed

A `completion` follows the human's explicit judgment, ordinarily recorded as a
`direction`. The agent's evidence or confidence is not approval.

`completion` and `end` are terminal. No later request reopens the agreement, and
no later event is appended to that record. Related work receives a new
agreement and record.

Archive and restore move the complete task directory. They add no event and
change no record byte. Archival changes routine visibility, not state.
Restoration does not reopen completed or ended work.

## Keep documents with their account

Agreements, reports, learning notes, and visual explanations are Markdown. A
`start` points to the agreement. A `report` points to its report. A visual
explanation lives under `diagrams/` and is referenced by the event that explains
why it exists; it has no event type of its own.

References remain within the work they describe. A new agreement, record, or
report does not point to another work's agreement or reports. It carries the
context needed to stand on its own.

The CLI validates structure and storage integrity. Validation proves that the
record is well formed. It cannot decide whether the right event was recorded or
whether a human judgment was earned.
