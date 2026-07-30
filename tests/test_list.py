#!/usr/bin/env python3
"""Behavior tests for read-only discovery of active and archived work."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LIST = REPO_ROOT / "plugins" / "accord" / "tools" / "list"
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


def event(task: str) -> dict[str, str]:
    return {
        "ts": "2026-07-30T12:00:00Z",
        "task": task,
        "schema": "1",
        "type": "note",
        "actor": "agent",
        "summary": "Stored work remains discoverable.",
    }


class ListTests(unittest.TestCase):
    def make_project(self, root: Path) -> tuple[Path, Path, Path, Path]:
        project = root / "project"
        home = root / "home"
        project.mkdir()
        home.mkdir()
        (project / ".git").mkdir()
        result = subprocess.run(
            [sys.executable, str(LOCATION), str(project)],
            text=True,
            capture_output=True,
            check=True,
            env=os.environ | {"HOME": str(home)},
        )
        active = Path(result.stdout.strip())
        archived = (
            home / ".accord" / "archive" / "projects" / active.name
        )
        return project, home, active, archived

    def write_work(self, root: Path, task: str) -> None:
        task_dir = root / task
        task_dir.mkdir(parents=True)
        (task_dir / "record.jsonl").write_text(
            json.dumps(event(task)) + "\n"
        )

    def run_list(self, project: Path, home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LIST)],
            cwd=project,
            text=True,
            capture_output=True,
            env=os.environ | {"HOME": str(home)},
        )

    def test_list_distinguishes_storage_without_implying_record_state(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active, archived = self.make_project(Path(directory))
            self.write_work(active, "zeta-active")
            self.write_work(active, "alpha-active")
            self.write_work(archived, "forced-incomplete")

            result = self.run_list(project, home)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "ACTIVE    alpha-active\n"
            "ACTIVE    zeta-active\n"
            "ARCHIVED  forced-incomplete\n",
        )

    def test_empty_list_is_an_explicit_success(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, _, _ = self.make_project(Path(directory))

            result = self.run_list(project, home)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            result.stdout,
            "No Accord work found for this project.\n",
        )

    def test_damaged_work_is_named_and_prevents_a_partial_success(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active, archived = self.make_project(Path(directory))
            self.write_work(active, "sound-work")
            (archived / "damaged-work").mkdir(parents=True)

            result = self.run_list(project, home)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(
            result.stdout,
            "ACTIVE    sound-work\n"
            "ARCHIVED  damaged-work\n",
        )
        self.assertEqual(
            result.stderr,
            "WARNING: archived work 'damaged-work' needs attention: "
            "record.jsonl is missing\n",
        )

    def test_unsafe_archive_root_is_refused_without_reading_through_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, _, archived = self.make_project(root)
            external = root / "external"
            self.write_work(external, "outside-work")
            archived.parent.mkdir(parents=True)
            archived.symlink_to(external, target_is_directory=True)

            result = self.run_list(project, home)

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("archived storage contains a symlink", result.stderr)
        self.assertNotIn("outside-work", result.stderr)


if __name__ == "__main__":
    unittest.main()
