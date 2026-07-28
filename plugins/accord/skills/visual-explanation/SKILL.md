---
name: visual-explanation
description: Show Accord work through Mermaid when the human asks to see a flow, relationship, or cross-cutting change without reconstructing it file by file.
---

# Show the work visually

A visual explanation gives the human another way to understand the work. It
turns a flow, relationship, or idea into something grasped at a glance.

Begin from the active agreement, record, and actual work. If they are not
already in hand, resume through the `accord` skill. A diagram neither reopens
closed work nor creates a review.

## Let picture and prose work together

Name its question and scope. Use a diagram where seeing helps more than
reading. Use prose for context, exceptions, uncertainty, and useful
implementation references. Keep implemented behavior, intent, and inference
distinct.

Choose the smallest set that preserves consequential differences. Flowcharts
suit relationships and decisions. Sequence diagrams suit order and
responsibility over time. Verify other Mermaid forms in the record view before
relying on them.

## Keep the picture with the work

Write active work as Markdown under `diagrams/{descriptive-name}.md`, with prose
around fenced `mermaid` blocks. Reference the account from the existing event
that explains it. The picture belongs to the narrative, not an event of its
own.

The record view owns theme and safety. Leave configuration, links, images,
click actions, and HTML out of Mermaid source.

If the human asks to inspect the account, return through Accord's existing
review boundary and `accord serve`. Without active Accord work, keep the
diagram in the conversation.
