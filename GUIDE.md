# Working with Accord

Accord is for substantial work whose outcome matters and whose implementation
cannot be specified honestly at the beginning. It gives the agent room to own
the work while keeping purpose and consequential judgment with the human.

It is unnecessary for small, routine, or fully specified tasks.

## Begin with agreement

Invoke the `accord` skill in the project where the work belongs. The agent uses
the standalone CLI to find active records and reads any agreement that may
already cover the request.

A completed or ended agreement stays closed. Later work begins with a new
agreement even when earlier history informs the agent's counsel.

When no agreement applies, the agent inspects enough context to draft one. The
draft names what matters, what good looks like, useful review points, accepted
risks and resources, the agent's room to act, and questions kept by the human.
It is an invitation to talk, not a request rewritten as policy.

Work begins only after the human has seen and explicitly accepted the
agreement. Invoking Accord is not acceptance.

## Let the agent hold the work

Within the agreement, the agent investigates, implements, verifies, delegates,
and changes approach as evidence demands. A hard implementation choice is not
automatically a human decision.

The agent returns a question when a choice touches purpose, accepted risk,
resources, authority, or judgment the human kept. It brings evidence and
counsel. The human's direction resolves that judgment without taking
implementation responsibility away from the agent.

The record keeps material events visible across sessions. It is memory, not a
score. Failed attempts and uncertainty belong beside successful work because
later judgment needs both.

## Review while change remains practical

At an agreed review point, the agent makes the actual work available and gives
enough orientation to inspect it. A report may point to evidence; it cannot
stand in for the work.

The human judges whether the work serves its purpose while consequential
choices can still change. A follow-up question leaves the reserved judgment
open. Direction returns the work to the agent.

Completion is the final judgment kept human. The agent may recommend completion,
but the record closes as complete only when the human explicitly agrees.

## Check in when context changes

Invoke `check-in`, or speak during active work, when the message bears directly
on the agreement or work. This includes requests for an account or inspection,
new context, changed risks or resources, and responses to open questions.

The agent answers from the agreement, record, durable documents, and actual
work. Sidebar questions remain ordinary conversation and stay out of the
record.

## Ask to see cross-cutting work

Invoke `visual-explanation` when behavior or intent is scattered across several
parts of the work. The agent prepares the smallest useful Markdown account,
using Mermaid where a picture clarifies relationships or order.

A diagram distinguishes implemented behavior, intent, and inference. It does
not create a review or replace the implementation beneath it.

## Understand where records live

From a project directory, `accord location` reports the active and archived
record roots. `accord list` reports stored work without deciding which agreement
applies. `accord context TASK` reads one explicitly named active record;
`--archived` reads explicitly named archived work.

Active work lives at:

```text
~/.accord/projects/{project-key}/{task}/
```

Archived work lives at:

```text
~/.accord/archive/projects/{project-key}/{task}/
```

Each task directory carries its agreement, `record.jsonl`, reports, learning
notes, and diagrams together. The project key is derived from the Git worktree
root so similarly named projects do not collide.

## Let history recede explicitly

Closing work does not archive it. Move closed work out of routine discovery
only through an explicit command:

```text
accord archive TASK
```

The CLI requires a valid record ending in `completion` or `end`. It moves the
whole directory without rewriting any file and refuses path collisions or
unsafe links.

An explicit override may archive unclosed work:

```text
accord archive TASK --force
```

The warning remains visible, and the record stays open. Restore that work before
resuming it:

```text
accord restore TASK
```

Restoration reverses storage placement. It never merges directories, rewrites
evidence, or reopens completed work.

## Keep the relationship capable

- Name why the work matters, not every move.
- Reach agreement rather than issuing one.
- Give the agent enough room to exercise judgment.
- Inspect the work itself, not only its report.
- Answer questions whose judgment remains human.
- Judge the outcome without demanding a straight line.
- Choose again when evidence changes the work's value or cost.

Accord clarifies responsibility so trust has room to work. It should never turn
collaboration into approval theater or the record into surveillance.
