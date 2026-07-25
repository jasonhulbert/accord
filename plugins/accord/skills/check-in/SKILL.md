---
name: check-in
description: Use when the user invokes this skill or speaks first during active work under Accord, including statuses, accounts, counsel, reviews, new context, changed terms, questions, and answers to open questions. Requires an existing Accord.
---

# Check in

The human has spoken first while work is active. Answer from the work itself.

The framework files are at the plugin root, two directories above this file. If
the creed has not been read in this session, read `creed/agent.md` and
`creed/human.md`. Read `spec/check-in.md`.

Run `tools/location` from the target project's root to find its record store
under `~/.accord/projects/`. Find the agreement there that covers the message.
If several could, ask which one. If none does, say so plainly and offer to begin
an Accord.

Read the agreement, record, reports, learning notes, and actual work before
responding. Do not reconstruct the state from memory or from the most recent
report alone.

Follow `spec/check-in.md`. For an open question, follow the responsibilities for
presenting work in `skills/accord/SKILL.md`. Use `templates/report.md` for a
durable account or when presenting work for review, and point to the work
itself.
