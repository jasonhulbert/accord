#!/usr/bin/env python3
"""Contract tests for role boundaries expressed by the framework text."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class FrameworkContractTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (REPO_ROOT / relative_path).read_text()

    def test_agreed_basecamp_returns_authority_to_the_patron(self):
        frontiersman = self.read("plugin/creed/frontiersman.md")
        patron = self.read("plugin/creed/patron.md")
        charter = self.read("plugin/templates/charter.md")
        dispatch = self.read("plugin/templates/dispatch.md")
        skill = self.read("plugin/skills/expedition/SKILL.md")

        self.assertIn("Some basecamps are named in the charter", frontiersman)
        self.assertIn("The company waits for the patron's word before traveling again", frontiersman)
        self.assertIn("The company waits there because the patron reserved judgment", patron)
        self.assertIn("## Basecamps", charter)
        self.assertIn("without presuming the answer", dispatch)
        self.assertIn("## Basecamp gate", skill)
        self.assertIn("Do not perform work beyond the basecamp in the same run.", skill)

    def test_basecamp_exposes_reviewable_work_before_choices_harden(self):
        frontiersman = self.read("plugin/creed/frontiersman.md")
        patron = self.read("plugin/creed/patron.md")
        charter = self.read("plugin/templates/charter.md")
        dispatch = self.read("plugin/templates/dispatch.md")
        skill = self.read("plugin/skills/expedition/SKILL.md")

        self.assertIn("while correction still costs less than regret", frontiersman)
        self.assertIn("shape, quality, usefulness, or character", patron)
        self.assertIn("the consequential choices that should remain open", charter)
        self.assertIn("## Work for review", dispatch)
        self.assertIn("it does not stand in for it", dispatch)
        self.assertIn("normally propose at least one basecamp", skill)

    def test_corrective_word_puts_company_in_motion_without_opening_road_beyond(self):
        frontiersman = self.read("plugin/creed/frontiersman.md")
        patron = self.read("plugin/creed/patron.md")
        skill = self.read("plugin/skills/expedition/SKILL.md")

        self.assertIn("A question keeps the company at camp", frontiersman)
        self.assertIn("a direction puts it back in motion", patron)
        self.assertIn("Word ends the wait and puts the company back in motion", skill)
        self.assertIn("another crossing over the reviewed ground", skill)
        self.assertIn("the road beyond remains closed", skill)
        self.assertNotIn("hold it at camp for correction", skill)
        self.assertIn("the outstanding rider and the halt remain", skill)

    def test_missive_can_request_review_without_making_every_message_a_halt(self):
        missive_spec = self.read("plugin/spec/missive.md")
        missive_skill = self.read("plugin/skills/expedition-missive/SKILL.md")

        self.assertIn("A clear direction answering one is `word`, not a missive", missive_spec)
        self.assertIn("making a basecamp where the company stands", missive_spec)
        self.assertIn("adding the requested judgment to its riders", missive_spec)
        self.assertIn("The `missive` event records this amendment", missive_spec)
        self.assertIn("A request for review is a halt", missive_spec)
        self.assertIn("Unless the missive requests review", missive_skill)

    def test_ordinary_camp_does_not_become_an_approval_gate(self):
        skill = self.read("plugin/skills/expedition/SKILL.md")

        self.assertIn(
            "A basecamp not named in the charter does not require word",
            skill,
        )


if __name__ == "__main__":
    unittest.main()
