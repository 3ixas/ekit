from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import threading
import time
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

    def test_empty_or_off_topic_answer_fails_no_fit(self) -> None:
        empty = evaluation.judge("codex", 43, self.CASE, "   ", "")
        self.assertEqual(empty.status, "fail")
        self.assertIn("empty", empty.reason)
        executed = evaluation.judge("codex", 43, self.CASE, "Teach is a guided mission workflow.", "")
        self.assertEqual(executed.status, "fail")
        self.assertIn("no skill applies", executed.reason)


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

    def test_nonzero_exit_with_stdout_raises_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            scratch = Path(root)
            crashed = mock.Mock(returncode=1, stdout="Authentication failed", stderr="")
            with mock.patch.object(evaluation.subprocess, "run", return_value=crashed):
                with self.assertRaises(RuntimeError) as context:
                    evaluation.ask("claude", "prompt", scratch, None, 5, scratch)
            self.assertNotIsInstance(context.exception, evaluation.QuotaError)
            self.assertIn("exited 1", str(context.exception))

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

    def test_every_routing_case_can_be_loaded_with_its_declared_stop(self) -> None:
        cases, declared_stops = evaluation.load_cases(None)
        self.assertGreaterEqual(len(cases), 75)
        self.assertTrue(declared_stops["implement"])
        self.assertEqual(declared_stops["debug"], "")

    def test_bare_only_flag_is_rejected(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exited:
                evaluation.main(["--only"])
        self.assertEqual(exited.exception.code, 2)

    def test_jobs_caps_concurrency_per_host(self) -> None:
        active: dict[str, int] = {"claude": 0, "codex": 0}
        peak: dict[str, int] = {"claude": 0, "codex": 0}
        lock = threading.Lock()

        def fake_ask(host: str, *_args) -> str:
            with lock:
                active[host] += 1
                peak[host] = max(peak[host], active[host])
            time.sleep(0.02)
            with lock:
                active[host] -= 1
            return "Owner: debug, unknown cause\nStops at: works locally"

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}"),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask),
            ):
                code, _ = self.run_main(["--host", "all", "--jobs", "1", "--only", "0", "18", "31", "--output-dir", str(out_dir)])
        self.assertEqual(code, 1)  # cases 18/31 expect how/verify, not debug
        self.assertEqual(peak, {"claude": 1, "codex": 1})


def _passing_answer(case: dict, declared_stop: str) -> str:
    if case.get("no_fit"):
        return "No EKit skill applies. Ask normally."
    stops = declared_stop or case.get("authority_stop") or "works locally"
    return f"Owner: {case['owner']}, matches request.\nStops at: {stops}"


def _run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = evaluation.main(argv)
    return code, out.getvalue(), err.getvalue()


class ResumeTests(unittest.TestCase):
    def test_resume_requires_output_dir(self) -> None:
        code, _out, err = _run_main(["--resume"])
        self.assertEqual(code, 2)
        self.assertIn("--output-dir", err)

    def test_resume_skips_passed_and_reruns_failed_errored_and_missing(self) -> None:
        cases, declared = evaluation.load_cases(["0", "18", "31", "2"])
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            # First run on 3 cases: 0 passes, 18 fails (wrong owner), 31 errors (RuntimeError). Case 2 is missing.
            first_calls: list[int] = []

            def fake_ask_first(_host: str, prompt: str, *_args) -> str:
                request = prompt.split("Request: ", 1)[1]
                index, case, stop = by_request[request]
                first_calls.append(index)
                if index == 0:
                    return _passing_answer(case, stop)
                if index == 18:
                    return "Owner: debug, wrong owner\nStops at: works locally"
                raise RuntimeError("transient cli crash")

            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask_first),
            ):
                code, _out, _err = _run_main(
                    ["--host", "claude", "--claude-model", "sonnet", "--jobs", "1", "--only", "0", "18", "31", "--output-dir", str(out_dir)]
                )
            self.assertEqual(code, 1)
            self.assertEqual(sorted(first_calls), [0, 18, 31])

            saved = json.loads((out_dir / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["fingerprint"], evaluation.compute_fingerprint(declared))
            self.assertEqual({item["index"]: item["status"] for item in saved["outcomes"]}, {0: "pass", 18: "fail", 31: "error"})
            self.assertTrue(all(item["model"] == "sonnet" for item in saved["outcomes"]))

            # Resume across 0, 18, 31, and newly added missing case 2 with matching model: case 0 must be skipped.
            second_calls: list[int] = []

            def fake_ask_second(_host: str, prompt: str, *_args) -> str:
                request = prompt.split("Request: ", 1)[1]
                index, case, stop = by_request[request]
                second_calls.append(index)
                return _passing_answer(case, stop)

            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask_second),
            ):
                code, out, err = _run_main(
                    [
                        "--host", "claude", "--claude-model", "sonnet", "--jobs", "1",
                        "--only", "0", "18", "31", "2", "--output-dir", str(out_dir), "--resume",
                    ]
                )
            self.assertEqual(code, 0, err)
            self.assertEqual(sorted(second_calls), [2, 18, 31])
            self.assertNotIn(0, second_calls)
            self.assertIn("reusing 1 passed case(s)", out)
            self.assertIn("claude: 4/4 pass", out)

            # Resuming again when all selected cases already passed makes zero CLI or workspace calls.
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace") as prep_mock,
                mock.patch.object(evaluation, "ask") as ask_mock,
            ):
                code, out, _err = _run_main(
                    [
                        "--host", "claude", "--claude-model", "sonnet",
                        "--only", "0", "18", "31", "2", "--output-dir", str(out_dir), "--resume",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(prep_mock.call_count, 0)
            self.assertEqual(ask_mock.call_count, 0)
            self.assertIn("all 4 selected case(s) already passed", out)

    def test_resume_rejects_model_mismatch_without_overwriting(self) -> None:
        cases, _declared = evaluation.load_cases(["0"])
        index, case, stop = cases[0]
        answer = _passing_answer(case, stop)
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", return_value=answer),
            ):
                code1, _, _ = _run_main(["--host", "claude", "--claude-model", "sonnet", "--only", str(index), "--output-dir", str(out_dir)])
            self.assertEqual(code1, 0)
            before = (out_dir / "results.json").read_text(encoding="utf-8")

            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "ask") as ask_mock,
            ):
                code2, _out, err = _run_main(
                    ["--host", "claude", "--claude-model", "opus", "--only", str(index), "--output-dir", str(out_dir), "--resume"]
                )
            self.assertEqual(code2, 2)
            self.assertIn("model mismatch", err)
            self.assertEqual(ask_mock.call_count, 0)
            self.assertEqual((out_dir / "results.json").read_text(encoding="utf-8"), before)

    def test_resume_preserves_other_host_outcomes(self) -> None:
        cases, _declared = evaluation.load_cases(["0"])
        index, case, stop = cases[0]
        answer = _passing_answer(case, stop)
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}"),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", return_value=answer) as ask_mock,
            ):
                code1, _, _ = _run_main(["--host", "claude", "--claude-model", "sonnet", "--only", str(index), "--output-dir", str(out_dir)])
                code2, _, _ = _run_main(
                    ["--host", "codex", "--codex-model", "gpt-6-luna", "--only", str(index), "--output-dir", str(out_dir), "--resume"]
                )
            self.assertEqual((code1, code2), (0, 0))
            self.assertEqual(ask_mock.call_count, 2)
            saved = json.loads((out_dir / "results.json").read_text(encoding="utf-8"))
            self.assertEqual({(item["host"], item["index"]) for item in saved["outcomes"]}, {("claude", index), ("codex", index)})

    def test_resume_rejects_mismatched_fingerprint_and_changes_on_input_edit(self) -> None:
        base_fp = evaluation.compute_fingerprint()
        orig_claude, orig_notes = evaluation.skills.claude_projection(evaluation.REPOSITORY_ROOT)
        mutated_claude = dict(orig_claude)
        mutated_claude["which-skill/SKILL.md"] = mutated_claude["which-skill/SKILL.md"] + b"\n# changed\n"
        with mock.patch.object(evaluation.skills, "claude_projection", return_value=(mutated_claude, orig_notes)):
            bundle_changed_fp = evaluation.compute_fingerprint()
        self.assertNotEqual(base_fp, bundle_changed_fp)

        real_read_bytes = Path.read_bytes

        def fake_read_bytes(path_obj: Path) -> bytes:
            data = real_read_bytes(path_obj)
            return data + b"\n" if path_obj == evaluation.REPOSITORY_ROOT / "evals" / "routing.json" else data

        with mock.patch.object(Path, "read_bytes", fake_read_bytes):
            routing_changed_fp = evaluation.compute_fingerprint()
        self.assertNotEqual(base_fp, routing_changed_fp)

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            out_dir.mkdir()
            results_path = out_dir / "results.json"
            original_payload = json.dumps({"fingerprint": "0" * 64, "outcomes": []})
            results_path.write_text(original_payload, encoding="utf-8")
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "ask") as ask_mock,
            ):
                code, _out, err = _run_main(["--host", "claude", "--only", "0", "--output-dir", str(out_dir), "--resume"])
            self.assertEqual(code, 2)
            self.assertIn("fingerprint mismatch", err)
            self.assertEqual(ask_mock.call_count, 0)
            self.assertEqual(results_path.read_text(encoding="utf-8"), original_payload)

    def test_resume_rejects_legacy_or_corrupt_results(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            out_dir.mkdir()
            results_path = out_dir / "results.json"
            for bad_content in ("[]", "{not valid json", json.dumps({"fingerprint": evaluation.compute_fingerprint(), "outcomes": [{"host": "claude"}]})):
                results_path.write_text(bad_content, encoding="utf-8")
                with (
                    mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                    mock.patch.object(evaluation, "ask") as ask_mock,
                ):
                    code, _out, err = _run_main(["--host", "claude", "--only", "0", "--output-dir", str(out_dir), "--resume"])
                self.assertEqual(code, 2)
                self.assertIn("Cannot resume", err)
                self.assertEqual(ask_mock.call_count, 0)

    def test_save_results_cleans_up_temp_file_on_write_error(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root)
            results_path = out_dir / "results.json"
            real_ntf = evaluation.tempfile.NamedTemporaryFile

            class FailingHandle:
                def __init__(self, wrapped) -> None:
                    self._wrapped = wrapped
                    self.name = wrapped.name

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return self._wrapped.__exit__(exc_type, exc, tb)

                def write(self, _data: str) -> int:
                    raise OSError("disk full")

            def fake_ntf(*args, **kwargs):
                return FailingHandle(real_ntf(*args, **kwargs))

            with mock.patch.object(evaluation.tempfile, "NamedTemporaryFile", side_effect=fake_ntf):
                with self.assertRaises(OSError):
                    evaluation.save_results(results_path, "a" * 64, {})
            self.assertEqual(list(out_dir.iterdir()), [])


class CanaryTests(unittest.TestCase):
    FIVE_CASES = ["0", "2", "9", "10", "13"]
    SIX_CASES = ["0", "2", "9", "10", "13", "14"]

    def test_canary_runs_one_case_per_host_before_fanout_and_persists_independently(self) -> None:
        cases, _declared = evaluation.load_cases(self.SIX_CASES)
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}
        first_index = cases[0][0]
        events: dict[str, list[tuple[str, int]]] = {"claude": [], "codex": []}
        active: dict[str, int] = {"claude": 0, "codex": 0}
        peak_after_canary: dict[str, int] = {"claude": 0, "codex": 0}
        canary_done: dict[str, bool] = {"claude": False, "codex": False}
        codex_canary_release = threading.Event()
        fanout_barrier = {host: threading.Barrier(2, timeout=5) for host in ("claude", "codex")}
        claude_fanout_persisted_while_codex_waiting = False
        lock = threading.Lock()

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            results_path = out_dir / "results.json"

            def fake_ask(host: str, prompt: str, *_args) -> str:
                nonlocal claude_fanout_persisted_while_codex_waiting
                request = prompt.split("Request: ", 1)[1]
                index, case, stop = by_request[request]
                with lock:
                    events[host].append(("start", index))
                    active[host] += 1
                    is_canary = not canary_done[host]
                    if is_canary:
                        self.assertEqual(index, first_index)
                        self.assertEqual(active[host], 1)
                    else:
                        peak_after_canary[host] = max(peak_after_canary[host], active[host])
                if is_canary and host == "codex":
                    # Wait until claude has persisted a post-canary outcome before releasing codex's canary.
                    deadline = time.monotonic() + 5.0
                    while time.monotonic() < deadline:
                        if results_path.exists():
                            saved = json.loads(results_path.read_text(encoding="utf-8"))
                            claude_saved = {item["index"] for item in saved["outcomes"] if item["host"] == "claude"}
                            if len(claude_saved) >= 2:
                                claude_fanout_persisted_while_codex_waiting = True
                                break
                        codex_canary_release.wait(0.01)
                elif not is_canary and index in (cases[1][0], cases[2][0]):
                    fanout_barrier[host].wait()
                with lock:
                    active[host] -= 1
                    events[host].append(("end", index))
                    if is_canary:
                        canary_done[host] = True
                return _passing_answer(case, stop)

            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}"),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask),
            ):
                code, out, err = _run_main(
                    ["--host", "all", "--jobs", "3", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 0, err)
        for host in ("claude", "codex"):
            self.assertIn(f"Running canary case {first_index} on {host}", out)
            self.assertEqual(events[host][:2], [("start", first_index), ("end", first_index)])
            self.assertGreaterEqual(peak_after_canary[host], 2)
        self.assertTrue(claude_fanout_persisted_while_codex_waiting)

    def test_canary_does_not_activate_at_or_below_threshold(self) -> None:
        cases, _declared = evaluation.load_cases(self.FIVE_CASES)
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}
        barrier = threading.Barrier(2, timeout=5)

        def fake_ask(_host: str, prompt: str, *_args) -> str:
            request = prompt.split("Request: ", 1)[1]
            index, case, stop = by_request[request]
            if index in (cases[0][0], cases[1][0]):
                barrier.wait()
            return _passing_answer(case, stop)

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask),
            ):
                code, out, err = _run_main(
                    ["--host", "claude", "--jobs", "2", "--only", *self.FIVE_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 0, err)
        self.assertNotIn("Running canary case", out)

    def test_canary_quota_error_stops_only_that_host_after_one_session(self) -> None:
        cases, _declared = evaluation.load_cases(self.SIX_CASES)
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}
        calls: dict[str, int] = {"claude": 0, "codex": 0}
        lock = threading.Lock()

        def fake_ask(host: str, prompt: str, *_args) -> str:
            with lock:
                calls[host] += 1
            if host == "claude":
                raise evaluation.QuotaError("claude refused: 5-hour limit")
            request = prompt.split("Request: ", 1)[1]
            _index, case, stop = by_request[request]
            return _passing_answer(case, stop)

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}"),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask),
            ):
                code, out, _err = _run_main(
                    ["--host", "all", "--jobs", "3", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 1)
        self.assertEqual(calls["claude"], 1)
        self.assertEqual(calls["codex"], len(self.SIX_CASES))
        self.assertIn("claude skipped after quota/rate limit", out)
        self.assertIn(f"codex: {len(self.SIX_CASES)}/{len(self.SIX_CASES)} pass", out)

    def test_canary_runtime_error_skips_remaining_cases(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=RuntimeError("Authentication failed")) as ask_mock,
            ):
                code, out, _err = _run_main(
                    ["--host", "claude", "--jobs", "3", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 1)
        self.assertEqual(ask_mock.call_count, 1)
        self.assertIn("claude skipped after canary error", out)

    def test_canary_routing_fail_still_fans_out(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", return_value="Owner: wrong-skill, nope\nStops at: works locally") as ask_mock,
            ):
                code, _out, _err = _run_main(
                    ["--host", "claude", "--jobs", "3", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 1)
        self.assertEqual(ask_mock.call_count, len(self.SIX_CASES))

    def test_no_canary_fans_out_immediately(self) -> None:
        cases, _declared = evaluation.load_cases(self.SIX_CASES)
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}
        barrier = threading.Barrier(2, timeout=5)

        def fake_ask(_host: str, prompt: str, *_args) -> str:
            request = prompt.split("Request: ", 1)[1]
            index, case, stop = by_request[request]
            if index in (cases[0][0], cases[1][0]):
                barrier.wait()
            return _passing_answer(case, stop)

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask),
            ):
                code, out, err = _run_main(
                    ["--host", "claude", "--jobs", "3", "--no-canary", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)]
                )
        self.assertEqual(code, 0, err)
        self.assertNotIn("Running canary case", out)

    def test_interrupt_preserves_completed_outcomes_and_cancels_remaining(self) -> None:
        cases, _declared = evaluation.load_cases(self.SIX_CASES)
        by_request = {case["request"]: (index, case, stop) for index, case, stop in cases}
        first_index = cases[0][0]
        calls: list[int] = []
        second_started = threading.Event()
        release_second = threading.Event()
        second_done = threading.Event()
        real_wait = evaluation.wait
        real_run_case = evaluation.run_case
        wait_count = 0

        def fake_ask(_host: str, prompt: str, *_args) -> str:
            request = prompt.split("Request: ", 1)[1]
            index, case, stop = by_request[request]
            calls.append(index)
            if index != first_index:
                second_started.set()
                release_second.wait(timeout=5)
            return _passing_answer(case, stop)

        def tracked_run_case(*args, **kwargs):
            try:
                return real_run_case(*args, **kwargs)
            finally:
                if second_started.is_set():
                    second_done.set()

        def interrupting_wait(fs, **kwargs):
            nonlocal wait_count
            wait_count += 1
            if wait_count == 1:
                return real_wait(fs, **kwargs)
            second_started.wait(timeout=5)
            raise KeyboardInterrupt()

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            try:
                with (
                    mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                    mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                    mock.patch.object(evaluation, "ask", side_effect=fake_ask),
                    mock.patch.object(evaluation, "run_case", side_effect=tracked_run_case),
                    mock.patch.object(evaluation, "wait", side_effect=interrupting_wait),
                ):
                    with self.assertRaises(KeyboardInterrupt):
                        _run_main(["--host", "claude", "--jobs", "1", "--only", *self.SIX_CASES, "--output-dir", str(out_dir)])
                saved = json.loads((out_dir / "results.json").read_text(encoding="utf-8"))
                self.assertEqual([item["index"] for item in saved["outcomes"]], [first_index])
                self.assertEqual(saved["outcomes"][0]["status"], "pass")
                self.assertEqual(len(calls), 2)
            finally:
                release_second.set()
                if second_started.is_set():
                    second_done.wait(timeout=5)


class SubsetTests(unittest.TestCase):
    def test_subset_presets_are_deterministic_and_smaller_than_full_suite(self) -> None:
        full_cases, declared = evaluation.load_cases(None)
        full_explicit_owners = {case["owner"] for _i, case, _stop in full_cases if case.get("explicit")}
        full_boundary_owners = {case["owner"] for _i, case, stop in full_cases if stop}
        full_no_fit_indexes = {index for index, case, _stop in full_cases if case.get("no_fit")}

        for subset in evaluation.SUBSETS:
            first, _ = evaluation.load_cases(None, subset=subset)
            second, _ = evaluation.load_cases(None, subset=subset)
            self.assertEqual([i for i, _, _ in first], [i for i, _, _ in second])
            self.assertGreater(len(first), 0)
            self.assertLess(len(first), len(full_cases))

        sample_cases, _ = evaluation.load_cases(None, subset="sample")
        self.assertEqual({c.get("owner") for _, c, _ in sample_cases if c.get("explicit")}, full_explicit_owners)
        self.assertTrue(full_boundary_owners.issubset({c.get("owner") for _, c, s in sample_cases if s}))
        self.assertEqual({i for i, c, _ in sample_cases if c.get("no_fit")}, full_no_fit_indexes)

        explicit_cases, _ = evaluation.load_cases(None, subset="explicit")
        self.assertTrue(all(case.get("explicit") for _i, case, _stop in explicit_cases))

        boundary_cases, _ = evaluation.load_cases(None, subset="boundary")
        self.assertTrue(all(bool(stop) or case.get("no_fit") for _i, case, stop in boundary_cases))

        # Smoke test CLI execution with --subset sample using mocked CLI.
        by_request = {case["request"]: (index, case, stop) for index, case, stop in sample_cases}

        def fake_ask(_host: str, prompt: str, *_args) -> str:
            request = prompt.split("Request: ", 1)[1]
            _idx, case, stop = by_request[request]
            return _passing_answer(case, stop)

        with tempfile.TemporaryDirectory() as root:
            out_dir = Path(root) / "out"
            with (
                mock.patch.object(evaluation.shutil, "which", side_effect=lambda h: f"/usr/bin/{h}" if h == "claude" else None),
                mock.patch.object(evaluation, "prepare_workspace", return_value=Path(root)),
                mock.patch.object(evaluation, "ask", side_effect=fake_ask) as ask_mock,
            ):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = evaluation.main(["--host", "claude", "--subset", "sample", "--output-dir", str(out_dir)])
        self.assertEqual(code, 0)
        self.assertEqual(ask_mock.call_count, len(sample_cases))
        self.assertIn(f"claude: {len(sample_cases)}/{len(sample_cases)} pass", out.getvalue())

    def test_subset_and_only_are_mutually_exclusive(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exited:
                evaluation.main(["--subset", "sample", "--only", "0"])
        self.assertEqual(exited.exception.code, 2)
        with self.assertRaises(ValueError):
            evaluation.load_cases(["0"], subset="sample")


if __name__ == "__main__":
    unittest.main()
