"""Read-only terminal presentation for Accord's global record catalogue."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Callable

import urwid

from .catalog import (
    Catalog,
    DocumentView,
    ProjectView,
    WorkView,
    global_catalog,
    read_work,
    reference_problem,
)
from .work import WorkError, WorkSummary


PALETTE = [
    ("header", "white,bold", "dark blue"),
    ("title", "light cyan,bold", ""),
    ("muted", "dark gray", ""),
    ("selected", "black", "light cyan"),
    ("error", "light red,bold", ""),
    ("status", "light green,bold", ""),
    ("actor-human", "light green", ""),
    ("actor-agent", "light cyan", ""),
    ("actor-supporting", "yellow", ""),
]


NAVIGATION_KEYS = {
    "up",
    "down",
    "page up",
    "page down",
    "home",
    "end",
    "j",
    "k",
    "g",
    "G",
}


@dataclass(frozen=True)
class DetailItem:
    """One selectable section in a work's detail view."""

    kind: str
    label: str
    value: Any = None
    identity: str = ""


class NavigationEntry(urwid.WidgetWrap):
    """A text-labelled, keyboard-selectable navigation row."""

    def __init__(self, label: str, payload: Any = None) -> None:
        self.payload = payload
        self.label = label
        self._text = urwid.Text(label, wrap="any")
        super().__init__(
            urwid.AttrMap(urwid.Padding(self._text, left=1), None, "selected")
        )

    def selectable(self) -> bool:
        return True

    def keypress(self, size: tuple[int, ...], key: str) -> str | None:
        return key


class AccordApp(urwid.WidgetWrap):
    """A small three-level browser: projects, work, then record details."""

    def __init__(self) -> None:
        self.catalog: Catalog = global_catalog()
        self.mode = "projects"
        self.project: ProjectView | None = None
        self.work_summary: WorkSummary | None = None
        self.work_view: WorkView | None = None
        self.nav_list: urwid.ListBox
        self.detail_list: urwid.ListBox
        self.columns: urwid.Columns
        self.detail_focused = False
        self._header = urwid.Text("")
        self._footer = urwid.Text("")
        super().__init__(urwid.Frame(urwid.Text("Loading Accord…")))
        self._show_projects()

    def _set_frame(
        self,
        title: str,
        nav_title: str,
        entries: list[NavigationEntry],
        detail_title: str,
        detail_lines: list[str],
    ) -> None:
        if not entries:
            entries = [NavigationEntry("[EMPTY] Nothing to show")]
        self.nav_list = urwid.ListBox(urwid.SimpleFocusListWalker(entries))
        self.detail_list = self._text_list(detail_lines)
        self.columns = urwid.Columns(
            [
                ("weight", 2, urwid.LineBox(self.nav_list, title=nav_title)),
                ("weight", 5, urwid.LineBox(self.detail_list, title=detail_title)),
            ],
            dividechars=1,
        )
        self.detail_focused = False
        self._header.set_text(("header", f" Accord — {title} "))
        self._footer.set_text(
            " ↑/↓ or j/k navigate   Enter open   Tab focus detail   Esc back   "
            "r refresh   q quit"
        )
        self._w.body = self.columns
        self._w.header = urwid.Padding(self._header, left=0, right=0)
        self._w.footer = urwid.Padding(self._footer, left=1, right=1)

    @staticmethod
    def _text_list(lines: list[str]) -> urwid.ListBox:
        widgets: list[urwid.Widget] = []
        for line in lines or ["[EMPTY] No readable content"]:
            widgets.append(urwid.Text(line, wrap="any"))
        return urwid.ListBox(urwid.SimpleFocusListWalker(widgets))

    @staticmethod
    def _work_label(summary: WorkSummary) -> str:
        problem = " [ERROR]" if summary.problem else ""
        return (
            f"[{summary.storage.upper()}] [{summary.state.upper()}] "
            f"{summary.task} — {summary.event_count} events{problem}"
        )

    @staticmethod
    def _project_label(project: ProjectView) -> str:
        problem = f" [ERRORS {len(project.problems)}]" if project.problems else ""
        return (
            f"{project.display_name} — active {len(project.active)}, "
            f"archived {len(project.archived)}{problem}"
        )

    def _show_projects(self, focus_key: str | None = None) -> None:
        self.mode = "projects"
        self.project = None
        self.work_summary = None
        self.work_view = None
        entries: list[NavigationEntry] = [
            NavigationEntry(
                f"[ERROR] {problem.text()}",
                DetailItem("problem", problem.message, problem),
            )
            for problem in self.catalog.problems
        ]
        entries.extend(
            NavigationEntry(self._project_label(project), project)
            for project in self.catalog.projects
        )
        lines = [
            "Global Accord catalogue",
            "",
            "Projects are identified by their stored project key.",
            "The launch directory does not limit this view.",
            "",
            f"Projects: {len(self.catalog.projects)}",
            f"Storage errors: {len(self.catalog.problems)}",
        ]
        if self.catalog.problems:
            lines.extend(["", "Errors remain visible in the project list."])
        self._set_frame("Projects", "Projects", entries, "Account", lines)
        if focus_key is not None:
            self._focus(
                lambda item: isinstance(item, ProjectView) and item.key == focus_key
            )

    def _show_work(
        self,
        focus_task: str | None = None,
        focus_storage: str | None = None,
    ) -> None:
        if self.project is None:
            self._show_projects()
            return
        self.mode = "work"
        self.work_summary = None
        self.work_view = None
        entries = [
            NavigationEntry(self._work_label(summary), summary)
            for summary in self.project.work
        ]
        lines = self._project_detail(self.project)
        self._set_frame(
            f"Project {self.project.key}",
            "Work",
            entries,
            "Project",
            lines,
        )
        if focus_task is not None:
            self._focus(
                lambda item: (
                    isinstance(item, WorkSummary)
                    and item.task == focus_task
                    and (focus_storage is None or item.storage == focus_storage)
                )
            )

    def _show_detail(self, focus_identity: str | None = None) -> None:
        if self.work_summary is None:
            self._show_work()
            return
        self.mode = "detail"
        self.work_view = read_work(self.work_summary)
        items = self._detail_items(self.work_view)
        entries = [NavigationEntry(item.label, item) for item in items]
        selected = focus_identity or (items[0].identity if items else "")
        self._set_frame(
            f"{self.work_summary.task} — {self.work_summary.storage}",
            "Record and documents",
            entries,
            "Details",
            self._detail_lines(items[0] if items else None),
        )
        self._focus(
            lambda item: isinstance(item, DetailItem) and item.identity == selected
        )
        self._update_detail()

    @staticmethod
    def _project_detail(project: ProjectView) -> list[str]:
        lines = [
            f"Project key: {project.key}",
            f"Display label: {project.display_name}",
            "",
            f"Active work: {len(project.active)}",
            f"Archived work: {len(project.archived)}",
        ]
        if project.problems:
            lines.extend(["", "Errors:"])
            lines.extend(f"[ERROR] {problem.text()}" for problem in project.problems)
        if not project.work:
            lines.extend(["", "This project has no readable work entries."])
        else:
            lines.extend(["", "Select work and press Enter to inspect its record."])
        return lines

    @staticmethod
    def _detail_items(work: WorkView) -> list[DetailItem]:
        items = [DetailItem("overview", "[OVERVIEW] Work summary", identity="overview")]
        if work.record_problem:
            items.append(
                DetailItem(
                    "problem",
                    "[ERROR] record.jsonl",
                    work.record_problem,
                    "record-error",
                )
            )
        for index, event in enumerate(work.events, 1):
            actor = event.get("actor", "unknown")
            event_type = event.get("type", "unknown")
            summary = str(event.get("summary", ""))
            items.append(
                DetailItem(
                    "event",
                    f"[{index:03d}] [{actor}] {event_type}: {summary}",
                    (index, event),
                    f"event-{index}",
                )
            )
        documents = [work.agreement, *work.documents]
        for document in documents:
            prefix = (
                "[ERROR] " if document.problem else f"[{document.category.upper()}] "
            )
            items.append(
                DetailItem(
                    "document",
                    f"{prefix}{document.name}",
                    document,
                    f"document-{document.category}-{document.name}",
                )
            )
        return items

    def _detail_lines(self, item: DetailItem | None) -> list[str]:
        if item is None or self.work_view is None:
            return ["No readable detail is selected."]
        if item.kind == "overview":
            return self._work_detail(self.work_view)
        if item.kind == "problem":
            return ["[ERROR] The stored record could not be read.", "", str(item.value)]
        if item.kind == "event":
            index, event = item.value
            return self._event_detail(self.work_view, index, event)
        if item.kind == "document":
            return self._document_detail(item.value)
        return ["[ERROR] Unknown detail type."]

    @staticmethod
    def _work_detail(work: WorkView) -> list[str]:
        summary = work.summary
        lines = [
            f"Project key: {summary.path.parent.name}",
            f"Task: {summary.task}",
            f"Storage: {summary.storage}",
            f"State: {summary.state.upper()}",
            f"Events: {len(work.events)}",
        ]
        if work.record:
            last = work.record.last_event or {}
            lines.extend(
                [
                    f"Last event: {last.get('type', 'unknown')}",
                    f"Last timestamp: {last.get('ts', 'unknown')}",
                    f"Closed by: {last.get('type') if work.record.closed else 'none'}",
                ]
            )
        if summary.problem:
            lines.extend(["", f"[ERROR] {summary.problem}"])
        if work.record_problem:
            lines.extend(["", f"[ERROR] {work.record_problem}"])
        if work.agreement.problem:
            lines.extend(["", f"[ERROR] {work.agreement.problem}"])
        lines.extend(
            [
                "",
                "Events are shown in append order.",
                "Select an event or document to inspect its stored contents.",
            ]
        )
        return lines

    @staticmethod
    def _event_detail(work: WorkView, index: int, event: dict[str, Any]) -> list[str]:
        lines = [
            f"Event {index}",
            "",
        ]
        for key, value in event.items():
            if key == "refs":
                lines.append("refs:")
                for reference in value:
                    problem = reference_problem(work, reference)
                    suffix = f" [ERROR: {problem}]" if problem else ""
                    lines.append(f"  - {reference}{suffix}")
            else:
                rendered = json.dumps(value, ensure_ascii=False)
                lines.append(f"{key}: {rendered}")
        return lines

    @staticmethod
    def _document_detail(document: DocumentView) -> list[str]:
        if document.problem:
            return [
                f"[ERROR] {document.category}: {document.name}",
                "",
                document.problem,
            ]
        content = document.content or ""
        return [
            f"{document.category}: {document.name}",
            "",
            *content.splitlines(),
        ]

    @staticmethod
    def _summary_detail(summary: WorkSummary) -> list[str]:
        lines = [
            f"Task: {summary.task}",
            f"Storage: {summary.storage}",
            f"State: {summary.state.upper()}",
            f"Events: {summary.event_count}",
            f"Last event: {summary.last_type or 'unknown'}",
            f"Last timestamp: {summary.last_timestamp or 'unknown'}",
        ]
        if summary.problem:
            lines.extend(["", f"[ERROR] {summary.problem}"])
        lines.extend(["", "Press Enter to inspect the stored record and documents."])
        return lines

    def _selected_payload(self) -> Any:
        focus = self.nav_list.focus
        return getattr(focus, "payload", None) if focus is not None else None

    def _focus(self, predicate: Callable[[Any], bool]) -> None:
        for index, widget in enumerate(self.nav_list.body):
            if predicate(getattr(widget, "payload", None)):
                self.nav_list.set_focus(index)
                return

    def _update_detail(self) -> None:
        if self.mode != "detail":
            return
        payload = self._selected_payload()
        if isinstance(payload, DetailItem):
            self._replace_detail(self._detail_lines(payload))

    def _update_selection_detail(self) -> None:
        payload = self._selected_payload()
        if self.mode == "projects":
            if isinstance(payload, ProjectView):
                self._replace_detail(self._project_detail(payload), "Account")
            elif isinstance(payload, DetailItem):
                self._replace_detail(["[ERROR]", "", str(payload.value)], "Account")
        elif self.mode == "work" and isinstance(payload, WorkSummary):
            self._replace_detail(self._summary_detail(payload), "Project")
        elif self.mode == "detail":
            self._update_detail()

    def _replace_detail(self, lines: list[str], title: str = "Details") -> None:
        self.detail_list = self._text_list(lines)
        options = self.columns.contents[1][1]
        self.columns.contents[1] = (
            urwid.LineBox(self.detail_list, title=title),
            options,
        )

    def _activate(self) -> None:
        payload = self._selected_payload()
        if self.mode == "projects" and isinstance(payload, ProjectView):
            self.project = payload
            self._show_work()
        elif self.mode == "work" and isinstance(payload, WorkSummary):
            self.work_summary = payload
            self._show_detail()

    def _back(self) -> None:
        if self.mode == "detail":
            self._show_work(
                self.work_summary.task if self.work_summary else None,
                self.work_summary.storage if self.work_summary else None,
            )
        elif self.mode == "work":
            self._show_projects(self.project.key if self.project else None)

    def _move(self, size: tuple[int, ...], key: str) -> None:
        movement = {
            "j": "down",
            "k": "up",
            "g": "home",
            "G": "end",
        }.get(key, key)
        if self.detail_focused:
            self.detail_list.keypress(size, movement)
        else:
            self.nav_list.keypress(size, movement)
            self._update_selection_detail()

    def refresh(self) -> None:
        payload = self._selected_payload()
        project_key = self.project.key if self.project else None
        task = self.work_summary.task if self.work_summary else None
        storage = self.work_summary.storage if self.work_summary else None
        if self.mode == "projects" and isinstance(payload, ProjectView):
            project_key = payload.key
        if self.mode == "work" and isinstance(payload, WorkSummary):
            task = payload.task
            storage = payload.storage
        detail_identity: str | None = None
        if self.mode == "detail":
            if isinstance(payload, DetailItem):
                detail_identity = payload.identity
        self.catalog = global_catalog()
        if self.mode == "projects":
            self._show_projects(project_key)
            return
        project = next(
            (item for item in self.catalog.projects if item.key == project_key), None
        )
        if project is None:
            self._show_projects()
            return
        self.project = project
        if self.mode == "work":
            self._show_work(task, storage)
            return
        summary = next(
            (
                item
                for item in project.work
                if item.task == task and item.storage == storage
            ),
            None,
        )
        if summary is None:
            self._show_work()
            return
        self.work_summary = summary
        self._show_detail(detail_identity)

    def keypress(self, size: tuple[int, ...], key: str) -> str | None:
        if key in {"q", "Q"}:
            raise urwid.ExitMainLoop()
        if key in {"r", "R"}:
            self.refresh()
            return None
        if key == "tab":
            self.detail_focused = not self.detail_focused
            self.columns.set_focus(1 if self.detail_focused else 0)
            return None
        if key in {"esc", "left"}:
            self._back()
            return None
        if key in {"enter", "right"} and not self.detail_focused:
            self._activate()
            return None
        if key in NAVIGATION_KEYS:
            self._move(size, key)
            return None
        return self._w.keypress(size, key)


def run_tui() -> int:
    """Run the terminal application without creating or changing storage."""
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise WorkError("accord serve requires an interactive terminal")
    app = AccordApp()
    urwid.MainLoop(app, palette=PALETTE).run()
    return 0
