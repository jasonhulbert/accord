---
name: visual-explanation
description: Show Accord work through Mermaid when the human asks to see a flow, relationship, or cross-cutting change without reconstructing it file by file.
---

# Show the work visually

A visual explanation gives the human another way to understand the work.

Invoke the `accord` skill to establish context from the active agreement,
record, durable documents, and actual work. A diagram neither reopens closed
work nor creates a review.

## Let picture and prose work together

Name the question and scope. Use a diagram where seeing helps more than reading.
Use prose for context and uncertainty. Keep implemented behavior, intent, and
inference distinct.

Choose the smallest set that preserves consequential differences. Use a
flowchart for relationships and a sequence diagram for order. Keep Mermaid
source free of configuration, links, and HTML.

## Keep the picture with the work

Put the completed Markdown in a temporary file and run:

```text
accord document TASK diagram --file FILE --name DESCRIPTION.md --json
```

Remove the temporary file after success. Use the returned `ref` on the event
that explains the account:

```text
accord append TASK TYPE --actor ACTOR --summary SUMMARY --ref REF --json
```

The picture belongs to the narrative, not an event of its own. It does not
replace the plain event summary or the implementation beneath it.

If the human asks to inspect the account, make its Markdown and the actual work
available through Accord's existing review boundary. Without active work, keep
the diagram in the conversation.
