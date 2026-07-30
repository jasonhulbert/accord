#!/usr/bin/env python3
"""Provide a factual Accord index when a session starts or regains context."""

from __future__ import annotations

import sys

from hook_support import (
    display_path,
    event_count_and_last,
    find_accord_root,
    last_event_type,
    latest_named_file,
    payload_cwd,
    read_payload,
    record_logs,
    validate_log,
    validation_excerpt,
)


def main() -> int:
    try:
        payload = read_payload()
    except ValueError as error:
        print(f"Accord SessionStart hook failed: {error}", file=sys.stderr)
        return 1

    accord_root = find_accord_root(payload_cwd(payload))
    if accord_root is None:
        return 0

    logs = record_logs(accord_root)
    if not logs:
        return 0

    lines = [
        f"Accord records found at {display_path(accord_root)}.",
        (
            "This is a factual index, not a decision that any agreement "
            "covers the current work."
        ),
    ]

    for log in logs:
        task_dir = log.parent
        valid, validation_output = validate_log(log)
        count, last = event_count_and_last(log)
        final_type = last_event_type(log) if valid else None
        closing = final_type if final_type in {"completion", "end"} else "none"
        agreement = task_dir / "agreement.md"
        learning = list(task_dir.glob("learning*.md"))
        reports = list((task_dir / "reports").glob("*.md"))
        lines.append(
            f"- {task_dir.name}: "
            f"agreement={'agreement.md' if agreement.is_file() else 'missing'}; "
            f"record={'valid' if valid else 'INVALID'} "
            f"({count} events; last {last}); "
            f"closing={closing}; "
            f"learning={latest_named_file(learning)}; "
            f"reports={latest_named_file(reports)}"
        )
        if not valid:
            lines.append("  Validation:")
            lines.extend(
                f"    {line}"
                for line in validation_excerpt(validation_output, accord_root)
            )

    lines.extend(
        [
            (
                "A completion or end event closes its agreement and record. "
                "Begin a new agreement for later work."
            ),
            (
                "Before resuming active work, read its agreement, record, "
                "reports, learning notes, and actual state."
            ),
        ]
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
