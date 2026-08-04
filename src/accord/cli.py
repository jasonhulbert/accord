"""Public command-line interface for Accord's mechanical work."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from . import PROTOCOL_VERSION, RECORD_SCHEMA_VERSION, __version__
from .archive import ArchiveError, move_work
from .locking import LockError
from .mutations import (
    MutationError,
    append_agreement,
    append_event,
    start_work,
    store_document,
    timestamp,
)
from .records import RecordError, read_record
from .storage import (
    accord_archive_root_for,
    accord_home,
    accord_root_for,
    project_root,
    symlink_component_below,
    task_directory,
)
from .work import WorkError, context_for, list_work


def project_path(raw: str | None) -> Path:
    """Resolve and require one project directory."""
    path = Path(raw).expanduser() if raw else Path.cwd()
    if not path.is_dir():
        raise WorkError(f"project directory does not exist: {path}")
    return path


def json_output(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def add_project_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--project",
        metavar="PATH",
        help="project directory (default: current directory)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="accord",
        description="Keep Accord's records through a provider-independent CLI.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    version = commands.add_parser("version", help="show CLI compatibility")
    version.add_argument("--json", action="store_true")

    location = commands.add_parser("location", help="show this project's record root")
    location.add_argument("project", nargs="?")
    location.add_argument("--json", action="store_true")

    listing = commands.add_parser("list", help="list active and archived work")
    add_project_argument(listing)
    listing.add_argument("--json", action="store_true")

    context = commands.add_parser("context", help="read one explicitly named work")
    context.add_argument("task")
    add_project_argument(context)
    context.add_argument("--archived", action="store_true")
    context.add_argument("--json", action="store_true")

    start = commands.add_parser("start", help="store an accepted agreement")
    start.add_argument("task")
    start.add_argument("--agreement", required=True, metavar="FILE")
    start.add_argument("--actor", required=True, choices=["human"])
    start.add_argument("--summary", required=True)
    add_project_argument(start)
    start.add_argument("--json", action="store_true")

    append = commands.add_parser("append", help="append one validated record event")
    append.add_argument("task")
    append.add_argument(
        "type",
        choices=[
            "investigation",
            "attempt",
            "review",
            "report",
            "question",
            "direction",
            "check-in",
            "approach-change",
            "completion",
            "end",
            "note",
        ],
    )
    append.add_argument(
        "--actor", required=True, choices=["human", "agent", "supporting-agent"]
    )
    append.add_argument("--summary", required=True)
    append.add_argument("--ref", action="append", default=[])
    append.add_argument("--outcome", choices=["succeeded", "failed"])
    append.add_argument("--subject")
    append.add_argument("--decision")
    add_project_argument(append)
    append.add_argument("--json", action="store_true")

    document = commands.add_parser("document", help="store one durable document")
    document.add_argument("task")
    document.add_argument("kind", choices=["report", "learning-note", "diagram"])
    document.add_argument("--file", required=True, metavar="FILE")
    document.add_argument("--name")
    add_project_argument(document)
    document.add_argument("--json", action="store_true")

    amend = commands.add_parser("amend", help="append an accepted agreement amendment")
    amend.add_argument("task")
    amend.add_argument("--file", required=True, metavar="FILE")
    add_project_argument(amend)
    amend.add_argument("--json", action="store_true")

    validate = commands.add_parser("validate", help="validate one stored record")
    validate.add_argument("task")
    add_project_argument(validate)
    validate.add_argument("--archived", action="store_true")
    validate.add_argument("--json", action="store_true")

    archive = commands.add_parser("archive", help="move work out of routine discovery")
    archive.add_argument("task")
    archive.add_argument("--force", action="store_true")
    add_project_argument(archive)
    archive.add_argument("--json", action="store_true")

    restore = commands.add_parser(
        "restore", help="return archived work to active storage"
    )
    restore.add_argument("task")
    add_project_argument(restore)
    restore.add_argument("--json", action="store_true")
    return parser


def version_result() -> dict[str, Any]:
    return {
        "accord": __version__,
        "agent_protocol": PROTOCOL_VERSION,
        "record_schema": RECORD_SCHEMA_VERSION,
        "commands": [
            "version",
            "location",
            "list",
            "context",
            "start",
            "append",
            "document",
            "amend",
            "validate",
            "archive",
            "restore",
        ],
    }


def run(args: argparse.Namespace) -> int:
    if args.command == "version":
        result = version_result()
        if args.json:
            json_output(result)
        else:
            print(
                f"accord {result['accord']} "
                f"(agent protocol {result['agent_protocol']}; "
                f"record schema {result['record_schema']})"
            )
        return 0

    if args.command == "location":
        project = project_path(args.project)
        result = {
            "project_root": str(project_root(project)),
            "active": str(accord_root_for(project)),
            "archived": str(accord_archive_root_for(project)),
        }
        if args.json:
            json_output(result)
        else:
            print(result["active"])
        return 0

    project = project_path(args.project)

    if args.command == "list":
        work = list_work(project)
        if args.json:
            json_output(
                {
                    "project_root": str(project_root(project)),
                    "work": [item.as_dict() for item in work],
                }
            )
        elif not work:
            print("No Accord work found for this project.")
        else:
            width = max(len(item.storage) for item in work)
            for item in work:
                print(f"{item.storage.upper():<{width}}  {item.task}  {item.state}")
                if item.problem:
                    print(
                        f"WARNING: {item.task!r} needs attention: {item.problem}",
                        file=sys.stderr,
                    )
        return 2 if any(item.problem for item in work) else 0

    if args.command == "context":
        result = context_for(project, args.task, args.archived)
        if args.json:
            json_output(result)
        else:
            print(f"{result['task']} ({result['storage']}, {result['state']})")
            print(f"Agreement: {result['agreement']['path']}")
            print(
                f"Events: {len(result['events'])}; last {result['last_type']} at {result['last_timestamp']}"
            )
        return 0

    if args.command == "start":
        path = start_work(
            project,
            args.task,
            Path(args.agreement).expanduser(),
            args.actor,
            args.summary,
        )
        result = {
            "task": args.task,
            "path": str(path),
            "record": str(path / "record.jsonl"),
        }
        json_output(result) if args.json else print(
            f"Started Accord work {args.task!r} at {path}"
        )
        return 0

    if args.command == "append":
        event: dict[str, Any] = {
            "ts": timestamp(),
            "task": args.task,
            "schema": "1",
            "type": args.type,
            "actor": args.actor,
            "summary": args.summary,
        }
        if args.ref:
            event["refs"] = args.ref
        for field in ("outcome", "subject", "decision"):
            value = getattr(args, field)
            if value is not None:
                event[field] = value
        path = append_event(project, args.task, event)
        result = {"record": str(path), "event": event}
        json_output(result) if args.json else print(
            f"Appended {args.type!r} to {args.task!r}"
        )
        return 0

    if args.command == "document":
        path, reference = store_document(
            project,
            args.task,
            args.kind,
            Path(args.file).expanduser(),
            args.name,
        )
        result = {
            "task": args.task,
            "kind": args.kind,
            "path": str(path),
            "ref": reference,
        }
        json_output(result) if args.json else print(reference)
        return 0

    if args.command == "amend":
        path = append_agreement(
            project,
            args.task,
            Path(args.file).expanduser(),
        )
        result = {"task": args.task, "agreement": str(path)}
        json_output(result) if args.json else print(
            f"Amended agreement for {args.task!r}"
        )
        return 0

    if args.command == "validate":
        root = (
            accord_archive_root_for(project)
            if args.archived
            else accord_root_for(project)
        )
        task_dir = task_directory(root, args.task)
        if task_dir is None:
            raise WorkError(f"invalid task ID: {args.task!r}")
        if (
            task_dir.is_symlink()
            or not task_dir.is_dir()
            or symlink_component_below(accord_home(), task_dir) is not None
        ):
            raise WorkError(
                f"{args.task!r}: no safe stored work found for this project"
            )
        record = read_record(task_dir / "record.jsonl", args.task)
        result = {
            "record": str(record.path),
            "events": len(record.events),
            "valid": True,
        }
        json_output(result) if args.json else print(
            f"{record.path}: {len(record.events)} lines valid"
        )
        return 0

    if args.command in {"archive", "restore"}:
        result = move_work(
            project,
            args.task,
            args.command,
            force=args.force if args.command == "archive" else False,
        )
        value = {
            "task": result.task,
            "action": result.action,
            "source": str(result.source),
            "destination": str(result.destination),
            "forced_unclosed": result.forced_unclosed,
        }
        if result.forced_unclosed:
            print(
                f"WARNING: {result.task!r} was archived without a closing event "
                "because --force was provided.",
                file=sys.stderr,
            )
        json_output(value) if args.json else print(
            f"{result.action.title()}d {result.task!r}: {result.destination}"
        )
        return 0

    raise WorkError(f"unknown command: {args.command}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return run(args)
    except (ArchiveError, LockError, MutationError, RecordError, WorkError) as error:
        print(f"accord: {error}", file=sys.stderr)
        return 2
