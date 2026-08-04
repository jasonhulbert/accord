"""Move Accord work between active and archived storage without rewriting it."""

from __future__ import annotations

import ctypes
import errno
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from .locking import locked_project
from .records import RecordError, read_record
from .storage import (
    accord_archive_root_for,
    accord_home,
    accord_root_for,
    symlink_component_below,
    task_directory,
)


class ArchiveError(Exception):
    """Stored work cannot be moved safely."""


class UnclosedWorkError(ArchiveError):
    """Archival needs an explicit override because the work is still open."""


@dataclass(frozen=True)
class MoveResult:
    """The factual result of one archive or restore operation."""

    task: str
    action: str
    source: Path
    destination: Path
    forced_unclosed: bool = False


def safe_task_tree(root: Path, task: str) -> Path:
    """Require one direct task tree containing no links or special files."""
    task_dir = task_directory(root, task)
    if task_dir is None:
        raise ArchiveError(f"invalid task ID: {task!r}")
    unsafe = symlink_component_below(accord_home(), task_dir)
    if unsafe is not None:
        raise ArchiveError(f"Accord storage contains a symlink at {unsafe}")
    if not task_dir.exists():
        raise ArchiveError(f"{task!r}: no stored work found for this project")
    if not task_dir.is_dir():
        raise ArchiveError(f"{task!r}: stored work is not a directory")
    try:
        for path in task_dir.rglob("*"):
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                relative = path.relative_to(task_dir)
                raise ArchiveError(
                    f"{task!r}: stored work contains an unsafe object at {relative}"
                )
    except OSError as error:
        raise ArchiveError(
            f"{task!r}: stored work cannot be inspected: {error}"
        ) from error
    return task_dir


def safe_destination_root(root: Path) -> None:
    """Create one storage root without following a link beneath Accord home."""
    home = accord_home()
    unsafe = symlink_component_below(home, root)
    if unsafe is not None:
        raise ArchiveError(f"destination storage contains a symlink at {unsafe}")
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise ArchiveError(
            f"cannot create destination storage {root}: {error}"
        ) from error
    unsafe = symlink_component_below(home, root)
    if unsafe is not None:
        raise ArchiveError(f"destination storage contains a symlink at {unsafe}")


def rename_without_replace(source: Path, destination: Path) -> None:
    """Rename one directory atomically without replacing another path."""
    if sys.platform == "win32":
        os.rename(source, destination)
        return

    libc = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    result: int | None = None
    if sys.platform == "darwin" and hasattr(libc, "renamex_np"):
        renamex_np = libc.renamex_np
        renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        renamex_np.restype = ctypes.c_int
        result = renamex_np(source_bytes, destination_bytes, 0x00000004)
    elif hasattr(libc, "renameat2"):
        renameat2 = libc.renameat2
        renameat2.argtypes = [
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        renameat2.restype = ctypes.c_int
        result = renameat2(
            -100,
            source_bytes,
            -100,
            destination_bytes,
            0x00000001,
        )
    if result is None:
        raise OSError(
            errno.ENOTSUP,
            "atomic no-replace directory moves are not supported on this platform",
            destination,
        )
    if result != 0:
        number = ctypes.get_errno()
        raise OSError(number, os.strerror(number), destination)


def move_work(cwd: Path, task: str, action: str, force: bool = False) -> MoveResult:
    """Archive closed work, or restore explicitly named archived work."""
    with locked_project(cwd):
        return move_work_unlocked(cwd, task, action, force)


def move_work_unlocked(
    cwd: Path, task: str, action: str, force: bool = False
) -> MoveResult:
    """Move work while the caller holds the stable project lock."""
    if action == "archive":
        source_root = accord_root_for(cwd)
        destination_root = accord_archive_root_for(cwd)
    elif action == "restore":
        source_root = accord_archive_root_for(cwd)
        destination_root = accord_root_for(cwd)
    else:
        raise ArchiveError(f"unknown move action: {action!r}")

    source = safe_task_tree(source_root, task)
    forced_unclosed = False
    if action == "archive":
        try:
            record = read_record(source / "record.jsonl", task)
        except RecordError as error:
            raise ArchiveError(str(error)) from error
        if not record.closed:
            if not force:
                raise UnclosedWorkError(
                    f"{task!r}: record does not end in completion or end; "
                    "nothing was archived"
                )
            forced_unclosed = True

    destination = task_directory(destination_root, task)
    if destination is None:
        raise ArchiveError(f"invalid task ID: {task!r}")
    safe_destination_root(destination_root)
    if destination.exists() or destination.is_symlink():
        raise ArchiveError(f"{task!r}: destination already exists; nothing was moved")
    try:
        rename_without_replace(source, destination)
    except OSError as error:
        raise ArchiveError(f"{task!r}: could not be moved: {error}") from error
    return MoveResult(task, action, source, destination, forced_unclosed)
