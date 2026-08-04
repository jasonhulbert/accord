"""Read-only global discovery and navigation data for Accord work."""

from __future__ import annotations

import string
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from .records import Record, RecordError, read_record
from .storage import (
    accord_archived_projects_root,
    accord_projects_root,
)
from .work import WorkError, WorkSummary, document, safe_storage_root, work_in


@dataclass(frozen=True)
class CatalogProblem:
    """A discovery failure kept visible beside otherwise readable work."""

    storage: str
    path: Path
    message: str

    def text(self) -> str:
        return f"{self.storage} {self.path}: {self.message}"


@dataclass(frozen=True)
class DocumentView:
    """One known Markdown document or one document-level failure."""

    category: str
    name: str
    path: Path
    content: str | None
    problem: str | None = None

    @property
    def readable(self) -> bool:
        return self.content is not None and self.problem is None


@dataclass(frozen=True)
class ProjectView:
    """All work found under one exact stored project key."""

    key: str
    display_name: str
    active: tuple[WorkSummary, ...]
    archived: tuple[WorkSummary, ...]
    problems: tuple[CatalogProblem, ...] = ()

    @property
    def work(self) -> tuple[WorkSummary, ...]:
        return (*self.active, *self.archived)


@dataclass(frozen=True)
class Catalog:
    """A fresh, factual snapshot of both global Accord storage roots."""

    projects: tuple[ProjectView, ...]
    problems: tuple[CatalogProblem, ...] = ()


@dataclass(frozen=True)
class WorkView:
    """A safe work summary with its readable record and Markdown documents."""

    summary: WorkSummary
    record: Record | None
    record_problem: str | None
    agreement: DocumentView
    documents: tuple[DocumentView, ...]

    @property
    def events(self) -> tuple[dict[str, Any], ...]:
        return tuple(self.record.events) if self.record else ()

    @property
    def problem(self) -> str | None:
        return self.summary.problem or self.record_problem or self.agreement.problem


def project_display_name(key: str) -> str:
    """Format the readable key prefix while keeping the full key visible."""
    prefix, separator, digest = key.rpartition("-")
    if (
        separator
        and len(digest) == 12
        and all(character in string.hexdigits for character in digest)
    ):
        return f"{prefix} [{key}]"
    return key


def _global_roots() -> tuple[tuple[str, Path], ...]:
    return (
        ("active", accord_projects_root()),
        ("archived", accord_archived_projects_root()),
    )


def _project_entries(root: Path, storage: str) -> list[Path]:
    safe_storage_root(root, storage)
    if not root.exists():
        return []
    try:
        return sorted(root.iterdir(), key=lambda path: path.name)
    except OSError as error:
        raise WorkError(f"{storage} storage could not be read: {error}") from error


def global_catalog() -> Catalog:
    """Discover all projects without depending on the current directory."""
    grouped: dict[str, dict[str, Any]] = {}
    problems: list[CatalogProblem] = []

    for storage, root in _global_roots():
        try:
            entries = _project_entries(root, storage)
        except WorkError as error:
            problems.append(CatalogProblem(storage, root, str(error)))
            continue

        for entry in entries:
            key = entry.name
            group = grouped.setdefault(
                key,
                {"active": [], "archived": [], "problems": []},
            )
            project_problems: list[CatalogProblem] = group["problems"]
            if entry.is_symlink():
                project_problems.append(
                    CatalogProblem(storage, entry, "project directory is a symlink")
                )
                continue
            if not entry.is_dir():
                project_problems.append(
                    CatalogProblem(storage, entry, "storage entry is not a directory")
                )
                continue
            try:
                group[storage].extend(work_in(entry, storage))
            except WorkError as error:
                project_problems.append(CatalogProblem(storage, entry, str(error)))

    projects = tuple(
        ProjectView(
            key=key,
            display_name=project_display_name(key),
            active=tuple(group["active"]),
            archived=tuple(group["archived"]),
            problems=tuple(group["problems"]),
        )
        for key, group in sorted(grouped.items())
    )
    return Catalog(projects=projects, problems=tuple(problems))


def _document_view(
    path: Path,
    category: str,
    name: str,
    task_dir: Path,
) -> DocumentView:
    try:
        value = document(path, task_dir)
    except WorkError as error:
        return DocumentView(category, name, path, None, str(error))
    return DocumentView(category, name, path, value["content"])


def _directory_documents(
    directory: Path,
    category: str,
    task_dir: Path,
) -> list[DocumentView]:
    if directory.is_symlink():
        return [
            DocumentView(
                category,
                directory.name,
                directory,
                None,
                f"unsafe document directory: {directory}",
            )
        ]
    if not directory.exists():
        return []
    if not directory.is_dir():
        return [
            DocumentView(
                category,
                directory.name,
                directory,
                None,
                f"unsafe document directory: {directory}",
            )
        ]
    try:
        paths = sorted(directory.glob("*.md"), key=lambda path: path.name)
    except OSError as error:
        return [DocumentView(category, directory.name, directory, None, str(error))]
    return [_document_view(path, category, path.name, task_dir) for path in paths]


def _learning_documents(task_dir: Path) -> list[DocumentView]:
    try:
        paths = sorted(task_dir.glob("learning*.md"), key=lambda path: path.name)
    except OSError as error:
        return [
            DocumentView("learning_notes", "learning notes", task_dir, None, str(error))
        ]
    return [
        _document_view(path, "learning_notes", path.name, task_dir) for path in paths
    ]


def read_work(summary: WorkSummary) -> WorkView:
    """Load one work entry while keeping record and document errors visible."""
    task_dir = summary.path
    agreement = DocumentView(
        "agreement", "agreement.md", task_dir / "agreement.md", None, summary.problem
    )
    if task_dir.is_symlink() or not task_dir.is_dir():
        return WorkView(summary, None, summary.problem, agreement, ())

    record_problem: str | None = None
    record: Record | None = None
    try:
        record = read_record(task_dir / "record.jsonl", summary.task)
    except RecordError as error:
        record_problem = str(error)

    agreement = _document_view(
        task_dir / "agreement.md", "agreement", "agreement.md", task_dir
    )
    documents = [agreement]
    documents.extend(_directory_documents(task_dir / "reports", "reports", task_dir))
    documents.extend(_learning_documents(task_dir))
    documents.extend(_directory_documents(task_dir / "diagrams", "diagrams", task_dir))
    return WorkView(
        summary=summary,
        record=record,
        record_problem=record_problem,
        agreement=agreement,
        documents=tuple(documents[1:]),
    )


def reference_problem(work: WorkView, reference: str) -> str | None:
    """Return an error for a reference that cannot safely name this work's docs."""
    path = PurePosixPath(reference)
    if path.is_absolute() or ".." in path.parts or "\\" in reference:
        return f"unsafe reference: {reference!r}"
    task_dir = work.summary.path
    known = {
        item.path.relative_to(task_dir).as_posix()
        for item in (work.agreement, *work.documents)
        if item.readable and item.path.is_relative_to(task_dir)
    }
    if reference not in known:
        return f"reference is not a readable document in this work: {reference!r}"
    return None
