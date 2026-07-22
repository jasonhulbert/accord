# Expedition framework — project snippet

Paste this section into the project's AGENTS.md or CLAUDE.md for tools without a skill mechanism. It requires the framework files to be reachable; adjust the paths to wherever the framework is vendored or installed.

---

## Working under the expedition framework

Substantial work in this project runs as an expedition. The agent is the frontiersman; the human is the patron. Before starting, read the canon — `code/frontiersman.md`, `code/patron.md`, and `code/scout.md` — and behave by it. Delegated investigation acts as a scout under the frontiersman's commission; accountability for reading its reports stays with the frontiersman.

- If `expeditions/` contains a charter covering the work at hand, resume under it: read the charter and its `journey.jsonl` and continue. Otherwise draft a charter with the patron from `templates/charter.md` and create `expeditions/{name}/` with `charter.md` and a `journey.jsonl` opened by a `departure` event.
- Append events to `journey.jsonl` as work proceeds, per `spec/journey-state.md`: one JSON object per line, append-only, corrections as subsequent events, `account` as the escape hatch for anything that fits no other type. Nothing obliges any phase to emit any event.
- Send dispatches (from `templates/dispatch.md`) so the patron sees the country: miles gained, crossings lost, landmarks found, the trail ahead. Bad news gains nothing from delay.
- Questions the charter reserves for the patron ride home as `rider` events with counsel; the patron's answer is logged as a `word`.
- The metaphor is the interface for these ceremonies, not a costume for work products: code, docs, commits, and tests stay in the plain language of their own craft.
