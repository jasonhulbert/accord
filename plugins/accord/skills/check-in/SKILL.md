---
name: check-in
description: Use when the user invokes this skill or human input during active work may be a check-in. Requires active work under an accepted agreement.
---

# Check in

Use this skill with the active agreement, record, durable documents, and actual
work. If the creeds are not already in hand, read `../../creed/agent.md` and
`../../creed/human.md`. Read `../../spec/check-in.md` before treating the
message as a check-in.

Run `accord version --json` and require agent protocol `"1"`. If the standalone
CLI is missing or incompatible, stop and say so. Do not fall back to bundled
tools or direct record writes.

Require a zero exit status and the expected JSON shape from every CLI command.
On failure, stop and surface the error. Do not act on partial output.

Run `accord list --json` in the target project. Find the active agreement that
may cover the message by requiring both `storage: "active"` and `state: "open"`,
then run `accord context TASK --json`. A record ending in `completion` or `end`
is closed. A closed agreement counts as none. Ask which work the human means
when several open agreements may fit. If none does, offer to use Accord to reach
an agreement for the work by invoking the `accord` skill.

For an open question, invoke the `accord` skill for resumption and review
handling. A skill handoff invokes a capability; it does not import hidden
reading instructions.

Use `../../templates/report.md` for a durable account or review orientation.
Store it through:

```text
accord document TASK report --file FILE --name report-DESCRIPTION.md --json
```

Then record the event through `accord append`. Point to the work itself.
