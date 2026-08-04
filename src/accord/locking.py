"""Serialize task mutations and moves on one stable project lock."""

from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, Iterator

from .storage import accord_home, project_key, project_root, symlink_component_below


class LockError(Exception):
    """Accord cannot establish a trustworthy project mutation lock."""


@contextmanager
def locked_project(cwd: Path) -> Iterator[None]:
    """Hold the stable lock shared by all mutations for one project."""
    home = accord_home()
    lock_root = home / "locks"
    unsafe = symlink_component_below(home, lock_root)
    if unsafe is not None:
        raise LockError(f"Accord lock storage contains a symlink at {unsafe}")
    try:
        lock_root.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise LockError(
            f"cannot create Accord lock storage {lock_root}: {error}"
        ) from error
    unsafe = symlink_component_below(home, lock_root)
    if unsafe is not None:
        raise LockError(f"Accord lock storage contains a symlink at {unsafe}")

    lock_path = lock_root / f"{project_key(project_root(cwd))}.lock"
    if lock_path.is_symlink():
        raise LockError(f"Accord project lock is a symlink: {lock_path}")
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as error:
        raise LockError(
            f"cannot open Accord project lock {lock_path}: {error}"
        ) from error
    try:
        handle: BinaryIO = os.fdopen(descriptor, "r+b", buffering=0)
    except (OSError, ValueError) as error:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise LockError(
            f"cannot use Accord project lock {lock_path}: {error}"
        ) from error
    acquired = False
    operation_failed = False
    try:
        try:
            details = os.fstat(handle.fileno())
            if not stat.S_ISREG(details.st_mode):
                raise LockError(
                    f"Accord project lock is not a regular file: {lock_path}"
                )
            if details.st_size == 0:
                if handle.write(b"\0") != 1:
                    raise LockError(
                        f"cannot initialize Accord project lock {lock_path}"
                    )
                handle.flush()
                os.fsync(handle.fileno())
            if os.name == "nt":
                import msvcrt

                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            else:
                import fcntl

                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        except LockError:
            raise
        except (ImportError, OSError, ValueError) as error:
            raise LockError(
                f"cannot acquire Accord project lock {lock_path}: {error}"
            ) from error
        acquired = True
        yield
    except BaseException:
        operation_failed = True
        raise
    finally:
        release_error: BaseException | None = None
        try:
            try:
                if acquired and os.name == "nt":
                    import msvcrt

                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                elif acquired:
                    import fcntl

                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            except (ImportError, OSError, ValueError) as error:
                release_error = error
        finally:
            try:
                handle.close()
            except (OSError, ValueError) as error:
                release_error = release_error or error
        if release_error is not None and not operation_failed:
            raise LockError(
                f"cannot release Accord project lock {lock_path}: {release_error}"
            ) from release_error
