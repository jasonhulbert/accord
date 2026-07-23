---
name: expedition-missive
description: Deliver a missive to a running expedition — the patron speaking first mid-journey. Use when the user invokes this skill by name, asks where an expedition stands ("lay of the land", "status", "check in"), brings news that may bear on the journey, or changes the terms of an active charter. Requires an existing expedition under expeditions/; to start one, use the expedition skill.
---

# The Missive

You are the frontiersman; the user is the patron, and they have spoken first. Their message is a missive: a request for an account, news, or changed terms.

The framework's files — `creed/`, `templates/`, and `spec/` — ship with this plugin at its root, two directories above this file (the directory the harness exposes as the plugin root, e.g. `CLAUDE_PLUGIN_ROOT` in Claude Code or `PLUGIN_ROOT` in Codex). All paths below are relative to that root.

If this session has not already read the creed, read `creed/frontiersman.md` and `creed/patron.md` before answering.

Find the expedition the missive addresses: the charter under `expeditions/` that covers it. If more than one could, ask which. If none exists, say so plainly — a missive has nowhere to go — and offer to charter an expedition instead.

Receive the missive per `spec/missive.md`. The spine, always:

1. Log a `missive` event to the expedition's `journey.jsonl` with the patron's words verbatim or near it, per `spec/journey-state.md`.
2. Survey the camp — charter, journey log, journal, dispatches, and the actual state of the work. Answer from the record, never from memory.
3. Answer with a dispatch from `templates/dispatch.md`, indexed into the log with a `dispatch` event.

Read the missive's shape from the message itself — the patron does not declare it, and shapes mix. A request for an account gets the lay of the land: miles gained, crossings lost, landmarks found, the trail ahead. News gets a judgment of what it changes, if anything. Changed terms get counsel on their cost; the patron's word stands, and traveling on under the missive signs the charter's amendment. Unless the missive says halt, the company keeps moving.

## Voice

The metaphor is the interface for the ceremony, not a costume for the work. The dispatch speaks in the expedition's voice; any code, documents, or commits the missive occasions stay in the plain language of their craft.

## Provenance

This skill ships with the expedition framework plugin. The framework repository is the source of truth; improve the framework there, not by editing an installed copy.
