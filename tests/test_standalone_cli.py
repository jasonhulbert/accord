#!/usr/bin/env python3
"""Focused contracts for the standalone CLI boundary."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "existing-work"
PLUGIN_ROOT = REPO_ROOT / "plugins" / "accord"
SKILLS = PLUGIN_ROOT / "skills"


class StandaloneCliTests(unittest.TestCase):
    """Prove the standalone CLI and thin plugin boundary."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.build_directory = tempfile.TemporaryDirectory()
        build_root = Path(cls.build_directory.name)
        source = build_root / "source"
        source.mkdir()
        shutil.copy2(REPO_ROOT / "pyproject.toml", source / "pyproject.toml")
        shutil.copy2(REPO_ROOT / "README.md", source / "README.md")
        shutil.copytree(REPO_ROOT / "src", source / "src")
        wheels = build_root / "wheels"
        wheels.mkdir()
        built = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-build-isolation",
                "--no-deps",
                "--wheel-dir",
                str(wheels),
                str(source),
            ],
            text=True,
            capture_output=True,
        )
        if built.returncode != 0:
            raise RuntimeError(f"could not build standalone wheel:\n{built.stderr}")
        cls.wheel = next(wheels.glob("*.whl"))
        cls.environment = build_root / "venv"
        venv.EnvBuilder(with_pip=True).create(cls.environment)
        cls.executable = (
            cls.environment / ("Scripts" if os.name == "nt" else "bin") / "accord"
        )
        pip = cls.environment / ("Scripts" if os.name == "nt" else "bin") / "pip"
        installed = subprocess.run(
            [str(pip), "install", "--no-deps", str(cls.wheel)],
            text=True,
            capture_output=True,
        )
        if installed.returncode != 0:
            raise RuntimeError(
                f"could not install standalone wheel:\n{installed.stderr}"
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.build_directory.cleanup()

    def project(self, root: Path) -> tuple[Path, Path, dict[str, str]]:
        project = root / "project"
        home = root / "home"
        project.mkdir()
        home.mkdir()
        (project / ".git").mkdir()
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        environment.pop("PYTHONPATH", None)
        return project, home, environment

    def run_cli(
        self,
        project: Path,
        environment: dict[str, str],
        *arguments: str,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(self.executable), *arguments],
            cwd=project,
            env=environment,
            text=True,
            capture_output=True,
        )

    def snapshot(self, directory: Path) -> dict[str, bytes]:
        return {
            str(path.relative_to(directory)): path.read_bytes()
            for path in sorted(directory.rglob("*"))
            if path.is_file()
        }

    def test_installed_cli_runs_without_a_repository_or_plugin_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            result = self.run_cli(project, environment, "version", "--json")

        self.assertEqual(result.returncode, 0, result.stderr)
        version = json.loads(result.stdout)
        self.assertEqual(version["agent_protocol"], "1")
        self.assertIn("context", version["commands"])

    def test_distribution_carries_the_current_record_schema(self):
        with zipfile.ZipFile(self.wheel) as archive:
            names = set(archive.namelist())
            schema_name = next(
                name
                for name in names
                if name.endswith("accord/resources/record.schema.json")
            )
            schema = json.loads(archive.read(schema_name))

        self.assertEqual(schema["properties"]["schema"]["const"], "1")
        self.assertEqual(
            set(schema["properties"]["type"]["enum"]),
            {
                "start",
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
            },
        )
        self.assertEqual(
            set(schema["properties"]["actor"]["enum"]),
            {"human", "agent", "supporting-agent", "investigator"},
        )
        conditional_fields = {
            clause["if"]["properties"]["type"]["const"]: set(clause["then"]["required"])
            for clause in schema["allOf"]
        }
        self.assertEqual(
            conditional_fields,
            {
                "attempt": {"outcome"},
                "question": {"subject"},
                "direction": {"decision"},
            },
        )

    def test_location_preserves_the_existing_project_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, environment = self.project(root)
            nested = project / "nested"
            nested.mkdir()
            result = self.run_cli(nested, environment, "location", "--json")
            identity = hashlib.sha256(str(project.resolve()).encode()).hexdigest()[:12]

        self.assertEqual(result.returncode, 0, result.stderr)
        location = json.loads(result.stdout)
        key = f"project-{identity}"
        self.assertEqual(location["project_root"], str(project.resolve()))
        self.assertEqual(location["active"], str(home / ".accord" / "projects" / key))
        self.assertEqual(
            location["archived"],
            str(home / ".accord" / "archive" / "projects" / key),
        )

    def test_context_reads_existing_work_without_changing_a_byte(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            location = json.loads(
                self.run_cli(project, environment, "location", "--json").stdout
            )
            task = Path(location["active"]) / "existing-work"
            shutil.copytree(FIXTURE, task)
            before = {
                path.relative_to(task): path.read_bytes()
                for path in task.rglob("*")
                if path.is_file()
            }

            result = self.run_cli(
                project, environment, "context", "existing-work", "--json"
            )
            after = {
                path.relative_to(task): path.read_bytes()
                for path in task.rglob("*")
                if path.is_file()
            }

        self.assertEqual(result.returncode, 0, result.stderr)
        context = json.loads(result.stdout)
        expected_events = [
            json.loads(line)
            for line in (FIXTURE / "record.jsonl").read_text().splitlines()
            if line
        ]
        self.assertEqual(before, after)
        self.assertEqual(context["events"], expected_events)
        self.assertEqual(
            context["agreement"]["content"],
            (FIXTURE / "agreement.md").read_text(),
        )
        for kind, relative in (
            ("reports", "reports/progress.md"),
            ("learning_notes", "learning-context.md"),
            ("diagrams", "diagrams/current-shape.md"),
        ):
            self.assertEqual(
                context["documents"][kind][0]["content"],
                (FIXTURE / relative).read_text(),
            )

    def test_start_and_append_preserve_history_and_terminal_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nThe human accepted this work.\n")
            started = self.run_cli(
                project,
                environment,
                "start",
                "new-work",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
                "--json",
            )
            record = Path(json.loads(started.stdout)["record"])
            original = record.read_bytes()
            appended = self.run_cli(
                project,
                environment,
                "append",
                "new-work",
                "note",
                "--actor",
                "agent",
                "--summary",
                "The implementation began.",
            )
            after_append = record.read_bytes()
            invalid = self.run_cli(
                project,
                environment,
                "append",
                "new-work",
                "attempt",
                "--actor",
                "agent",
                "--summary",
                "An outcome was omitted.",
            )
            after_invalid = record.read_bytes()
            completed = self.run_cli(
                project,
                environment,
                "append",
                "new-work",
                "completion",
                "--actor",
                "agent",
                "--summary",
                "The agent recorded the human's approval of completion.",
            )
            closed = record.read_bytes()
            stored_agreement = record.parent / "agreement.md"
            agreement_after_close = stored_agreement.read_bytes()
            report = root / "late-report.md"
            report.write_text("# Late report\n\nThis must not be stored.\n")
            refused_document = self.run_cli(
                project,
                environment,
                "document",
                "new-work",
                "report",
                "--file",
                str(report),
            )
            amendment = root / "late-amendment.md"
            amendment.write_text("### Late amendment\n\nThis must not be appended.\n")
            refused_amendment = self.run_cli(
                project,
                environment,
                "amend",
                "new-work",
                "--file",
                str(amendment),
            )
            report_stored = (record.parent / "reports" / report.name).exists()
            agreement_after_refusal = stored_agreement.read_bytes()
            refused = self.run_cli(
                project,
                environment,
                "append",
                "new-work",
                "note",
                "--actor",
                "agent",
                "--summary",
                "This must not be appended.",
            )
            after_refused = record.read_bytes()

        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertEqual(appended.returncode, 0, appended.stderr)
        self.assertTrue(after_append.startswith(original))
        self.assertEqual(invalid.returncode, 2)
        self.assertEqual(after_invalid, after_append)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(refused_document.returncode, 2)
        self.assertFalse(report_stored)
        self.assertEqual(refused_amendment.returncode, 2)
        self.assertEqual(agreement_after_refusal, agreement_after_close)
        self.assertEqual(refused.returncode, 2)
        self.assertIn("record is closed", refused.stderr)
        self.assertEqual(after_refused, closed)

    def test_append_separates_an_existing_record_without_a_final_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            location = json.loads(
                self.run_cli(project, environment, "location", "--json").stdout
            )
            task = Path(location["active"]) / "existing-work"
            shutil.copytree(FIXTURE, task)
            record = task / "record.jsonl"
            original = record.read_bytes().rstrip(b"\n")
            record.write_bytes(original)

            result = self.run_cli(
                project,
                environment,
                "append",
                "existing-work",
                "note",
                "--actor",
                "agent",
                "--summary",
                "The existing history remained distinct.",
            )
            changed = record.read_bytes()

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(changed.startswith(original + b"\n"))
        self.assertEqual(len(changed.splitlines()), 5)

    def test_document_storage_refuses_symlink_escape_and_non_utf8(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nAccepted.\n")
            started = self.run_cli(
                project,
                environment,
                "start",
                "safe-documents",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
                "--json",
            )
            task = Path(json.loads(started.stdout)["path"])
            outside = root / "outside"
            outside.mkdir()
            (task / "reports").symlink_to(outside, target_is_directory=True)
            report = root / "report.md"
            report.write_text("# Report\n\nMust stay within the task.\n")
            escaped = self.run_cli(
                project,
                environment,
                "document",
                "safe-documents",
                "report",
                "--file",
                str(report),
            )
            invalid = root / "invalid.md"
            invalid.write_bytes(b"\xff\xfe")
            invalid_result = self.run_cli(
                project,
                environment,
                "amend",
                "safe-documents",
                "--file",
                str(invalid),
            )
            outside_files = list(outside.iterdir())

        self.assertEqual(escaped.returncode, 2)
        self.assertIn("symlink", escaped.stderr)
        self.assertEqual(outside_files, [])
        self.assertEqual(invalid_result.returncode, 2)
        self.assertIn("must be UTF-8", invalid_result.stderr)

    def test_project_lock_cannot_escape_accord_storage_through_a_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, environment = self.project(root)
            location = json.loads(
                self.run_cli(project, environment, "location", "--json").stdout
            )
            project_key = Path(location["active"]).name
            lock_root = home / ".accord" / "locks"
            lock_root.mkdir(parents=True)
            outside = root / "outside.lock"
            outside.write_bytes(b"outside evidence")
            (lock_root / f"{project_key}.lock").symlink_to(outside)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nAccepted.\n")

            result = self.run_cli(
                project,
                environment,
                "start",
                "symlinked-lock",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
            )
            outside_content = outside.read_bytes()

        self.assertEqual(result.returncode, 2)
        self.assertIn("project lock is a symlink", result.stderr)
        self.assertEqual(outside_content, b"outside evidence")

    def test_documents_and_amendments_stay_behind_the_cli_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nThe original accepted terms.\n")
            report = root / "progress.md"
            report.write_text("# Report\n\nEvidence for human review.\n")
            amendment = root / "amendment.md"
            amendment.write_text(
                "### Accepted amendment\n\nThe resource bound changed.\n"
            )
            started = self.run_cli(
                project,
                environment,
                "start",
                "documented-work",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
            )
            stored = self.run_cli(
                project,
                environment,
                "document",
                "documented-work",
                "report",
                "--file",
                str(report),
                "--json",
            )
            amended = self.run_cli(
                project,
                environment,
                "amend",
                "documented-work",
                "--file",
                str(amendment),
            )
            context_result = self.run_cli(
                project,
                environment,
                "context",
                "documented-work",
                "--json",
            )

        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertEqual(stored.returncode, 0, stored.stderr)
        self.assertEqual(json.loads(stored.stdout)["ref"], "reports/progress.md")
        self.assertEqual(amended.returncode, 0, amended.stderr)
        context = json.loads(context_result.stdout)
        self.assertIn("Accepted amendment", context["agreement"]["content"])
        self.assertEqual(
            context["documents"]["reports"][0]["content"],
            "# Report\n\nEvidence for human review.\n",
        )

    def test_archive_and_restore_move_closed_work_without_changing_it(self):
        for closing_type in ("completion", "end"):
            with self.subTest(closing_type=closing_type):
                with tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    project, _, environment = self.project(root)
                    agreement = root / "agreement.md"
                    agreement.write_text("# Agreement\n\nAccepted.\n")
                    started = self.run_cli(
                        project,
                        environment,
                        "start",
                        "finished-work",
                        "--agreement",
                        str(agreement),
                        "--actor",
                        "human",
                        "--summary",
                        "The human accepted the agreement.",
                        "--json",
                    )
                    task = Path(json.loads(started.stdout)["path"])
                    closed = self.run_cli(
                        project,
                        environment,
                        "append",
                        "finished-work",
                        closing_type,
                        "--actor",
                        "agent",
                        "--summary",
                        "The human directed that this work be closed.",
                    )
                    before = self.snapshot(task)

                    archived = self.run_cli(
                        project,
                        environment,
                        "archive",
                        "finished-work",
                        "--json",
                    )
                    archived_path = Path(json.loads(archived.stdout)["destination"])
                    archived_list = self.run_cli(
                        project,
                        environment,
                        "list",
                        "--json",
                    )
                    restored = self.run_cli(
                        project,
                        environment,
                        "restore",
                        "finished-work",
                        "--json",
                    )
                    active_list = self.run_cli(
                        project,
                        environment,
                        "list",
                        "--json",
                    )

                    self.assertEqual(started.returncode, 0, started.stderr)
                    self.assertEqual(closed.returncode, 0, closed.stderr)
                    self.assertEqual(archived.returncode, 0, archived.stderr)
                    archived_item = json.loads(archived_list.stdout)["work"][0]
                    self.assertEqual(archived_item["storage"], "archived")
                    self.assertEqual(archived_item["state"], "closed")
                    self.assertFalse(archived_path.exists())
                    self.assertEqual(restored.returncode, 0, restored.stderr)
                    active_item = json.loads(active_list.stdout)["work"][0]
                    self.assertEqual(active_item["storage"], "active")
                    self.assertEqual(active_item["state"], "closed")
                    self.assertEqual(self.snapshot(task), before)

    def test_forced_archive_is_explicit_and_restore_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nAccepted.\n")
            started = self.run_cli(
                project,
                environment,
                "start",
                "open-work",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
                "--json",
            )
            active = Path(json.loads(started.stdout)["path"])
            refused = self.run_cli(
                project,
                environment,
                "archive",
                "open-work",
            )
            forced = self.run_cli(
                project,
                environment,
                "archive",
                "open-work",
                "--force",
                "--json",
            )
            forced_result = json.loads(forced.stdout)
            archived = Path(forced_result["destination"])
            active.mkdir()
            marker = active / "keep.txt"
            marker.write_text("do not replace")
            collision = self.run_cli(
                project,
                environment,
                "restore",
                "open-work",
            )
            marker_content = marker.read_text()
            shutil.rmtree(active)
            archived_record = archived / "record.jsonl"
            archived_record.write_text("not-json\n")
            damaged = self.snapshot(archived)
            damaged_list = self.run_cli(
                project,
                environment,
                "list",
                "--json",
            )
            restored_damaged = self.run_cli(
                project,
                environment,
                "restore",
                "open-work",
            )
            invalid_force = self.run_cli(
                project,
                environment,
                "archive",
                "open-work",
                "--force",
            )

            self.assertEqual(started.returncode, 0, started.stderr)
            self.assertEqual(refused.returncode, 2)
            self.assertIn("nothing was archived", refused.stderr)
            self.assertEqual(forced.returncode, 0, forced.stderr)
            self.assertTrue(forced_result["forced_unclosed"])
            self.assertIn("WARNING", forced.stderr)
            self.assertEqual(collision.returncode, 2)
            self.assertIn("destination already exists", collision.stderr)
            self.assertEqual(marker_content, "do not replace")
            self.assertEqual(damaged_list.returncode, 2)
            damaged_item = json.loads(damaged_list.stdout)["work"][0]
            self.assertEqual(damaged_item["storage"], "archived")
            self.assertEqual(damaged_item["state"], "damaged")
            self.assertIsNotNone(damaged_item["problem"])
            self.assertEqual(restored_damaged.returncode, 0, restored_damaged.stderr)
            self.assertEqual(self.snapshot(active), damaged)
            self.assertEqual(invalid_force.returncode, 2)
            self.assertIn("invalid JSON", invalid_force.stderr)
            self.assertTrue(active.is_dir())
            self.assertFalse(archived.exists())

    def test_archive_refuses_links_inside_stored_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            agreement = root / "agreement.md"
            agreement.write_text("# Agreement\n\nAccepted.\n")
            started = self.run_cli(
                project,
                environment,
                "start",
                "linked-work",
                "--agreement",
                str(agreement),
                "--actor",
                "human",
                "--summary",
                "The human accepted the agreement.",
                "--json",
            )
            task = Path(json.loads(started.stdout)["path"])
            closed = self.run_cli(
                project,
                environment,
                "append",
                "linked-work",
                "completion",
                "--actor",
                "agent",
                "--summary",
                "The human directed that this work be complete.",
            )
            outside = root / "outside.md"
            outside.write_text("external evidence")
            (task / "linked.md").symlink_to(outside)

            archived = self.run_cli(
                project,
                environment,
                "archive",
                "linked-work",
            )

        self.assertEqual(started.returncode, 0, started.stderr)
        self.assertEqual(closed.returncode, 0, closed.stderr)
        self.assertEqual(archived.returncode, 2)
        self.assertIn("unsafe object", archived.stderr)

    def test_skills_use_only_the_public_cli_without_a_bundled_fallback(self):
        skill_paths = sorted(SKILLS.glob("*/SKILL.md"))
        skills = [path.read_text() for path in skill_paths]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, _, environment = self.project(root)
            version = self.run_cli(project, environment, "version", "--json")
        self.assertEqual(version.returncode, 0, version.stderr)
        public_commands = set(json.loads(version.stdout)["commands"])

        plugin_files = {
            path.relative_to(PLUGIN_ROOT).as_posix()
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual(
            plugin_files,
            {
                ".claude-plugin/plugin.json",
                ".codex-plugin/plugin.json",
                "creed/agent.md",
                "creed/human.md",
                "creed/supporting-agent.md",
                "skills/accord/SKILL.md",
                "skills/check-in/SKILL.md",
                "skills/visual-explanation/SKILL.md",
                "skills/visual-explanation/agents/openai.yaml",
                "spec/check-in.md",
                "spec/record.md",
                "templates/agreement.md",
                "templates/learning-note.md",
                "templates/report.md",
            },
        )
        self.assertEqual(len(skills), 3)
        self.assertTrue(
            any("CLI must be installed or updated" in skill for skill in skills)
        )
        self.assertTrue(
            any("write a record directly as a fallback" in skill for skill in skills)
        )
        for path, skill in zip(skill_paths, skills):
            self.assertNotIn("tools/", skill)
            self.assertNotIn("PLUGIN_ROOT", skill)
            self.assertNotIn(".codex", skill)
            self.assertNotIn(".claude", skill)
            self.assertNotIn("record.jsonl", skill)
            for command in re.findall(r"\baccord ([a-z][a-z-]*)\b", skill):
                self.assertIn(command, public_commands)
            for reference in re.findall(r"`((?:\.\./)+[^`]+)`", skill):
                target = (path.parent / reference).resolve()
                target.relative_to(PLUGIN_ROOT.resolve())
                self.assertTrue(target.is_file(), reference)


if __name__ == "__main__":
    unittest.main()
