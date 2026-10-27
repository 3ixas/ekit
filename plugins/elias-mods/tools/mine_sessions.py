"""Summarise local Claude Code usage for an explicitly requested diagnostic.

Reads ~/.claude/projects/*/*.jsonl and prints aggregate counts only, never prompt text.
Run with: python3 -I mine_sessions.py [--days 60] [--since YYYY-MM-DD] [--json]
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import time
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"
# Background security reviews and other headless runs are not Elias typing
INTERACTIVE = {"claude-desktop", "cli"}
# A short reply that only approves or waves Claude on: what the answer sheet replaces
APPROVAL = re.compile(
    r"^\W*(yes|yep|yeah|ok|okay|sure|approved|confirmed|agreed?|go ahead|do it|do that|looks good|lgtm|sounds good|"
    r"push( it)?( and close)?|merge it|ship it|go with your|1\.\s*agreed?)\b",
    re.IGNORECASE,
)
APPROVAL_MAX_CHARS = 200
# An approval this short carries no instruction of its own, so one button could have sent it
PURE_APPROVAL_MAX_CHARS = 40
COMMAND_NAME = re.compile(r"<command-name>/?([^<]+)</command-name>")


def is_mod_reply(record: dict) -> bool:
    """True for a reply the elias-mods answer sheet submitted as Elias's words."""
    origin = record.get("origin")
    return record.get("type") == "user" and isinstance(origin, dict) and origin.get("kind") == "plugin" and origin.get("name") == "elias-mods"


def typed_prompt_text(record: dict) -> str | None:
    """Return the prompt text when the record is something the user typed."""
    if record.get("type") != "user" or record.get("isMeta") or record.get("isSidechain") or is_mod_reply(record):
        return None
    content = (record.get("message") or {}).get("content")
    if not isinstance(content, str):
        return None
    text = content.strip()
    if not text or text.startswith("<") or text.startswith("Caveat") or "Request interrupted" in text:
        return None
    return text


def percentile(values: list[int], q: float) -> int:
    ordered = sorted(values)
    return ordered[min(int(len(ordered) * q), len(ordered) - 1)] if ordered else 0


def summarise(days: int, since: str | None = None) -> dict:
    """Count over transcripts touched in the last `days`; with `since`, only records from that date on.

    Files are picked by modification time, so a session that began before the window
    and continued into it is read whole; `since` keeps its earlier records out.
    """
    cutoff = time.time() - days * 86400
    sessions = collections.Counter()
    skills = collections.Counter()
    slash_commands = collections.Counter()
    prompts = approvals = pure_approvals = mod_replies = 0
    max_context: list[int] = []
    for path in PROJECTS.glob("*/*.jsonl"):
        if path.stat().st_mtime < cutoff:
            continue
        records = []
        with path.open(errors="ignore") as lines:
            for line in lines:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    records.append(record)
        entrypoint = next((r["entrypoint"] for r in records if r.get("entrypoint")), "unknown")
        sessions[entrypoint] += 1
        if entrypoint not in INTERACTIVE:
            continue
        peak = 0
        for record in records:
            if since and str(record.get("timestamp") or "") < since:
                continue
            message = record.get("message")
            if not isinstance(message, dict):
                message = {}
            usage = message.get("usage")
            if isinstance(usage, dict):
                peak = max(peak, sum(usage.get(k) or 0 for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")))
            content = message.get("content")
            if record.get("type") == "assistant" and isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                        tool_input = block.get("input")
                        skill = tool_input.get("skill") if isinstance(tool_input, dict) else None
                        if skill:
                            skills[skill] += 1
            # Skills and commands typed as /name arrive as a command-name tag, not a Skill call
            typed = record.get("type") == "user" and not record.get("isMeta") and not record.get("isSidechain") and not is_mod_reply(record)
            if typed and isinstance(content, str):
                command = COMMAND_NAME.search(content)
                if command:
                    slash_commands[command.group(1)] += 1
            mod_replies += is_mod_reply(record)
            text = typed_prompt_text(record)
            if text:
                prompts += 1
                if len(text) <= APPROVAL_MAX_CHARS and APPROVAL.match(text):
                    approvals += 1
                    pure_approvals += len(text) <= PURE_APPROVAL_MAX_CHARS
        max_context.append(peak)
    return {
        "days": days,
        "since": since,
        "sessions_by_entrypoint": dict(sessions.most_common()),
        "typed_prompts": prompts,
        "approval_replies": approvals,
        "pure_approval_replies": pure_approvals,
        "mod_replies": mod_replies,
        "skill_loads": dict(skills.most_common(15)),
        "slash_commands": dict(slash_commands.most_common(15)),
        "peak_context_tokens": {q: percentile(max_context, p) for q, p in (("p50", 0.5), ("p75", 0.75), ("p90", 0.9), ("p99", 0.99))},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--days", type=int, default=60)
    parser.add_argument("--since", help="count only records from this date on (YYYY-MM-DD)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = summarise(args.days, args.since)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Last {result['days']} days" + (f", records from {result['since']} on" if result["since"] else ""))
    print(f"Sessions by entrypoint: {result['sessions_by_entrypoint']}")
    print(f"Typed prompts (interactive sessions): {result['typed_prompts']}")
    print(f"Approval replies: {result['approval_replies']} (pure, {PURE_APPROVAL_MAX_CHARS} chars or fewer: {result['pure_approval_replies']})")
    print(f"Replies sent from the answer sheet (not counted above): {result['mod_replies']}")
    print(f"Peak context tokens per session: {result['peak_context_tokens']}")
    for title, key in (("Skill loads (Skill tool):", "skill_loads"), ("Slash commands typed:", "slash_commands")):
        print(title)
        for name, count in result[key].items():
            print(f"  {count:4} {name}")


if __name__ == "__main__":
    main()
