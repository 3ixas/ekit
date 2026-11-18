"""UserPromptSubmit hook: tell Claude to offer a handoff once context passes a threshold.

A plain Claude Code command hook, so it runs on Claude Code Desktop and in T3 Code,
where the Desktop band does not draw. Context fill comes from the transcript's latest
main-thread usage. The hook fails open: any error prints nothing and exits 0.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

DEFAULT_THRESHOLD = 70
DEFAULT_WINDOW = 1_000_000
TAIL_BYTES = 4 * 1024 * 1024


def _number(name: str, default: int) -> int:
    try:
        value = int(float(os.environ.get(name, "")))
    except (ValueError, OverflowError):
        return default
    return value if value > 0 else default


def context_tokens(transcript: Path) -> int | None:
    """Tokens the main thread sent with its latest model call."""
    with transcript.open("rb") as handle:
        handle.seek(0, os.SEEK_END)
        size = handle.tell()
        handle.seek(max(0, size - TAIL_BYTES))
        lines = handle.read().splitlines()
    for raw in reversed(lines):
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("type") != "assistant" or entry.get("isSidechain"):
            continue
        usage = (entry.get("message") or {}).get("usage")
        if isinstance(usage, dict):
            return sum(int(usage.get(key) or 0) for key in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return None


def message(percent: int, tokens: int, window: int) -> str:
    return (
        f"Context for this conversation is at {percent}% ({tokens:,} of {window:,} tokens), past Elias's handoff threshold. "
        "Along with this turn's answer, offer Elias a handoff with the handoff skill. "
        "In T3 Code, once Elias approves and the handoff file is written, open a new thread with t3_thread_launch "
        "whose prompt asks it to use the pickup skill on that file, and give Elias the thread."
    )


def run(payload: dict, state_root: Path) -> str | None:
    if payload.get("agent_id"):
        return None
    transcript = payload.get("transcript_path")
    session = str(payload.get("session_id") or "")
    if not transcript or not session or Path(session).name != session or session.startswith("."):
        return None
    tokens = context_tokens(Path(transcript))
    if tokens is None:
        return None
    window = _number("CLAUDE_PLUGIN_OPTION_CONTEXT_WINDOW", DEFAULT_WINDOW)
    threshold = _number("CLAUDE_PLUGIN_OPTION_HANDOFF_AT", DEFAULT_THRESHOLD)
    percent = min(100, round(tokens * 100 / window))
    flag = state_root / "context-handoff" / session
    if percent < threshold:
        flag.unlink(missing_ok=True)
        return None
    if flag.exists():
        return None
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(str(percent), encoding="utf-8")
    return message(percent, tokens, window)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
        state_root = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or Path.home() / ".claude" / "plugins" / "data" / "ekit-context")
        text = run(payload, state_root)
    except Exception:
        return 0
    if text:
        json.dump({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": text}}, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
