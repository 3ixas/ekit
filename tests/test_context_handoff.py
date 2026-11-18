from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPOSITORY_ROOT / "plugins" / "ekit-context" / "hooks" / "context_handoff.py"


def assistant(tokens: int, sidechain: bool = False) -> dict:
    return {
        "type": "assistant",
        "isSidechain": sidechain,
        "message": {"usage": {"input_tokens": 2, "cache_creation_input_tokens": tokens - 2, "cache_read_input_tokens": 0, "output_tokens": 50}},
    }


class ContextHandoffHookTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.transcript = self.base / "session.jsonl"
        self.data = self.base / "data"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write(self, *entries: dict) -> None:
        self.transcript.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n", encoding="utf-8")

    def run_hook(self, payload: dict | None = None, **env: str) -> str:
        body = {"session_id": "s-1", "transcript_path": str(self.transcript), "hook_event_name": "UserPromptSubmit"}
        body.update(payload or {})
        environment = {**os.environ, "CLAUDE_PLUGIN_DATA": str(self.data), "CLAUDE_PLUGIN_OPTION_CONTEXT_WINDOW": "1000", **env}
        completed = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(body), capture_output=True, text=True, env=environment)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return completed.stdout

    def test_silent_below_threshold(self) -> None:
        self.write(assistant(600))
        self.assertEqual(self.run_hook(), "")

    def test_offers_handoff_once_per_crossing(self) -> None:
        self.write(assistant(720))
        output = json.loads(self.run_hook())
        context = output["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "UserPromptSubmit")
        self.assertIn("72%", context)
        self.assertIn("t3_thread_launch", context)
        self.assertEqual(self.run_hook(), "", "a second prompt above the threshold stays silent")
        self.write(assistant(300))
        self.assertEqual(self.run_hook(), "", "dropping below clears the flag")
        self.write(assistant(800))
        self.assertIn("80%", self.run_hook())

    def test_uses_latest_main_thread_usage_and_ignores_sidechains(self) -> None:
        self.write(assistant(900), assistant(100), {"type": "user"}, assistant(900, sidechain=True), {"type": "user"})
        self.assertEqual(self.run_hook(), "")

    def test_reads_only_the_transcript_tail(self) -> None:
        self.transcript.write_text(json.dumps(assistant(900)) + "\n" + "x" * 5_000_000 + "\n", encoding="utf-8")
        self.assertEqual(self.run_hook(), "", "usage older than the tail is out of reach, so the hook stays silent")

    def test_missing_or_unsafe_session_id_is_ignored(self) -> None:
        self.write(assistant(900))
        self.assertEqual(self.run_hook({"session_id": ""}), "")
        self.assertEqual(self.run_hook({"session_id": "../escape"}), "")
        self.assertEqual(self.run_hook({"session_id": ".."}), "")
        self.assertFalse((self.base / "escape").exists())

    def test_threshold_option_is_respected(self) -> None:
        self.write(assistant(550))
        self.assertIn("55%", self.run_hook(CLAUDE_PLUGIN_OPTION_HANDOFF_AT="50"))

    def test_subagent_prompt_is_ignored(self) -> None:
        self.write(assistant(900))
        self.assertEqual(self.run_hook({"agent_id": "a-1"}), "")

    def test_fails_open(self) -> None:
        self.assertEqual(self.run_hook({"transcript_path": str(self.base / "missing.jsonl")}), "")
        completed = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
        self.assertEqual((completed.returncode, completed.stdout), (0, ""))


class ContextPluginTests(unittest.TestCase):
    def test_threshold_default_matches_elias_mods(self) -> None:
        plugins = REPOSITORY_ROOT / "plugins"
        ours = json.loads((plugins / "ekit-context" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        mods = json.loads((plugins / "elias-mods" / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(ours["userConfig"]["handoff_at"]["default"], mods["userConfig"]["handoff_at"]["default"])

    @unittest.skipUnless(shutil.which("claude"), "claude CLI unavailable")
    def test_plugin_validates_strictly(self) -> None:
        completed = subprocess.run(
            ["claude", "plugin", "validate", str(REPOSITORY_ROOT / "plugins" / "ekit-context"), "--strict"],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
