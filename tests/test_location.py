#!/usr/bin/env python3
"""Behavior tests for locating per-user Accord record storage."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


class LocationTests(unittest.TestCase):
    def locate(self, project: Path, home: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(LOCATION), str(project)],
            text=True,
            capture_output=True,
            check=False,
            env=os.environ | {"HOME": str(home)},
        )

    def test_location_uses_a_hidden_home_store_and_the_git_worktree(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            project = root / "project"
            nested = project / "src" / "feature"
            home.mkdir()
            nested.mkdir(parents=True)
            (project / ".git").mkdir()

            result = self.locate(nested, home)

        self.assertEqual(result.returncode, 0, result.stderr)
        location = Path(result.stdout.strip())
        self.assertEqual(location.parent, home / ".accord" / "projects")
        self.assertRegex(location.name, r"^project-[0-9a-f]{12}$")
        self.assertNotIn(str(project), str(location))

    def test_location_keeps_same_named_projects_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            first = root / "one" / "api"
            second = root / "two" / "api"
            home.mkdir()
            first.mkdir(parents=True)
            second.mkdir(parents=True)
            (first / ".git").mkdir()
            (second / ".git").mkdir()

            first_result = self.locate(first, home)
            second_result = self.locate(second, home)

        self.assertEqual(first_result.returncode, 0, first_result.stderr)
        self.assertEqual(second_result.returncode, 0, second_result.stderr)
        self.assertNotEqual(first_result.stdout, second_result.stdout)

    def test_location_fails_loudly_for_a_missing_project_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing"
            result = self.locate(missing, Path(directory) / "home")

        self.assertEqual(result.returncode, 2)
        self.assertIn("project directory does not exist", result.stderr)
