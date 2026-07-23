#!/usr/bin/env python3
"""Shared, read-only support for Expedition lifecycle hooks."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = PLUGIN_ROOT / "tools" / "validate"


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


def find_expeditions_root(cwd: Path) -> Path | None:
    """Find the nearest .expeditions directory at or above cwd."""
    current = cwd if cwd.is_dir() else cwd.parent
    for candidate in (current, *current.parents):
        expeditions = candidate / ".expeditions"
        if expeditions.is_dir():
            return expeditions
    return None


def journey_logs(expeditions_root: Path) -> list[Path]:
    """Return journey logs in stable expedition-name order."""
    return sorted(
        path
        for path in expeditions_root.glob("*/journey.jsonl")
        if path.is_file()
    )


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


def validation_excerpt(output: str, project_root: Path, limit: int = 8) -> list[str]:
    """Keep validation feedback useful without flooding model context."""
    relative = output.replace(f"{project_root}{Path('/')}", "")
    lines = [line for line in relative.splitlines() if line.strip()]
    if len(lines) <= limit:
        return lines
    return [*lines[:limit], f"... {len(lines) - limit} more validation lines"]


def event_count_and_last(path: Path) -> tuple[int, str]:
    """Describe the last nonblank event without interpreting expedition state."""
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


def latest_named_file(paths: list[Path]) -> str:
    """Summarize a collection whose names carry their dates."""
    if not paths:
        return "none"
    latest = sorted(paths)[-1]
    return f"{len(paths)} (latest {latest.name})"


def tool_input_mentions_expeditions(payload: dict[str, Any]) -> bool:
    """Conservatively recognize tool calls that name expedition records."""
    tool_input = payload.get("tool_input")
    try:
        serialized = json.dumps(tool_input, sort_keys=True)
    except (TypeError, ValueError):
        serialized = repr(tool_input)
    return ".expeditions" in serialized or "journey.jsonl" in serialized
