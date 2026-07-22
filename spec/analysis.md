# Reading the corpus

Because every journey line is self-describing, `cat expeditions/*/journey.jsonl` is a valid cross-expedition corpus with no join logic. It can answer descriptive questions such as:

- **Rider frequency** — how often questions ride home, and in which charter categories. A charter that generates riders at every fork was drawn too narrow; one that never generates them may be drawn too loose.
- **First-approach survival** — how often the route approved at departure holds to arrival, versus how often `course-change` events redraw it.
- **Crossings failed** — where attempts fail, and what the failures had in common.
- **Scout reports later contradicted** — where a `scout-report` was corrected by later events, a measure of how much the nearer view changed the map.

**These analytics are descriptive only.** They exist to feed the patron's judgment — calibrating future charters, choosing where to send scouts, deciding what dangers to accept in advance. They must never auto-generate rules, scores, or instructions that flow back to the agent. Punishing every wrong turn teaches the company to conceal them; a corpus mined for compliance stops being an honest map. This boundary is permanent, not merely out of scope.
