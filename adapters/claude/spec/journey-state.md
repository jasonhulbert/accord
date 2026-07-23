# Journey State

Each expedition keeps one append-only log: `expeditions/{name}/journey.jsonl`, one JSON object per line. The log is the expedition's memory of what happened. It describes; it never prescribes. No schema here creates an obligation to emit any event — "every phase must emit event X" is the failure mode this spec exists to avoid.

## Rules

- **Append-only.** Lines are never rewritten or deleted. A correction is a subsequent event that says what the earlier one got wrong.
- **Self-describing.** Every line carries `expedition` and `schema`, even though they are redundant within one file, so `cat expeditions/*/journey.jsonl` is a valid cross-expedition corpus with no join logic.
- **Narrative-first.** Prose lives inside events, in `account`. The structured payload carries only what comparison and rendering need; everything else stays narrative.
- **Escape hatch.** Anything that fits no other type is logged as an `account` event rather than forced into the wrong type or skipped.

## Envelope

Every event has:

| Field | Required | Meaning |
|---|---|---|
| `ts` | yes | ISO 8601 timestamp |
| `expedition` | yes | expedition id (the `{name}` in `expeditions/{name}/`) |
| `schema` | yes | schema version, currently `"1"` |
| `type` | yes | one of the twelve event types below |
| `actor` | yes | `patron`, `frontiersman`, or `scout` |
| `account` | yes | free-text prose telling what happened |
| `refs` | no | paths or ids this event points to (documents, earlier events) |

Three types carry one additional required field each: `crossing.outcome`, `rider.category`, `word.answer`. No other structured payload is defined; new structure must earn its place.

## Event taxonomy

A closed set of twelve, each traceable to the canon. Adding, removing, or renaming a type is a rider to the patron, never an implementation choice.

| Type | Canonical root | Meaning |
|---|---|---|
| `departure` | "An expedition begins when the patron decides that something beyond the horizon is worth seeking." | The expedition begins under charter. |
| `scout-report` | "The scouts test the crossing, climb the ridge, and report the land as they found it." | An investigation reports the land as found, not as hoped. |
| `crossing` | "Failed crossings beside successful ones." | An attempt at part of the route. `outcome`: `succeeded` or `failed`. |
| `basecamp` | "Build basecamps, not settlements." | A rest point: gather, compare what was learned, prepare for what comes next. |
| `dispatch` | "A patron who remains behind learns through dispatches." | Reference event indexing a markdown dispatch (in `refs`). |
| `rider` | "Answer the questions that ride home." | A question sent to the patron. `category` matches one of the charter's rider categories. |
| `word` | "The patron sends back word: press on, turn aside, or return." | The patron's answer. `answer`: free text; `refs` points at the rider. |
| `missive` | "The patron need not wait to be asked." | The patron speaks first: a request for an account, news, or changed terms. `account` carries the patron's words verbatim or near it. |
| `course-change` | "The craft lies in changing course without losing the reason for the journey." | The route changed while the purpose held. |
| `arrival` | "It says what will count as arrival." | The expedition accomplished its commission. |
| `return` | "Press on, turn aside, or return." | The expedition ends without arrival. |
| `account` | "The day's discoveries are recorded while the fire still burns." | Free-form escape hatch. |

## Authority split

Charters and dispatches are **markdown-primary**: documents with voice, indexed into the log by reference events (`departure`, `dispatch`) whose `refs` point at them. Crossings, scout reports, riders, words, missives, basecamps, and course changes are **log-primary**: the log line is the record, rendered into prose when needed.

## Validation

`tools/validate` checks a `.jsonl` file line-by-line against `spec/journey.schema.json`. Validation confirms only that a line is well-formed; it never judges whether the right events were logged.
