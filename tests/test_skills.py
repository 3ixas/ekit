from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import skills  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_repo(root: Path) -> None:
    for lifecycle in skills.LIFECYCLES:
        for group in skills.GROUPS:
            (root / lifecycle / group).mkdir(parents=True)
    (root / "config").mkdir()
    (root / "licenses").mkdir()
    (root / "config" / "AGENTS.md").write_text("# Canonical\n", encoding="utf-8")
    write_json(root / "config" / "tools.json", {"git": {"kind": "executable", "probe": ["git", "--version"]}})
    write_json(
        root / "config" / "agent-capabilities.json",
        json.loads((REPOSITORY_ROOT / "config" / "agent-capabilities.json").read_text(encoding="utf-8")),
    )
    write_json(root / "config" / "runtime.json", {
        "skills": "~/.agents/skills",
        "global_agents": "~/.codex/AGENTS.md",
        "backups": "~/.agents/skill-backups",
        "claude_skills": "~/.claude/skills",
        "claude_runtime": "~/.claude/agent-skills-runtime",
        "claude_rules": "~/.claude/rules/elias-agent-skills.md",
        "claude_backups": "~/.claude/skill-backups/elias-agent-skills",
        "opencode_agents": "~/.config/opencode/AGENTS.md",
        "opencode_backups": "~/.config/opencode/skill-backups/elias-agent-skills",
    })
    (root / "licenses" / "mit-test.txt").write_text("MIT\n", encoding="utf-8")


def add_skill(
    root: Path,
    skill_id: str,
    *,
    lifecycle: str = "skills",
    group: str = "agent-system",
    invocation: list[str] | None = None,
    dependencies: list[str] | None = None,
    origin: str = "original",
    sources: list[dict[str, str]] | None = None,
) -> Path:
    bundle = root / lifecycle / group / skill_id
    bundle.mkdir(parents=True)
    (bundle / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: Exercise {skill_id} when its exact workflow applies.\n---\n\n# {skill_id}\n",
        encoding="utf-8",
    )
    invocation = invocation or ["automatic"]
    if "explicit" in invocation:
        (bundle / "agents").mkdir()
        (bundle / "agents" / "openai.yaml").write_text("policy:\n  allow_implicit_invocation: true\n", encoding="utf-8")
    write_json(bundle / "metadata.json", {
        "id": skill_id,
        "group": group,
        "origin": origin,
        "invocation": invocation,
        "sources": sources or [],
        "dependencies": {"skills": dependencies or [], "tools": []},
        "reviewed": "2026-09-14",
    })
    return bundle


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)
    return result.stdout.strip()


class RepositoryValidationTests(unittest.TestCase):
    def test_project_claude_entrypoint_imports_agent_instructions(self) -> None:
        self.assertEqual((REPOSITORY_ROOT / "CLAUDE.md").read_text(encoding="utf-8").strip(), "@AGENTS.md")

    def test_valid_grouped_repository_and_projection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            active = add_skill(root, "active")
            add_skill(root, "later", lifecycle="candidates")
            (active / "references").mkdir()
            (active / "references" / "guide.md").write_text("guide\n", encoding="utf-8")
            (active / "SKILL.md").write_text((active / "SKILL.md").read_text() + "\nRead [the guide](references/guide.md).\n", encoding="utf-8")
            self.assertEqual(skills.check_repo(root), [])
            self.assertEqual(set(skills.active_projection(root)), {"active/SKILL.md", "active/references/guide.md"})

    def test_duplicate_id_and_inactive_dependency_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            add_skill(root, "shared", lifecycle="candidates")
            add_skill(root, "shared", lifecycle="paused")
            add_skill(root, "consumer", dependencies=["shared"])
            errors = skills.check_repo(root)
            self.assertTrue(any("duplicate skill id shared" in error for error in errors))
            self.assertTrue(any("active skill depends on inactive shared" in error for error in errors))

    def test_dependency_cycle_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            add_skill(root, "alpha", dependencies=["beta"])
            add_skill(root, "beta", dependencies=["alpha"])
            self.assertTrue(any("dependency cycle" in error for error in skills.check_repo(root)))

    def test_explicit_skill_requires_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "explicit-one", invocation=["explicit"])
            (bundle / "agents" / "openai.yaml").unlink()
            self.assertTrue(any("user-requested skill requires" in error for error in skills.check_repo(root)))

    def test_requested_skill_rejects_manual_only_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "requested", invocation=["explicit"])
            policy = bundle / "agents" / "openai.yaml"
            policy.write_text("policy:\n  allow_implicit_invocation: false\n")
            self.assertTrue(any("model-loadable" in error for error in skills.check_repo(root)))
            policy.write_text("policy:\n  allow_implicit_invocation: true\n")
            skill = bundle / "SKILL.md"
            skill.write_text(skill.read_text().replace("description:", "disable-model-invocation: true\ndescription:"))
            self.assertTrue(any("must remain model-loadable" in error for error in skills.check_repo(root)))

    def test_inactive_manual_only_source_remains_unmodified_and_unprojected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            add_skill(root, "active")
            bundle = add_skill(root, "candidate", lifecycle="candidates", invocation=["explicit"])
            policy = bundle / "agents" / "openai.yaml"
            policy.write_text("policy:\n  allow_implicit_invocation: false\n")
            self.assertEqual(skills.check_repo(root), [])
            self.assertNotIn("candidate/SKILL.md", skills.runtime_projection(root))
            self.assertIn("false", policy.read_text())

    def test_unlinked_reference_is_reported_until_linked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "referenced")
            (bundle / "references" / "deep").mkdir(parents=True)
            (bundle / "references" / "guide.md").write_text("# Guide\n\nSee [detail](deep/detail.md).\n", encoding="utf-8")
            (bundle / "references" / "deep" / "detail.md").write_text("# Detail\n", encoding="utf-8")
            (bundle / "references" / "notes.md").write_text("# Notes\n", encoding="utf-8")
            unlinked = [error for error in skills.check_repo(root) if "is not linked" in error]
            self.assertEqual(len(unlinked), 3)
            skill = bundle / "SKILL.md"
            skill.write_text(skill.read_text() + "\nRead [the guide](references/guide.md) and `references/notes.md`.\n", encoding="utf-8")
            self.assertEqual([error for error in skills.check_repo(root) if "is not linked" in error], [])

    def test_named_bundle_paths_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "named")
            snapshots = bundle / "references" / "source-methods"
            snapshots.mkdir(parents=True)
            (snapshots / "upstream.md").write_text("# Upstream\n\nRead `references/upstream-only.md`.\n", encoding="utf-8")
            skill = bundle / "SKILL.md"
            skill.write_text(skill.read_text() + (
                "\nRead `references/missing.md` and run scripts/setup.sh.\n"
                "Use the installed `other` skill's `references/contract.md` as the handoff contract.\n"
                "See [snapshot](references/source-methods/upstream.md).\n"
                "```md\nExample: `references/fenced.md`\n```\n"
            ), encoding="utf-8")
            named = sorted(error.rsplit(": ", 1)[1] for error in skills.check_repo(root) if "names missing bundle file" in error)
            self.assertEqual(named, ["references/missing.md", "scripts/setup.sh"])
            (bundle / "references" / "missing.md").write_text("# Missing\n", encoding="utf-8")
            (bundle / "scripts").mkdir()
            (bundle / "scripts" / "setup.sh").write_text("#!/bin/sh\n", encoding="utf-8")
            self.assertFalse(any("names missing bundle file" in error for error in skills.check_repo(root)))

    def test_handoff_permission_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            handoffs = home / ".agents" / "handoffs"
            codex = home / "config.toml"
            codex.write_text('sandbox_mode = "workspace-write"\n', encoding="utf-8")
            self.assertEqual(len(skills.codex_handoff_warnings(codex, handoffs)), 1)
            codex.write_text(f'sandbox_mode = "workspace-write"\n[sandbox_workspace_write]\nwritable_roots = ["{handoffs}"]\n', encoding="utf-8")
            self.assertEqual(skills.codex_handoff_warnings(codex, handoffs), [])
            settings = home / "settings.json"
            settings.write_text(json.dumps({"permissions": {"allow": [f"Read({handoffs}/**)"]}}), encoding="utf-8")
            self.assertEqual(skills.claude_permission_warnings(settings, "Read", [handoffs], "x"), [])
            self.assertEqual(len(skills.claude_permission_warnings(settings, "Edit", [handoffs], "x")), 1)

    def test_source_schema_and_license_are_validated(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            add_skill(root, "derived", origin="adapted", sources=[{
                "repository": "https://example.com/repo", "ref": "a" * 40,
                "path": "../escape", "digest": "wrong", "license": "missing",
                "use": "adapted", "changes": "Rewritten.",
            }])
            errors = skills.check_repo(root)
            self.assertTrue(any("safe repository-relative path" in error for error in errors))
            self.assertTrue(any("supported exact digest" in error for error in errors))
            self.assertTrue(any("missing licence file" in error for error in errors))

    def test_markdown_link_checks_ignore_fenced_examples(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "linked")
            skill_file = bundle / "SKILL.md"
            skill_file.write_text(skill_file.read_text() + "\n```md\n[example](./missing.md)\n```\n[bad](../../outside.md)\n")
            errors = skills.check_repo(root)
            self.assertEqual(sum("link escapes" in error for error in errors), 1)
            self.assertFalse(any("missing.md" in error for error in errors))

    def test_nested_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); make_repo(root)
            bundle = add_skill(root, "linked")
            (bundle / "references").mkdir()
            (bundle / "references" / "outside").symlink_to(root / "config" / "AGENTS.md")
            self.assertTrue(any("symlinks are not allowed" in error for error in skills.check_repo(root)))


class SyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        self.root, self.target = base / "repo", base / "runtime"
        self.global_target, self.backups = base / "home" / "AGENTS.md", base / "backups"
        make_repo(self.root)
        self.bundle = add_skill(self.root, "example")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_preview_reports_exact_add_change_remove_sets(self) -> None:
        self.target.mkdir()
        (self.target / "example").mkdir()
        (self.target / "example" / "SKILL.md").write_text("old\n")
        (self.target / "obsolete.txt").write_text("old\n")
        status = skills.sync_status(self.root, self.target, self.global_target)
        self.assertEqual(status.adds, [])
        self.assertEqual(status.changes, ["example/SKILL.md"])
        self.assertEqual(status.removes, ["obsolete.txt"])
        self.assertEqual(status.drift, ["runtime is unmarked"])

    def test_apply_creates_exact_projection_marker_global_and_backup(self) -> None:
        self.target.mkdir(parents=True)
        self.global_target.parent.mkdir(parents=True)
        self.global_target.write_text("old global\n")
        backup = skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        self.assertEqual(skills.doctor(self.root, self.target, self.global_target, probe_tools=False), [])
        self.assertEqual((backup / "AGENTS.md").read_text(), "old global\n")
        snapshot = skills.read_json(backup / "snapshot.json")
        self.assertEqual(snapshot["runtime_existed"], True)
        self.assertEqual(snapshot["runtime_files"], {})
        self.assertEqual(snapshot["global_agents"], skills.file_hash(backup / "AGENTS.md"))
        marker = skills.read_json(self.target / skills.MARKER)
        self.assertEqual(marker["schema"], skills.MARKER_SCHEMA)
        self.assertEqual(marker["files"], skills.desired_hashes(self.root))

    def test_apply_replaces_managed_runtime_and_keeps_snapshot(self) -> None:
        skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        old = (self.target / "example" / "SKILL.md").read_text()
        (self.bundle / "SKILL.md").write_text(old + "\nChanged canonically.\n")
        backup = skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        self.assertIn("Changed canonically", (self.target / "example" / "SKILL.md").read_text())
        self.assertEqual((backup / "skills" / "example" / "SKILL.md").read_text(), old)

    def test_apply_refuses_hand_edited_runtime(self) -> None:
        skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        (self.target / "example" / "SKILL.md").write_text("hand edit\n")
        with self.assertRaisesRegex(skills.CheckError, "runtime drift"):
            skills.sync_apply(self.root, self.target, self.global_target, self.backups)

    def test_adopt_unmanaged_is_explicit_and_preserves_old_runtime(self) -> None:
        self.target.mkdir(parents=True)
        (self.target / "legacy.txt").write_text("legacy\n")
        with self.assertRaisesRegex(skills.CheckError, "unmarked"):
            skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        backup = skills.sync_apply(
            self.root, self.target, self.global_target, self.backups, adopt_unmanaged=True
        )
        self.assertEqual((backup / "skills" / "legacy.txt").read_text(), "legacy\n")
        self.assertFalse((self.target / "legacy.txt").exists())
        self.assertEqual(skills.doctor(self.root, self.target, self.global_target, probe_tools=False), [])

    def test_apply_refuses_hand_edited_global_agents(self) -> None:
        skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        self.global_target.write_text("hand edit\n")
        with self.assertRaisesRegex(skills.CheckError, "global AGENTS.md was edited"):
            skills.sync_apply(self.root, self.target, self.global_target, self.backups)

    def test_apply_refuses_deleted_global_agents_after_managed_sync(self) -> None:
        skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        self.global_target.unlink()
        with self.assertRaisesRegex(skills.CheckError, "global AGENTS.md was edited"):
            skills.sync_apply(self.root, self.target, self.global_target, self.backups)

    def test_failed_verification_rolls_back_both_targets(self) -> None:
        self.target.mkdir(parents=True)
        (self.target / "legacy.txt").write_text("legacy runtime\n")
        self.global_target.parent.mkdir(parents=True)
        self.global_target.write_text("legacy global\n")
        # An unmarked non-empty target is intentionally refused, so establish a managed baseline first.
        self.target.unlink() if self.target.is_file() else None
        for child in list(self.target.iterdir()): child.unlink()
        skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        baseline_runtime = (self.target / "example" / "SKILL.md").read_text()
        baseline_global = self.global_target.read_text()
        (self.bundle / "SKILL.md").write_text(baseline_runtime + "changed\n")
        with mock.patch.object(skills, "_verify_runtime", side_effect=skills.CheckError("injected")):
            with self.assertRaisesRegex(skills.CheckError, "injected"):
                skills.sync_apply(self.root, self.target, self.global_target, self.backups)
        self.assertEqual((self.target / "example" / "SKILL.md").read_text(), baseline_runtime)
        self.assertEqual(self.global_target.read_text(), baseline_global)


class ClaudeSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root, self.home = self.base / "repo", self.base / "home"
        make_repo(self.root)
        self.auto = add_skill(self.root, "automatic")
        self.support = add_skill(self.root, "supporting-only", invocation=["supporting"])
        self.explicit = add_skill(self.root, "explicit-only", invocation=["explicit"])
        self.mixed = add_skill(self.root, "automatic-supporting", invocation=["automatic", "supporting"])
        (self.auto / "SKILL.md").write_text(
            (self.auto / "SKILL.md").read_text().replace("description: Exercise", "disable-model-invocation: true\ndescription: Exercise"),
            encoding="utf-8",
        )
        (self.explicit / "SKILL.md").write_text(
            (self.explicit / "SKILL.md").read_text().replace("description: Exercise", "disable-model-invocation: false\ndescription: Exercise"),
            encoding="utf-8",
        )
        self.skills_target = self.home / ".claude" / "skills"
        self.runtime_target = self.home / ".claude" / "agent-skills-runtime"
        self.rules_target = self.home / ".claude" / "rules" / "elias-agent-skills.md"
        self.backups = self.home / ".claude" / "skill-backups" / "elias-agent-skills"
        self.global_target = self.home / ".codex" / "AGENTS.md"
        self.global_target.parent.mkdir(parents=True)
        self.global_target.write_text((self.root / "config" / "AGENTS.md").read_text())
        self.skills_target.mkdir(parents=True)
        (self.skills_target / "private-user-skill").mkdir()
        (self.skills_target / "private-user-skill" / "SKILL.md").write_text("owned elsewhere\n")
        (self.skills_target / "old-dangling-link").symlink_to(self.home / "missing" / "old-skill")
        self.codex_runtime = self.home / ".agents" / "skills"
        legacy = self.codex_runtime / "automatic"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("legacy copy\n")
        write_json(self.codex_runtime / skills.MARKER, {
            "schema": skills.MARKER_SCHEMA,
            "repository": "elias-agent-skills",
            "files": {"automatic/SKILL.md": skills.file_hash(legacy / "SKILL.md")},
        })
        (self.skills_target / "automatic").symlink_to(legacy)
        self.environ = mock.patch.dict("os.environ", {"HOME": str(self.home)})
        self.environ.start()

    def tearDown(self) -> None:
        self.environ.stop()
        self.temporary.cleanup()

    def sync(self) -> skills.ClaudeSyncStatus:
        return skills.claude_sync_status(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, backup_root=self.backups,
        )

    def apply(self) -> Path | None:
        return skills.claude_sync_apply(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, self.backups,
        )

    def test_preview_maps_invocation_and_preserves_unmanaged_skill_entries(self) -> None:
        status = self.sync()
        self.assertIn("explicit-only/SKILL.md", status.adds)
        self.assertEqual(status.skill_links_adds, ["automatic-supporting", "explicit-only", "supporting-only"])
        self.assertEqual(status.skill_links_changes, ["automatic"])
        self.assertEqual(status.unsupported, ["supporting-only"])
        self.assertEqual(status.rule_changed, True)
        self.assertEqual(status.conflicts, [])

    def test_apply_projects_policy_rules_and_preserves_unmanaged_entries(self) -> None:
        canonical_explicit = (self.explicit / "SKILL.md").read_text()
        binary_asset = self.auto / "assets" / "test.png"
        binary_asset.parent.mkdir()
        binary_asset.write_bytes(b"\x89PNG\x00\xff")
        helper_script = self.auto / "scripts" / "run.sh"
        helper_script.parent.mkdir()
        helper_script.write_text("#!/bin/sh\nexit 0\n")
        helper_script.chmod(0o755)
        self.assertEqual(
            skills.claude_projection(self.root)[0]["automatic/assets/test.png"],
            b"\x89PNG\x00\xff",
        )
        backup = self.apply()
        self.assertIsNotNone(backup)
        self.assertNotIn("disable-model-invocation", (self.runtime_target / "explicit-only" / "SKILL.md").read_text())
        self.assertNotIn("disable-model-invocation", (self.runtime_target / "automatic" / "SKILL.md").read_text())
        self.assertNotIn("disable-model-invocation", (self.runtime_target / "automatic-supporting" / "SKILL.md").read_text())
        self.assertEqual((self.explicit / "SKILL.md").read_text(), canonical_explicit)
        self.assertTrue((self.runtime_target / "automatic" / "scripts" / "run.sh").stat().st_mode & 0o111)
        self.assertEqual((self.skills_target / "automatic").resolve(), (self.runtime_target / "automatic").resolve())
        self.assertTrue((self.skills_target / "private-user-skill" / "SKILL.md").is_file())
        self.assertEqual((self.skills_target / "old-dangling-link").readlink(), self.home / "missing" / "old-skill")
        rule = self.rules_target.read_text()
        self.assertFalse(rule.startswith("@"), "the rules file must not import AGENTS.md; CLAUDE.md links to it")
        self.assertIn(f"managed link to `{self.global_target.resolve()}`", rule)
        self.assertIn("supporting-only", rule)
        self.assertIn("no native supporting-only invocation mode", rule)
        self.assertIn("read the root `AGENTS.md` before work", rule)
        snapshot = skills.read_json(backup / "snapshot.json")
        self.assertEqual(snapshot["skill_links"]["automatic"], str(self.codex_runtime / "automatic"))
        self.assertFalse(snapshot["runtime_existed"])
        self.assertEqual(skills.claude_doctor(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, backup_root=self.backups,
        ), [])

    def test_apply_is_idempotent(self) -> None:
        self.apply()
        self.assertIsNone(self.apply())
        self.assertEqual(self.sync().adds, [])
        self.assertEqual(self.sync().changes, [])
        self.assertEqual(self.sync().skill_links_adds, [])
        self.assertFalse(self.sync().rule_changed)

    def test_relative_target_paths_create_absolute_skill_links(self) -> None:
        previous = Path.cwd()
        os.chdir(self.base)
        try:
            skills.claude_sync_apply(
                self.root,
                Path("home/.claude/skills"),
                Path("home/.claude/agent-skills-runtime"),
                Path("home/.claude/rules/elias-agent-skills.md"),
                Path("home/.codex/AGENTS.md"),
                Path("home/.agents/skills"),
                Path("home/.claude/skill-backups/elias-agent-skills"),
            )
        finally:
            os.chdir(previous)
        self.assertEqual(
            (self.skills_target / "supporting-only").resolve(),
            (self.runtime_target / "supporting-only").resolve(),
        )

    def test_apply_refuses_unmanaged_colliding_skill_directory(self) -> None:
        (self.skills_target / "supporting-only").mkdir()
        status = self.sync()
        self.assertTrue(any("supporting-only" in conflict for conflict in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            self.apply()
        self.assertTrue((self.skills_target / "supporting-only").is_dir())

    def test_apply_links_claude_global_instructions_to_agents(self) -> None:
        link = self.home / ".claude" / "CLAUDE.md"
        self.assertTrue(self.sync_with_link(link).global_link_changed)
        skills.claude_sync_apply(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, self.backups, link,
        )
        self.assertTrue(link.is_symlink())
        self.assertEqual(link.resolve(), self.global_target.resolve())
        self.assertFalse(self.sync_with_link(link).global_link_changed)
        self.assertEqual(skills.claude_doctor(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, backup_root=self.backups, global_link=link,
        ), [])

    def test_apply_refuses_to_replace_a_real_claude_global_file(self) -> None:
        link = self.home / ".claude" / "CLAUDE.md"
        link.write_text("hand-written Claude instructions\n")
        self.assertTrue(any("CLAUDE.md" in item for item in self.sync_with_link(link).conflicts))
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            skills.claude_sync_apply(
                self.root, self.skills_target, self.runtime_target, self.rules_target,
                self.global_target, self.codex_runtime, self.backups, link,
            )
        self.assertEqual(link.read_text(), "hand-written Claude instructions\n")

    def test_read_permission_warnings_name_uncovered_skill_paths(self) -> None:
        settings = self.home / ".claude" / "settings.json"
        targets = [self.skills_target, self.runtime_target]
        self.assertEqual(len(skills.claude_read_permission_warnings(settings, targets)), 2)
        write_json(settings, {"permissions": {"allow": ["Read(~/.claude/skills/**)"]}})
        warnings = skills.claude_read_permission_warnings(settings, targets)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Read(~/.claude/agent-skills-runtime/**)", warnings[0])
        write_json(settings, {"permissions": {"allow": ["Read(~/.claude/skills/**)", "Read(~/.claude/agent-skills-runtime/**)"]}})
        self.assertEqual(skills.claude_read_permission_warnings(settings, targets), [])
        write_json(settings, {"permissions": {"allow": ["Read(~/.claude/**)"]}})
        self.assertEqual(skills.claude_read_permission_warnings(settings, targets), [])

    def sync_with_link(self, link: Path) -> skills.ClaudeSyncStatus:
        return skills.claude_sync_status(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, backup_root=self.backups, global_link=link,
        )

    def test_apply_refuses_unmanaged_rules_file_without_replacing_it(self) -> None:
        self.rules_target.parent.mkdir(parents=True)
        self.rules_target.write_text("user-owned Claude rules\n")
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            self.apply()
        self.assertEqual(self.rules_target.read_text(), "user-owned Claude rules\n")

    def test_apply_refuses_an_unrelated_symlink_at_an_active_skill_path(self) -> None:
        unrelated = self.home / "private-skill"
        unrelated.mkdir()
        (self.skills_target / "supporting-only").symlink_to(unrelated)
        status = self.sync()
        self.assertTrue(any("supporting-only" in conflict for conflict in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            self.apply()
        self.assertEqual((self.skills_target / "supporting-only").resolve(), unrelated.resolve())

    def test_apply_refuses_overlapping_managed_and_backup_targets(self) -> None:
        status = skills.claude_sync_status(
            self.root, self.skills_target, self.skills_target / "runtime",
            self.rules_target, self.global_target, self.codex_runtime,
            backup_root=self.backups,
        )
        self.assertTrue(any("must be separate" in conflict for conflict in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            skills.claude_sync_apply(
                self.root, self.skills_target, self.skills_target / "runtime",
                self.rules_target, self.global_target, self.codex_runtime, self.backups,
            )
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            skills.claude_sync_apply(
                self.root, self.skills_target, self.runtime_target, self.rules_target,
                self.global_target, self.codex_runtime, self.runtime_target / "backups",
            )
        self.assertFalse(self.runtime_target.exists())

    def test_apply_refuses_a_symlinked_backup_root(self) -> None:
        actual = self.home / "actual-backups"
        actual.mkdir()
        linked = self.home / "linked-backups"
        linked.symlink_to(actual)
        status = skills.claude_sync_status(
            self.root, self.skills_target, self.runtime_target, self.rules_target,
            self.global_target, self.codex_runtime, backup_root=linked,
        )
        self.assertTrue(any("backup path must be a real directory" in item for item in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "Claude sync conflict"):
            skills.claude_sync_apply(
                self.root, self.skills_target, self.runtime_target, self.rules_target,
                self.global_target, self.codex_runtime, linked,
            )
        self.assertEqual(list(actual.iterdir()), [])

    def test_apply_refuses_runtime_drift_and_hand_edited_rule(self) -> None:
        self.apply()
        (self.runtime_target / "automatic" / "SKILL.md").write_text("manual edit\n")
        with self.assertRaisesRegex(skills.CheckError, "Claude runtime drift"):
            self.apply()
        (self.runtime_target / "automatic" / "SKILL.md").write_text(
            (self.root / "skills" / "agent-system" / "automatic" / "SKILL.md").read_text()
        )
        self.rules_target.write_text("manual rule edit\n")
        with self.assertRaisesRegex(skills.CheckError, "Claude rule file drift"):
            self.apply()

    def test_apply_refuses_unexpected_empty_runtime_directory(self) -> None:
        self.apply()
        extra = self.runtime_target / "untracked-empty"
        extra.mkdir()
        status = self.sync()
        self.assertTrue(any("untracked-empty" in error for error in status.drift))
        with self.assertRaisesRegex(skills.CheckError, "unexpected directory untracked-empty"):
            self.apply()
        self.assertTrue(extra.is_dir())

    def test_failed_verification_restores_runtime_rules_and_legacy_link(self) -> None:
        self.apply()
        previous_runtime = (self.runtime_target / "automatic" / "SKILL.md").read_text()
        previous_rules = self.rules_target.read_text()
        previous_link = (self.skills_target / "automatic").readlink()
        (self.auto / "SKILL.md").write_text(previous_runtime + "updated\n")
        with mock.patch.object(skills, "_verify_claude_runtime", side_effect=skills.CheckError("injected")):
            with self.assertRaisesRegex(skills.CheckError, "injected"):
                self.apply()
        self.assertEqual((self.runtime_target / "automatic" / "SKILL.md").read_text(), previous_runtime)
        self.assertEqual(self.rules_target.read_text(), previous_rules)
        self.assertEqual((self.skills_target / "automatic").readlink(), previous_link)
        self.assertTrue((self.skills_target / "private-user-skill" / "SKILL.md").is_file())

    def test_removed_active_skill_only_removes_its_managed_projection_and_link(self) -> None:
        self.apply()
        paused = self.root / "candidates" / "agent-system" / "automatic"
        self.auto.rename(paused)
        status = self.sync()
        self.assertEqual(status.skill_links_removes, ["automatic"])
        self.assertEqual(status.removes, ["automatic/SKILL.md"])
        self.apply()
        self.assertFalse((self.skills_target / "automatic").exists())
        self.assertFalse((self.runtime_target / "automatic").exists())
        self.assertTrue((self.skills_target / "private-user-skill" / "SKILL.md").is_file())

    def test_requires_synced_canonical_global_instructions_before_apply(self) -> None:
        self.global_target.write_text("stale instructions\n")
        status = self.sync()
        self.assertTrue(any("global AGENTS.md" in error for error in status.prerequisites))
        with self.assertRaisesRegex(skills.CheckError, "global AGENTS.md must be synced"):
            self.apply()


class OpenCodeSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root, self.home = self.base / "repo", self.base / "home"
        make_repo(self.root)
        self.auto = add_skill(self.root, "automatic")
        self.support = add_skill(self.root, "supporting-only", invocation=["supporting"])
        self.explicit = add_skill(self.root, "explicit-only", invocation=["explicit"])
        self.mixed = add_skill(self.root, "automatic-supporting", invocation=["automatic", "supporting"])
        self.skills_target = self.home / ".agents" / "skills"
        self.global_target = self.home / ".codex" / "AGENTS.md"
        self.global_target.parent.mkdir(parents=True)
        self.global_target.write_text((self.root / "config" / "AGENTS.md").read_text())
        self.shared_backups = self.home / ".agents" / "skill-backups"
        skills.sync_apply(self.root, self.skills_target, self.global_target, self.shared_backups)
        self.agents_target = self.home / ".config" / "opencode" / "AGENTS.md"
        self.backups = self.home / ".config" / "opencode" / "skill-backups" / "elias-agent-skills"
        self.environ = mock.patch.dict("os.environ", {"HOME": str(self.home)})
        self.environ.start()

    def tearDown(self) -> None:
        self.environ.stop()
        self.temporary.cleanup()

    def sync(self) -> skills.OpenCodeSyncStatus:
        return skills.opencode_sync_status(
            self.root, self.agents_target, self.skills_target, self.global_target,
            backup_root=self.backups,
        )

    def apply(self) -> Path | None:
        return skills.opencode_sync_apply(
            self.root, self.agents_target, self.skills_target, self.global_target, self.backups,
        )

    def test_shared_projection_enables_v2_loading_for_requested_skills(self) -> None:
        canonical_explicit = (self.explicit / "SKILL.md").read_bytes()
        projection = skills.runtime_projection(self.root, opencode_v2=True)
        self.assertIn(b"metadata:\n  opencode/autoinvoke: true", projection["explicit-only/SKILL.md"])
        self.assertNotIn(b"opencode/autoinvoke", projection["automatic/SKILL.md"])
        self.assertNotIn(b"opencode/autoinvoke", projection["supporting-only/SKILL.md"])
        self.assertNotIn(b"opencode/autoinvoke", projection["automatic-supporting/SKILL.md"])
        self.assertEqual((self.explicit / "SKILL.md").read_bytes(), canonical_explicit)
        self.assertNotIn(b"opencode/autoinvoke", skills.runtime_projection(self.root, opencode_v2=False)["explicit-only/SKILL.md"])

    def test_v2_sync_applies_metadata_only_to_generated_runtime(self) -> None:
        canonical_explicit = (self.explicit / "SKILL.md").read_bytes()
        with mock.patch.object(skills, "opencode_major_version", return_value=2):
            skills.sync_apply(self.root, self.skills_target, self.global_target, self.shared_backups)
        self.assertIn(b"opencode/autoinvoke: true", (self.skills_target / "explicit-only" / "SKILL.md").read_bytes())
        self.assertEqual((self.explicit / "SKILL.md").read_bytes(), canonical_explicit)

    def test_projection_preserves_existing_skill_metadata_and_normalizes_policy(self) -> None:
        source = (
            b"---\nname: explicit-only\nmetadata:\n  author: Elias\n  opencode/autoinvoke: true\n---\n\n# Skill\n"
        )
        projected = skills._opencode_skill_text(source, ["explicit"])
        self.assertIn(b"  author: Elias\n", projected)
        self.assertIn(b"  opencode/autoinvoke: true\n", projected)
        self.assertEqual(projected.count(b"opencode/autoinvoke:"), 1)

    def test_major_version_detection_selects_only_verified_v2_behavior(self) -> None:
        skills.opencode_major_version.cache_clear()
        with mock.patch.object(skills.shutil, "which", return_value="/usr/local/bin/opencode"), mock.patch.object(
            skills.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "opencode 2.1.0\n", ""),
        ):
            self.assertEqual(skills.opencode_major_version(), 2)
        skills.opencode_major_version.cache_clear()
        with mock.patch.object(skills.shutil, "which", return_value="/usr/local/bin/opencode"), mock.patch.object(
            skills.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "opencode 1.12.3\n", ""),
        ):
            self.assertEqual(skills.opencode_major_version(), 1)
        skills.opencode_major_version.cache_clear()
        with mock.patch.object(skills.shutil, "which", return_value=None):
            self.assertIsNone(skills.opencode_major_version())
        skills.opencode_major_version.cache_clear()

    def test_preview_reports_invocation_mapping_and_shared_runtime_prerequisite(self) -> None:
        self.skills_target = self.home / ".agents" / "missing-skills"
        with mock.patch.object(skills, "opencode_major_version", return_value=1):
            status = self.sync()
        self.assertTrue(any("shared Agent Skills runtime needs sync" in item for item in status.prerequisites))
        self.assertEqual(status.routing["automatic"], ["automatic", "automatic-supporting"])
        self.assertEqual(status.routing["supporting_only"], ["supporting-only"])
        self.assertEqual(status.routing["explicit"], ["explicit-only"])
        self.assertEqual(len(status.limitations), 2)

    def test_apply_preserves_other_opencode_files_and_is_idempotent(self) -> None:
        user_config = self.agents_target.parent / "opencode.json"
        private_skill = self.agents_target.parent / "skills" / "private-skill" / "SKILL.md"
        user_config.parent.mkdir(parents=True)
        user_config.write_text('{"model":"user/model"}\n')
        private_skill.parent.mkdir(parents=True)
        private_skill.write_text("private OpenCode skill\n")
        backup = self.apply()
        self.assertIsNotNone(backup)
        self.assertTrue(self.agents_target.is_file())
        self.assertIn("supporting-only", self.agents_target.read_text())
        self.assertEqual(user_config.read_text(), '{"model":"user/model"}\n')
        self.assertEqual(private_skill.read_text(), "private OpenCode skill\n")
        self.assertEqual(skills.opencode_doctor(
            self.root, self.agents_target, self.skills_target, self.global_target,
            backup_root=self.backups,
        ), [])
        self.assertIsNone(self.apply())

    def test_apply_refuses_unmanaged_instruction_file_and_detects_managed_drift(self) -> None:
        self.agents_target.parent.mkdir(parents=True)
        self.agents_target.write_text("user-owned OpenCode instructions\n")
        status = self.sync()
        self.assertTrue(any("not owned by this sync" in item for item in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "OpenCode sync conflict"):
            self.apply()
        self.assertEqual(self.agents_target.read_text(), "user-owned OpenCode instructions\n")

        self.agents_target.unlink()
        self.apply()
        self.agents_target.write_bytes(self.agents_target.read_bytes() + b"manual edit\n")
        self.assertTrue(any("edited after" in item for item in self.sync().drift))
        with self.assertRaisesRegex(skills.CheckError, "OpenCode runtime drift"):
            self.apply()

    def test_apply_refuses_overlapping_managed_and_backup_targets(self) -> None:
        status = skills.opencode_sync_status(
            self.root, self.skills_target / "AGENTS.md", self.skills_target,
            self.global_target, backup_root=self.backups,
        )
        self.assertTrue(any("must be separate" in item for item in status.conflicts))
        with self.assertRaisesRegex(skills.CheckError, "OpenCode sync conflict"):
            skills.opencode_sync_apply(
                self.root, self.skills_target / "AGENTS.md", self.skills_target,
                self.global_target, self.backups,
            )
        status = skills.opencode_sync_status(
            self.root, self.root / "AGENTS.md", self.skills_target,
            self.global_target, backup_root=self.backups,
        )
        self.assertTrue(any("outside the canonical repository" in item for item in status.conflicts))

        overlapping_backups = self.skills_target / "backups"
        status = skills.opencode_sync_status(
            self.root, self.agents_target, self.skills_target, self.global_target,
            backup_root=overlapping_backups,
        )
        self.assertTrue(any("backup directory must be separate" in item for item in status.conflicts))

    def test_failed_verification_restores_previous_managed_instructions(self) -> None:
        self.apply()
        previous = self.agents_target.read_bytes()
        canonical = self.root / "config" / "AGENTS.md"
        canonical.write_text(canonical.read_text() + "\nUpdated canonical instruction.\n")
        skills.sync_apply(self.root, self.skills_target, self.global_target, self.shared_backups)
        with mock.patch.object(skills, "_verify_opencode", side_effect=skills.CheckError("injected")):
            with self.assertRaisesRegex(skills.CheckError, "injected"):
                self.apply()
        self.assertEqual(self.agents_target.read_bytes(), previous)


class RoutingFixtureTests(unittest.TestCase):
    def test_active_requested_workflows_stay_model_loadable(self) -> None:
        bundles = [item for item in skills.discover(REPOSITORY_ROOT) if item["lifecycle"] == "skills"
                   and "explicit" in skills.read_json(item["path"] / "metadata.json")["invocation"]]
        self.assertTrue(bundles)
        shared = skills.runtime_projection(REPOSITORY_ROOT, opencode_v2=True)
        claude, _ = skills.claude_projection(REPOSITORY_ROOT)
        for item in bundles:
            with self.subTest(skill=item["id"]):
                path = f"{item['id']}/SKILL.md"
                self.assertNotIn(b"disable-model-invocation: true", shared[path])
                self.assertNotIn(b"disable-model-invocation", claude[path])
                self.assertIn(b"opencode/autoinvoke: true", shared[path])
                self.assertIn(b"allow_implicit_invocation: true", shared[f"{item['id']}/agents/openai.yaml"])

    def test_routing_scenarios_reference_owned_skills_and_authority(self) -> None:
        scenarios = json.loads((REPOSITORY_ROOT / "evals" / "routing.json").read_text())
        bundles = skills.discover(REPOSITORY_ROOT)
        by_id = {item["id"]: item for item in bundles}
        self.assertGreaterEqual(len(scenarios), 10)
        for scenario in scenarios:
            with self.subTest(request=scenario["request"]):
                self.assertIn(scenario["owner"], by_id)
                expected_lifecycle = "candidates" if scenario.get("candidate") else "skills"
                self.assertEqual(by_id[scenario["owner"]]["lifecycle"], expected_lifecycle)
                self.assertTrue(scenario["authority_stop"].strip())
                for support in scenario.get("supports", []):
                    self.assertIn(support, by_id)
                    self.assertEqual(by_id[support]["lifecycle"], "skills")
                metadata = skills.read_json(by_id[scenario["owner"]]["path"] / "metadata.json")
                if scenario.get("explicit"):
                    self.assertIn("explicit", metadata["invocation"])
                if scenario.get("next"):
                    self.assertIn(scenario["next"], by_id)


class SourceUpdateTests(unittest.TestCase):
    def test_repository_root_path_uses_the_commit_tree(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "upstream"
            repo.mkdir(); git(repo, "init", "--quiet"); git(repo, "config", "user.email", "test@example.com"); git(repo, "config", "user.name", "Test")
            (repo / "SKILL.md").write_text("one\n")
            git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "one")
            pinned = git(repo, "rev-parse", "HEAD")
            tree = git(repo, "rev-parse", "HEAD^{tree}")
            source = {"repository": str(repo), "ref": pinned, "path": ".", "digest": f"git-tree:{tree}"}
            result = skills.inspect_source_update(source)
            self.assertEqual(result.status, "unchanged")
            self.assertEqual(result.pinned_digest, f"git-tree:{tree}")

    def test_exact_path_object_detects_unchanged_and_changed_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "upstream"
            repo.mkdir(); git(repo, "init", "--quiet"); git(repo, "config", "user.email", "test@example.com"); git(repo, "config", "user.name", "Test")
            (repo / "skill").mkdir(); (repo / "skill" / "SKILL.md").write_text("one\n")
            git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "one")
            pinned = git(repo, "rev-parse", "HEAD")
            source = {"repository": str(repo), "ref": pinned, "path": "skill", "digest": f"git-commit:{pinned}"}
            unchanged = skills.inspect_source_update(source)
            self.assertEqual(unchanged.status, "unchanged")
            self.assertTrue(unchanged.pinned_digest.startswith("git-tree:"))
            (repo / "unrelated.txt").write_text("unrelated\n"); git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "unrelated")
            self.assertEqual(skills.inspect_source_update(source).status, "unchanged")
            (repo / "skill" / "SKILL.md").write_text("two\n"); git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "two")
            self.assertEqual(skills.inspect_source_update(source).status, "review available")

    def test_recorded_tree_digest_is_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "upstream"
            repo.mkdir(); git(repo, "init", "--quiet"); git(repo, "config", "user.email", "test@example.com"); git(repo, "config", "user.name", "Test")
            (repo / "skill").mkdir(); (repo / "skill" / "SKILL.md").write_text("one\n")
            git(repo, "add", "."); git(repo, "commit", "--quiet", "-m", "one")
            pinned = git(repo, "rev-parse", "HEAD")
            source = {"repository": str(repo), "ref": pinned, "path": "skill", "digest": "git-tree:" + "0" * 40}
            self.assertEqual(skills.inspect_source_update(source).status, "invalid")

    def test_grouped_update_check_fetches_once_and_returns_each_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary); upstream = base / "upstream"; catalog = base / "catalog"
            upstream.mkdir(); git(upstream, "init", "--quiet"); git(upstream, "config", "user.email", "test@example.com"); git(upstream, "config", "user.name", "Test")
            (upstream / "one").mkdir(); (upstream / "two").mkdir()
            (upstream / "one" / "SKILL.md").write_text("one\n"); (upstream / "two" / "SKILL.md").write_text("two\n")
            git(upstream, "add", "."); git(upstream, "commit", "--quiet", "-m", "initial")
            pinned = git(upstream, "rev-parse", "HEAD")
            make_repo(catalog)
            for skill_id, path in (("one", "one"), ("two", "two")):
                add_skill(catalog, skill_id, origin="adapted", sources=[{
                    "repository": str(upstream), "ref": pinned, "path": path,
                    "digest": f"git-commit:{pinned}", "license": "mit-test",
                    "use": "adapted", "changes": "Adapted for the catalog.",
                }])
            results = skills.source_updates(catalog)
            self.assertEqual(len(results), 2)
            self.assertEqual({result.status for result in results}, {"unchanged"})


if __name__ == "__main__":
    unittest.main()
