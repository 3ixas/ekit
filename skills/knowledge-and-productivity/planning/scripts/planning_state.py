#!/usr/bin/env python3
"""Maintain private task-review dates and deliberately chosen daily snapshots."""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any


def date_value(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def identifier(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 256:
        raise ValueError("task ID must be a non-empty string")
    return value


def load(path: Path, account: str) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "account": account, "reviews": {}, "snapshots": {}, "pending": []}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != {"version", "account", "reviews", "snapshots", "pending"} or value["version"] != 1:
        raise ValueError("invalid state schema")
    if value["account"] != account:
        raise ValueError("state belongs to a different account")
    validate_ids(value["pending"])
    if not isinstance(value["reviews"], dict) or not isinstance(value["snapshots"], dict):
        raise ValueError("invalid state collections")
    for key, day in value["reviews"].items():
        identifier(key)
        date_value(day)
    for day, entries in value["snapshots"].items():
        date_value(day)
        if not isinstance(entries, dict) or set(entries) != {"complete", "items"} or type(entries["complete"]) is not bool:
            raise ValueError("invalid snapshot schema")
        validate_snapshot(entries["items"], day)
    return value


def validate_ids(items: Any) -> list[str]:
    if not isinstance(items, list):
        raise ValueError("IDs must be an array")
    ids = [identifier(item) for item in items]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate ID")
    return ids


def validate_snapshot(items: Any, day: str) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        raise ValueError("snapshot must be an array")
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "time"}:
            raise ValueError("snapshot items must contain only id and time")
        task_id = identifier(item["id"])
        if task_id in seen:
            raise ValueError("duplicate snapshot task ID")
        seen.add(task_id)
        value = item["time"]
        if value is not None:
            if not isinstance(value, str) or dt.datetime.fromisoformat(value).date() != date_value(day):
                raise ValueError("snapshot time must be an ISO datetime on the snapshot day")
    return items


def save(path: Path, state: dict[str, Any]) -> None:
    fd, name = tempfile.mkstemp(prefix=".planning-state-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def write_change(path: Path, account: str, change: Any) -> dict[str, Any]:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = path.with_name(path.name + ".lock")
    with lock_path.open("a", encoding="utf-8") as lock:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = load(path, account)
        change(state)
        save(path, state)
    return state


def stale(state: dict[str, Any], items: Any, today: dt.date) -> dict[str, list[str]]:
    if not isinstance(items, list):
        raise ValueError("tasks must be an array")
    output: dict[str, list[str]] = {"eligible": [], "held": [], "unknown": []}
    seen: set[str] = set()
    for item in items:
        if not isinstance(item, dict) or set(item) != {"id", "created_at", "recurring", "waiting_for_future_trigger"}:
            raise ValueError("task must contain only id, created_at, recurring and waiting_for_future_trigger")
        task_id = identifier(item["id"])
        if task_id in seen:
            raise ValueError("duplicate task ID")
        seen.add(task_id)
        if type(item["recurring"]) is not bool or type(item["waiting_for_future_trigger"]) is not bool:
            raise ValueError("recurring and waiting_for_future_trigger must be booleans")
        if item["recurring"]:
            continue
        if item["waiting_for_future_trigger"]:
            output["held"].append(task_id)
            continue
        raw = state["reviews"].get(task_id) or item["created_at"]
        try:
            start = date_value(raw[:10]) if isinstance(raw, str) else None
        except ValueError:
            start = None
        if start is None or start > today:
            output["unknown"].append(task_id)
        elif (today - start).days >= 30:
            output["eligible"].append(task_id)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("show", "stale", "review", "snapshot", "queue", "resolve"):
        p = sub.add_parser(command)
        p.add_argument("--state", type=Path, required=True)
        p.add_argument("--account", required=True)
        if command in ("stale", "review"):
            p.add_argument("--today", required=True)
        if command in ("review", "resolve"):
            p.add_argument("--task-id", required=True)
        if command == "snapshot":
            p.add_argument("--date", required=True)
            p.add_argument("--complete", action="store_true")
    args = parser.parse_args()
    try:
        account = identifier(args.account)
        if args.command == "show":
            output = load(args.state, account)
        elif args.command == "stale":
            output = stale(load(args.state, account), json.load(sys.stdin), date_value(args.today))
        elif args.command == "review":
            day = date_value(args.today).isoformat()
            task_id = identifier(args.task_id)
            output = write_change(args.state, account, lambda state: state["reviews"].__setitem__(task_id, day))
        elif args.command == "queue":
            ids = validate_ids(json.load(sys.stdin))
            def enqueue(state: dict[str, Any]) -> None:
                state["pending"].extend(item for item in ids if item not in state["pending"])
            output = write_change(args.state, account, enqueue)
        elif args.command == "resolve":
            task_id = identifier(args.task_id)
            def resolve(state: dict[str, Any]) -> None:
                if task_id in state["pending"]:
                    state["pending"].remove(task_id)
            output = write_change(args.state, account, resolve)
        else:
            day = date_value(args.date).isoformat()
            entries = validate_snapshot(json.load(sys.stdin), day)
            output = write_change(args.state, account, lambda state: state["snapshots"].__setitem__(day, {"complete": args.complete, "items": entries}))
        print(json.dumps(output, ensure_ascii=False))
        return 0
    except (ValueError, TypeError, OSError, json.JSONDecodeError) as exc:
        print(f"planning state: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
