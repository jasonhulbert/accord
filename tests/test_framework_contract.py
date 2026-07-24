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
        self.assertIn("Do not advance beyond the review in the same run.", skill)
        self.assertIn("responsibility for implementation remains yours", skill)

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

    def test_corrective_direction_reopens_the_same_review(self):
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("a follow-up question is a `check-in`", skill)
        self.assertIn("the review remains open", skill)
        self.assertIn(
            "revise the reviewed work without advancing beyond the review", skill
        )
        self.assertIn("then report and ask again", skill)

    def test_check_in_can_request_review_without_making_every_message_a_halt(self):
        check_in_spec = self.read("plugins/accord/spec/check-in.md")
        check_in_skill = self.read("plugins/accord/skills/check-in/SKILL.md")

        self.assertIn("A clear answer to that question is `direction`", check_in_spec)
        self.assertIn("A review request", check_in_spec)
        self.assertIn("creates a review where the work stands", check_in_spec)
        self.assertIn(
            "does not halt work merely because the human spoke first", check_in_spec
        )
        self.assertIn("make the current work inspectable", check_in_skill)

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
            "If the agreement keeps that judgment human, bring it to review",
            skill_prose,
        )

    def test_investigation_informs_agent_judgment_without_inheriting_it(self):
        investigator = self.read("plugins/accord/creed/investigator.md")
        agent = self.read("plugins/accord/creed/agent.md")

        self.assertIn("evidence and inference distinct", investigator)
        self.assertIn("The investigator finds. The agent decides.", investigator)
        self.assertIn("Delegation can move an inquiry", agent)
        self.assertIn("It cannot move accountability", agent)

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
        self.assertEqual(codex_manifest["version"], "0.1.0")
        self.assertEqual(claude_manifest["name"], "accord")
        self.assertEqual(claude_manifest["version"], "0.1.0")
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
            {"human", "agent", "investigator"},
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

        self.assertIn("ACCORD_STYLE_GUIDE.md", agents)
        self.assertIn("literal", agents)


if __name__ == "__main__":
    unittest.main()
