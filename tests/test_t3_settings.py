from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import t3_settings  # noqa: E402

SELECTION = {"instanceId": "claudeAgent", "model": "claude-opus-5-5", "options": [{"id": "effort", "value": "medium"}]}


class T3SettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root = base / "repo"
        (self.root / "config").mkdir(parents=True)
        self.workspace = base / "work" / "demo"
        self.workspace.mkdir(parents=True)
        self.managed = {
            "schema": 1,
            "settings": {"defaultRuntimeMode": "auto", "defaultModelSelection": SELECTION, "storageCleanup": {"worktreeOnMerge": True}},
            "providerEnvironment": {"claudeAgent": {"driver": "claudeAgent", "variables": {"CLAUDE_CODE_ENABLE_TODO_TOOLS": "1"}}},
            "projects": {
                "demo": {"workspaceRoot": str(self.workspace), "defaultModelSelection": SELECTION},
                "absent": {"workspaceRoot": str(base / "missing"), "defaultModelSelection": SELECTION},
            },
        }
        (self.root / "config" / "t3-settings.json").write_text(json.dumps(self.managed), encoding="utf-8")
        userdata = base / "t3" / "userdata"
        userdata.mkdir(parents=True)
        self.paths = t3_settings.T3Paths(userdata / "settings.json", userdata / "state.sqlite", base / "t3" / "worktrees", base / "t3" / "backups")
        connection = sqlite3.connect(self.paths.state)
        connection.execute("CREATE TABLE projection_projects (project_id TEXT, workspace_root TEXT, deleted_at TEXT)")
        connection.execute("INSERT INTO projection_projects VALUES ('p-1', ?, NULL)", (str(self.workspace),))
        connection.commit()
        connection.close()
        self.paths.settings.write_text(json.dumps({
            "defaultRuntimeMode": "full-access",
            "storageCleanup": {"worktreeOnMerge": False, "worktreeAfterDays": 7},
            "providerInstances": {
                "codex": {"driver": "codex", "enabled": True},
                "claudeAgent": {"driver": "claudeAgent", "environment": [{"name": "KEEP_ME", "value": "x", "sensitive": True}]},
            },
            "projectSettingsOverrides": {"other": {"defaultModelSelection": {"instanceId": "codex", "model": "m"}}},
            "appOnly": {"nested": [1, 2]},
        }), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def settings(self) -> dict:
        return json.loads(self.paths.settings.read_text(encoding="utf-8"))

    def test_apply_merges_managed_keys_and_preserves_the_rest(self) -> None:
        backup = t3_settings.apply(self.root, self.paths)
        self.assertIsNotNone(backup)
        settings = self.settings()
        self.assertEqual(settings["defaultRuntimeMode"], "auto")
        self.assertEqual(settings["defaultModelSelection"], SELECTION)
        self.assertEqual(settings["storageCleanup"], {"worktreeOnMerge": True, "worktreeAfterDays": 7})
        self.assertEqual(settings["appOnly"], {"nested": [1, 2]})
        self.assertEqual(settings["providerInstances"]["codex"], {"driver": "codex", "enabled": True})
        environment = settings["providerInstances"]["claudeAgent"]["environment"]
        self.assertIn({"name": "KEEP_ME", "value": "x", "sensitive": True}, environment)
        self.assertIn({"name": "CLAUDE_CODE_ENABLE_TODO_TOOLS", "value": "1", "sensitive": False}, environment)
        self.assertEqual(settings["projectSettingsOverrides"]["p-1"]["defaultModelSelection"], SELECTION)
        self.assertEqual(settings["projectSettingsOverrides"]["other"]["defaultModelSelection"]["model"], "m")
        self.assertTrue((backup / "settings.json").is_file())

    def test_apply_keeps_the_settings_file_mode(self) -> None:
        self.paths.settings.chmod(0o600)
        backup = t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.paths.settings.stat().st_mode & 0o777, 0o600)
        self.assertEqual(backup.stat().st_mode & 0o777, 0o700)

    def test_new_settings_file_is_private(self) -> None:
        self.paths.settings.unlink()
        t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.paths.settings.stat().st_mode & 0o777, 0o600)

    def test_apply_is_idempotent(self) -> None:
        t3_settings.apply(self.root, self.paths)
        before = self.paths.settings.read_bytes()
        self.assertIsNone(t3_settings.apply(self.root, self.paths))
        self.assertEqual(self.paths.settings.read_bytes(), before)

    def test_missing_project_is_skipped_not_invented(self) -> None:
        result = t3_settings.plan(self.root, self.paths)
        self.assertEqual(len(result.skipped), 1)
        self.assertIn("absent", result.skipped[0])
        t3_settings.apply(self.root, self.paths)
        self.assertEqual(set(self.settings()["projectSettingsOverrides"]), {"p-1", "other"})

    def test_secret_value_for_managed_variable_is_replaced(self) -> None:
        settings = self.settings()
        settings["providerInstances"]["claudeAgent"]["environment"].append(
            {"name": "CLAUDE_CODE_ENABLE_TODO_TOOLS", "value": "", "sensitive": True, "secret": {"ref": "x"}}
        )
        self.paths.settings.write_text(json.dumps(settings), encoding="utf-8")
        t3_settings.apply(self.root, self.paths)
        variables = [item for item in self.settings()["providerInstances"]["claudeAgent"]["environment"] if item["name"] == "CLAUDE_CODE_ENABLE_TODO_TOOLS"]
        self.assertEqual(variables, [{"name": "CLAUDE_CODE_ENABLE_TODO_TOOLS", "value": "1", "sensitive": False}])

    def test_doctor_reports_drift_until_applied(self) -> None:
        errors, warnings = t3_settings.doctor(self.root, self.paths)
        self.assertTrue(any("defaultRuntimeMode" in error for error in errors))
        self.assertTrue(any("absent" in warning for warning in warnings))
        t3_settings.apply(self.root, self.paths)
        errors, _ = t3_settings.doctor(self.root, self.paths)
        self.assertEqual(errors, [])

    def test_favorites_are_added_without_removing_app_choices(self) -> None:
        self.managed["settings"]["favorites"] = [{"provider": "claudeAgent", "model": "claude-opus-5-5"}]
        (self.root / "config" / "t3-settings.json").write_text(json.dumps(self.managed), encoding="utf-8")
        settings = self.settings()
        settings["favorites"] = [{"provider": "codex", "model": "app-starred"}]
        self.paths.settings.write_text(json.dumps(settings), encoding="utf-8")
        t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.settings()["favorites"], [
            {"provider": "codex", "model": "app-starred"},
            {"provider": "claudeAgent", "model": "claude-opus-5-5"},
        ])
        self.assertEqual(t3_settings.doctor(self.root, self.paths)[0], [])

    def test_non_list_environment_is_replaced_safely(self) -> None:
        settings = self.settings()
        settings["providerInstances"]["claudeAgent"]["environment"] = None
        self.paths.settings.write_text(json.dumps(settings), encoding="utf-8")
        t3_settings.apply(self.root, self.paths)
        self.assertEqual(
            self.settings()["providerInstances"]["claudeAgent"]["environment"],
            [{"name": "CLAUDE_CODE_ENABLE_TODO_TOOLS", "value": "1", "sensitive": False}],
        )

    def test_variable_marked_sensitive_by_the_app_is_not_drift(self) -> None:
        t3_settings.apply(self.root, self.paths)
        settings = self.settings()
        for item in settings["providerInstances"]["claudeAgent"]["environment"]:
            if item["name"] == "CLAUDE_CODE_ENABLE_TODO_TOOLS":
                item["sensitive"] = True
                item["valueRedacted"] = False
        self.paths.settings.write_text(json.dumps(settings), encoding="utf-8")
        self.assertEqual(t3_settings.doctor(self.root, self.paths)[0], [])

    def test_preview_shows_old_and_new_values(self) -> None:
        changes = t3_settings.plan(self.root, self.paths).changes
        self.assertIn('change defaultRuntimeMode: "full-access" -> "auto"', changes)

    def test_concurrent_app_write_aborts_without_writing(self) -> None:
        original_plan = t3_settings.plan

        def plan_then_app_writes(root, paths):
            result = original_plan(root, paths)
            paths.settings.write_text(json.dumps({"appWroteThis": True}), encoding="utf-8")
            return result

        with mock.patch.object(t3_settings, "plan", plan_then_app_writes):
            with self.assertRaises(t3_settings.CheckError):
                t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.settings(), {"appWroteThis": True})
        self.assertFalse(self.paths.backups.exists() and any(self.paths.backups.iterdir()))
        self.assertEqual(list(self.paths.settings.parent.glob(".settings.json.ekit-*")), [])

    def test_failed_verification_restores_previous_file(self) -> None:
        before = self.paths.settings.read_bytes()
        original_plan = t3_settings.plan
        calls = []

        def plan_fails_verification(root, paths):
            calls.append(1)
            result = original_plan(root, paths)
            if len(calls) > 1:
                result.changes.append("still drifting")
            return result

        with mock.patch.object(t3_settings, "plan", plan_fails_verification):
            with self.assertRaises(t3_settings.CheckError):
                t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.paths.settings.read_bytes(), before)

    def test_failed_verification_keeps_a_concurrent_app_save(self) -> None:
        original_plan = t3_settings.plan
        calls = []

        def app_saves_during_verification(root, paths):
            calls.append(1)
            if len(calls) > 1:
                paths.settings.write_text(json.dumps({"appSavedLater": True}), encoding="utf-8")
            return original_plan(root, paths)

        with mock.patch.object(t3_settings, "plan", app_saves_during_verification):
            with self.assertRaises(t3_settings.CheckError):
                t3_settings.apply(self.root, self.paths)
        self.assertEqual(self.settings(), {"appSavedLater": True})

    def test_projects_committed_only_to_the_wal_are_seen(self) -> None:
        state = Path(self.temporary.name) / "wal.sqlite"
        writer = sqlite3.connect(state)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE projection_projects (project_id TEXT, workspace_root TEXT, deleted_at TEXT)")
        writer.execute("INSERT INTO projection_projects VALUES ('p-wal', ?, NULL)", (str(self.workspace),))
        writer.commit()
        try:
            self.assertEqual(t3_settings.project_ids(state), {os.path.realpath(self.workspace): "p-wal"})
        finally:
            writer.close()

    def test_cli_reports_invalid_settings_without_traceback(self) -> None:
        bad = Path(self.temporary.name) / "bad.json"
        bad.write_text("[1]", encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(REPOSITORY_ROOT / "scripts" / "skills.py"), "t3-sync", "--settings-target", str(bad)],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("expected a JSON object", completed.stderr)
        self.assertNotIn("Traceback", completed.stderr)

    def test_worktree_whose_branch_is_gone_upstream_is_listed(self) -> None:
        git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
        origin = Path(self.temporary.name) / "origin"
        subprocess.run(["git", "init", "-q", "-b", "main", str(origin)], check=True)
        subprocess.run([*git, "-C", str(origin), "commit", "-q", "--allow-empty", "-m", "base"], check=True)
        subprocess.run(["git", "-C", str(origin), "branch", "feature"], check=True)
        clone = Path(self.temporary.name) / "clone"
        subprocess.run(["git", "clone", "-q", str(origin), str(clone)], check=True)
        tree = self.paths.worktrees / "demo" / "feature"
        tree.parent.mkdir(parents=True)
        subprocess.run(["git", "-C", str(clone), "worktree", "add", "-q", "--track", "-b", "feature", str(tree), "origin/feature"], check=True)
        self.assertEqual(t3_settings.leftover_worktrees(self.paths.worktrees), [], "a fresh worktree is not leftover")
        subprocess.run(["git", "-C", str(origin), "branch", "-D", "feature"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(clone), "fetch", "-q", "--prune"], check=True)
        leftovers = t3_settings.leftover_worktrees(self.paths.worktrees)
        self.assertEqual(len(leftovers), 1)
        self.assertIn("gone upstream", leftovers[0])


if __name__ == "__main__":
    unittest.main()
