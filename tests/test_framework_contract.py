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

    def test_check_in_can_request_review_without_making_every_message_a_halt(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        check_in_spec = self.read("plugins/accord/spec/check-in.md")
        check_in_skill = self.read("plugins/accord/skills/check-in/SKILL.md")

        self.assertIn("A clear answer to that question is `direction`", check_in_spec)
        self.assertIn("A request to inspect the work", check_in_spec)
        self.assertIn("reserves judgment where the work stands", check_in_spec)
        self.assertIn(
            "does not halt work merely because the human spoke first", check_in_spec
        )
        self.assertIn("Changed terms may require counsel and an", agent)
        self.assertIn("reserves judgment where the work stands", agent)
        self.assertIn("seek the agent's counsel", human)
        self.assertIn("A request for counsel", check_in_spec)
        self.assertIn("accounts, counsel, reviews", check_in_skill)
        self.assertIn("Follow `spec/check-in.md`", check_in_skill)

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

    def test_replaced_actor_name_does_not_invalidate_append_only_history(self):
        schema = json.loads(self.read("plugins/accord/spec/record.schema.json"))
        record = self.prose("plugins/accord/spec/record.md")

        self.assertIn("supporting-agent", schema["properties"]["actor"]["enum"])
        self.assertIn("investigator", schema["properties"]["actor"]["enum"])
        self.assertIn(
            "records written before the supporting-agent role was adopted remain valid",
            record,
        )
        self.assertIn("append-only history is not rewritten", record)

    def test_templates_hold_substance_without_choreographing_conversation(self):
        for name in ("agreement.md", "report.md", "learning-note.md"):
            template = self.read(f"plugins/accord/templates/{name}")
            self.assertNotRegex(template, r"(?m)^\d+\.\s")
            self.assertNotIn("Step 1", template)

        agreement = self.read("plugins/accord/templates/agreement.md")
        self.assertIn("## What matters", agreement)
        self.assertIn("## Where we meet", agreement)
        self.assertIn("## Questions kept by the human", agreement)

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
