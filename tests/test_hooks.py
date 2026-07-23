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
HOOKS_ROOT = REPO_ROOT / "plugin" / "hooks"
HOOK_CONFIG = HOOKS_ROOT / "hooks.json"
SESSION_START = HOOKS_ROOT / "session_start.py"
POST_TOOL_USE = HOOKS_ROOT / "post_tool_use.py"


def event(event_type: str = "departure") -> dict[str, str]:
    return {
        "ts": "2026-07-23T12:00:00Z",
        "expedition": "ridge",
        "schema": "1",
        "type": event_type,
        "actor": "patron",
        "account": "The patron sent the company out.",
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

    def make_expedition(self, root: Path, contents: str) -> Path:
        expedition = root / ".expeditions" / "ridge"
        expedition.mkdir(parents=True)
        (expedition / "charter.md").write_text("# Charter: ridge\n")
        log = expedition / "journey.jsonl"
        log.write_text(contents)
        return log

    def test_one_shared_config_wires_both_portable_hook_events(self):
        config = json.loads(HOOK_CONFIG.read_text())

        self.assertEqual(
            set(config["hooks"]),
            {"SessionStart", "PostToolUse"},
        )
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

    def test_session_start_is_silent_without_expedition_records(self):
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

    def test_session_start_reports_facts_without_selecting_an_expedition(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_expedition(root, json.dumps(event()) + "\n")

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "resume",
                    "cwd": str(root / ".expeditions" / "ridge"),
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("- ridge: charter=charter.md; journey=valid", result.stdout)
        self.assertIn("last departure at 2026-07-23T12:00:00Z", result.stdout)
        self.assertIn("not a decision that any charter covers", result.stdout)

    def test_session_start_surfaces_invalid_history_without_blocking_startup(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_expedition(root, '{"type": "departure"}\n')

            result = self.run_hook(
                SESSION_START,
                {
                    "hook_event_name": "SessionStart",
                    "source": "compact",
                    "cwd": str(root),
                },
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("journey=INVALID", result.stdout)
        self.assertIn("missing required field", result.stdout)

    def test_post_tool_use_ignores_unrelated_edits_even_with_invalid_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_expedition(root, '{"type": "departure"}\n')

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

    def test_post_tool_use_stays_silent_when_touched_logs_are_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = self.make_expedition(root, json.dumps(event()) + "\n")

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

    def test_post_tool_use_blocks_progress_after_malformed_log_append(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = self.make_expedition(root, json.dumps(event()) + "\nnot-json\n")

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
        self.assertIn(".expeditions/ridge/journey.jsonl", result.stderr)


if __name__ == "__main__":
    unittest.main()
