"""Inspect Accord work without inferring authority or intent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .records import RecordError, read_record
from .storage import (
    accord_archive_root_for,
    accord_home,
    accord_root_for,
    project_root,
    symlink_component_below,
    task_directory,
)


class WorkError(Exception):
    """Stored work cannot be described safely or completely."""


@dataclass(frozen=True)
class WorkSummary:
    """Mechanical facts about one stored body of work."""

    task: str
    storage: str
    path: Path
    state: str
    last_type: str | None
    last_timestamp: str | None
    event_count: int
    problem: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "storage": self.storage,
            "path": str(self.path),
            "state": self.state,
            "last_type": self.last_type,
            "last_timestamp": self.last_timestamp,
            "event_count": self.event_count,
            "problem": self.problem,
        }


def safe_storage_root(root: Path, storage: str) -> None:
    """Refuse storage that reaches records through a symlink."""
    unsafe = symlink_component_below(accord_home(), root)
    if unsafe is not None:
        raise WorkError(f"{storage} storage contains a symlink at {unsafe}")
    if root.exists() and not root.is_dir():
        raise WorkError(f"{storage} storage is not a directory: {root}")


def inspect_task(task_dir: Path, storage: str) -> WorkSummary:
    """Inspect one direct storage entry without hiding damage."""
    task = task_dir.name
    if task_dir.is_symlink():
        return WorkSummary(
            task,
            storage,
            task_dir,
            "damaged",
            None,
            None,
            0,
            "task directory is a symlink",
        )
    if not task_dir.is_dir():
        return WorkSummary(
            task,
            storage,
            task_dir,
            "damaged",
            None,
            None,
            0,
            "storage entry is not a directory",
        )
    record_path = task_dir / "record.jsonl"
    if not record_path.is_file():
        return WorkSummary(
            task, storage, task_dir, "damaged", None, None, 0, "record.jsonl is missing"
        )
    try:
        record = read_record(record_path, task)
    except RecordError as error:
        return WorkSummary(
            task, storage, task_dir, "damaged", None, None, 0, str(error)
        )
    last = record.last_event or {}
    return WorkSummary(
        task=task,
        storage=storage,
        path=task_dir,
        state="closed" if record.closed else "open",
        last_type=last.get("type"),
        last_timestamp=last.get("ts"),
        event_count=len(record.events),
    )


def work_in(root: Path, storage: str) -> list[WorkSummary]:
    """List direct work entries beneath one safe storage root."""
    safe_storage_root(root, storage)
    if not root.exists():
        return []
    try:
        entries = sorted(root.iterdir(), key=lambda path: path.name)
    except OSError as error:
        raise WorkError(f"{storage} storage could not be read: {error}") from error
    return [inspect_task(entry, storage) for entry in entries]


def list_work(cwd: Path) -> list[WorkSummary]:
    """List active work first and archived work second."""
    return [
        *work_in(accord_root_for(cwd), "active"),
        *work_in(accord_archive_root_for(cwd), "archived"),
    ]


def document(path: Path, task_dir: Path) -> dict[str, str]:
    """Read one Markdown document without following a link."""
    if (
        path.is_symlink()
        or not path.is_file()
        or symlink_component_below(task_dir, path) is not None
    ):
        raise WorkError(f"unsafe document path: {path}")
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise WorkError(f"cannot read document {path}: {error}") from error
    return {"path": str(path), "content": content}


def documents_in(directory: Path, task_dir: Path) -> list[dict[str, str]]:
    """Read direct Markdown documents from one known task directory."""
    if not directory.exists():
        return []
    if directory.is_symlink() or not directory.is_dir():
        raise WorkError(f"unsafe document directory: {directory}")
    return [
        document(path, task_dir)
        for path in sorted(directory.glob("*.md"), key=lambda item: item.name)
    ]


def context_for(cwd: Path, task: str, archived: bool = False) -> dict[str, Any]:
    """Return factual context for one explicitly named body of work."""
    storage = "archived" if archived else "active"
    root = accord_archive_root_for(cwd) if archived else accord_root_for(cwd)
    safe_storage_root(root, storage)
    task_dir = task_directory(root, task)
    if task_dir is None:
        raise WorkError(f"invalid task ID: {task!r}")
    if task_dir.is_symlink() or not task_dir.is_dir():
        raise WorkError(f"{task!r}: no safe {storage} work found for this project")

    try:
        record = read_record(task_dir / "record.jsonl", task)
    except RecordError as error:
        raise WorkError(str(error)) from error

    agreement_path = task_dir / "agreement.md"
    if not agreement_path.is_file():
        raise WorkError(f"{agreement_path}: agreement is missing")

    last = record.last_event or {}
    return {
        "project_root": str(project_root(cwd)),
        "record_root": str(root),
        "task": task,
        "storage": storage,
        "path": str(task_dir),
        "state": "closed" if record.closed else "open",
        "last_type": last.get("type"),
        "last_timestamp": last.get("ts"),
        "agreement": document(agreement_path, task_dir),
        "events": record.events,
        "documents": {
            "reports": documents_in(task_dir / "reports", task_dir),
            "learning_notes": [
                document(path, task_dir)
                for path in sorted(
                    task_dir.glob("learning*.md"), key=lambda item: item.name
                )
            ],
            "diagrams": documents_in(task_dir / "diagrams", task_dir),
        },
    }
