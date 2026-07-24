#!/usr/bin/env python3
"""Behavior tests for the shared Claude Code and Codex hook handlers."""

from __future__ import annotations

import json
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
    def run_hook(self, script: Path, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def make_accord(self, root: Path, contents: str) -> Path:
        task = root / ".accord" / "rate-limit"
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
            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "startup",
                    "cwd": directory,
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_session_start_reports_facts_without_selecting_an_agreement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_accord(root, json.dumps(event()) + "\n")

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "resume",
                    "cwd": str(root / ".accord" / "rate-limit"),
                },
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
        self.assertIn(
            "not a decision that any agreement covers",
            result.stdout,
        )

    def test_session_start_surfaces_invalid_history_without_blocking_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_accord(root, '{"type": "start"}\n')

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "compact",
                    "cwd": str(root),
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("record=INVALID", result.stdout)
        self.assertIn("missing required field", result.stdout)

    def test_post_tool_use_ignores_unrelated_edits_even_with_invalid_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_accord(root, '{"type": "start"}\n')

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Edit",
                    "tool_input": {"file_path": str(root / "README.md")},
                    "cwd": str(root),
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_post_tool_use_stays_silent_when_touched_records_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = self.make_accord(root, json.dumps(event()) + "\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Write",
                    "tool_input": {"file_path": str(log)},
                    "cwd": str(root),
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_post_tool_use_blocks_progress_after_malformed_record_append(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = self.make_accord(root, json.dumps(event()) + "\nnot-json\n")

            result = self.run_hook(
                POST_TOOL_USE,
                {
                    "hook_event_name": "PostToolUse",
                    "tool_name": "Bash",
                    "tool_input": {"command": f"printf malformed >> {log}"},
                    "cwd": str(root),
                },
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("tool has already run", result.stderr)
        self.assertIn("invalid JSON", result.stderr)
        self.assertIn(".accord/rate-limit/record.jsonl", result.stderr)


if __name__ == "__main__":
    unittest.main()
