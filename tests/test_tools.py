#!/usr/bin/env python3
"""Behavior tests for the Accord record tools."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = REPO_ROOT / "plugins" / "accord"
VALIDATE = PLUGIN_ROOT / "tools" / "validate"
RENDER = PLUGIN_ROOT / "tools" / "render"
EXAMPLE = PLUGIN_ROOT / "spec" / "examples" / "rate-limiting.jsonl"


class ToolTests(unittest.TestCase):
    def run_tool(self, tool: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(tool), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_example_validates_as_the_shared_record_contract(self):
        result = self.run_tool(VALIDATE, str(EXAMPLE))

        self.assertEqual(result.returncode, 0)
        self.assertIn("16 lines valid", result.stdout)
        self.assertEqual(result.stderr, "")

    def test_validator_rejects_type_specific_fields_on_other_events(self):
        invalid = {
            "ts": "2026-07-23T12:00:00Z",
            "task": "test",
            "schema": "1",
            "type": "start",
            "actor": "human",
            "summary": "Accepted.",
            "outcome": "succeeded",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            path.write_text(json.dumps(invalid) + "\n")
            result = self.run_tool(VALIDATE, str(path))

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "field 'outcome' is not allowed on type 'start'",
            result.stdout,
        )

    def test_validator_requires_the_payload_that_gives_a_question_meaning(self):
        invalid = {
            "ts": "2026-07-23T12:00:00Z",
            "task": "test",
            "schema": "1",
            "type": "question",
            "actor": "agent",
            "summary": "A choice returned to the human.",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            path.write_text(json.dumps(invalid) + "\n")
            result = self.run_tool(VALIDATE, str(path))

        self.assertEqual(result.returncode, 1)
        self.assertIn(
            "type 'question' requires field 'subject'",
            result.stdout,
        )

    def test_renderer_creates_a_self_contained_literal_timeline(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.html"
            result = self.run_tool(
                RENDER,
                str(EXAMPLE),
                "-o",
                str(output),
            )
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn("rendered 16 events", result.stdout)
        self.assertIn("<title>Accord record</title>", html)
        self.assertIn("rate-limiting", html)
        self.assertIn("A factual view of what changed", html)
        self.assertNotIn("Journey map", html)
        self.assertNotIn("https://", html)

    def test_renderer_rejects_incomplete_events_before_rendering(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            path.write_text("{}\nnot-json\n")
            result = self.run_tool(RENDER, str(path))

        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{path}:1: missing required fields", result.stderr)

    def test_renderer_reports_the_exact_invalid_json_line(self):
        valid = {
            "ts": "2026-07-23T12:00:00Z",
            "task": "test",
            "schema": "1",
            "type": "start",
            "actor": "human",
            "summary": "Accepted.",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            path.write_text(json.dumps(valid) + "\nnot-json\n")
            result = self.run_tool(RENDER, str(path))

        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{path}:2: invalid JSON", result.stderr)


if __name__ == "__main__":
    unittest.main()
