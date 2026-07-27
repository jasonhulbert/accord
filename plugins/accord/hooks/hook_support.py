#!/usr/bin/env python3
"""Shared, read-only support for Accord lifecycle hooks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = PLUGIN_ROOT / "tools" / "validate"
sys.path.insert(0, str(PLUGIN_ROOT))

from storage import accord_home, accord_root_for  # noqa: E402


def read_payload() -> dict[str, Any]:
    """Read one hook payload from stdin."""
    try:
        payload = json.load(sys.stdin)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read hook input: {error}") from error
    if not isinstance(payload, dict):
        raise ValueError("hook input must be a JSON object")
    return payload


def payload_cwd(payload: dict[str, Any]) -> Path:
    """Return the hook working directory without trusting it to exist."""
    raw = payload.get("cwd")
    if not isinstance(raw, str) or not raw:
        return Path.cwd().resolve()
    return Path(raw).expanduser().resolve()


def find_accord_root(cwd: Path) -> Path | None:
    """Find this project's Accord directory in the user's hidden home store."""
    accord = accord_root_for(cwd)
    return accord if accord.is_dir() else None


def record_logs(accord_root: Path) -> list[Path]:
    """Return record logs in stable task-name order."""
    return sorted(path for path in accord_root.glob("*/record.jsonl") if path.is_file())


def validate_log(path: Path) -> tuple[bool, str]:
    """Run the framework validator and return its complete result."""
    if not VALIDATOR.is_file():
        return False, f"{VALIDATOR}: validator is missing"
    try:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return False, f"{path}: validation could not run: {error}"
    output = "\n".join(
        part.strip() for part in (result.stdout, result.stderr) if part.strip()
    )
    return result.returncode == 0, output


def display_path(path: Path) -> str:
    """Keep home-store paths recognizable without depending on a username."""
    try:
        return f"~/{path.relative_to(Path.home()).as_posix()}"
    except ValueError:
        return str(path)


def validation_excerpt(output: str, accord_root: Path, limit: int = 8) -> list[str]:
    """Keep validation feedback useful without flooding model context."""
    readable = output.replace(str(accord_root), display_path(accord_root))
    lines = [line for line in readable.splitlines() if line.strip()]
    if len(lines) <= limit:
        return lines
    return [*lines[:limit], f"... {len(lines) - limit} more validation lines"]


def event_count_and_last(path: Path) -> tuple[int, str]:
    """Describe the last nonblank event without interpreting task state."""
    try:
        lines = [
            (number, raw)
            for number, raw in enumerate(path.read_text().splitlines(), 1)
            if raw.strip()
        ]
    except OSError as error:
        return 0, f"unreadable ({error})"
    if not lines:
        return 0, "none"
    number, raw = lines[-1]
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        return len(lines), f"unreadable line {number}"
    if not isinstance(event, dict):
        return len(lines), f"non-object line {number}"
    event_type = event.get("type", "unknown")
    timestamp = event.get("ts", "unknown time")
    return len(lines), f"{event_type} at {timestamp}"


def contains_event_type(path: Path, event_type: str) -> bool:
    """Return whether a readable record contains the named event type."""
    try:
        lines = path.read_text().splitlines()
    except OSError:
        return False
    for raw in lines:
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == event_type:
            return True
    return False


def latest_named_file(paths: list[Path]) -> str:
    """Summarize a collection whose names carry their dates."""
    if not paths:
        return "none"
    latest = sorted(paths)[-1]
    return f"{len(paths)} (latest {latest.name})"


def tool_input_mentions_accord(payload: dict[str, Any]) -> bool:
    """Conservatively recognize tool calls that name Accord records."""
    tool_input = payload.get("tool_input")
    try:
        serialized = json.dumps(tool_input, sort_keys=True)
    except (TypeError, ValueError):
        serialized = repr(tool_input)
    return str(accord_home()) in serialized or "~/.accord" in serialized
