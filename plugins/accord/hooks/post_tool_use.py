#!/usr/bin/env python3
"""Fail loudly when a relevant tool call leaves an Accord record malformed."""

from __future__ import annotations

import sys

from hook_support import (
    display_path,
    find_archive_root,
    find_accord_root,
    payload_cwd,
    read_payload,
    record_logs,
    roots_named_by_tool_input,
    tool_input_mentions_accord,
    validate_log,
    validation_excerpt,
)


def main() -> int:
    try:
        payload = read_payload()
    except ValueError as error:
        print(f"Accord PostToolUse hook failed: {error}", file=sys.stderr)
        return 1

    if not tool_input_mentions_accord(payload):
        return 0

    cwd = payload_cwd(payload)
    roots = [
        root
        for root in (find_accord_root(cwd), find_archive_root(cwd))
        if root is not None
    ]
    if not roots:
        return 0
    roots = roots_named_by_tool_input(payload, roots)

    failures: list[str] = []
    for root in roots:
        for log in record_logs(root):
            valid, output = validate_log(log)
            if valid:
                continue
            failures.append(f"{display_path(log)} is invalid:")
            failures.extend(
                f"  {line}" for line in validation_excerpt(output, root)
            )

    if not failures:
        return 0

    tool_name = payload.get("tool_name", "tool")
    print(
        f"Accord record validation failed after {tool_name}. "
        "The tool has already run. Restore syntactic validity without "
        "altering previously valid events; a malformed newest append may be "
        "corrected before further events are recorded.",
        file=sys.stderr,
    )
    print("\n".join(failures), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
