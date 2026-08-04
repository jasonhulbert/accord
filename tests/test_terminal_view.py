#!/usr/bin/env python3
"""Focused contracts for global discovery and the read-only terminal view."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from accord.catalog import global_catalog, project_display_name, read_work
from accord.cli import build_parser, version_result
from accord.tui import AccordApp


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "existing-work"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "accord"


class TerminalViewTests(unittest.TestCase):
    """Protect why the global viewer exists without freezing its styling."""

    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.home = Path(self.directory.name) / "home"
        self.home.mkdir()
        self.home_environment = patch.dict(os.environ, {"HOME": str(self.home)})
        self.home_environment.start()

    def tearDown(self) -> None:
        self.home_environment.stop()
        self.directory.cleanup()

    def copy_work(
        self, storage: str, project: str, task: str = "existing-work"
    ) -> Path:
        root = (
            self.home
            / ".accord"
            / ("projects" if storage == "active" else "archive/projects")
        )
        destination = root / project / task
        shutil.copytree(FIXTURE, destination)
        if task != "existing-work":
            record = [
                json.loads(line)
                for line in (destination / "record.jsonl").read_text().splitlines()
                if line
            ]
            for event in record:
                event["task"] = task
            (destination / "record.jsonl").write_text(
                "".join(
                    json.dumps(event, ensure_ascii=False) + "\n" for event in record
                )
            )
        return destination

    def test_project_labels_keep_the_stored_identity_visible(self):
        self.assertEqual(
            project_display_name("accord-ab9dec8c5b7b"),
            "accord [accord-ab9dec8c5b7b]",
        )
        self.assertEqual(
            project_display_name("unusual-project-key"), "unusual-project-key"
        )

    def test_global_catalog_groups_both_storage_roots_without_using_cwd(self):
        active = self.copy_work("active", "accord-ab9dec8c5b7b")
        archived = self.copy_work(
            "archived", "accord-ab9dec8c5b7b", task="archived-work"
        )
        archived_only = self.copy_work("archived", "retired-123456789abc")

        with patch("pathlib.Path.cwd", return_value=Path("/outside/project")):
            catalog = global_catalog()

        self.assertEqual(
            [project.key for project in catalog.projects],
            ["accord-ab9dec8c5b7b", "retired-123456789abc"],
        )
        project = catalog.projects[0]
        self.assertEqual([item.path for item in project.active], [active])
        self.assertEqual([item.path for item in project.archived], [archived])
        self.assertEqual(
            [item.path for item in catalog.projects[1].archived], [archived_only]
        )

    def test_one_damaged_entry_remains_visible_with_valid_neighboring_work(self):
        valid = self.copy_work("active", "good-project-123456789abc")
        project_root = valid.parent
        damaged = project_root / "damaged-work"
        damaged.mkdir()
        (damaged / "record.jsonl").write_text("not-json\n")
        (damaged / "agreement.md").write_text("# Agreement for damaged work\n")
        (project_root / "unsafe-entry").write_text("not a task directory")

        catalog = global_catalog()
        project = catalog.projects[0]
        summaries = {item.task: item for item in project.active}

        self.assertEqual(summaries["existing-work"].state, "open")
        self.assertIn("invalid JSON", summaries["damaged-work"].problem or "")
        self.assertEqual(summaries["unsafe-entry"].state, "damaged")
        self.assertIn("not a directory", summaries["unsafe-entry"].problem or "")
        damaged_view = read_work(summaries["damaged-work"])
        self.assertIn(
            "Agreement for damaged work", damaged_view.agreement.content or ""
        )
        self.assertIn("invalid JSON", damaged_view.record_problem or "")

    def test_unsafe_project_entry_is_an_error_without_following_the_link(self):
        self.copy_work("active", "good-project-123456789abc")
        outside = self.home / "outside"
        outside.mkdir()
        active_root = self.home / ".accord" / "projects"
        (active_root / "unsafe-project-123456789abc").symlink_to(
            outside, target_is_directory=True
        )

        catalog = global_catalog()
        unsafe = next(
            project
            for project in catalog.projects
            if project.key == "unsafe-project-123456789abc"
        )

        self.assertEqual(len(unsafe.active), 0)
        self.assertEqual(len(unsafe.problems), 1)
        self.assertIn("symlink", unsafe.problems[0].message)

    def test_reading_existing_work_preserves_order_documents_and_bytes(self):
        task_dir = self.copy_work("active", "read-project-123456789abc")
        before = {
            path.relative_to(task_dir): path.read_bytes()
            for path in task_dir.rglob("*")
            if path.is_file()
        }
        summary = global_catalog().projects[0].active[0]

        view = read_work(summary)

        after = {
            path.relative_to(task_dir): path.read_bytes()
            for path in task_dir.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)
        self.assertEqual(
            [event["type"] for event in view.events],
            ["start", "investigation", "report", "note"],
        )
        self.assertEqual(
            {(document.category, document.name) for document in view.documents},
            {
                ("reports", "progress.md"),
                ("learning_notes", "learning-context.md"),
                ("diagrams", "current-shape.md"),
            },
        )
        self.assertEqual(
            view.agreement.content, (task_dir / "agreement.md").read_text()
        )

    def test_event_rendering_keeps_actor_outcome_questions_and_references_explicit(
        self,
    ):
        task_dir = self.copy_work("active", "render-project-123456789abc")
        summary = global_catalog().projects[0].active[0]
        view = read_work(summary)
        event = {
            "ts": "2026-08-04T01:00:00Z",
            "task": "existing-work",
            "schema": "1",
            "type": "attempt",
            "actor": "supporting-agent",
            "summary": "The bounded check completed.",
            "outcome": "succeeded",
            "refs": ["reports/progress.md", "../outside.md"],
        }
        question = {
            "type": "question",
            "actor": "human",
            "subject": "Whether the evidence is sufficient.",
            "summary": "A consequential choice was returned to the human.",
        }
        direction = {
            "type": "direction",
            "actor": "human",
            "decision": "Continue within the accepted bounds.",
            "summary": "The human answered the question.",
        }

        rendered = "\n".join(
            AccordApp._event_detail(view, 5, event)
            + AccordApp._event_detail(view, 6, question)
            + AccordApp._event_detail(view, 7, direction)
        )

        self.assertIn('actor: "supporting-agent"', rendered)
        self.assertIn('outcome: "succeeded"', rendered)
        self.assertIn('subject: "Whether the evidence is sufficient."', rendered)
        self.assertIn('decision: "Continue within the accepted bounds."', rendered)
        self.assertIn("reports/progress.md", rendered)
        self.assertIn("ERROR: unsafe reference", rendered)
        self.assertNotIn(str(task_dir.parent.parent), rendered)

    def test_navigation_refresh_and_back_keep_the_view_read_only(self):
        task_dir = self.copy_work("active", "navigate-project-123456789abc")
        self.copy_work("active", "other-project-123456789abc")
        before = {
            path.relative_to(task_dir): path.read_bytes()
            for path in task_dir.rglob("*")
            if path.is_file()
        }
        app = AccordApp()
        app.render((40, 20))
        app.render((120, 40))

        app.keypress((120, 40), "down")
        self.assertEqual(app._selected_payload().key, "other-project-123456789abc")
        app.keypress((120, 40), "r")
        self.assertEqual(app._selected_payload().key, "other-project-123456789abc")
        app.keypress((120, 40), "enter")
        self.assertEqual(app.mode, "work")
        app.keypress((120, 40), "enter")
        self.assertEqual(app.mode, "detail")
        app.keypress((120, 40), "r")
        self.assertEqual(app.mode, "detail")
        app.keypress((120, 40), "esc")
        self.assertEqual(app.mode, "work")

        after = {
            path.relative_to(task_dir): path.read_bytes()
            for path in task_dir.rglob("*")
            if path.is_file()
        }
        self.assertEqual(before, after)

    def test_serve_is_a_public_terminal_command_without_web_options(self):
        parser = build_parser()
        args = parser.parse_args(["serve"])

        self.assertEqual(args.command, "serve")
        self.assertIn("serve", version_result()["commands"])
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit):
            parser.parse_args(["serve", "--port", "8080"])
        skill = (PLUGIN_ROOT / "skills" / "accord" / "SKILL.md").read_text()
        self.assertIn("accord serve", skill)
        self.assertIn("read-only terminal view", skill)
        self.assertNotIn("localhost", skill)


if __name__ == "__main__":
    unittest.main()
