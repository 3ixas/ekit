"""Focused behaviour checks for private planning state."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from datetime import date

SCRIPT = Path(__file__).parents[1] / "skills/knowledge-and-productivity/planning/scripts/planning_state.py"
spec = importlib.util.spec_from_file_location("planning_state", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PlanningStateTests(unittest.TestCase):
    def item(self, task_id, created, recurring=False, waiting=False):
        return {"id": task_id, "created_at": created, "recurring": recurring, "waiting_for_future_trigger": waiting}

    def test_stale_threshold_review_reset_unknown_and_waiting(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            data = [self.item("old", "2026-09-27"), self.item("new", "2026-09-28"),
                    self.item("unknown", None), self.item("waiting", "2026-01-01", waiting=True),
                    self.item("repeat", "2026-01-01", recurring=True)]
            result = module.stale(module.load(path, "account"), data, date(2026, 10, 27))
            self.assertEqual(result, {"eligible": ["old"], "held": ["waiting"], "unknown": ["unknown"]})
            self.assertFalse(path.exists(), "a scan must not create state or reset reviews")
            module.write_change(path, "account", lambda state: state["reviews"].__setitem__("old", "2026-10-27"))
            self.assertEqual(module.stale(module.load(path, "account"), data, date(2026, 11, 25))["eligible"], ["new"])
            self.assertIn("old", module.stale(module.load(path, "account"), data, date(2026, 11, 26))["eligible"])

    def test_snapshot_keeps_only_identifiers_and_times_and_round_trips(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            entries = module.validate_snapshot([{"id": "a", "time": "2026-10-28T20:00:00"}, {"id": "b", "time": None}], "2026-10-28")
            module.write_change(path, "account", lambda state: state["snapshots"].__setitem__("2026-10-28", {"complete": False, "items": entries}))
            self.assertEqual(module.load(path, "account")["snapshots"]["2026-10-28"]["items"], entries)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(ValueError):
                module.validate_snapshot([{"id": "a", "time": None, "title": "private"}], "2026-10-28")
            with self.assertRaises(ValueError):
                module.validate_snapshot([{"id": "a", "time": "2026-10-29T09:00:00"}], "2026-10-28")

    def test_malformed_state_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            path.write_text('{"unexpected": true}')
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                module.write_change(path, "account", lambda state: state["reviews"].__setitem__("a", "2026-10-27"))
            self.assertEqual(path.read_bytes(), before)

    def test_account_binding_and_interrupted_review_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "state.json"
            def run(command, extra=(), payload=None, account="account"):
                return subprocess.run([sys.executable, str(SCRIPT), command, "--state", str(path), "--account", account, *extra], input=json.dumps(payload) if payload is not None else None, text=True, capture_output=True)
            self.assertEqual(run("queue", payload=["missed", "moved", "partial"]).returncode, 0)
            self.assertEqual(run("review", ["--today", "2026-10-27", "--task-id", "missed"]).returncode, 0)
            self.assertEqual(json.loads(run("show").stdout)["pending"], ["missed", "moved", "partial"])
            self.assertEqual(run("resolve", ["--task-id", "missed"]).returncode, 0)
            before = path.read_bytes()
            self.assertNotEqual(run("queue", payload=["other"], account="wrong").returncode, 0)
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(json.loads(run("show").stdout)["pending"], ["moved", "partial"])
            snapshot = [{"id": "moved", "time": "2026-10-28T19:00:00"}]
            self.assertEqual(run("snapshot", ["--date", "2026-10-28"], snapshot).returncode, 0)
            self.assertFalse(json.loads(run("show").stdout)["snapshots"]["2026-10-28"]["complete"])
            self.assertEqual(run("snapshot", ["--date", "2026-10-28", "--complete"], snapshot).returncode, 0)
            self.assertTrue(json.loads(run("show").stdout)["snapshots"]["2026-10-28"]["complete"])


if __name__ == "__main__":
    unittest.main()
