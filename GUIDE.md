# Working with Accord

Accord is for substantial work whose outcome matters and whose implementation
cannot be specified honestly from the beginning. It gives the agent room to own
the work while keeping purpose and consequential judgment with the human.

It is unnecessary for small, routine, or fully specified tasks. Agreement should
clarify uncertain work, not make ordinary work feel important.

## How the work begins

Invoke the `accord` skill in the project where the work belongs. If an existing
active agreement already covers it, the agent reads the record and actual work
before resuming. A completed agreement stays closed. Later work begins with a
new agreement, even when it follows closely from what came before.

Earlier work may inform the agent's counsel, but it does not lend authority to
the new work. The new agreement and record stand on their own rather than
linking to earlier agreements or reports.

When no active agreement covers the request, the agent inspects enough context
to draft an agreement and offer counsel.

The draft names:

- what matters and what good looks like;
- where the agent recommends beginning;
- resources and accepted risks;
- the agent's room to act;
- review points where your judgment will still have leverage;
- questions that must return to you before the agent acts.

The draft is an invitation to talk. Question it. Correct missing context. Push
back on bounds that feel too narrow or too loose. Ask what the agent recommends
and why. The agent should name costs, dangers, and omissions rather than turning
your first request into polished agreement language.

When both sides can stand behind the result, accept it plainly. The invocation
that began the conversation does not also count as acceptance. You cannot
accept an agreement you have not seen.

## While the agent works

Within the agreement, the agent owns implementation. It may investigate,
experiment, verify, and change approach as evidence demands. A difficult
implementation choice is not automatically a human decision.

The agent returns a question when a choice touches purpose, resources, accepted
risk, authority, or judgment you kept. Expect evidence and counsel with the
question. Your direction resolves that judgment and puts the work back in
motion.

The agent keeps the work's record outside the project workspace so material
events remain visible across sessions. It is memory, not surveillance. Failed
attempts belong beside successful ones because later judgment needs both.

## Review while change remains practical

At an agreed review point, the agent makes the actual work available, gives you
enough orientation to inspect it, and stops before advancing beyond the
judgment you reserved.

Review the work, not merely the report. Say where its shape, quality,
usefulness, or character serves the purpose and where it does not. The agent
remains responsible for turning that judgment into implementation.

A follow-up question keeps the review open. Direction may continue the work,
request another pass over what you reviewed, change the approach, amend the
agreement, or end the work.

A review is useful because choices remain open. If every detail requires
approval, the agreement gave the agent no room. If the first meaningful review
arrives after every consequential choice has hardened, the human never held
meaningful judgment.

Completion is the final judgment kept human. When the agent believes the
agreement has been satisfied, it presents the work and its evidence. The record
closes as complete only when you explicitly agree.

## Check in when you need to

You do not have to wait for a scheduled review. Invoke `check-in`, or simply
speak during active work, when your message bears directly on the agreement or
the work:

- you want an account of where things stand;
- you need to inspect the current work;
- you have context the agent could not know;
- resources, risks, or priorities have changed;
- you are answering or following up on an open question.

The agent reads the agreement, record, reports, and current work before
responding. A status request does not automatically halt execution. A request
to inspect the work creates a review where it stands. Changed terms receive
counsel before they become part of the agreement.

Sidebar questions remain ordinary conversation and stay out of the record.

## What Accord asks of the human

**Name why, not only what.** A result can satisfy a request and still fail its
purpose.

**Reach agreement rather than issuing one.** The agent's counsel is part of the
agreement, not resistance to it.

**Give trust a shape.** Too little authority turns the agent into a sequence of
permission requests. Too much makes every consequential choice appear
delegated.

**Inspect the work itself.** Reports orient judgment. They cannot exercise it
for you.

**Answer reserved questions.** Work waiting for human judgment still spends
time and attention.

**Judge the outcome without demanding a straight line.** Failed attempts and
changed approaches may be evidence that the agent was paying attention. Decide
plainly when the work should be recorded as complete.

**Choose again when the evidence changes.** Only the human can decide whether
an outcome remains worth its cost.

## Common failures

**The handed-down agreement.** A finished specification presented for obedience
has skipped the conversation where practical risk and authority become clear.

**The everything agreement.** Trying to predict every choice recreates
step-by-step management. Agree on what must remain true and who owns the
judgment.

**The unbroken run.** Substantial, taste-sensitive work can advance past the
point where human judgment has leverage. Choose review points with something
coherent to inspect and meaningful options still open.

**Review by summary.** A convincing account can conceal an unhelpful result.
Follow the references and inspect the work.

**Taking implementation back.** Human feedback about quality and purpose is not
micromanagement. Prescribing every corrective move without hearing the agent's
counsel is.

**Treating every message as a check-in.** Incidental conversation does not
belong in the work's record. A check-in changes only what its content changes;
it does not make the agent surrender ordinary execution.

**A record used as a score.** Once failure is punished through the record,
failure will disappear from the record before it disappears from the work.

**Cold literalism.** Human and agent are collaborators with different
responsibilities, not components exchanging inputs and approvals.

## Where things live

Accord keeps its records outside the project workspace. From the project root,
`tools/location` prints its record directory. The default location is
`~/.accord/projects/{project-key}/`; `{project-key}` is derived from that
project's root so records from similarly named projects do not collide.
Each body of work has a technical task ID used only in paths and interfaces.
`{task}` stands for that ID below.

- `~/.accord/projects/{project-key}/{task}/agreement.md` — the accepted understanding and later
  amendments;
- `~/.accord/projects/{project-key}/{task}/record.jsonl` — the append-only factual record;
- `~/.accord/projects/{project-key}/{task}/reports/` — durable reports and review orientation;
- `~/.accord/projects/{project-key}/{task}/learning-*.md` — context another session should not have to
  rediscover.

The agreement gives the work room. The record lets that room survive a change
of session.

## Inspect a live record

To inspect active work under Accord, run the user-facing command from the
target project root:

```text
accord serve
```

Plugin hosts that expose plugin `bin` commands make this available when the
plugin is installed. If your host does not expose it, install the launcher once
from the installed plugin directory. From a source checkout, run:

```text
plugins/accord/tools/install-launcher
```

The view lists the project's records, lets you choose one, and refreshes as new
events are appended. It binds to localhost, opens a browser when possible, and
stops when you press `Ctrl-C`. Use `accord serve --task TASK` when the task ID
is already known, or `accord serve --no-open` when you only need the printed
URL.
