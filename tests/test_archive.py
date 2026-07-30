#!/usr/bin/env python3
"""Behavior tests for reversible archival of completed Accord work."""

from __future__ import annotations

import json
from importlib.machinery import SourceFileLoader
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = REPO_ROOT / "plugins" / "accord" / "tools" / "archive"
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


def load_archive_tool():
    loader = SourceFileLoader("accord_archive_tool", str(ARCHIVE))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise ImportError(f"cannot load {ARCHIVE}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def event(event_type: str) -> dict[str, str]:
    return {
        "ts": "2026-07-30T01:00:00Z",
        "task": "finished-work",
        "schema": "1",
        "type": event_type,
        "actor": "human" if event_type in {"start", "completion"} else "agent",
        "summary": f"The work recorded {event_type}.",
    }


class ArchiveTests(unittest.TestCase):
    def make_project(self, root: Path) -> tuple[Path, Path, Path, Path]:
        project = root / "project"
        home = root / "home"
        project.mkdir()
        home.mkdir()
        (project / ".git").mkdir()
        result = subprocess.run(
            [sys.executable, str(LOCATION), str(project)],
            text=True,
            capture_output=True,
            check=True,
            env=os.environ | {"HOME": str(home)},
        )
        active_root = Path(result.stdout.strip())
        archive_root = home / ".accord" / "archive" / "projects" / active_root.name
        return project, home, active_root, archive_root

    def write_task(
        self,
        active_root: Path,
        events: list[dict[str, str]],
        task: str = "finished-work",
    ) -> Path:
        task_dir = active_root / task
        reports = task_dir / "reports"
        diagrams = task_dir / "diagrams"
        reports.mkdir(parents=True)
        diagrams.mkdir()
        (task_dir / "agreement.md").write_bytes(b"# Agreement\n\nPreserve me.\n")
        (task_dir / "record.jsonl").write_text(
            "".join(json.dumps(item) + "\n" for item in events)
        )
        (reports / "report.md").write_bytes(b"# Report\n\nEvidence.\n")
        (diagrams / "view.md").write_bytes(b"```mermaid\ngraph LR\nA-->B\n```\n")
        return task_dir

    def run_archive(
        self,
        project: Path,
        home: Path,
        action: str,
        task: str = "finished-work",
        force: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        arguments = [action]
        if force:
            arguments.append("--force")
        arguments.append(task)
        return subprocess.run(
            [sys.executable, str(ARCHIVE), *arguments],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
            env=os.environ | {"HOME": str(home)},
        )

    def snapshot(self, directory: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(directory)): path.read_bytes()
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        }

    def test_archive_and_restore_move_the_complete_task_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            task_dir = self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            before = self.snapshot(task_dir)

            archived = self.run_archive(project, home, "archive")

            self.assertEqual(archived.returncode, 0, archived.stderr)
            self.assertFalse(task_dir.exists())
            archived_task = archive_root / "finished-work"
            self.assertEqual(self.snapshot(archived_task), before)

            restored = self.run_archive(project, home, "restore")

            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertFalse(archived_task.exists())
            self.assertEqual(self.snapshot(task_dir), before)

    def test_archive_warns_deterministically_and_keeps_incomplete_work_active(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            task_dir = self.write_task(active_root, [event("start")])

            result = self.run_archive(project, home, "archive")

            self.assertEqual(result.returncode, 2)
            self.assertEqual(
                result.stderr,
                "WARNING: 'finished-work' is not complete; "
                "nothing was archived.\n",
            )
            self.assertEqual(result.stdout, "")
            self.assertTrue(task_dir.is_dir())
            self.assertFalse((archive_root / "finished-work").exists())

    def test_force_archives_incomplete_work_with_a_deterministic_warning(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            task_dir = self.write_task(active_root, [event("start")])
            before = self.snapshot(task_dir)

            result = self.run_archive(project, home, "archive", force=True)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                result.stderr,
                "WARNING: 'finished-work' is not complete; "
                "archived because --force was provided.\n",
            )
            self.assertIn("Archived 'finished-work':", result.stdout)
            self.assertFalse(task_dir.exists())
            self.assertEqual(
                self.snapshot(archive_root / "finished-work"),
                before,
            )

    def test_force_does_not_bypass_invalid_record_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            task_dir = self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            (task_dir / "record.jsonl").write_text("not-json\n")

            result = self.run_archive(project, home, "archive", force=True)

            self.assertEqual(result.returncode, 2)
            self.assertIn("record is invalid", result.stderr)
            self.assertTrue(task_dir.is_dir())
            self.assertFalse((archive_root / "finished-work").exists())

    def test_archive_and_restore_never_merge_or_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            active_task = self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            archived_task = archive_root / "finished-work"
            archived_task.mkdir(parents=True)
            marker = archived_task / "keep.txt"
            marker.write_text("existing archive")

            archive_result = self.run_archive(project, home, "archive")

            self.assertEqual(archive_result.returncode, 2)
            self.assertIn("destination already exists", archive_result.stderr)
            self.assertTrue(active_task.is_dir())
            self.assertEqual(marker.read_text(), "existing archive")

            archived_task.rename(archive_root / "collision")
            archived_task = self.write_task(
                archive_root,
                [event("start"), event("completion")],
            )
            restore_result = self.run_archive(project, home, "restore")

            self.assertEqual(restore_result.returncode, 2)
            self.assertIn("destination already exists", restore_result.stderr)
            self.assertTrue(active_task.is_dir())
            self.assertTrue(archived_task.is_dir())

    def test_archive_rejects_task_ids_that_could_escape_the_project_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, _ = self.make_project(Path(directory))
            self.write_task(active_root, [event("start"), event("completion")])

            result = self.run_archive(project, home, "archive", "../finished-work")

            self.assertEqual(result.returncode, 2)
            self.assertIn("one path-safe name", result.stderr)
            self.assertTrue((active_root / "finished-work").is_dir())

    def test_archive_refuses_symlinks_instead_of_moving_external_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, active_root, archive_root = self.make_project(root)
            task_dir = self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            external = root / "external-report.md"
            external.write_text("outside the task")
            link = task_dir / "reports" / "external.md"
            try:
                link.symlink_to(external)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = self.run_archive(project, home, "archive")

            self.assertEqual(result.returncode, 2)
            self.assertIn("unsafe filesystem object", result.stderr)
            self.assertTrue(task_dir.is_dir())
            self.assertFalse((archive_root / "finished-work").exists())

    def test_archive_refuses_a_symlinked_archive_ancestor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, active_root, _ = self.make_project(root)
            task_dir = self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            external = root / "external-archive"
            external.mkdir()
            archive_component = home / ".accord" / "archive"
            archive_component.parent.mkdir(parents=True, exist_ok=True)
            try:
                archive_component.symlink_to(external, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = self.run_archive(project, home, "archive")

            self.assertEqual(result.returncode, 2)
            self.assertIn("destination storage contains a symlink", result.stderr)
            self.assertTrue(task_dir.is_dir())
            self.assertEqual(list(external.iterdir()), [])

    def test_restore_refuses_a_symlinked_archive_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, active_root, archive_root = self.make_project(root)
            external = root / "external-archive"
            archived_task = self.write_task(
                external / "projects" / active_root.name,
                [event("start"), event("completion")],
            )
            archive_component = home / ".accord" / "archive"
            archive_component.parent.mkdir(parents=True, exist_ok=True)
            try:
                archive_component.symlink_to(external, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"symlinks unavailable: {error}")

            result = self.run_archive(project, home, "restore")

            self.assertEqual(result.returncode, 2)
            self.assertIn("storage contains a symlink", result.stderr)
            self.assertTrue(archived_task.is_dir())
            self.assertFalse((active_root / "finished-work").exists())
            self.assertTrue(archive_root.is_dir())

    def test_archive_refuses_a_record_whose_events_name_another_task(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            task_dir = self.write_task(
                active_root,
                [event("start"), event("completion")],
                task="misnamed",
            )

            result = self.run_archive(project, home, "archive", "misnamed")

            self.assertEqual(result.returncode, 2)
            self.assertIn("every record event must name", result.stderr)
            self.assertTrue(task_dir.is_dir())
            self.assertFalse((archive_root / "misnamed").exists())

    def test_restore_recovers_damaged_archived_evidence_without_rewriting_it(self):
        with tempfile.TemporaryDirectory() as directory:
            project, home, active_root, archive_root = self.make_project(
                Path(directory)
            )
            self.write_task(
                active_root,
                [event("start"), event("completion")],
            )
            archived = self.run_archive(project, home, "archive")
            self.assertEqual(archived.returncode, 0, archived.stderr)
            archived_task = archive_root / "finished-work"
            (archived_task / "record.jsonl").write_text("damaged\n")
            damaged = self.snapshot(archived_task)

            restored = self.run_archive(project, home, "restore")

            self.assertEqual(restored.returncode, 0, restored.stderr)
            self.assertEqual(
                self.snapshot(active_root / "finished-work"),
                damaged,
            )

    def test_no_replace_move_refuses_even_an_empty_destination_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            destination = root / "destination"
            source.mkdir()
            destination.mkdir()
            module = load_archive_tool()

            with self.assertRaises(OSError):
                module.rename_without_replace(source, destination)

            self.assertTrue(source.is_dir())
            self.assertTrue(destination.is_dir())


if __name__ == "__main__":
    unittest.main()
