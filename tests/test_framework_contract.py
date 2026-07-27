#!/usr/bin/env python3
"""Contract tests for the responsibilities Accord expresses in prose."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "accord"


class FrameworkContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text()

    def prose(self, relative_path: str) -> str:
        return " ".join(self.read(relative_path).split())

    def test_agreement_is_dialogue_before_explicit_acceptance(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")
        agreement = self.read("plugins/accord/templates/agreement.md")

        self.assertIn("An agreement is not a request rewritten", agent)
        self.assertIn("### Reach agreement. Do not issue one.", human)
        self.assertIn("Present the complete draft and counsel", skill)
        self.assertIn("a subsequent human message explicitly accepts", skill)
        self.assertIn(
            "understanding reached by the\nhuman and agent before the work begins",
            agreement,
        )

    def test_completion_closes_authority_without_erasing_history(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")
        check_in = self.prose("plugins/accord/skills/check-in/SKILL.md")
        record = self.prose("plugins/accord/spec/record.md")
        check_in_spec = self.prose("plugins/accord/spec/check-in.md")
        agreement = self.prose("plugins/accord/templates/agreement.md")
        guide = self.prose("GUIDE.md")

        self.assertIn("Completion closes an agreement", agent)
        self.assertIn("Reach a new agreement for later work", skill)
        self.assertIn("do not reopen or append", skill)
        self.assertIn("A closed agreement counts as none", check_in)
        self.assertIn("A `completion` event is terminal", record)
        self.assertIn("A later message cannot be a check-in", check_in_spec)
        self.assertIn("A completed agreement stays closed", guide)

        self.assertIn("History may inform judgment", agent)
        self.assertIn("History may inform counsel", skill)
        self.assertIn("The agreement stands on its own", agreement)
        self.assertIn(
            "does not point to another work's agreement or reports",
            record,
        )

        creed_boundary = agent.split(
            "### Let completed work remain complete.", 1
        )[1].split("### Leave a record another session can trust.", 1)[0]
        accord_entry = skill.split(
            "Run `tools/location` from the target project's root", 1
        )[1].split(
            "When the human asks to inspect work in progress under Accord", 1
        )[0]
        check_in_entry = check_in.split(
            "For a possible check-in, run `tools/location`", 1
        )[1].split("For an open question", 1)[0]

        self.assertLessEqual(len(creed_boundary.split()), 45)
        self.assertLessEqual(len(accord_entry.split()), 110)
        self.assertLessEqual(len(check_in_entry.split()), 75)

    def test_accord_names_the_framework_not_a_body_of_work(self):
        style = self.prose("ACCORD_STYLE_GUIDE.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")
        check_in = self.prose("plugins/accord/skills/check-in/SKILL.md")
        guide = self.prose("GUIDE.md")
        readme = self.prose("README.md")

        self.assertIn(
            "Use **Accord** for the framework and the creed-driven way of working",
            style,
        )
        self.assertIn(
            "Do not use it as the name of a particular body of work", style
        )
        self.assertIn(
            "**work** for the bounded undertaking carried under one agreement",
            style,
        )
        self.assertIn("asks to resume work under it", skill)
        self.assertIn("inspect work in progress under Accord", skill)
        self.assertIn(
            "Requires active work under an accepted agreement", check_in
        )
        self.assertIn("To inspect active work under Accord", guide)
        self.assertIn("for one body of work before it begins", readme)
        self.assertIn(
            "Accord governs the work. The agreement gives trust a shape", readme
        )
        self.assertIn(
            "The agent keeps the work's record outside the project workspace",
            guide,
        )
        self.assertIn(
            "read it together with the record, reports, learning notes, and "
            "actual work",
            skill,
        )
        self.assertIn("resume the work within the agreement", skill)
        self.assertIn("use Accord to reach an agreement for the work", check_in)

        conceptual_prose = " ".join((skill, check_in, guide, readme))
        for misuse in (
            "resume one",
            "an Accord in progress",
            "Requires an existing Accord",
            "begin an Accord",
            "while an Accord is active",
        ):
            self.assertNotIn(misuse, conceptual_prose)

        framework_prose = " ".join(
            self.prose(path)
            for path in (
                "ACCORD_STYLE_GUIDE.md",
                "GUIDE.md",
                "README.md",
                "AGENTS.md",
                "plugins/accord/creed/agent.md",
                "plugins/accord/creed/human.md",
                "plugins/accord/creed/supporting-agent.md",
                "plugins/accord/skills/accord/SKILL.md",
                "plugins/accord/skills/check-in/SKILL.md",
                "plugins/accord/templates/agreement.md",
                "plugins/accord/templates/report.md",
                "plugins/accord/templates/learning-note.md",
                "plugins/accord/spec/record.md",
                "plugins/accord/spec/check-in.md",
                "plugins/accord/spec/analysis.md",
            )
        )
        self.assertNotRegex(
            framework_prose,
            r"\b(?:an|another|each|one|existing|new|active) Accord\b",
        )
        self.assertNotRegex(
            framework_prose,
            r"\b(?:begin|resume|complete|end|inspect) "
            r"(?:an|the|this|that|existing|new) Accord\b",
        )

    def test_record_language_is_evidence_not_vocabulary_authority(self):
        record = self.prose("plugins/accord/spec/record.md")

        self.assertIn(
            "Each body of work under Accord has an append-only record", record
        )
        self.assertIn(
            "The agent opens the record after the human accepts the agreement",
            record,
        )
        self.assertIn(
            "The words in a record show what was said and done; they do not "
            "define Accord's vocabulary",
            record,
        )
        self.assertIn(
            "reads it against the agreement, surrounding events, and actual work",
            record,
        )
        self.assertIn(
            "ambiguity affecting purpose, authority, or state cannot be resolved",
            record,
        )
        self.assertIn("the question returns to the human", record)
        self.assertIn(
            "`investigator` remains valid in stored schema version `\"1\"` records",
            record,
        )
        self.assertNotIn("before the supporting-agent role was adopted", record)

    def test_review_returns_reserved_judgment_without_returning_implementation(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("the human has kept judgment over what comes next", agent)
        self.assertIn("then waits", agent)
        self.assertIn("The agent remains responsible for how that judgment", human)
        self.assertIn(
            "stop before making or foreclosing the reserved choice", skill
        )
        self.assertIn("Responsibility for implementation remains yours", skill)

    def test_review_names_the_work_and_question_not_a_phase_to_approve(self):
        style = self.prose("ACCORD_STYLE_GUIDE.md")
        agent = self.prose("plugins/accord/creed/agent.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")
        agreement = self.prose("plugins/accord/templates/agreement.md")

        self.assertIn("Review is what the human does with the work", style)
        self.assertIn("The agent names the work that is ready", agent)
        self.assertIn(
            "Do not name the review as though it were a phase, deliverable", skill
        )
        self.assertIn(
            "is not a substitute for saying what will be ready", agreement
        )

    def test_review_exposes_work_while_human_judgment_has_leverage(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        agreement = self.prose("plugins/accord/templates/agreement.md")
        report = self.prose("plugins/accord/templates/report.md")

        self.assertIn("Too late, and judgment becomes regret", agent)
        self.assertIn("inspects the work itself", human)
        self.assertIn("what may become harder to change", agreement)
        self.assertIn("## Work to inspect", report)
        self.assertIn("does not stand in for the work itself", report)

    def test_corrective_direction_keeps_reserved_judgment_visible(self):
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("a follow-up question is a `check-in`", skill)
        self.assertIn("the reserved judgment remains open", skill)
        self.assertIn(
            "revise the work without acting beyond the unresolved judgment", skill
        )
        self.assertIn("then report and ask again", skill)

    def test_check_in_can_request_review_without_recording_every_message(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        check_in_spec = self.prose("plugins/accord/spec/check-in.md")
        check_in_skill = self.prose("plugins/accord/skills/check-in/SKILL.md")
        record = self.prose("plugins/accord/spec/record.md")

        self.assertIn(
            "A clear answer to an open `question` is `direction`", check_in_spec
        )
        self.assertIn(
            "Acceptance of the initial agreement is `start`, not `check-in`",
            check_in_spec,
        )
        self.assertIn("A request to inspect the work", check_in_spec)
        self.assertIn("reserves judgment where the work stands", check_in_spec)
        self.assertIn("does not halt work by itself", check_in_spec)
        self.assertIn("ordinary conversation, not a check-in", check_in_spec)
        self.assertIn("do not append an event", check_in_spec)
        self.assertIn("accepts an amendment or authorizes", check_in_spec)
        self.assertIn("materially affects the agreement", check_in_spec)
        self.assertIn("directly asks about, provides feedback on", check_in_spec)
        self.assertIn("meets the consequential boundary", record)
        self.assertIn("Changed terms may require counsel and an", agent)
        self.assertIn("answers incidental conversation without adding it", agent)
        self.assertIn("reserves judgment where the work stands", agent)
        self.assertIn("seek the agent's counsel", human)
        self.assertIn("Incidental questions remain ordinary conversation", human)
        self.assertIn("A request for counsel", check_in_spec)
        self.assertIn("before treating the message as a check-in", check_in_skill)

    def test_internal_pause_does_not_become_an_approval_gate(self):
        agent = self.read("plugins/accord/creed/agent.md")
        skill = self.read("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("Not every useful pause is a review point", agent)
        self.assertIn(
            "An internal pause for testing or reflection is not a review", skill
        )

    def test_agent_owns_adaptation_within_literal_authority_bounds(self):
        agent = self.read("plugins/accord/creed/agent.md")
        agreement = self.read("plugins/accord/templates/agreement.md")
        skill = self.read("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("changes implementation choices within its authority", agent)
        self.assertIn("routine implementation details", agent)
        self.assertIn("## Room to act", agreement)
        self.assertIn(
            "Within the agreement, choose and adapt the implementation", skill
        )
        skill_prose = self.prose("plugins/accord/skills/accord/SKILL.md")
        self.assertIn(
            "Do not make or foreclose the consequential choice before direction arrives",
            skill_prose,
        )
        self.assertIn(
            "present the completed work for review and ask the question",
            skill_prose,
        )

    def test_delegation_moves_work_without_fragmenting_accountability(self):
        supporting_agent = self.prose(
            "plugins/accord/creed/supporting-agent.md"
        )
        agent = self.prose("plugins/accord/creed/agent.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn(
            "The supporting agent contributes. The primary agent integrates",
            supporting_agent,
        )
        self.assertIn("It cannot move responsibility for the whole", agent)
        self.assertIn(
            "evidence, implementation, verification, review", supporting_agent
        )
        self.assertIn("Look actively for bounded parts", skill)
        self.assertIn(
            "keep responsibility for the course, integration, and the completed work",
            skill,
        )
        self.assertIn(
            "act and delegate with judgment, meet the human where judgment remains theirs",
            agent,
        )
        self.assertIn(
            "return useful work with its evidence and limits visible",
            supporting_agent,
        )

    def test_direction_remains_the_human_answer_not_a_delegation_synonym(self):
        record = self.prose("plugins/accord/spec/record.md")
        delegation_text = " ".join(
            [
                self.prose("plugins/accord/creed/agent.md"),
                self.prose("plugins/accord/creed/human.md"),
                self.prose("plugins/accord/creed/supporting-agent.md"),
                self.prose("plugins/accord/skills/accord/SKILL.md"),
            ]
        )

        self.assertIn("The human answers an open question", record)
        self.assertNotIn("responsibility for direction", delegation_text)
        self.assertNotIn("leave direction of the whole", delegation_text)
        self.assertIn("responsibility for the course", delegation_text)

    def test_each_creed_closes_by_reinforcing_its_distinct_charge(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        supporting_agent = self.prose(
            "plugins/accord/creed/supporting-agent.md"
        )

        self.assertIn("This is the agent's creed:", agent)
        self.assertIn("meet the human where judgment remains theirs", agent)
        self.assertIn("This is the human's charge:", human)
        self.assertIn("answer the questions only the human can answer", human)
        self.assertIn("This is the supporting agent's charge:", supporting_agent)
        self.assertIn(
            "leave responsibility for the whole with the primary agent",
            supporting_agent,
        )

    def test_plugin_and_marketplaces_share_the_accord_identity(self):
        codex_manifest = json.loads(
            self.read("plugins/accord/.codex-plugin/plugin.json")
        )
        claude_manifest = json.loads(
            self.read("plugins/accord/.claude-plugin/plugin.json")
        )
        codex_marketplace = json.loads(self.read(".agents/plugins/marketplace.json"))
        claude_marketplace = json.loads(self.read(".claude-plugin/marketplace.json"))

        self.assertEqual(codex_manifest["name"], "accord")
        self.assertEqual(codex_manifest["version"], "0.1.1")
        self.assertEqual(claude_manifest["name"], "accord")
        self.assertEqual(claude_manifest["version"], "0.1.1")
        self.assertEqual(codex_marketplace["name"], "accord")
        self.assertEqual(
            codex_marketplace["plugins"][0]["source"]["path"],
            "./plugins/accord",
        )
        self.assertEqual(
            claude_marketplace["plugins"][0]["source"],
            "./plugins/accord",
        )

    def test_record_schema_keeps_actor_and_event_vocabulary_small(self):
        schema = json.loads(self.read("plugins/accord/spec/record.schema.json"))
        expected_types = {
            "start",
            "investigation",
            "attempt",
            "review",
            "report",
            "question",
            "direction",
            "check-in",
            "approach-change",
            "completion",
            "end",
            "note",
        }
        self.assertEqual(set(schema["properties"]["type"]["enum"]), expected_types)
        self.assertEqual(
            set(schema["properties"]["actor"]["enum"]),
            {"human", "agent", "supporting-agent", "investigator"},
        )

        conditional_requirements = {
            clause["if"]["properties"]["type"]["const"]: set(clause["then"]["required"])
            for clause in schema["allOf"]
        }
        self.assertEqual(
            conditional_requirements,
            {
                "attempt": {"outcome"},
                "question": {"subject"},
                "direction": {"decision"},
            },
        )

    def test_stored_actor_name_does_not_invalidate_append_only_history(self):
        schema = json.loads(self.read("plugins/accord/spec/record.schema.json"))
        record = self.prose("plugins/accord/spec/record.md")

        self.assertIn("supporting-agent", schema["properties"]["actor"]["enum"])
        self.assertIn("investigator", schema["properties"]["actor"]["enum"])
        self.assertIn(
            "`investigator` remains valid in stored schema version `\"1\"` records",
            record,
        )
        self.assertIn("valid history is not rewritten", record)

    def test_templates_hold_substance_without_choreographing_conversation(self):
        for name in ("agreement.md", "report.md", "learning-note.md"):
            template = self.read(f"plugins/accord/templates/{name}")
            self.assertNotRegex(template, r"(?m)^\d+\.\s")
            self.assertNotIn("Step 1", template)

        agreement = self.read("plugins/accord/templates/agreement.md")
        report = self.read("plugins/accord/templates/report.md")
        learning = self.read("plugins/accord/templates/learning-note.md")
        self.assertIn("## What matters", agreement)
        self.assertIn("## Where we meet", agreement)
        self.assertIn("## Questions kept by the human", agreement)
        self.assertIn("# Agreement: {work}", agreement)
        self.assertIn("# Report: {work} — {date}", report)
        self.assertIn("# Learning note: {work} — {date}", learning)

    def test_record_analysis_cannot_become_agent_scoring(self):
        analysis = self.read("plugins/accord/spec/analysis.md")

        self.assertIn("descriptive questions", analysis)
        self.assertIn("must not generate instructions, compliance scores", analysis)

    def test_contributor_guidance_preserves_voice(self):
        agents = self.read("AGENTS.md")
        skill = self.read("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("ACCORD_STYLE_GUIDE.md", agents)
        self.assertIn("literal", agents)
        self.assertIn("Improve Accord at its source", skill)


if __name__ == "__main__":
    unittest.main()
