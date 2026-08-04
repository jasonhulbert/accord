#!/usr/bin/env python3
"""Focused contracts for Accord's division of authority and record meaning."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class FrameworkContractTests(unittest.TestCase):
    """Protect the reasons Accord exists without freezing incidental prose."""

    def prose(self, relative: str) -> str:
        return " ".join((REPO_ROOT / relative).read_text().split())

    def test_agreement_requires_dialogue_acceptance_and_bounded_authority(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn(
            "The human holds the purpose. Within the agreement, the agent holds the work",
            human,
        )
        self.assertIn("No agreement is active until the human has seen it", agent)
        self.assertIn("subsequent human message explicitly accepts", skill)
        self.assertIn("changes implementation choices within its authority", agent)
        self.assertIn("routine implementation details", agent)

    def test_review_returns_judgment_without_returning_implementation(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("the human has kept judgment over what comes next", agent)
        self.assertIn("then waits", agent)
        self.assertIn("The agent remains responsible for how that judgment", human)
        self.assertIn("stop before making or foreclosing the human's choice", skill)
        self.assertIn("Responsibility for implementation remains yours", skill)
        self.assertIn(
            "An internal pause for testing or reflection is not a review", skill
        )

    def test_completion_is_human_judgment_and_closure_ends_authority(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        human = self.prose("plugins/accord/creed/human.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")
        record = self.prose("plugins/accord/spec/record.md")

        self.assertIn("Judging completion belongs to the human", agent)
        self.assertIn(
            "only the human decides whether the work should be recorded as complete",
            human,
        )
        self.assertIn(
            "Evidence, confidence, silence, and earlier authorization do not", skill
        )
        self.assertIn(
            "After the human's `direction`, append the `completion` event", skill
        )
        self.assertIn("`completion` and `end` are terminal", record)
        self.assertIn("No later request reopens the agreement", record)

    def test_check_ins_and_direction_keep_the_human_question_visible(self):
        specification = self.prose("plugins/accord/spec/check-in.md")
        skill = self.prose("plugins/accord/skills/check-in/SKILL.md")

        self.assertIn("ordinary conversation, not a check-in", specification)
        self.assertIn(
            "A clear answer to an open `question` is `direction`", specification
        )
        self.assertIn(
            "A direct follow-up while judgment remains open is a check-in",
            specification,
        )
        self.assertIn(
            "does not authorize the work that depends on that judgment", specification
        )
        self.assertIn("before treating the message as a check-in", skill)
        self.assertIn("A closed agreement counts as none", skill)

    def test_delegation_moves_work_without_moving_accountability(self):
        agent = self.prose("plugins/accord/creed/agent.md")
        supporting = self.prose("plugins/accord/creed/supporting-agent.md")
        skill = self.prose("plugins/accord/skills/accord/SKILL.md")

        self.assertIn("Delegation can move part of the work", agent)
        self.assertIn("It cannot move responsibility for the whole", agent)
        self.assertIn("does not inherit authority the agreement kept human", agent)
        self.assertIn(
            "Responsibility for the whole remains with the agent that delegated the part",
            supporting,
        )
        self.assertIn("do not delegate reserved decisions", skill)

    def test_record_is_append_only_evidence_not_policy_or_scoring(self):
        record = self.prose("plugins/accord/spec/record.md")
        agents = self.prose("AGENTS.md")
        learning = self.prose("plugins/accord/templates/learning-note.md")

        self.assertIn("The record describes what happened", record)
        self.assertIn("does not score the agent", record)
        self.assertIn("Valid history is never rewritten", record)
        self.assertIn("Words in a record show what was said and done", record)
        self.assertIn("analytics over records remain descriptive", agents.lower())
        self.assertIn("evidence for later judgment, not rules", learning)

    def test_templates_hold_substance_without_choreographing_conversation(self):
        agreement = self.prose("plugins/accord/templates/agreement.md")
        report = self.prose("plugins/accord/templates/report.md")
        learning = self.prose("plugins/accord/templates/learning-note.md")

        self.assertIn(
            "without trying to predict every implementation choice", agreement
        )
        self.assertIn("Review points are not implementation steps", agreement)
        self.assertIn("does not stand in for the work itself", report)
        self.assertIn("What did not work", report)
        self.assertIn("What remains uncertain", learning)
        self.assertIn("counsel rather than mandate", learning)


if __name__ == "__main__":
    unittest.main()
