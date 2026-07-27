---
name: check-in
description: Use when the user invokes this skill or human input during active work may be a check-in. Requires active work under an accepted agreement.
---

# Check in

The framework files are at the plugin root, two directories above this file. If
the creed has not been read in this session, read `creed/agent.md` and
`creed/human.md`. Read `spec/check-in.md` before treating the message as a
check-in.

For a possible check-in, run `tools/location` from the target project's root.
Find the active agreement that covers the message. A record with a `completion`
event is closed; do not reopen or append to it. If several active agreements
could cover the message, ask which one. If none does, say so plainly and offer
to use Accord to reach an agreement for the work. A closed agreement counts as
none.

For an open question, follow the responsibilities for presenting work in
`skills/accord/SKILL.md`. Use `templates/report.md` for a durable account or
when presenting work for review, and point to the work itself.
