---
name: check-in
description: Check in on active work under Accord. Use when the user invokes this skill by name, asks for status or an account, requests an unscheduled review, supplies context that may change the work, answers or follows up on an open question, or proposes changed terms for an existing Accord. Requires an existing Accord; use the accord skill to begin one.
---

# Check in

The human has spoken first while work is active. Answer from the work itself.

The framework files are at the plugin root, two directories above this file. If
the creed has not been read in this session, read `creed/agent.md` and
`creed/human.md`. Read `spec/check-in.md`.

Run `tools/location` from the target project's root to find its record store
under `~/.accord/projects/`. Find the agreement there that covers the message.
If several could, ask which one.

If the project contains a legacy `.accord/` directory that covers the message,
ask the human whether it should move to the home store. Do not create a second
record for the same work. If neither location contains an agreement, say so
plainly and offer to begin an Accord.

Read the agreement, record, reports, learning notes, and actual work before
responding. Do not reconstruct the state from memory or from the most recent
report alone.

First look for an open `question`. A clear human answer is `direction`, not a
`check-in`; record it and follow the review responsibilities in
`skills/accord/SKILL.md`. A follow-up question or request for evidence does not
resolve the review.

Otherwise append a `check-in` event with the human's words verbatim or near
them, then respond to what the message changes:

- For an account, report what changed, what did not work, what is known now, and
  what the agent recommends next.
- For a review request, make the current work inspectable, write a report, append
  `review`, `report`, and `question`, and wait for direction.
- For new context, explain its effect on the agreement and approach. If it
  changes nothing material, say so.
- For changed terms, counsel on cost, risk, and lost options. Treat the change
  as active only when human and agent share a workable understanding; record
  the amendment before continuing under it.

Use `templates/report.md` when the response needs a durable account or supports
a review. Point to actual work and evidence rather than substituting summary for
inspection.

A check-in does not halt execution merely because the human spoke first. Work
waits when the human requests review or a halt, closes authority the agreement
left open, or leaves a reserved question unanswered.

This skill ships with Accord. Improve the source framework rather than editing
an installed copy.
