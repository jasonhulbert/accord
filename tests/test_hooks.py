#!/usr/bin/env python3
"""Behavior tests for the shared Claude Code and Codex hook handlers."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
HOOKS_ROOT = REPO_ROOT / "plugins" / "accord" / "hooks"
HOOK_CONFIG = HOOKS_ROOT / "hooks.json"
SESSION_START = HOOKS_ROOT / "session_start.py"
POST_TOOL_USE = HOOKS_ROOT / "post_tool_use.py"
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


def event(event_type: str = "start") -> dict[str, str]:
    return {
        "ts": "2026-07-23T12:00:00Z",
        "task": "rate-limit",
        "schema": "1",
        "type": event_type,
        "actor": "human",
        "summary": "The human accepted the agreement.",
    }


class HookTests(unittest.TestCase):
    def run_hook(
        self, script: Path, payload: dict, home: Path
    ) -> subprocess.CompletedProcess[str]:
        environment = os.environ | {"HOME": str(home)}
        return subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )

    def accord_root(self, root: Path, home: Path) -> Path:
        result = subprocess.run(
            [sys.executable, str(LOCATION), str(root)],
            text=True,
            capture_output=True,
            check=False,
            env=os.environ | {"HOME": str(home)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(result.stdout.strip())

    def make_accord(self, root: Path, home: Path, contents: str) -> Path:
        (root / ".git").mkdir(exist_ok=True)
        task = self.accord_root(root, home) / "rate-limit"
        task.mkdir(parents=True)
        (task / "agreement.md").write_text("# Agreement: rate-limit\n")
        log = task / "record.jsonl"
        log.write_text(contents)
        return log

    def test_one_shared_config_wires_both_portable_hook_events(self):
        config = json.loads(HOOK_CONFIG.read_text())

        self.assertEqual(set(config["hooks"]), {"SessionStart", "PostToolUse"})
        session_group = config["hooks"]["SessionStart"][0]
        self.assertEqual(session_group["matcher"], "startup|resume|compact")
        post_tool_group = config["hooks"]["PostToolUse"][0]
        self.assertEqual(
            post_tool_group["matcher"],
            "Bash|Edit|Write|apply_patch",
        )
        for group in (session_group, post_tool_group):
            handler = group["hooks"][0]
            self.assertIn("${CLAUDE_PLUGIN_ROOT}", handler["command"])
            self.assertIn("%CLAUDE_PLUGIN_ROOT%", handler["commandWindows"])

    def test_session_start_is_silent_without_accord_records(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            home.mkdir()
            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "startup",
                    "cwd": directory,
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_session_start_reports_facts_without_selecting_an_agreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            self.make_accord(root, home, json.dumps(event()) + "\n")
            nested = root / "src"
            nested.mkdir()

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "resume",
                    "cwd": str(nested),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn(
            "- rate-limit: agreement=agreement.md; record=valid",
            result.stdout,
        )
        self.assertIn(
            "last start at 2026-07-23T12:00:00Z",
            result.stdout,
        )
        self.assertIn("completion=none", result.stdout)
        self.assertIn(
            "not a decision that any agreement covers",
            result.stdout,
        )
        self.assertIn("~/.accord/projects/", result.stdout)

    def test_session_start_marks_completion_as_a_closed_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            contents = "\n".join(
                [
                    json.dumps(event()),
                    json.dumps(event("completion")),
                    "",
                ]
            )
            log = self.make_accord(root, home, contents)
            archive_root = (
                home
                / ".accord"
                / "archive"
                / "projects"
                / log.parents[1].name
            )

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "resume",
                    "cwd": str(root),
                },
                home,
            )
            still_active = log.is_file()
            archived_automatically = (archive_root / "rate-limit").exists()

        self.assertEqual(result.returncode, 0)
        self.assertIn("completion=recorded", result.stdout)
        self.assertIn(
            "A completion event closes its agreement and record",
            result.stdout,
        )
        self.assertIn("Begin a new agreement for later work", result.stdout)
        self.assertTrue(still_active)
        self.assertFalse(archived_automatically)

    def test_session_start_excludes_archived_history_from_routine_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            active_log = self.make_accord(
                root,
                home,
                json.dumps(event("completion")) + "\n",
            )
            archive_root = (
                home
                / ".accord"
                / "archive"
                / "projects"
                / active_log.parents[1].name
            )
            archived_task = archive_root / "rate-limit"
            archived_task.parent.mkdir(parents=True)
            active_log.parent.rename(archived_task)

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "startup",
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_session_start_surfaces_invalid_history_without_blocking_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            self.make_accord(root, home, '{"type": "start"}\n')

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "compact",
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("record=INVALID", result.stdout)
        self.assertIn("missing required field", result.stdout)

    def test_post_tool_use_ignores_unrelated_edits_even_with_invalid_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            self.make_accord(root, home, '{"type": "start"}\n')

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Edit",
                    "tool_input": {"file_path": str(root / "README.md")},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_post_tool_use_stays_silent_when_touched_records_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            log = self.make_accord(root, home, json.dumps(event()) + "\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(log)},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_recording_completion_does_not_archive_work_automatically(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            log = self.make_accord(
                root,
                home,
                json.dumps(event("completion")) + "\n",
            )
            archive_root = (
                home
                / ".accord"
                / "archive"
                / "projects"
                / log.parents[1].name
            )

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(log)},
                    "cwd": str(root),
                },
                home,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(log.is_file())
            self.assertFalse((archive_root / "rate-limit").exists())

    def test_post_tool_use_checks_history_after_a_related_document_edit(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            log = self.make_accord(root, home, '{"type": "start"}\n')

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Edit",
                    "tool_input": {"file_path": str(log.parent / "agreement.md")},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("record validation failed", result.stderr)

    def test_post_tool_use_blocks_progress_after_malformed_record_append(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            log = self.make_accord(root, home, json.dumps(event()) + "\nnot-json\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": f"printf malformed >> {log}"},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("tool has already run", result.stderr)
        self.assertIn("invalid JSON", result.stderr)
        self.assertIn("~/.accord/projects/", result.stderr)
        self.assertIn("rate-limit/record.jsonl", result.stderr)

    def test_post_tool_use_still_surfaces_invalid_archived_history_when_touched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            active_log = self.make_accord(root, home, json.dumps(event()) + "\n")
            archive_root = (
                home
                / ".accord"
                / "archive"
                / "projects"
                / active_log.parents[1].name
            )
            archived_task = archive_root / "rate-limit"
            archived_task.parent.mkdir(parents=True)
            active_log.parent.rename(archived_task)
            archived_log = archived_task / "record.jsonl"
            archived_log.write_text("not-json\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Edit",
                    "tool_input": {"file_path": str(archived_log)},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("record validation failed", result.stderr)
        self.assertIn("archive/projects/", result.stderr)

    def test_active_record_edits_do_not_rescan_archived_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            home.mkdir()
            active_log = self.make_accord(root, home, json.dumps(event()) + "\n")
            archive_root = (
                home
                / ".accord"
                / "archive"
                / "projects"
                / active_log.parents[1].name
            )
            archived_task = archive_root / "old-work"
            archived_task.mkdir(parents=True)
            (archived_task / "record.jsonl").write_text("not-json\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(active_log)},
                    "cwd": str(root),
                },
                home,
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
