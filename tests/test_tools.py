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
        self.assertNotIn("https://", html)

    def test_renderer_places_task_documents_after_the_events_that_reference_them(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "task"
            reports = task / "reports"
            reports.mkdir(parents=True)
            record = task / "record.jsonl"
            agreement = task / "agreement.md"
            report = reports / "2026-07-26.md"
            learning = task / "learning-2026-07-26.md"
            agreement.write_text("# Agreement: task\n\nThe accepted purpose.\n")
            report.write_text("# Report: task\n\nEvidence from the work.\n")
            learning.write_text("# Learning note: task\n\nContext worth keeping.\n")
            events = [
                {
                    **{
                        "ts": "2026-07-26T12:00:00Z",
                        "task": "task",
                        "schema": "1",
                        "actor": "human",
                    },
                    "type": "start",
                    "summary": "The agreement was accepted.",
                    "refs": ["agreement.md"],
                },
                {
                    **{
                        "ts": "2026-07-26T13:00:00Z",
                        "task": "task",
                        "schema": "1",
                        "actor": "agent",
                    },
                    "type": "review",
                    "summary": "The report informed a reserved judgment.",
                    "refs": ["reports/2026-07-26.md"],
                },
                {
                    **{
                        "ts": "2026-07-26T13:05:00Z",
                        "task": "task",
                        "schema": "1",
                        "actor": "agent",
                    },
                    "type": "report",
                    "summary": "The work was reported.",
                    "refs": [
                        "reports/2026-07-26.md",
                        "learning-2026-07-26.md",
                    ],
                },
            ]
            record.write_text("".join(json.dumps(item) + "\n" for item in events))
            output = Path(directory) / "record.html"

            result = self.run_tool(RENDER, str(record), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn("<dialog id=\"document-dialog\">", html)
        self.assertIn('"kind":"agreement"', html)
        self.assertIn('"kind":"report"', html)
        self.assertIn('"kind":"learning"', html)
        self.assertIn('"title":"Agreement: task"', html)
        self.assertIn('"title":"Report: task"', html)
        self.assertIn('"title":"Learning note: task"', html)
        self.assertIn('"after":0', html)
        self.assertNotIn('"kind":"report","title":"Report: task","content":"# Report: task\\n\\nEvidence from the work.\\n","after":1', html)
        self.assertEqual(html.count('"after":2'), 2)
        self.assertIn("documentDialog.showModal()", html)
        self.assertIn("renderMarkdown(documentItem.content", html)

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

    def test_renderer_keeps_record_text_that_matches_view_placeholders(self):
        valid = {
            "ts": "2026-07-23T12:00:00Z",
            "task": "test",
            "schema": "1",
            "type": "note",
            "actor": "agent",
            "summary": "__TITLE__ __HEADING__ __INTRO__ __NAV__ __LIVE_SCRIPT__",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            output = Path(directory) / "record.html"
            path.write_text(json.dumps(valid) + "\n")
            result = self.run_tool(RENDER, str(path), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        for placeholder in (
            "__TITLE__",
            "__HEADING__",
            "__INTRO__",
            "__NAV__",
            "__LIVE_SCRIPT__",
        ):
            self.assertIn(placeholder, html)

    def test_renderer_preserves_the_black_surface_and_state_marks(self):
        valid = {
            "ts": "2026-07-23T12:00:00Z",
            "task": "test",
            "schema": "1",
            "type": "question",
            "actor": "human",
            "summary": "A judgment returned to the human.",
            "subject": "view-access-pattern",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            output = Path(directory) / "record.html"
            path.write_text(json.dumps(valid) + "\n")
            result = self.run_tool(RENDER, str(path), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn("--paper: #000", html)
        self.assertIn("--running:", html)
        self.assertIn("--warning:", html)
        self.assertIn("--danger:", html)
        self.assertIn("--human:", html)
        self.assertIn("--agent:", html)
        self.assertIn("--supporting-agent:", html)
        self.assertIn(".event::after", html)
        self.assertIn("left: 4px", html)
        self.assertIn("margin-top: 20px", html)
        self.assertIn('<span class="legend-human">Human</span>', html)
        self.assertIn('<span class="legend-agent">Agent</span>', html)
        self.assertIn('<span class="legend-supporting-agent">Supporting agent</span>', html)
        self.assertNotIn("border-radius:", html)


if __name__ == "__main__":
    unittest.main()
