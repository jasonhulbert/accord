#!/usr/bin/env python3
"""Behavior tests for the bundled local Accord web view."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
SERVE = REPO_ROOT / "plugins" / "accord" / "tools" / "serve"
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


def event(summary: str, event_type: str = "note") -> dict[str, str]:
    return {
        "ts": "2026-07-25T12:00:00Z",
        "task": "rate-limit",
        "schema": "1",
        "type": event_type,
        "actor": "agent",
        "summary": summary,
    }


class ServerTests(unittest.TestCase):
    def make_project(self, root: Path) -> tuple[Path, Path, Path]:
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
        return project, home, Path(result.stdout.strip())

    def write_record(self, store: Path, task: str, contents: str) -> Path:
        directory = store / task
        directory.mkdir(parents=True)
        path = directory / "record.jsonl"
        path.write_text(contents)
        return path

    def start_server(
        self,
        project: Path,
        home: Path,
        *arguments: str,
    ) -> tuple[subprocess.Popen[str], str]:
        process = subprocess.Popen(
            [sys.executable, str(SERVE), "--no-open", "--port", "0", *arguments],
            cwd=project,
            env=os.environ | {"HOME": str(home)},
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.addCleanup(self.stop_server, process)
        line = process.stdout.readline().strip() if process.stdout else ""
        self.assertTrue(line.startswith("Accord web view: http://127.0.0.1:"), line)
        return process, line.removeprefix("Accord web view: ")

    def stop_server(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()

    def get(self, url: str) -> tuple[int, str]:
        try:
            with urlopen(url, timeout=3) as response:
                return response.status, response.read().decode()
        except HTTPError as error:
            return error.code, error.read().decode()

    def test_server_lists_records_and_explicitly_refreshes_a_task_view_from_disk(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, store = self.make_project(Path(directory))
            self.write_record(
                store,
                "rate-limit",
                json.dumps(event("The agreement was accepted.", "start")) + "\n",
            )
            task = store / "rate-limit"
            (task / "agreement.md").write_text(
                "# Agreement: rate-limit\n\nThe agreement is visible.\n"
            )
            reports = task / "reports"
            reports.mkdir()
            (reports / "2026-07-25.md").write_text(
                "# Report: rate-limit\n\nThe report is visible.\n"
            )
            (task / "learning-2026-07-25.md").write_text(
                "# Learning note: rate-limit\n\nThe learning is visible.\n"
            )
            self.write_record(
                store,
                "second-task",
                json.dumps(event("Another record exists.")) + "\n",
            )
            _, url = self.start_server(project, home)

            status, index = self.get(url)
            self.assertEqual(status, 200)
            self.assertIn("Accord records", index)
            self.assertIn('href="/task/rate-limit"', index)
            self.assertIn('href="/task/second-task"', index)
            self.assertIn("Refresh the list", index)
            self.assertNotIn('<meta http-equiv="refresh"', index)
            self.assertIn("--paper: #000", index)
            self.assertIn("status-mark", index)
            self.assertEqual(index.count("@font-face"), 4)
            self.assertIn("font: 15px/1.55 var(--font-sans)", index)
            self.assertIn("line-height: 1.1", index)
            self.assertIn(".record > .meta { margin-left: 18px; }", index)
            self.assertIn('data:font/woff2;base64,', index)
            self.assertNotIn("Avenir", index)
            self.assertNotIn("border-radius:", index)

            task_url = url.rstrip("/") + "/task/rate-limit"
            status, page = self.get(task_url)
            self.assertEqual(status, 200)
            self.assertIn("The agreement was accepted.", page)
            self.assertIn("<dialog id=\"document-dialog\">", page)
            self.assertIn("The agreement is visible.", page)
            self.assertIn("The report is visible.", page)
            self.assertIn("The learning is visible.", page)
            self.assertIn('<a href="/task/rate-limit">Refresh</a>', page)
            self.assertNotIn("window.location.reload", page)
            self.assertNotIn("setTimeout", page)
            self.assertNotIn('document.querySelector("dialog[open]")', page)
            self.assertIn("font: 13px/1.5 var(--font-mono)", page)
            self.assertIn(
                'import mermaid from "/assets/web/mermaid/mermaid.js"',
                page,
            )

            status, mermaid_entry = self.get(
                url.rstrip("/") + "/assets/web/mermaid/mermaid.js"
            )
            self.assertEqual(status, 200)
            self.assertIn("export", mermaid_entry)

            record = store / "rate-limit" / "record.jsonl"
            with record.open("a") as handle:
                handle.write(json.dumps(event("A new event is visible.")) + "\n")
            status, refreshed = self.get(task_url)
            self.assertEqual(status, 200)
            self.assertIn("A new event is visible.", refreshed)

    def test_task_option_opens_the_requested_record_without_selecting_one_silently(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, store = self.make_project(Path(directory))
            self.write_record(
                store,
                "rate-limit",
                json.dumps(event("The selected record.")) + "\n",
            )
            _, url = self.start_server(project, home, "--task", "rate-limit")

            self.assertTrue(url.endswith("/task/rate-limit"), url)
            status, page = self.get(url)
            self.assertEqual(status, 200)
            self.assertIn("The selected record.", page)

    def test_server_surfaces_malformed_records_in_the_index_and_task_view(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, store = self.make_project(Path(directory))
            self.write_record(
                store,
                "broken",
                json.dumps(event("The record begins.")) + "\nnot-json\n",
            )
            _, url = self.start_server(project, home)

            status, index = self.get(url)
            self.assertEqual(status, 200)
            self.assertIn("needs attention", index)
            self.assertIn("invalid JSON", index)

            status, page = self.get(url.rstrip("/") + "/task/broken")
            self.assertEqual(status, 422)
            self.assertIn("The record was not changed.", page)
            self.assertIn("invalid JSON", page)
            self.assertEqual(page.count("@font-face"), 4)
            self.assertIn('<nav class="view-nav"><a href="/">All records</a></nav>', page)
            self.assertIn('<div class="error-copy">', page)
            self.assertIn("font: 12px/1.5 var(--font-mono)", page)
            self.assertNotIn("ui-monospace", page)


if __name__ == "__main__":
    unittest.main()
