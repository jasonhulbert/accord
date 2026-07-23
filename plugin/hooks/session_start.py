#!/usr/bin/env python3
"""Provide a factual camp index when a session starts or regains context."""

from __future__ import annotations

import sys

from hook_support import (
    event_count_and_last,
    find_expeditions_root,
    journey_logs,
    latest_named_file,
    payload_cwd,
    read_payload,
    validate_log,
    validation_excerpt,
)


def main() -> int:
    try:
        payload = read_payload()
    except ValueError as error:
        print(f"Expedition SessionStart hook failed: {error}", file=sys.stderr)
        return 1

    expeditions_root = find_expeditions_root(payload_cwd(payload))
    if expeditions_root is None:
        return 0

    logs = journey_logs(expeditions_root)
    if not logs:
        return 0

    project_root = expeditions_root.parent
    lines = [
        f"Expedition records found at {expeditions_root}.",
        (
            "This is a factual camp index, not a decision that any charter "
            "covers the current work."
        ),
    ]

    for log in logs:
        expedition_dir = log.parent
        valid, validation_output = validate_log(log)
        count, last = event_count_and_last(log)
        charter = expedition_dir / "charter.md"
        journals = list(expedition_dir.glob("journal*.md"))
        dispatches = list((expedition_dir / "dispatches").glob("*.md"))
        lines.append(
            f"- {expedition_dir.name}: "
            f"charter={'charter.md' if charter.is_file() else 'missing'}; "
            f"journey={'valid' if valid else 'INVALID'} "
            f"({count} events; last {last}); "
            f"journals={latest_named_file(journals)}; "
            f"dispatches={latest_named_file(dispatches)}"
        )
        if not valid:
            lines.append("  Validation:")
            lines.extend(
                f"    {line}"
                for line in validation_excerpt(validation_output, project_root)
            )

    lines.append(
        "Before resuming an expedition, survey its charter, journey log, "
        "journal, dispatches, and the actual state of the work."
    )
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
