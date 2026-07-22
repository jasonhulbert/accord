# Implementation Plan: The Expedition Framework

This plan is the charter for the framework's first expedition: building itself. It records every decision settled during planning so implementation does not re-litigate them, breaks the work into basecamps, and names the questions that must ride home. An agent implementing from this plan acts as the frontiersman; Jason is the patron.

## Purpose

Package the expedition framework — a narrative role framework for human-in-the-loop AI work — so it is reusable across projects and distributable, without letting the packaging calcify into the prescriptive process it exists to replace. What must never be sacrificed: the canon shapes the traveler, never predicts the terrain; the framework prescribes that its ceremonies exist, never their choreography.

## Arrival

The expedition arrives when: the repo has the layered structure below with the canon unchanged in substance; the journey-state substrate is specified, exampled, and validatable; the skill adapter installs and operates with zero target-project configuration; a map rendering exists that replays a `journey.jsonl` into a visual journey; and the framework has been dogfooded on at least one real task (this implementation itself qualifies).

---

## Settled decisions (do not re-open; a change here requires a rider)

### Layers

- **Code** (`code/`): permanent, role-level, amended rarely. Ships with the package.
- **Charter**: per-expedition, disposable, allowed to be specific because it expires with the task. Templates ship; charters never live in the framework repo.
- **Journal**: per-project, accumulating. Maps, not mandates — entries inform future judgment, never bind it. Never travels back into the framework repo.
- Updates flow one way: canon improvements via package upgrade; project learnings stay home.

### Repository layout

```
code/                       frontiersman.md, patron.md (the canon — current approved revisions, unchanged)
templates/                  charter.md, dispatch.md, journal-entry.md
spec/                       journey-state.md (schema spec), journey.schema.json, examples/
adapters/
  claude/                   self-contained skill: SKILL.md + vendored code/ + templates/ (+ spec essentials)
  project-snippet.md        fallback for tools without a skill mechanism
tools/                      validate + render scripts, skill build script
README.md                   layer model, adoption path, amendment discipline
AGENTS.md                   existing contributor rules + layout + amendment discipline section
```

### Adoption model

- **Skill-first.** The skill installs per-user and travels across projects; no target-project configuration required. It establishes roles, drafts the charter with the patron, and creates `expeditions/{name}/` in the target project.
- The skill folder is **self-contained** (vendored copies of canon, templates, spec essentials). The repo is the source of truth; the skill is a build target. A build script produces `expedition.skill` (zip).
- On invocation in a project with an existing `expeditions/` charter for the work at hand, the skill **resumes** under that charter rather than drafting a new one. The `expeditions/` directory is the persistence mechanism.
- `adapters/project-snippet.md` remains as a deterministic fallback (paste into AGENTS.md/CLAUDE.md) for tools without skills.

### Journey state substrate

- **Per-expedition** append-only log: `expeditions/{name}/journey.jsonl`. One JSON object per line. Never rewritten; corrections are subsequent events.
- **Every line is self-describing**: carries the expedition id and schema version even though redundant within one file, so `cat expeditions/*/journey.jsonl` is a valid cross-expedition corpus with no join logic.
- **Actors**: `patron`, `frontiersman`, `scout`.
- **Event taxonomy — closed set of eleven**, drawn strictly from canonical vocabulary:
  `departure`, `scout-report`, `crossing` (with outcome), `basecamp`, `dispatch` (reference event), `rider` (with category matching the charter's rider categories), `word` (the patron's answer), `course-change`, `arrival`, `return` (expedition ends without arrival), `account` (free-form escape hatch — anything that fits no other type is logged here rather than forced or skipped).
- **Authority split**: charters and dispatches are markdown-primary (documents with voice), indexed into the log by reference events. Crossings, scout reports, riders, words, basecamps, and course changes are log-primary, rendered into prose when needed.
- **Envelope** (to be finalized in spec, roughly): `ts`, `expedition`, `schema`, `type`, `actor`, `account` (free text — prose lives inside events), plus optional `refs` and a minimal type-specific payload (`outcome`, `category`, `answer`). The structured payload carries only what comparison and rendering need; everything else stays narrative.
- Adding a new canonical term or event type falls under the AGENTS.md rule: only if the existing vocabulary cannot express a distinct responsibility — and it is a rider, not an implementation choice.

### Anti-calcification guardrails (binding on this implementation and future ones)

1. Templates name what a ceremony contains, never steps. A template that grows steps has failed.
2. No schema-driven behavioral obligations: the log describes what happened; it never prescribes what must happen ("every phase must emit event X" is the failure mode).
3. Analytics over logs are descriptive only, feeding the patron's judgment. They never auto-generate rules, scores, or instructions that flow back to the agent. (Goodhart guard: "punishing every wrong turn teaches the company to conceal them.")
4. Mid-task fixes go in that task's charter; lessons go in the journal as dated accounts; only role responsibilities go in the canon. Additions to the canon must be fought for; clarifications and removals are cheap.
5. The metaphor is the interface for ceremonies, not a costume for work products. The skill must say this explicitly.

---

## Basecamps

Each basecamp ends with a dispatch to the patron and verification before moving on. Order matters only where noted; exercise judgment on everything unnamed.

**B1 — Structure and canon.** Restructure the repo per the layout above, moving the two narratives into `code/` byte-for-byte unchanged. Write README (layer model, adoption, amendment discipline) and extend AGENTS.md (layout + amendment discipline; preserve the existing contributor rules verbatim). Verify: canon diffs empty against the approved revisions.

**B2 — Templates.** Charter, dispatch, journal-entry. Fields drawn from what the narratives already name (the charter's sections from "Charter the journey, not every footstep"; the dispatch's from "Read the dispatches"; the journal's from "Ink the journal"). Each a page or less. Verify against guardrail 1.

**B3 — Journey-state spec.** `spec/journey-state.md` (prose spec: envelope, taxonomy with the canonical sentence each type traces to, authority split, self-description rule, append-only rule, escape hatch). `spec/journey.schema.json` (JSON Schema for one event line). At least one full example log in `spec/examples/` telling a complete small expedition including a failed crossing, a rider/word exchange, and a `return` or `arrival`. `tools/validate` (small, dependency-light script) that checks a jsonl file against the schema. Verify: example logs validate; an intentionally malformed line fails.

**B4 — Skill adapter.** Self-contained `adapters/claude/` skill: establishes roles, checks for an existing `expeditions/` charter and resumes, otherwise drafts one; appends log-primary events as work proceeds; writes markdown dispatches/charters and indexes them with reference events; includes the Voice section (guardrail 5) and a provenance note pointing contributors to the repo. `tools/build-skill` zips it into `expedition.skill`. Verify: skill folder contains no relative references outside itself; zip structure is `expedition/SKILL.md` + vendored folders.

**B5 — Map rendering.** A self-contained HTML template (inline CSS/JS, no external fetches) that ingests one or more `journey.jsonl` files and renders the journey: planned route faint, actual path over it, basecamps as nodes, failed crossings as dead-end spurs, riders as branches out to the patron and back, terminal state marked as arrival or return. Also a short `spec/analysis.md` noting the descriptive questions the corpus can answer (rider frequency as charter calibration, first-approach survival, crossings failed, scout reports later contradicted) — with guardrail 3 stated in the same file.

**B6 — Dogfood and close.** Run this implementation as an expedition using its own artifacts: maintain `expeditions/self-build/journey.jsonl` from B1 onward (retroactively for B1 if needed), validate it with the B3 tool, render it with the B5 map. Record a journal entry: what fought back, what the templates failed to express, open questions. This is the arrival check.

## Riders — questions that must come home before acting

- **Any change to canon wording**, including the pending scout clarification (planning settled the substance — scouts travel under the frontiersman's commission and consume its provisions, accountability stays with the frontiersman — but the sentence itself is the patron's to approve; propose wording, do not commit it).
- Adding, removing, or renaming any event type, actor, or canonical term.
- Anything that would make a template or the skill prescribe sequence or steps.
- Publishing/distribution decisions (git hosting, marketplace listing, naming the package publicly).
- Spending materially beyond scope: new dependencies, services, or tooling not implied above.

## Provisions and non-goals

Plain markdown, jsonl, and dependency-light scripts only; no services, no databases, no framework runtime. Non-goals for this expedition: multi-agent orchestration features, automated metrics dashboards, feedback loops from analytics into agent instructions (guardrail 3 makes the last permanent, not just out of scope).
