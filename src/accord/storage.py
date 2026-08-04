"""Resolve Accord's per-user, per-project record storage."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


def project_root(cwd: Path) -> Path:
    """Return the enclosing Git worktree, or the supplied directory itself."""
    current = cwd.expanduser().resolve()
    if not current.is_dir():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate
    return current


def project_key(root: Path) -> str:
    """Create the existing readable, collision-resistant project identifier."""
    resolved = root.expanduser().resolve()
    name = re.sub(r"[^a-z0-9]+", "-", resolved.name.lower()).strip("-")
    digest = hashlib.sha256(str(resolved).encode()).hexdigest()[:12]
    return f"{name or 'project'}-{digest}"


def accord_home() -> Path:
    """Return the hidden per-user home for every Accord record."""
    return Path.home() / ".accord"


def accord_root_for(cwd: Path) -> Path:
    """Return active record storage for the project containing ``cwd``."""
    return accord_home() / "projects" / project_key(project_root(cwd))


def accord_archive_root_for(cwd: Path) -> Path:
    """Return archived record storage for the project containing ``cwd``."""
    return accord_home() / "archive" / "projects" / project_key(project_root(cwd))


def accord_projects_root() -> Path:
    """Return the global active-project storage root."""
    return accord_home() / "projects"


def accord_archived_projects_root() -> Path:
    """Return the global archived-project storage root."""
    return accord_home() / "archive" / "projects"


def task_directory(root: Path, task: str) -> Path | None:
    """Resolve a task ID to one direct child without accepting path syntax."""
    if not task or task in {".", ".."} or "/" in task or "\\" in task or "\x00" in task:
        return None
    return root / task


def symlink_component_below(base: Path, target: Path) -> Path | None:
    """Return the first symlink below a logical storage root."""
    if base.is_symlink():
        return base
    try:
        relative = target.relative_to(base)
    except ValueError:
        return target
    current = base
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            return current
    return None
