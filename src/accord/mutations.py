"""Create and append Accord records through one validated write boundary."""

from __future__ import annotations

import json
import os
import shutil
import stat
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO, Iterator

from .locking import locked_project
from .records import (
    NEW_EVENT_ACTORS,
    RecordError,
    parse_record_bytes,
    validate_event,
)
from .storage import (
    accord_home,
    accord_root_for,
    symlink_component_below,
    task_directory,
)


class MutationError(Exception):
    """A requested record mutation is unsafe or structurally invalid."""


def timestamp() -> str:
    """Return a schema-1 UTC timestamp."""
    return (
        datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    )


def event_bytes(event: dict[str, Any]) -> bytes:
    """Serialize one complete JSONL event write."""
    return (json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def validate_new_event(event: dict[str, Any]) -> None:
    """Require valid structure and the current actor vocabulary for new events."""
    errors = validate_event(event)
    if event.get("actor") not in NEW_EVENT_ACTORS:
        errors.append("new events use human, agent, or supporting-agent as actor")
    for reference in event.get("refs", []):
        path = PurePosixPath(reference)
        if path.is_absolute() or ".." in path.parts or "\\" in reference:
            errors.append(f"ref must stay within this work: {reference!r}")
    if errors:
        raise MutationError("invalid event: " + "; ".join(errors))


def sync_file(path: Path, content: bytes) -> None:
    """Write and sync one new file."""
    with path.open("xb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def write_all(descriptor: int, content: bytes) -> None:
    """Write every byte while the caller holds the file lock."""
    remaining = memoryview(content)
    while remaining:
        written = os.write(descriptor, remaining)
        if written == 0:
            raise OSError("write returned no bytes")
        remaining = remaining[written:]


def markdown_bytes(source: Path, kind: str) -> bytes:
    """Read nonempty UTF-8 Markdown without changing its bytes."""
    try:
        content = source.read_bytes()
    except OSError as error:
        raise MutationError(f"cannot read {kind} {source}: {error}") from error
    if not content.strip():
        raise MutationError(f"{kind} must not be empty")
    try:
        content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise MutationError(f"{kind} must be UTF-8: {error}") from error
    return content


def sync_directory(path: Path) -> None:
    """Sync directory entries where the platform supports it."""
    try:
        descriptor = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(descriptor)
    except OSError:
        pass
    finally:
        os.close(descriptor)


def require_safe_root(root: Path) -> None:
    """Create the active root without accepting symlinked Accord storage."""
    home = accord_home()
    if home.exists() and home.is_symlink():
        raise MutationError(f"Accord home is a symlink: {home}")
    unsafe = symlink_component_below(home, root)
    if unsafe is not None:
        raise MutationError(f"Accord storage contains a symlink at {unsafe}")
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise MutationError(f"cannot create Accord storage {root}: {error}") from error


def start_work(
    cwd: Path,
    task: str,
    agreement_source: Path,
    actor: str,
    summary: str,
) -> Path:
    """Store an accepted agreement and start event as one task creation."""
    if actor != "human":
        raise MutationError("start events record the human's acceptance")
    agreement = markdown_bytes(agreement_source, "accepted agreement")

    event = {
        "ts": timestamp(),
        "task": task,
        "schema": "1",
        "type": "start",
        "actor": actor,
        "summary": summary,
        "refs": ["agreement.md"],
    }
    validate_new_event(event)

    with locked_project(cwd):
        root = accord_root_for(cwd)
        target = task_directory(root, task)
        if target is None:
            raise MutationError(f"invalid task ID: {task!r}")
        require_safe_root(root)
        if target.exists() or target.is_symlink():
            raise MutationError(
                f"{task!r}: Accord work already exists for this project"
            )
        temporary = Path(tempfile.mkdtemp(prefix=f".{task}.", dir=root))
        try:
            sync_file(temporary / "agreement.md", agreement)
            sync_file(temporary / "record.jsonl", event_bytes(event))
            sync_directory(temporary)
            if target.exists() or target.is_symlink():
                raise MutationError(
                    f"{task!r}: Accord work already exists for this project"
                )
            try:
                os.rename(temporary, target)
            except OSError as error:
                raise MutationError(
                    f"cannot create Accord work {target}: {error}"
                ) from error
            sync_directory(root)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    return target


@contextmanager
def append_handle(path: Path) -> Iterator[BinaryIO]:
    """Open one regular file for append without following its final path."""
    flags = os.O_RDWR | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        raise MutationError(f"cannot open stored file {path}: {error}") from error
    handle = os.fdopen(descriptor, "r+b", buffering=0)
    try:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise MutationError(f"stored file is not regular: {path}")
        yield handle
    finally:
        handle.close()


def safe_task_directory(cwd: Path, task: str) -> tuple[Path, Path]:
    """Return one safe active task and its record path."""
    root = accord_root_for(cwd)
    task_dir = task_directory(root, task)
    if task_dir is None:
        raise MutationError(f"invalid task ID: {task!r}")
    if task_dir.is_symlink() or not task_dir.is_dir():
        raise MutationError(f"{task!r}: no safe active work found for this project")
    unsafe = symlink_component_below(accord_home(), task_dir)
    if unsafe is not None:
        raise MutationError(f"Accord storage contains a symlink at {unsafe}")
    record_path = task_dir / "record.jsonl"
    if record_path.is_symlink() or not record_path.is_file():
        raise MutationError(f"record is missing or unsafe: {record_path}")
    return task_dir, record_path


def require_open_record(handle: BinaryIO, path: Path, task: str) -> bytes:
    """Validate locked history and require that it remains open."""
    handle.seek(0)
    raw = handle.read()
    try:
        record = parse_record_bytes(path, raw)
    except RecordError as error:
        raise MutationError(str(error)) from error
    if any(item.get("task") != task for item in record.events):
        raise MutationError(f"{path}: record events do not name {task!r}")
    if record.closed:
        raise MutationError(
            f"{task!r}: record is closed by {record.last_event['type']!r}"
        )
    return raw


def append_event(cwd: Path, task: str, event: dict[str, Any]) -> Path:
    """Validate history and append one complete event without rewriting it."""
    if event.get("task") != task:
        raise MutationError(f"event does not name task {task!r}")
    if event.get("type") == "start":
        raise MutationError("start events are created only by `accord start`")
    validate_new_event(event)
    payload = event_bytes(event)
    with locked_project(cwd):
        _, record_path = safe_task_directory(cwd, task)
        with append_handle(record_path) as handle:
            raw = require_open_record(handle, record_path, task)
            separator = b"\n" if raw and not raw.endswith((b"\n", b"\r")) else b""
            try:
                write_all(handle.fileno(), separator + payload)
                os.fsync(handle.fileno())
            except OSError as error:
                raise MutationError(
                    f"cannot append to {record_path}: {error}"
                ) from error
    return record_path


def safe_document_name(name: str) -> str:
    """Require a direct Markdown filename."""
    if (
        not name
        or name in {".", ".."}
        or "/" in name
        or "\\" in name
        or "\x00" in name
        or not name.endswith(".md")
    ):
        raise MutationError(f"document name must be one Markdown filename: {name!r}")
    return name


def atomic_create(path: Path, content: bytes, task_dir: Path) -> None:
    """Create a file atomically without replacing an existing document."""
    unsafe = symlink_component_below(task_dir, path.parent)
    if unsafe is not None:
        raise MutationError(f"document directory contains a symlink at {unsafe}")
    if path.parent.exists():
        if path.parent.is_symlink() or not path.parent.is_dir():
            raise MutationError(f"document directory is unsafe: {path.parent}")
    else:
        try:
            path.parent.mkdir()
        except OSError as error:
            raise MutationError(
                f"cannot create document directory {path.parent}: {error}"
            ) from error
    if path.parent.is_symlink():
        raise MutationError(f"document directory is unsafe: {path.parent}")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        with temporary.open("wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as error:
            raise MutationError(f"document already exists: {path}") from error
        except OSError as error:
            raise MutationError(f"cannot store document {path}: {error}") from error
        sync_directory(path.parent)
    finally:
        temporary.unlink(missing_ok=True)


def store_document(
    cwd: Path,
    task: str,
    kind: str,
    source: Path,
    name: str | None = None,
) -> tuple[Path, str]:
    """Store one durable Markdown document and return its record reference."""
    content = markdown_bytes(source, "document")
    filename = safe_document_name(name or source.name)
    if kind == "report":
        relative = PurePosixPath("reports") / filename
    elif kind == "diagram":
        relative = PurePosixPath("diagrams") / filename
    elif kind == "learning-note":
        if not filename.startswith("learning"):
            raise MutationError("learning-note filenames must begin with 'learning'")
        relative = PurePosixPath(filename)
    else:
        raise MutationError(f"unknown document kind: {kind!r}")
    with locked_project(cwd):
        task_dir, record_path = safe_task_directory(cwd, task)
        destination = task_dir.joinpath(*relative.parts)
        with append_handle(record_path) as handle:
            require_open_record(handle, record_path, task)
            atomic_create(destination, content, task_dir)
    return destination, relative.as_posix()


def append_agreement(cwd: Path, task: str, source: Path) -> Path:
    """Append one accepted amendment without replacing the agreement."""
    content = markdown_bytes(source, "amendment")
    suffix = b"" if content.endswith(b"\n") else b"\n"
    with locked_project(cwd):
        task_dir, record_path = safe_task_directory(cwd, task)
        agreement = task_dir / "agreement.md"
        if agreement.is_symlink() or not agreement.is_file():
            raise MutationError(f"agreement is missing or unsafe: {agreement}")
        with append_handle(record_path) as record_handle:
            require_open_record(record_handle, record_path, task)
            with append_handle(agreement) as agreement_handle:
                try:
                    write_all(agreement_handle.fileno(), b"\n\n" + content + suffix)
                    os.fsync(agreement_handle.fileno())
                except OSError as error:
                    raise MutationError(
                        f"cannot append to {agreement}: {error}"
                    ) from error
    return agreement
