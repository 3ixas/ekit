from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts" / "verification"))

import which_skill_eval as evaluation  # noqa: E402

CASE = {
    "request": "Babysit PR #118 through checks",
    "owner": "babysit-pr",
    "authority_stop": "Monitor checks and reply to feedback; never merge, deploy, or change the base branch.",
}
GOOD = """Owner: babysit-pr, it watches one PR through checks and review.
Brings in: pr-feedback, ci
Say: "Babysit PR #118"
Stops at: Monitors checks and replies to review feedback; it never merges, deploys, or changes
the base branch.
Also worth naming: full-send when you also want it merged

Want me to start babysit-pr?"""


class ParseTests(unittest.TestCase):
    def test_parses_plain_and_markdown_labels(self) -> None:
        owners, stops = evaluation.parse_recommendation(GOOD)
        self.assertEqual(owners, ["babysit-pr"])
        self.assertIn("never merges, deploys", stops)
        self.assertIn("base branch", stops)
        self.assertNotIn("Also worth naming", stops)
        owners, stops = evaluation.parse_recommendation("**Owner:** `debug`, cause unknown\n**Stops at:** works locally")
        self.assertEqual((owners, stops), (["debug"], "works locally"))

    def test_ambiguous_answer_reads_stops_at_from_the_first_block(self) -> None:
        text = "If A:\nOwner: debug, a\nStops at: works locally\n\nIf B:\nOwner: implement, b\nStops at: task branch only"
        owners, stops = evaluation.parse_recommendation(text)
        self.assertEqual((owners, stops), (["debug", "implement"], "works locally"))

    def test_no_owner_line(self) -> None:
        self.assertEqual(evaluation.parse_recommendation("No skill applies; ask normally."), ([], ""))


class JudgeTests(unittest.TestCase):
    def test_exact_owner_and_boundary_pass(self) -> None:
        outcome = evaluation.judge("claude", 0, CASE, GOOD, CASE["authority_stop"])
        self.assertEqual(outcome.status, "pass")
        self.assertTrue(outcome.boundary_checked)

    def test_owner_must_match_exactly(self) -> None:
        wrong = GOOD.replace("Owner: babysit-pr", "Owner: full-send")
        outcome = evaluation.judge("codex", 0, CASE, wrong, CASE["authority_stop"])
        self.assertEqual(outcome.status, "fail")
        self.assertIn("expected 'babysit-pr'", outcome.reason)

    def test_missing_boundary_fails_side_effecting_owner_only(self) -> None:
        vague = GOOD.replace("Stops at: Monitors checks", "Stops at: Whatever you like. Monitors checks").split("Stops at:")[0]
        vague += "Stops at: works locally"
        failing = evaluation.judge("claude", 0, CASE, vague, "Monitor checks, reply to feedback, never merge or deploy.")
        self.assertEqual(failing.status, "fail")
        self.assertIn("labelled boundary", failing.reason)
        local = evaluation.judge("claude", 0, CASE, vague, "")
        self.assertEqual(local.status, "pass")
        self.assertFalse(local.boundary_checked)

    def test_owner_declared_stop_also_satisfies_the_boundary(self) -> None:
        case = dict(CASE, authority_stop="Reuse the existing smoke-test harness without a duplicate guide.")
        declared = "Authorizes task-branch work and guarded merge; deployment and paid actions require separate authority."
        faithful = "Owner: implement, x\nStops at: Task-branch work and guarded merge; deployment and paid actions need separate authority."
        self.assertEqual(evaluation.judge("codex", 0, dict(case, owner="implement"), faithful, declared).status, "pass")
        outcome_only = "Owner: implement, x\nStops at: A merged pull request."
        self.assertEqual(evaluation.judge("codex", 0, dict(case, owner="implement"), outcome_only, declared).status, "fail")

    def test_quota_message_is_not_a_recommendation(self) -> None:
        self.assertTrue(evaluation.QUOTA_RE.search("You've hit your 5-hour limit · resets 9:50pm"))
        self.assertFalse(evaluation.QUOTA_RE.search(GOOD))

    def test_short_label_needs_every_keyword(self) -> None:
        ok, shared = evaluation.boundary_overlap("Never publish", "It will never publish anything")
        self.assertTrue(ok)
        self.assertEqual(shared, ["never", "publish"])


class NoFitTests(unittest.TestCase):
    CASE = {"request": "Explain what Teach does", "no_fit": True, "must_not_execute": ["teach"], "authority_stop": "x"}

    def test_plain_no_skill_answer_passes(self) -> None:
        outcome = evaluation.judge("codex", 43, self.CASE, "No EKit skill applies. Just ask normally.", "")
        self.assertEqual(outcome.status, "pass")

    def test_any_owner_fails(self) -> None:
        outcome = evaluation.judge("codex", 43, self.CASE, "Owner: teach, it teaches\nStops at: works locally", "")
        self.assertEqual(outcome.status, "fail")
        self.assertIn("expected no skill", outcome.reason)


class IsolationTests(unittest.TestCase):
    def test_workspace_holds_this_checkout_active_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            workspace = evaluation.prepare_workspace(Path(root))
            for parent in (".claude/skills", ".agents/skills"):
                bundle = workspace / parent / "which-skill"
                source = REPOSITORY_ROOT / "skills" / "agent-system" / "which-skill" / "SKILL.md"
                self.assertEqual((bundle / "SKILL.md").read_text(), source.read_text())
                self.assertTrue((workspace / parent / "implement" / "SKILL.md").exists())
                self.assertFalse((bundle / "metadata.json").exists())

    def captured_call(self, host: str, scratch: Path) -> mock.Mock:
        done = mock.Mock(returncode=0, stdout=GOOD, stderr="")
        with mock.patch.object(evaluation.subprocess, "run", return_value=done) as run:
            evaluation.ask(host, "prompt", scratch, None, 5, scratch)
        return run.call_args

    def test_claude_ignores_installed_personal_skills(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            command = self.captured_call("claude", Path(root)).args[0]
        self.assertEqual(command[command.index("--setting-sources") + 1], "project")
        self.assertIn("--no-session-persistence", command)

    def test_quota_error_on_stderr_or_stdout_raises_quota_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            scratch = Path(root)
            stderr_limit = mock.Mock(returncode=1, stdout="", stderr="You’ve hit your usage limit.")
            with mock.patch.object(evaluation.subprocess, "run", return_value=stderr_limit):
                with self.assertRaises(evaluation.QuotaError):
                    evaluation.ask("codex", "prompt", scratch, None, 5, scratch)
            stdout_limit = mock.Mock(returncode=0, stdout="You've hit your 5-hour limit", stderr="")
            with mock.patch.object(evaluation.subprocess, "run", return_value=stdout_limit):
                with self.assertRaises(evaluation.QuotaError):
                    evaluation.ask("claude", "prompt", scratch, None, 5, scratch)

    def test_quota_error_skips_remaining_cases_for_that_host(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=evaluation.QuotaError("claude refused: limit")) as ask_mock,
            ):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = evaluation.main(["--host", "claude", "--jobs", "1", "--only", "0", "1", "2", "--output-dir", str(out_dir)])
            self.assertEqual(code, 1)
            self.assertEqual(ask_mock.call_count, 1)
            self.assertIn("skipped after quota/rate limit", out.getvalue())

    def test_codex_hides_installed_skills_and_keeps_its_sign_in(self) -> None:
        with tempfile.TemporaryDirectory() as root, mock.patch.dict(evaluation.os.environ, {}, clear=True):
            expected = str(Path.home() / ".codex")
            env = self.captured_call("codex", Path(root)).kwargs["env"]
            self.assertEqual(env["HOME"], str(Path(root) / "home"))
        self.assertEqual(env["CODEX_HOME"], expected)


class RunnerTests(unittest.TestCase):
    def run_main(self, argv: list[str]) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = evaluation.main(argv)
        return code, out.getvalue()

    def test_skips_cleanly_without_the_clis(self) -> None:
        with mock.patch.object(evaluation.shutil, "which", return_value=None):
            code, output = self.run_main([])
        self.assertEqual(code, 0)
        self.assertIn("Skipping claude", output)
        self.assertIn("Skipping codex", output)
        self.assertIn("skipping the which-skill behavioural eval", output)

    def test_every_routing_case_can_be_loaded_with_its_side_effect_flag(self) -> None:
        cases, side_effecting = evaluation.load_cases(None)
        self.assertGreaterEqual(len(cases), 75)
        self.assertTrue(side_effecting["implement"])
        self.assertEqual(side_effecting["debug"], "")


if __name__ == "__main__":
    unittest.main()
