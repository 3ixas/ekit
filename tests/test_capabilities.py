from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import capabilities  # noqa: E402
import skills  # noqa: E402


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


class CapabilityReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "skills" / "agent-system" / "demo").mkdir(parents=True)
        (self.root / "skills" / "agent-system" / "demo" / "SKILL.md").write_text(
            "---\nname: demo\ndescription: Use the demo workflow for a focused test.\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        write_json(self.root / "skills" / "agent-system" / "demo" / "metadata.json", {
            "id": "demo",
            "group": "agent-system",
            "origin": "original",
            "invocation": ["automatic", "supporting", "explicit"],
            "sources": [],
            "dependencies": {"skills": [], "tools": ["github", "stitch", "browser"]},
            "reviewed": "2026-09-26",
        })
        write_json(self.root / "config" / "tools.json", {
            "browser": {"kind": "connector", "capability": "inspect a rendered browser"},
            "github": {"kind": "executable", "probe": ["gh", "auth", "status"]},
            "stitch": {"kind": "connector", "capability": "edit a Google Stitch design"},
        })
        manifest = json.loads((REPOSITORY_ROOT / "config" / "agent-capabilities.json").read_text(encoding="utf-8"))
        write_json(self.root / "config" / "agent-capabilities.json", manifest)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_reports_per_host_routing_tool_states_and_skill_impacts_without_probe_output(self) -> None:
        credential_output = "account elias ghp_SHOULD_NEVER_APPEAR_IN_REPORT"
        run = mock.Mock(return_value=subprocess.CompletedProcess([], 0, credential_output, ""))
        report = capabilities.build_report(
            self.root,
            which=lambda executable: "/usr/bin/" + executable,
            run=run,
        )

        self.assertEqual({agent["id"] for agent in report["agents"]}, {"codex", "claude-code", "opencode"})
        for agent in report["agents"]:
            self.assertEqual(agent["tools"]["github"]["status"], "available")
            self.assertEqual(agent["tools"]["stitch"]["status"], "unverified")
            self.assertEqual(agent["tools"]["browser"]["status"], "unverified")
            self.assertEqual(agent["orchestration"]["issue_tracker"]["status"], "unverified")
            self.assertEqual(agent["skill_dependency_impacts"]["unverified"], ["demo (browser, stitch)"])
            self.assertEqual(agent["routing"]["supporting"]["status"], "unsupported")
            self.assertTrue(agent["routing"]["supporting"]["fallback"])
            self.assertEqual(agent["skill_routing_impacts"]["unsupported"], ["demo (supporting)"])
        self.assertEqual(report["agents"][0]["skill_routing_impacts"]["unverified"], [])
        self.assertEqual(report["agents"][2]["skill_routing_impacts"]["unverified"], [])
        self.assertEqual(report["agents"][0]["orchestration"]["model_roles"]["status"], "unverified")
        self.assertEqual(report["agents"][1]["orchestration"]["model_roles"]["status"], "available")
        serialized = json.dumps(report)
        self.assertNotIn("ghp_SHOULD_NEVER_APPEAR_IN_REPORT", serialized)
        self.assertNotIn("account elias", serialized)
        run.assert_called_once_with(
            ["/usr/bin/gh", "auth", "status"], capture_output=True, text=True, check=False, timeout=8,
        )

    def test_missing_executable_is_reported_as_missing_without_running_probe(self) -> None:
        run = mock.Mock()
        report = capabilities.build_report(self.root, which=lambda _: None, run=run)
        self.assertTrue(all(agent["tools"]["github"]["status"] == "missing" for agent in report["agents"]))
        self.assertTrue(all(agent["skill_dependency_impacts"]["missing"] == ["demo (github)"] for agent in report["agents"]))
        self.assertTrue(all("do not claim workflows" in agent["tools"]["github"]["detail"] for agent in report["agents"]))
        run.assert_not_called()

    def test_auth_and_network_failures_remain_unverified_and_hide_raw_output(self) -> None:
        def report_for(stdout: str) -> dict:
            return capabilities.build_report(
                self.root,
                which=lambda _: "/usr/bin/gh",
                run=lambda *args, **kwargs: subprocess.CompletedProcess([], 1, stdout, ""),
            )

        auth_failure = report_for("You are not logged in to any GitHub hosts")
        network_failure = report_for("error connecting to api.github.com")
        self.assertEqual(auth_failure["agents"][0]["tools"]["github"]["status"], "unverified")
        self.assertEqual(network_failure["agents"][0]["tools"]["github"]["status"], "unverified")
        self.assertNotIn("api.github.com", json.dumps(network_failure))
        self.assertIn("host/keyring-enabled context", json.dumps(auth_failure))

    def test_issue_tracker_permission_is_not_inferred_from_local_cli_auth_or_entrypoint(self) -> None:
        authenticated = capabilities.build_report(
            self.root,
            which=lambda executable: "/usr/bin/" + executable,
            run=lambda *args, **kwargs: subprocess.CompletedProcess([], 0, "", ""),
        )
        self.assertEqual(authenticated["agents"][1]["tools"]["github"]["status"], "available")
        self.assertEqual(authenticated["agents"][1]["orchestration"]["issue_tracker"]["status"], "unverified")

        no_hosts = capabilities.build_report(self.root, which=lambda _: None)
        self.assertEqual(no_hosts["agents"][1]["entrypoint"]["status"], "missing")
        self.assertEqual(no_hosts["agents"][1]["orchestration"]["issue_tracker"]["status"], "missing")

    def test_catalog_budget_warning_requires_an_explicit_local_threshold(self) -> None:
        no_threshold = capabilities.build_report(self.root, which=lambda _: None)
        warning = capabilities.build_report(self.root, warning_threshold_tokens=1, which=lambda _: None)
        self.assertEqual(no_threshold["catalog"]["status"], "unverified")
        self.assertEqual(warning["catalog"]["status"], "warning")
        self.assertIn("not a product limit", warning["catalog"]["message"])
        self.assertGreater(warning["catalog"]["estimated_tokens"], 0)

    def test_requested_routing_is_model_guided_on_all_opencode_versions(self) -> None:
        with mock.patch.object(skills, "opencode_major_version", return_value=2):
            v2 = capabilities.build_report(self.root, which=lambda _: None)
        with mock.patch.object(skills, "opencode_major_version", return_value=1):
            v1 = capabilities.build_report(self.root, which=lambda _: None)
        with mock.patch.object(skills, "opencode_major_version", return_value=None):
            unknown = capabilities.build_report(self.root, which=lambda _: None)
        self.assertEqual(v2["agents"][2]["routing"]["explicit"]["status"], "available")
        self.assertEqual(v1["agents"][2]["routing"]["explicit"]["status"], "available")
        self.assertEqual(unknown["agents"][2]["routing"]["explicit"]["status"], "available")
        self.assertEqual(v2["agents"][2]["skill_routing_impacts"]["unverified"], [])
        self.assertEqual(v1["agents"][2]["skill_routing_impacts"]["unsupported"], ["demo (supporting)"])
        self.assertEqual(unknown["agents"][2]["skill_routing_impacts"]["unverified"], [])

    def test_filtered_text_report_names_unsupported_skill_invocation(self) -> None:
        report = capabilities.build_report(self.root, skill_id="demo", which=lambda _: None)
        rendered = capabilities.render_report(report)
        self.assertIn("Skills with unsupported invocation mappings: 1 — demo (supporting)", rendered)


if __name__ == "__main__":
    unittest.main()
