#!/usr/bin/env python3
"""Fail loudly when a relevant tool call leaves a journey log malformed."""

from __future__ import annotations

import sys

from hook_support import (
    find_expeditions_root,
    journey_logs,
    payload_cwd,
    read_payload,
    tool_input_mentions_expeditions,
    validate_log,
    validation_excerpt,
)


def main() -> int:
    try:
        payload = read_payload()
    except ValueError as error:
        print(f"Expedition PostToolUse hook failed: {error}", file=sys.stderr)
        return 1

    if not tool_input_mentions_expeditions(payload):
        return 0

    expeditions_root = find_expeditions_root(payload_cwd(payload))
    if expeditions_root is None:
        return 0

    failures: list[str] = []
    project_root = expeditions_root.parent
    for log in journey_logs(expeditions_root):
        valid, output = validate_log(log)
        if valid:
            continue
        failures.append(f"{log.relative_to(project_root)} is invalid:")
        failures.extend(
            f"  {line}" for line in validation_excerpt(output, project_root)
        )

    if not failures:
        return 0

    tool_name = payload.get("tool_name", "tool")
    print(
        f"Expedition journey-log validation failed after {tool_name}. "
        "The tool has already run. Restore syntactic validity without "
        "altering previously valid events; a malformed newest append may be "
        "corrected before further events are recorded.",
        file=sys.stderr,
    )
    print("\n".join(failures), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
