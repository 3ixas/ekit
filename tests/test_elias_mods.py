from __future__ import annotations

import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PLUGIN = REPOSITORY_ROOT / "plugins" / "elias-mods"
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import skills  # noqa: E402


class GeneratedGuidanceMarkersTests(unittest.TestCase):
    def test_generator_still_writes_what_the_skill_guard_parses(self) -> None:
        # An installed copy of the mod reads the routing lists from the generated
        # guidance by these markers; rewording one would turn the guard off
        source = (PLUGIN / "hooks" / "route.ts").read_text(encoding="utf-8")
        block = re.search(r"PROJECTION_MARKERS = \{(.*?)\} as const", source, re.S)
        self.assertIsNotNone(block, "PROJECTION_MARKERS not found in route.ts")
        markers = re.findall(r"^\s*\w+: '([^']+)',?$", block.group(1), re.M)
        self.assertEqual(len(markers), 3, markers)
        routing = {"automatic": ["implement"], "explicit": ["wayfinder"], "supporting_only": ["tdd"]}
        rules = skills._claude_rules(Path("/home/user/.codex/AGENTS.md"), routing)
        lines = rules.splitlines()
        for marker in markers:
            self.assertTrue(any(line.startswith(marker) if marker.startswith("- ") else line == marker for line in lines), marker)
        # The items the parser reads under those markers: backticked ids on the list
        # lines, and "- `id`" bullets under the supporting-only heading
        automatic, explicit, heading = markers
        self.assertIn("`implement`", next(line for line in lines if line.startswith(automatic)))
        self.assertIn("`wayfinder`", next(line for line in lines if line.startswith(explicit)))
        self.assertIn("- `tdd`", rules.split(f"\n{heading}\n", 1)[1].splitlines())


class StatusCommandTests(unittest.TestCase):
    def test_status_command_is_a_static_skill_the_module_answers(self) -> None:
        # Desktop's command menu reads a probe that runs no hooks, so a command only
        # $.command.register declares is missing there ("isn't a command here")
        skill = (PLUGIN / "skills" / "elias-mods" / "SKILL.md").read_text(encoding="utf-8")
        self.assertRegex(skill, r"(?m)^name: elias-mods$")
        self.assertRegex(skill, r"(?m)^disable-model-invocation: true$")
        source = (PLUGIN / "hooks" / "register.ts").read_text(encoding="utf-8")
        self.assertIn("const COMMAND = 'elias-mods:elias-mods'", source)
        self.assertIn("on('command.run', { command: COMMAND }", source)
        # The engine refuses a registered name that the skill's alias already holds
        self.assertNotIn("$.command.register", source)


class MiningScriptTests(unittest.TestCase):
    def test_answer_sheet_replies_are_not_counted_as_typed(self) -> None:
        # Local diagnostics separate typed prompts from plugin-submitted replies.
        sys.path.insert(0, str(PLUGIN / "tools"))
        try:
            import mine_sessions
        finally:
            sys.path.pop(0)
        typed = {"type": "user", "message": {"content": "Q1 agreed."}, "origin": {"kind": "human"}}
        sent = {**typed, "origin": {"kind": "plugin", "name": "elias-mods", "asUser": True}}
        other = {**typed, "origin": {"kind": "plugin", "name": "someone-else"}}
        self.assertEqual(mine_sessions.typed_prompt_text(typed), "Q1 agreed.")
        self.assertIsNone(mine_sessions.typed_prompt_text(sent))
        self.assertTrue(mine_sessions.is_mod_reply(sent))
        self.assertFalse(mine_sessions.is_mod_reply(other))

    def test_summary_counts_sheet_replies_apart_and_honours_since(self) -> None:
        sys.path.insert(0, str(PLUGIN / "tools"))
        try:
            import mine_sessions
        finally:
            sys.path.pop(0)
        import json
        import tempfile

        def reply(text: str, at: str, **extra: object) -> dict:
            return {"type": "user", "entrypoint": "claude-desktop", "timestamp": at, "message": {"content": text}, **extra}

        with tempfile.TemporaryDirectory() as projects:
            session = Path(projects) / "project" / "session.jsonl"
            session.parent.mkdir()
            records = [
                reply("Yes, go ahead.", "2026-10-20T10:00:00Z"),
                reply("Agreed.", "2026-10-26T10:00:00Z"),
                reply("Q1 agreed.", "2026-10-26T11:00:00Z", origin={"kind": "plugin", "name": "elias-mods", "asUser": True}),
                reply("What does this function do?", "2026-10-26T12:00:00Z"),
            ]
            session.write_text("\n".join(json.dumps(record) for record in records), encoding="utf-8")
            original = mine_sessions.PROJECTS
            mine_sessions.PROJECTS = Path(projects)
            try:
                everything = mine_sessions.summarise(14)
                after_install = mine_sessions.summarise(14, "2026-10-25")
            finally:
                mine_sessions.PROJECTS = original
        self.assertEqual((everything["typed_prompts"], everything["pure_approval_replies"], everything["mod_replies"]), (3, 2, 1))
        self.assertEqual((after_install["typed_prompts"], after_install["pure_approval_replies"], after_install["mod_replies"]), (2, 1, 1))


@unittest.skipUnless(shutil.which("claude"), "claude CLI unavailable")
class EliasModsTests(unittest.TestCase):
    def run_claude(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["claude", "plugin", *args], cwd=PLUGIN, capture_output=True, text=True, timeout=120)

    def test_validates_strictly(self) -> None:
        result = self.run_claude("validate", "--strict", ".")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_never_hooks_tool_approval(self) -> None:
        # tool.check is the event that can approve a call; mods may observe, hold, or refuse only
        result = self.run_claude("validate", ".")
        hooks = [line for line in result.stdout.splitlines() if " hooks: " in line]
        self.assertTrue(hooks, result.stdout)
        self.assertFalse(any("tool.check" in line for line in hooks), hooks)

    def test_mod_tests_pass(self) -> None:
        result = self.run_claude("test")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("tsc"), "tsc unavailable")
    def test_type_checks_against_generated_types(self) -> None:
        # Claude Code writes these types when it loads the plugin from a directory
        config = PLUGIN / ".claude-plugin" / "types" / "tsconfig.json"
        if not config.exists():
            self.skipTest("load the plugin once to generate its types")
        result = subprocess.run(["tsc", "-p", str(config), "--noEmit"], cwd=PLUGIN, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
