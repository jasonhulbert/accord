#!/usr/bin/env python3
"""Behavior tests for the stable self-service Accord launcher."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from urllib.request import urlopen


REPO_ROOT = Path(__file__).resolve().parent.parent
INSTALL = REPO_ROOT / "plugins" / "accord" / "tools" / "install-launcher"
LOCATION = REPO_ROOT / "plugins" / "accord" / "tools" / "location"


def event(summary: str) -> dict[str, str]:
    return {
        "ts": "2026-07-26T12:00:00Z",
        "task": "rate-limit",
        "schema": "1",
        "type": "note",
        "actor": "agent",
        "summary": summary,
    }


class CliTests(unittest.TestCase):
    def make_project(self, root: Path) -> tuple[Path, Path, Path]:
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
        return project, home, Path(result.stdout.strip())

    def install(self, home: Path, bin_dir: Path) -> Path:
        return self.install_from(home, bin_dir, REPO_ROOT / "plugins" / "accord")

    def install_from(self, home: Path, bin_dir: Path, plugin_root: Path) -> Path:
        result = subprocess.run(
            [
                sys.executable,
                str(plugin_root / "tools" / "install-launcher"),
                "--bin-dir",
                str(bin_dir),
            ],
            text=True,
            capture_output=True,
            env=os.environ | {"HOME": str(home)},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return bin_dir / "accord"

    def write_record(self, store: Path, summary: str) -> None:
        task = store / "rate-limit"
        task.mkdir(parents=True)
        (task / "record.jsonl").write_text(json.dumps(event(summary)) + "\n")

    def test_installer_creates_a_stable_command_outside_the_plugin_root(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, home, _ = self.make_project(root)
            bin_dir = root / "bin"
            launcher = self.install(home, bin_dir)

            self.assertTrue(launcher.is_file())
            self.assertTrue(os.access(launcher, os.X_OK))
            result = subprocess.run(
                [str(launcher), "--help"],
                cwd=root,
                text=True,
                capture_output=True,
                env=os.environ | {"HOME": str(home)},
            )

        self.assertEqual(result.returncode, 0)
        self.assertIn("accord serve", result.stdout)

    def test_installed_command_uses_the_target_project_cwd(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, store = self.make_project(root)
            self.write_record(store, "Existing work is still visible.")
            launcher = self.install(home, root / "bin")
            process = subprocess.Popen(
                [str(launcher), "serve", "--no-open", "--port", "0"],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ | {"HOME": str(home)},
            )
            self.addCleanup(self.stop, process)
            line = process.stdout.readline().strip() if process.stdout else ""

            self.assertTrue(line.startswith("Accord web view: http://127.0.0.1:"), line)
            url = line.removeprefix("Accord web view: ")
            with urlopen(url.rstrip("/") + "/task/rate-limit", timeout=3) as response:
                page = response.read().decode()

        self.assertIn("Existing work is still visible.", page)

    def test_installed_command_follows_a_newer_plugin_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, store = self.make_project(root)
            self.write_record(store, "The launcher survived the update.")

            family = root / "plugin-cache" / "accord"
            old_root = family / "0.1.0"
            new_root = family / "0.1.1"
            shutil.copytree(REPO_ROOT / "plugins" / "accord", old_root)
            shutil.copytree(REPO_ROOT / "plugins" / "accord", new_root)
            launcher = self.install_from(home, root / "bin", old_root)
            shutil.rmtree(old_root)

            process = subprocess.Popen(
                [str(launcher), "serve", "--no-open", "--port", "0"],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ | {"HOME": str(home)},
            )
            self.addCleanup(self.stop, process)
            line = process.stdout.readline().strip() if process.stdout else ""

            self.assertTrue(line.startswith("Accord web view: http://127.0.0.1:"), line)
            url = line.removeprefix("Accord web view: ")
            with urlopen(url.rstrip("/") + "/task/rate-limit", timeout=3) as response:
                page = response.read().decode()

        self.assertIn("The launcher survived the update.", page)

    def test_installed_command_prefers_newer_plugin_while_old_cache_remains(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, store = self.make_project(root)
            self.write_record(store, "The updated view is required.")

            family = root / "plugin-cache" / "accord"
            old_root = family / "0.1.9"
            new_root = family / "0.1.10"
            shutil.copytree(REPO_ROOT / "plugins" / "accord", old_root)
            shutil.copytree(REPO_ROOT / "plugins" / "accord", new_root)
            launcher = self.install_from(home, root / "bin", old_root)

            new_view = new_root / "assets" / "web" / "record.html"
            new_view.write_text(
                new_view.read_text().replace(
                    "<title>__TITLE__</title>",
                    "<title>__TITLE__</title><!-- updated-plugin-view -->",
                )
            )

            process = subprocess.Popen(
                [str(launcher), "serve", "--no-open", "--port", "0"],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ | {"HOME": str(home)},
            )
            self.addCleanup(self.stop, process)
            line = process.stdout.readline().strip() if process.stdout else ""

            self.assertTrue(line.startswith("Accord web view: http://127.0.0.1:"), line)
            url = line.removeprefix("Accord web view: ")
            with urlopen(url.rstrip("/") + "/task/rate-limit", timeout=3) as response:
                page = response.read().decode()

        self.assertIn("updated-plugin-view", page)

    def test_installed_command_skips_a_newer_incomplete_plugin(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, store = self.make_project(root)
            self.write_record(store, "A complete installation is required.")

            family = root / "plugin-cache" / "accord"
            old_root = family / "0.1.1"
            new_root = family / "0.1.2"
            shutil.copytree(REPO_ROOT / "plugins" / "accord", old_root)
            shutil.copytree(REPO_ROOT / "plugins" / "accord", new_root)
            launcher = self.install_from(home, root / "bin", old_root)

            old_view = old_root / "assets" / "web" / "record.html"
            old_view.write_text(
                old_view.read_text().replace(
                    "<title>__TITLE__</title>",
                    "<title>__TITLE__</title><!-- complete-plugin-view -->",
                )
            )
            (new_root / "assets" / "web" / "record.html").unlink()

            process = subprocess.Popen(
                [str(launcher), "serve", "--no-open", "--port", "0"],
                cwd=project,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ | {"HOME": str(home)},
            )
            self.addCleanup(self.stop, process)
            line = process.stdout.readline().strip() if process.stdout else ""

            self.assertTrue(line.startswith("Accord web view: http://127.0.0.1:"), line)
            url = line.removeprefix("Accord web view: ")
            with urlopen(url.rstrip("/") + "/task/rate-limit", timeout=3) as response:
                page = response.read().decode()

        self.assertIn("complete-plugin-view", page)
        self.assertIn("A complete installation is required.", page)

    def test_installed_command_rejects_an_incomplete_plugin_before_serving(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project, home, _ = self.make_project(root)
            plugin_root = root / "plugin-cache" / "accord" / "0.1.2"
            shutil.copytree(REPO_ROOT / "plugins" / "accord", plugin_root)
            launcher = self.install_from(home, root / "bin", plugin_root)
            (plugin_root / "assets" / "web" / "record.html").unlink()

            result = subprocess.run(
                [str(launcher), "serve", "--no-open", "--port", "0"],
                cwd=project,
                text=True,
                capture_output=True,
                env=os.environ | {"HOME": str(home)},
                timeout=3,
            )

        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("complete Accord plugin installation", result.stderr)
        self.assertIn("update or reinstall Accord", result.stderr)

    def test_installer_refuses_to_replace_an_unrelated_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, home, _ = self.make_project(root)
            bin_dir = root / "bin"
            bin_dir.mkdir()
            destination = bin_dir / "accord"
            destination.write_text("#!/bin/sh\necho unrelated\n")

            result = subprocess.run(
                [sys.executable, str(INSTALL), "--bin-dir", str(bin_dir)],
                text=True,
                capture_output=True,
                env=os.environ | {"HOME": str(home)},
            )
            preserved = destination.read_text()

        self.assertEqual(result.returncode, 2)
        self.assertIn("refusing to replace", result.stderr)
        self.assertIn("unrelated", preserved)

    def test_installed_command_rejects_unknown_subcommands(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, home, _ = self.make_project(root)
            launcher = self.install(home, root / "bin")
            result = subprocess.run(
                [str(launcher), "render"],
                text=True,
                capture_output=True,
                env=os.environ | {"HOME": str(home)},
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("unknown command: render", result.stderr)

    def stop(self, process: subprocess.Popen[str]) -> None:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()


if __name__ == "__main__":
    unittest.main()
