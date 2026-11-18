"""Merge EKit-managed values into T3 Code's settings and check them.

T3 Code writes its own settings file whenever Elias changes something in the
app, so this projection owns individual keys, never the whole file. Every key
it does not manage survives an apply unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import skills

CheckError = skills.CheckError

SCHEMA = 1
WORKTREE_DEPTH = 3


@dataclass
class T3Paths:
    settings: Path
    state: Path
    worktrees: Path
    backups: Path


@dataclass
class T3Plan:
    """The managed changes one apply would make, and anything it cannot do."""

    desired: dict[str, Any]
    source_hash: str | None
    changes: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)


def runtime_paths(root: Path) -> T3Paths:
    raw = skills.read_json(root / "config" / "runtime.json")
    keys = ("t3_settings", "t3_state", "t3_worktrees", "t3_backups")
    if not isinstance(raw, dict) or not all(isinstance(raw.get(key), str) for key in keys):
        raise CheckError(f"{root / 'config' / 'runtime.json'}: missing T3 Code runtime paths")
    return T3Paths(*(Path(os.path.abspath(os.path.expanduser(raw[key]))) for key in keys))


def load_managed(root: Path) -> dict[str, Any]:
    path = root / "config" / "t3-settings.json"
    managed = skills.read_json(path)
    if not isinstance(managed, dict) or managed.get("schema") != SCHEMA:
        raise CheckError(f"{path}: expected schema {SCHEMA}")
    for key in ("settings", "providerEnvironment", "projects"):
        if not isinstance(managed.get(key, {}), dict):
            raise CheckError(f"{path}: {key} must be an object")
    for name, project in managed.get("projects", {}).items():
        if not isinstance(project, dict) or not isinstance(project.get("workspaceRoot"), str):
            raise CheckError(f"{path}: project {name} needs a workspaceRoot")
    return managed


def _real(path: str) -> str:
    return os.path.realpath(os.path.expanduser(path))


def project_ids(state: Path) -> dict[str, str]:
    """Map workspace roots to T3 project ids from a consistent snapshot of the live database."""
    if not state.is_file():
        return {}
    try:
        # The backup API copies one committed snapshot, even while T3 writes and checkpoints.
        source = sqlite3.connect(f"{state.resolve().as_uri()}?mode=ro", uri=True)
        snapshot = sqlite3.connect(":memory:")
        try:
            source.backup(snapshot)
            rows = snapshot.execute(
                "SELECT workspace_root, project_id FROM projection_projects WHERE deleted_at IS NULL"
            ).fetchall()
        finally:
            source.close()
            snapshot.close()
    except sqlite3.Error as exc:
        raise CheckError(f"{state}: cannot read T3 projects ({exc})") from exc
    return {_real(root): project_id for root, project_id in rows}


def _show(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 80 else text[:77] + "..."


def _note(changes: list[str], path: str, old: Any, new: Any, present: bool) -> None:
    changes.append(f"change {path}: {_show(old)} -> {_show(new)}" if present else f"add {path}: {_show(new)}")


def _merge(target: dict[str, Any], values: dict[str, Any], prefix: str, changes: list[str]) -> None:
    for key, value in values.items():
        path = f"{prefix}{key}"
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge(target[key], value, f"{path}.", changes)
        elif key == "favorites" and not prefix and isinstance(value, list):
            current = target.get(key) if isinstance(target.get(key), list) else []
            missing = [item for item in value if item not in current]
            if missing or not isinstance(target.get(key), list):
                _note(changes, path, target.get(key), current + missing, key in target)
                target[key] = current + copy.deepcopy(missing)
        elif target.get(key) != value:
            _note(changes, path, target.get(key), value, key in target)
            target[key] = copy.deepcopy(value)


def _merge_environment(settings: dict[str, Any], instance_id: str, spec: dict[str, Any], changes: list[str]) -> None:
    instances = settings.get("providerInstances")
    if not isinstance(instances, dict):
        instances = settings["providerInstances"] = {}
    instance = instances.get(instance_id)
    prefix = f"providerInstances.{instance_id}"
    if not isinstance(instance, dict):
        instance = instances[instance_id] = {"driver": spec["driver"]}
        changes.append(f"add {prefix}: {_show(instance)}")
    if not isinstance(instance.get("environment"), list):
        instance["environment"] = []
    environment = instance["environment"]
    for name, value in spec.get("variables", {}).items():
        wanted = {"name": name, "value": value, "sensitive": False}
        matches = [item for item in environment if isinstance(item, dict) and item.get("name") == name]
        if len(matches) == 1 and matches[0].get("value") == value and matches[0].get("secret") is None:
            continue
        _note(changes, f"{prefix}.environment.{name}", matches[0].get("value") if matches else None, value, bool(matches))
        environment[:] = [item for item in environment if item not in matches] + [wanted]


def _read_settings(path: Path) -> tuple[dict[str, Any], str | None]:
    if not path.exists():
        return {}, None
    content = path.read_bytes()
    try:
        current = json.loads(content)
    except json.JSONDecodeError as exc:
        raise CheckError(f"{path}: {exc}") from exc
    if not isinstance(current, dict):
        raise CheckError(f"{path}: expected a JSON object")
    return current, hashlib.sha256(content).hexdigest()


def plan(root: Path, paths: T3Paths) -> T3Plan:
    managed = load_managed(root)
    current, source_hash = _read_settings(paths.settings)
    result = T3Plan(copy.deepcopy(current), source_hash)
    desired = result.desired
    _merge(desired, managed.get("settings", {}), "", result.changes)
    for instance_id, spec in managed.get("providerEnvironment", {}).items():
        _merge_environment(desired, instance_id, spec, result.changes)
    ids = project_ids(paths.state)
    for name, project in managed.get("projects", {}).items():
        project_id = ids.get(_real(project["workspaceRoot"]))
        if project_id is None:
            result.skipped.append(f"project {name}: not added to T3 Code ({_real(project['workspaceRoot'])})")
            continue
        overrides = desired.get("projectSettingsOverrides")
        if not isinstance(overrides, dict):
            overrides = desired["projectSettingsOverrides"] = {}
        entry = overrides.get(project_id)
        if not isinstance(entry, dict):
            entry = overrides[project_id] = {}
        values = {key: value for key, value in project.items() if key != "workspaceRoot"}
        _merge(entry, values, f"projectSettingsOverrides.{project_id} ({name}).", result.changes)
    return result


def apply(root: Path, paths: T3Paths) -> Path | None:
    result = plan(root, paths)
    if not result.changes:
        return None
    if _read_settings(paths.settings)[1] != result.source_hash:
        raise CheckError(f"{paths.settings}: T3 Code changed the file during sync; nothing was written, run t3-sync again")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = paths.backups / stamp
    backup.mkdir(mode=0o700, parents=True, exist_ok=False)
    had_settings = paths.settings.exists()
    if had_settings:
        shutil.copy2(paths.settings, backup / "settings.json")
    skills.write_json(backup / "changes.json", {
        "schema": 1, "settings": str(paths.settings), "existed": had_settings, "changes": result.changes,
    })
    paths.settings.parent.mkdir(parents=True, exist_ok=True)
    stage = paths.settings.parent / f".{paths.settings.name}.ekit-{stamp}"
    installed = False
    try:
        # The file can hold provider credentials: create it private, then match the original mode.
        with os.fdopen(os.open(stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as handle:
            handle.write(json.dumps(result.desired, indent=2, ensure_ascii=False) + "\n")
        if had_settings:
            shutil.copymode(paths.settings, stage)
        written = hashlib.sha256(stage.read_bytes()).hexdigest()
        if _read_settings(paths.settings)[1] != result.source_hash:
            raise CheckError(f"{paths.settings}: T3 Code changed the file during sync; nothing was written, run t3-sync again")
        os.replace(stage, paths.settings)
        installed = True
        if plan(root, paths).changes:
            raise CheckError(f"{paths.settings}: verification failed after apply")
    except Exception as exc:
        if not installed:
            shutil.rmtree(backup, ignore_errors=True)
            raise
        # Restore only our own write: if T3 saved the file since, keep its version.
        live = hashlib.sha256(paths.settings.read_bytes()).hexdigest() if paths.settings.exists() else None
        if live != written:
            raise CheckError(f"{exc}; T3 Code saved the file meanwhile, so its version was kept (backup: {backup})") from exc
        if had_settings:
            shutil.copy2(backup / "settings.json", paths.settings)
        else:
            paths.settings.unlink(missing_ok=True)
        raise CheckError(f"{exc}; the previous file was restored") from exc
    finally:
        stage.unlink(missing_ok=True)
    return backup


def _git(tree: Path, *args: str) -> str:
    completed = subprocess.run(["git", "-C", str(tree), *args], capture_output=True, text=True)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def leftover_worktrees(worktrees: Path) -> list[str]:
    """Worktrees under T3's folder whose branch has been deleted upstream, as after a merged PR."""
    if not worktrees.is_dir():
        return []
    found = []
    frontier = [worktrees]
    for _ in range(WORKTREE_DEPTH):
        next_level = []
        for directory in frontier:
            for child in sorted(p for p in directory.iterdir() if p.is_dir() and not p.is_symlink()):
                if (child / ".git").exists():
                    branch = _git(child, "rev-parse", "--abbrev-ref", "HEAD")
                    track = _git(child, "for-each-ref", "--format=%(upstream:track)", f"refs/heads/{branch}") if branch else ""
                    if "[gone]" in track:
                        found.append(f"{child} ({branch}: gone upstream)")
                else:
                    next_level.append(child)
        frontier = next_level
    return found


def doctor(root: Path, paths: T3Paths) -> tuple[list[str], list[str]]:
    """Return (errors, warnings)."""
    result = plan(root, paths)
    errors = [f"drift: {change}" for change in result.changes]
    warnings = result.skipped + [f"leftover worktree: {item}" for item in leftover_worktrees(paths.worktrees)]
    return errors, warnings
