# Reading Accord records

Because every record line is self-describing, combining
`.accord/*/record.jsonl` creates a cross-task corpus without join logic. It can
support descriptive questions such as:

- how often reserved questions return to the human, and about which subjects;
- how often the first approach holds compared with later `approach-change`
  events;
- where attempts fail and what those failures have in common;
- where investigation findings are corrected by later evidence;
- where reviews occur relative to changes that become expensive.

These observations exist to improve human judgment: shaping future agreements,
choosing useful review points, and deciding which risks to accept in advance.
They must not generate instructions, compliance scores, or autonomy ratings
that flow back to the agent.

A record mined for obedience will stop being an honest record.
