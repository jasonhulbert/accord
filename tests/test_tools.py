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
FONT_ROOT = PLUGIN_ROOT / "assets" / "fonts"


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
        self.assertIn("21 lines valid", result.stdout)
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

    def test_renderer_creates_an_offline_literal_timeline_and_local_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.html"
            result = self.run_tool(
                RENDER,
                str(EXAMPLE),
                "-o",
                str(output),
            )
            html = output.read_text()
            assets = Path(directory) / "record.assets"
            asset_exists = (assets / "mermaid.js").is_file()
            output_size = output.stat().st_size

        self.assertEqual(result.returncode, 0)
        self.assertIn("rendered 21 events", result.stdout)
        self.assertIn("<title>Accord record</title>", html)
        self.assertIn("rate-limiting", html)
        self.assertIn("A factual view of what changed", html)
        self.assertIn("default-src 'none'", html)
        self.assertIn(
            'import mermaid from "record.assets/mermaid/mermaid.js"',
            html,
        )
        self.assertTrue(asset_exists)
        self.assertLess(output_size, 500_000)
        self.assertNotRegex(html, r'<(?:script|link)[^>]+(?:src|href)="https://')

    def test_renderer_carries_the_chosen_typography_without_a_network_or_system_font(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.html"
            result = self.run_tool(RENDER, str(EXAMPLE), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertEqual(html.count("@font-face"), 4)
        self.assertEqual(html.count("data:font/woff2;base64,"), 4)
        self.assertIn('font-family: "IBM Plex Sans"', html)
        self.assertIn('font-family: "IBM Plex Mono"', html)
        self.assertIn('--font-sans: "IBM Plex Sans", sans-serif', html)
        self.assertIn('--font-mono: "IBM Plex Mono", monospace', html)
        self.assertIn("font: 15px/1.55 var(--font-sans)", html)
        self.assertIn("font: 13px/1.5 var(--font-mono)", html)
        self.assertNotIn("Avenir", html)
        self.assertNotIn("ui-monospace", html)
        self.assertNotRegex(html, r'<(?:script|link)[^>]+(?:src|href)="https://')

    def test_shipped_font_assets_preserve_the_license_that_allows_distribution(self):
        license_text = (FONT_ROOT / "LICENSE.txt").read_text()
        expected_fonts = {
            "IBMPlexSans-Regular.woff2",
            "IBMPlexSans-SemiBold.woff2",
            "IBMPlexSans-Bold.woff2",
            "IBMPlexMono-Regular.woff2",
        }

        self.assertTrue(expected_fonts.issubset(path.name for path in FONT_ROOT.iterdir()))
        self.assertIn("SIL OPEN FONT LICENSE Version 1.1", license_text)
        self.assertIn('Reserved Font Name "Plex"', license_text)

    def test_generated_web_distribution_is_split_pinned_and_licensed(self):
        web_root = PLUGIN_ROOT / "assets" / "web"
        javascript = list(web_root.rglob("*.js"))

        self.assertGreater(len(javascript), 2)
        self.assertTrue((web_root / "mermaid" / "mermaid.js").is_file())
        self.assertLess(max(path.stat().st_size for path in javascript), 600_000)
        self.assertLess(
            sum(path.stat().st_size for path in web_root.rglob("*") if path.is_file()),
            2_000_000,
        )
        self.assertIn("The MIT License", (web_root / "LICENSE.txt").read_text())
        self.assertIn("Mermaid 11.16.0", (web_root / "README.md").read_text())

    def test_generated_web_distribution_matches_its_sources(self):
        result = subprocess.run(
            ["npm", "run", "check:web"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

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

    def test_renderer_anchors_only_referenced_visual_explanations(self):
        with tempfile.TemporaryDirectory() as directory:
            task = Path(directory) / "task"
            diagrams = task / "diagrams"
            diagrams.mkdir(parents=True)
            record = task / "record.jsonl"
            explanation = diagrams / "entitlements.md"
            unreferenced = diagrams / "draft.md"
            explanation.write_text(
                "# Entitlement enforcement\n\n"
                "Implemented behavior across the affected features.\n\n"
                "```mermaid\n"
                "flowchart LR\n"
                "  Request --> Entitlement\n"
                "  Entitlement --> Feature\n"
                "```\n"
            )
            unreferenced.write_text("# Draft\n\n```mermaid\nflowchart LR\nA --> B\n```\n")
            item = {
                "ts": "2026-07-28T12:00:00Z",
                "task": "task",
                "schema": "1",
                "type": "investigation",
                "actor": "agent",
                "summary": "Mapped implemented entitlement enforcement for inspection.",
                "refs": ["diagrams/entitlements.md"],
            }
            record.write_text(json.dumps(item) + "\n")
            output = Path(directory) / "record.html"

            result = self.run_tool(RENDER, str(record), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn('"kind":"visual-explanation"', html)
        self.assertIn('"title":"Entitlement enforcement"', html)
        self.assertIn('"after":0', html)
        self.assertIn("flowchart LR", html)
        self.assertNotIn('"title":"Draft"', html)
        self.assertIn('securityLevel: "strict"', html)
        self.assertIn("themeVariables: {", html)
        self.assertIn('fontFamily: \'"IBM Plex Sans", sans-serif\'', html)
        self.assertIn("Mermaid source", html)
        self.assertIn("Accord could not render this diagram.", html)

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
            "summary": "__TITLE__ __HEADING__ __INTRO__ __NAV__ __FONT_CSS__ __LIVE_SCRIPT__",
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
            "__FONT_CSS__",
            "__LIVE_SCRIPT__",
        ):
            self.assertIn(placeholder, html)

    def test_renderer_preserves_the_black_surface_and_precise_timeline_geometry(self):
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
        self.assertIn("--danger:", html)
        self.assertIn("--human:", html)
        self.assertIn("--agent:", html)
        self.assertIn("--supporting-agent:", html)
        self.assertIn(".event::after", html)
        self.assertIn("left: 4px", html)
        self.assertIn("--event-pad-top: 20px", html)
        self.assertIn("margin-top: calc(var(--event-pad-top) + 3px)", html)
        self.assertIn("padding: var(--event-pad-top) 0 24px", html)
        self.assertNotIn(".card { padding: 18px", html)
        self.assertIn('<span class="legend-human">Human</span>', html)
        self.assertIn('<span class="legend-agent">Agent</span>', html)
        self.assertIn('<span class="legend-supporting-agent">Supporting agent</span>', html)
        page_css = html.split("</style>", 1)[0]
        self.assertNotIn("border-radius:", page_css)

    def test_renderer_uses_actor_as_the_only_meaning_of_event_color(self):
        events = [
            {
                "ts": "2026-07-27T12:00:00Z",
                "task": "test",
                "schema": "1",
                "type": "attempt",
                "actor": "human",
                "summary": "A failed attempt attributed to the human.",
                "outcome": "failed",
            },
            {
                "ts": "2026-07-27T12:01:00Z",
                "task": "test",
                "schema": "1",
                "type": "completion",
                "actor": "agent",
                "summary": "A completion event attributed to the agent.",
            },
            {
                "ts": "2026-07-27T12:02:00Z",
                "task": "test",
                "schema": "1",
                "type": "question",
                "actor": "supporting-agent",
                "summary": "A question attributed to the supporting agent.",
                "subject": "color-source",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.jsonl"
            output = Path(directory) / "record.html"
            path.write_text("".join(json.dumps(item) + "\n" for item in events))
            result = self.run_tool(RENDER, str(path), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            '.event[data-actor="human"] .dot { background: var(--human); }',
            html,
        )
        self.assertIn(
            '.event[data-actor="agent"] .dot { background: var(--agent); }',
            html,
        )
        self.assertIn('.event[data-actor="supporting-agent"] .dot {', html)
        self.assertNotIn('.event[data-type="completion"] .dot', html)
        self.assertNotIn('.event[data-type="question"] .dot', html)
        self.assertNotIn('.event[data-outcome="succeeded"] .dot', html)
        self.assertNotIn('.event[data-outcome="failed"] .dot', html)
        self.assertNotIn("--running:", html)
        self.assertNotIn("--success:", html)
        self.assertNotIn("--warning:", html)

    def test_renderer_keeps_documents_neutral_and_reserves_danger_for_view_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.html"
            result = self.run_tool(RENDER, str(EXAMPLE), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn(".event.document .dot {", html)
        self.assertIn("background: var(--paper)", html)
        self.assertIn("border: 2px solid var(--ink)", html)
        self.assertIn('.event.document[data-error="true"] .dot {', html)
        self.assertIn("border-color: var(--danger)", html)

    def test_renderer_assigns_type_by_meaning_and_uses_an_explicit_heading_rhythm(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "record.html"
            result = self.run_tool(RENDER, str(EXAMPLE), "-o", str(output))
            html = output.read_text()

        self.assertEqual(result.returncode, 0)
        self.assertIn(".meta time {", html)
        self.assertIn("font-family: var(--font-mono)", html)
        self.assertIn(".event.document .detail {", html)
        self.assertIn("h2 { margin: 0; font-size: 1.45rem; line-height: 1.1; }", html)
        self.assertIn(".document-body h1 {", html)
        self.assertIn(".document-body h2 {", html)
        self.assertIn("dialog {", html)
        self.assertIn("max-width: none", html)
        self.assertIn(":focus-visible", html)


if __name__ == "__main__":
    unittest.main()
