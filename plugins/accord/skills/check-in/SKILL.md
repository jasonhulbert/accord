---
name: check-in
description: Use when the user invokes this skill or human input during active work may be a check-in. Requires active work under an accepted agreement.
---

# Check in

Use this skill with the target project's agreement, record, reports, learning
notes, and actual work. If the creeds are not already in hand, read
`creed/agent.md` and `creed/human.md`. Read `spec/check-in.md` before treating
the message as a check-in.

For a possible check-in, run `tools/location` from the target project's root.
Find the active agreement that covers the message. A record ending in
`completion` or `end` is closed. If the message explicitly resumes unclosed
work archived with `--force`, use the `accord` skill; never search archives
speculatively. Ask which agreement when several fit. If none does, offer to use
Accord to reach an agreement for the work. A closed agreement counts as none.

For an open question, invoke the `accord` skill for agreement, resumption, and
review handling. This handoff does not import hidden reading instructions.

Use `templates/report.md` for a durable account or when presenting work for
review, and point to the work itself.
