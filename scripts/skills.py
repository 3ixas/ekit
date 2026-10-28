#!/usr/bin/env python3
"""Validate, install, update-check, and diagnose Elias's owned skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Sequence
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ("software-workflows", "engineering-specialists", "frontend-and-design", "research-and-decisions", "writing-and-artifacts", "knowledge-and-productivity", "personal-workflows", "agent-system")
LIFECYCLES = ("skills", "candidates", "paused")
INVOCATIONS = {"automatic", "supporting", "explicit"}
ORIGINS = {"original", "imported", "adapted", "synthesized"}
SOURCE_USES = {"copied", "adapted", "informed-by"}
CAPABILITY_STATUSES = {"available", "missing", "unverified", "unsupported", "conditional"}
SKILL_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DIGEST_RE = re.compile(r"^(?:sha256|git-(?:commit|tree|blob)|version):[^\s]+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\n]+)\)")
SECRET_PATTERNS = (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), re.compile(r"\bAKIA[0-9A-Z]{16}\b"), re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"))
RUNTIME_ENTRIES = {"SKILL.md", "agents", "references", "scripts", "assets", "LICENSE.txt", "NOTICE.txt"}
BUNDLE_ENTRIES = RUNTIME_ENTRIES | {"metadata.json", "evals"}
MARKER = ".elias-agent-skills.json"
MARKER_SCHEMA = 1
OPENCODE_FILE_MARKER = re.compile(rb"^<!-- elias-agent-skills opencode managed v1 sha256:([0-9a-f]{64}) -->\n")


class CheckError(ValueError):
    """A user-correctable repository or runtime integrity error."""


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CheckError(f"{path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def files_under(root: Path) -> Iterable[Path]:
    ignored = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            continue
        if path.is_file() and not any(part in ignored for part in path.relative_to(root).parts):
            yield path


def bytes_hash(content: bytes) -> str:
    return "sha256:" + hashlib.sha256(content).hexdigest()


def file_hash(path: Path) -> str:
    return bytes_hash(path.read_bytes())


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise CheckError(f"{path}: missing frontmatter")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise CheckError(f"{path}: unclosed frontmatter") from exc
    result: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        if not separator:
            raise CheckError(f"{path}: unsupported frontmatter line {line!r}")
        key = key.strip()
        if key in result:
            raise CheckError(f"{path}: duplicate frontmatter key {key}")
        result[key] = value.strip().strip('"').strip("'")
    return result


def discover(root: Path) -> list[dict[str, Any]]:
    bundles: list[dict[str, Any]] = []
    for lifecycle in LIFECYCLES:
        lifecycle_root = root / lifecycle
        if not lifecycle_root.is_dir():
            continue
        for group_dir in sorted(p for p in lifecycle_root.iterdir() if p.is_dir()):
            if group_dir.name not in GROUPS:
                continue
            for bundle in sorted(p for p in group_dir.iterdir() if p.is_dir()):
                bundles.append({"lifecycle": lifecycle, "group": group_dir.name, "id": bundle.name, "path": bundle})
    return bundles


def _safe_relative_source_path(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and "." not in path.parts


BACKTICK_REFERENCE_RE = re.compile(r"`((?:\./)?references/[^`\s]+\.md)`")


def _unlinked_reference_errors(bundle: Path) -> list[str]:
    """Every reference Markdown file must be reachable from SKILL.md through links or backticked paths."""
    references = bundle / "references"
    if not references.is_dir():
        return []
    expected = {path.resolve() for path in references.rglob("*.md") if not path.is_symlink()}
    skill = (bundle / "SKILL.md").resolve()
    seen: set[Path] = set()
    pending = [skill]
    while pending:
        current = pending.pop()
        if current in seen or not current.is_file():
            continue
        seen.add(current)
        text = current.read_text(encoding="utf-8", errors="replace")
        for raw in LINK_RE.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0]
            if target and not urlparse(target).scheme and target.endswith(".md"):
                pending.append((current.parent / target).resolve())
        for target in BACKTICK_REFERENCE_RE.findall(text):
            for base in (current.parent, bundle):
                candidate = (base / target).resolve()
                if candidate.is_file():
                    pending.append(candidate)
    return [f"{path}: reference is not linked from SKILL.md or a linked reference" for path in sorted(expected - seen)]


NAMED_PATH_RE = re.compile(r"(?<![\w/.-])((?:\./)?(?:references|scripts|assets)/[\w./-]+\.\w+)")
OTHER_SKILL_PREFIX_RE = re.compile(r"skill's\s+`?$")


def _visible_markdown(markdown: Path) -> str:
    """Return the Markdown text outside fenced code blocks."""
    visible: list[str] = []
    fence: str | None = None
    for line in markdown.read_text(encoding="utf-8").splitlines():
        stripped = line.lstrip()
        if fence is None and (stripped.startswith("```") or stripped.startswith("~~~")):
            fence = stripped[:3]
            continue
        if fence is not None and stripped.startswith(fence):
            fence = None
            continue
        if fence is None:
            visible.append(line)
    return "\n".join(visible)


def _missing_named_path_errors(bundle: Path) -> list[str]:
    """A bundle path named in prose or backticks must exist, unless it is attributed to another skill."""
    errors: list[str] = []
    snapshots = bundle / "references" / "source-methods"
    files = [bundle / "SKILL.md", *sorted((bundle / "references").rglob("*.md"))]
    for markdown in files:
        if not markdown.is_file() or markdown.is_symlink() or snapshots in markdown.parents:
            continue
        text = _visible_markdown(markdown)
        for match in NAMED_PATH_RE.finditer(text):
            if OTHER_SKILL_PREFIX_RE.search(text[max(0, match.start() - 40):match.start()]):
                continue
            target = match.group(1)
            if not any((base / target).exists() for base in (markdown.parent, bundle)):
                errors.append(f"{markdown}: names missing bundle file: {target}")
    return sorted(set(errors))


def _markdown_errors(bundle: Path) -> list[str]:
    errors: list[str] = []
    for markdown in bundle.rglob("*.md"):
        if markdown.is_symlink():
            continue
        for raw in LINK_RE.findall(_visible_markdown(markdown)):
            target = raw.strip().strip("<>").split("#", 1)[0]
            if not target or urlparse(target).scheme in {"http", "https", "mailto"}:
                continue
            candidate = (markdown.parent / target).resolve()
            try:
                candidate.relative_to(bundle.resolve())
            except ValueError:
                errors.append(f"{markdown}: link escapes its skill bundle: {raw}")
                continue
            if not candidate.exists():
                errors.append(f"{markdown}: missing linked file: {raw}")
    return errors


def _metadata_errors(root: Path, item: dict[str, Any], tools: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    bundle: Path = item["path"]
    skill_id = item["id"]
    skill_path = bundle / "SKILL.md"
    metadata_path = bundle / "metadata.json"
    if not skill_path.is_file():
        return [f"{bundle}: SKILL.md is required"], []
    try:
        fm = frontmatter(skill_path)
    except (CheckError, UnicodeDecodeError) as exc:
        errors.append(str(exc))
        fm = {}
    if fm.get("name") != skill_id:
        errors.append(f"{skill_path}: frontmatter name must equal {skill_id}")
    if not fm.get("description"):
        errors.append(f"{skill_path}: description is required")
    try:
        metadata = read_json(metadata_path)
    except CheckError as exc:
        return errors + [str(exc)], []
    if not isinstance(metadata, dict):
        return errors + [f"{metadata_path}: must contain an object"], []
    for key, expected in (("id", skill_id), ("group", item["group"])):
        if metadata.get(key) != expected:
            errors.append(f"{metadata_path}: {key} must equal {expected}")
    origin = metadata.get("origin")
    if origin not in ORIGINS:
        errors.append(f"{metadata_path}: invalid origin")
    invocation = metadata.get("invocation")
    if not isinstance(invocation, list) or not invocation or not all(isinstance(v, str) for v in invocation):
        errors.append(f"{metadata_path}: invocation must be a non-empty string list")
        invocation_values: list[str] = []
    else:
        invocation_values = invocation
        if len(set(invocation_values)) != len(invocation_values) or not set(invocation_values) <= INVOCATIONS:
            errors.append(f"{metadata_path}: invalid or duplicate invocation")
    if "explicit" in invocation_values and item["lifecycle"] == "skills":
        if fm.get("disable-model-invocation") == "true":
            errors.append(f"{bundle}: user-requested skill must remain model-loadable")
        policy_path = bundle / "agents" / "openai.yaml"
        if not policy_path.is_file() or "allow_implicit_invocation: true" not in policy_path.read_text(encoding="utf-8"):
            errors.append(f"{bundle}: user-requested skill requires model-loadable agents/openai.yaml policy")
    sources = metadata.get("sources")
    if not isinstance(sources, list):
        errors.append(f"{metadata_path}: sources must be a list")
        sources = []
    if origin != "original" and not sources:
        errors.append(f"{metadata_path}: non-original skill requires at least one source")
    for index, source in enumerate(sources):
        label = f"{metadata_path}: source {index + 1}"
        if not isinstance(source, dict):
            errors.append(f"{label} must be an object")
            continue
        required = {"repository", "ref", "path", "digest", "license", "use", "changes"}
        missing = sorted(required - set(source))
        if missing:
            errors.append(f"{label} missing {', '.join(missing)}")
            continue
        if not isinstance(source["repository"], str) or not source["repository"]:
            errors.append(f"{label} repository must be a non-empty string")
        if not isinstance(source["ref"], str) or not source["ref"]:
            errors.append(f"{label} ref must be a non-empty string")
        if not _safe_relative_source_path(source["path"]):
            errors.append(f"{label} path must be a safe repository-relative path")
        if not isinstance(source["digest"], str) or not DIGEST_RE.fullmatch(source["digest"]):
            errors.append(f"{label} digest must be a supported exact digest")
        if source["use"] not in SOURCE_USES:
            errors.append(f"{label} use must be one of {', '.join(sorted(SOURCE_USES))}")
        if not isinstance(source["changes"], str) or not source["changes"].strip():
            errors.append(f"{label} changes must explain the adaptation")
        license_id = source["license"]
        if not isinstance(license_id, str) or not (root / "licenses" / f"{license_id}.txt").is_file():
            errors.append(f"{label} missing licence file {license_id}.txt")
    reviewed = metadata.get("reviewed")
    try:
        if not isinstance(reviewed, str):
            raise ValueError
        date.fromisoformat(reviewed)
    except ValueError:
        errors.append(f"{metadata_path}: reviewed must be an ISO date")
    deps = metadata.get("dependencies")
    if not isinstance(deps, dict) or set(deps) != {"skills", "tools"}:
        errors.append(f"{metadata_path}: dependencies must contain only skills and tools")
        deps = {}
    skill_deps, tool_deps = deps.get("skills", []), deps.get("tools", [])
    if not isinstance(skill_deps, list) or not all(isinstance(v, str) for v in skill_deps):
        errors.append(f"{metadata_path}: dependencies.skills must be a string list")
        skill_deps = []
    if len(set(skill_deps)) != len(skill_deps) or skill_id in skill_deps:
        errors.append(f"{metadata_path}: dependencies.skills contains a duplicate or self dependency")
    if not isinstance(tool_deps, list) or not all(isinstance(v, str) for v in tool_deps):
        errors.append(f"{metadata_path}: dependencies.tools must be a string list")
        tool_deps = []
    if len(set(tool_deps)) != len(tool_deps):
        errors.append(f"{metadata_path}: dependencies.tools contains a duplicate")
    for tool in tool_deps:
        if tool not in tools:
            errors.append(f"{metadata_path}: unknown tool dependency {tool}")
    for child in bundle.iterdir():
        if child.is_symlink():
            errors.append(f"{child}: symlinks are not allowed in owned bundles")
        if child.name not in BUNDLE_ENTRIES:
            errors.append(f"{child}: unsupported bundle entry")
    for child in bundle.rglob("*"):
        if child.is_symlink():
            errors.append(f"{child}: symlinks are not allowed in owned bundles")
    errors.extend(_markdown_errors(bundle))
    errors.extend(_unlinked_reference_errors(bundle))
    errors.extend(_missing_named_path_errors(bundle))
    for path in files_under(bundle):
        if path.suffix.lower() in {".md", ".json", ".yaml", ".yml", ".txt", ".py", ".sh"}:
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    errors.append(f"{path}: possible secret matching {pattern.pattern}")
    return errors, skill_deps


def check_repo(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    tools_path = root / "config" / "tools.json"
    try:
        tools = read_json(tools_path)
    except CheckError as exc:
        errors.append(str(exc)); tools = {}
    if not isinstance(tools, dict):
        errors.append(f"{tools_path}: must contain an object"); tools = {}
    capabilities_path = root / "config" / "agent-capabilities.json"
    try:
        capabilities = read_json(capabilities_path)
    except CheckError as exc:
        errors.append(str(exc)); capabilities = {}
    if not isinstance(capabilities, dict) or capabilities.get("schema") != 1:
        errors.append(f"{capabilities_path}: expected a schema 1 object")
        capabilities = {}
    configured_agents = capabilities.get("agents", {})
    required_agents = {"codex", "claude-code", "opencode"}
    if not isinstance(configured_agents, dict) or set(configured_agents) != required_agents:
        errors.append(f"{capabilities_path}: agents must define Codex, Claude Code, and OpenCode")
    else:
        for agent_id, agent in configured_agents.items():
            if not isinstance(agent, dict):
                errors.append(f"{capabilities_path}: {agent_id} must be an object")
                continue
            for section in ("routing", "orchestration"):
                values = agent.get(section)
                if not isinstance(values, dict) or not values:
                    errors.append(f"{capabilities_path}: {agent_id}.{section} must be a non-empty object")
                    continue
                for capability_id, definition in values.items():
                    if not isinstance(definition, dict) or definition.get("status") not in CAPABILITY_STATUSES:
                        errors.append(f"{capabilities_path}: invalid status for {agent_id}.{section}.{capability_id}")
            entrypoint = agent.get("entrypoint")
            if not isinstance(entrypoint, dict) or entrypoint.get("kind") not in {"session", "executable"}:
                errors.append(f"{capabilities_path}: invalid entrypoint for {agent_id}")
    catalog_config = capabilities.get("catalog", {})
    if (
        not isinstance(catalog_config, dict)
        or not isinstance(catalog_config.get("chars_per_estimated_token"), int)
        or isinstance(catalog_config.get("chars_per_estimated_token"), bool)
        or catalog_config.get("chars_per_estimated_token", 0) < 1
    ):
        errors.append(f"{capabilities_path}: catalog.chars_per_estimated_token must be a positive integer")
    elif catalog_config.get("warning_threshold_tokens") is not None and (
        not isinstance(catalog_config.get("warning_threshold_tokens"), int)
        or isinstance(catalog_config.get("warning_threshold_tokens"), bool)
        or catalog_config.get("warning_threshold_tokens", 0) < 1
    ):
        errors.append(f"{capabilities_path}: catalog.warning_threshold_tokens must be null or a positive integer")
    for lifecycle in LIFECYCLES:
        base = root / lifecycle
        if not base.is_dir():
            errors.append(f"{base}: lifecycle directory is required"); continue
        present = {p.name for p in base.iterdir() if p.is_dir()}
        errors.extend(f"{base / name}: unknown group" for name in sorted(present - set(GROUPS)))
        errors.extend(f"{base / name}: group directory is required" for name in sorted(set(GROUPS) - present))
    bundles = discover(root)
    by_id: dict[str, dict[str, Any]] = {}
    dependencies: dict[str, list[str]] = {}
    for item in bundles:
        bundle, skill_id = item["path"], item["id"]
        if not SKILL_ID_RE.fullmatch(skill_id):
            errors.append(f"{bundle}: invalid skill id")
        if skill_id in by_id:
            errors.append(f"duplicate skill id {skill_id}: {by_id[skill_id]['path']} and {bundle}")
        by_id[skill_id] = item
        item_errors, dependencies[skill_id] = _metadata_errors(root, item, tools)
        errors.extend(item_errors)
    active_ids = {item["id"] for item in bundles if item["lifecycle"] == "skills"}
    for item in bundles:
        for dependency in dependencies.get(item["id"], []):
            if dependency not in by_id:
                errors.append(f"{item['path']}: missing skill dependency {dependency}")
            elif item["lifecycle"] == "skills" and dependency not in active_ids:
                errors.append(f"{item['path']}: active skill depends on inactive {dependency}")
    visiting: set[str] = set()
    visited: set[str] = set()
    def visit(node: str, trail: list[str]) -> None:
        if node in visiting:
            cycle = trail[trail.index(node):] + [node] if node in trail else trail + [node]
            errors.append("skill dependency cycle: " + " -> ".join(cycle)); return
        if node in visited:
            return
        visiting.add(node)
        for nxt in dependencies.get(node, []):
            if nxt in active_ids:
                visit(nxt, trail + [node])
        visiting.remove(node); visited.add(node)
    for skill_id in sorted(active_ids):
        visit(skill_id, [])
    return sorted(set(errors))


def active_projection(root: Path = ROOT) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for item in discover(root):
        if item["lifecycle"] != "skills":
            continue
        bundle: Path = item["path"]
        for child in bundle.iterdir():
            if child.name not in RUNTIME_ENTRIES:
                continue
            if child.is_symlink():
                raise CheckError(f"{child}: symlinks are not allowed in the runtime projection")
            if child.is_file():
                result[f"{item['id']}/{child.name}"] = child
            else:
                for path in files_under(child):
                    result[f"{item['id']}/{path.relative_to(bundle).as_posix()}"] = path
    return result


def _opencode_skill_text(source: bytes, invocation: Sequence[str]) -> bytes:
    """Enable OpenCode V2 model loading for user-requested skills to the generated shared runtime."""
    if "explicit" not in invocation:
        return source
    try:
        text = source.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CheckError("explicit OpenCode skills must use UTF-8 frontmatter") from exc
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise CheckError("OpenCode projection requires SKILL.md frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise CheckError("OpenCode projection found unclosed SKILL.md frontmatter") from exc

    newline = "\r\n" if any(line.endswith("\r\n") for line in lines[:end + 1]) else "\n"
    metadata_lines = [index for index, line in enumerate(lines[1:end], start=1) if re.match(r"^metadata\s*:", line)]
    if len(metadata_lines) > 1:
        raise CheckError("OpenCode projection found duplicate metadata fields")
    if not metadata_lines:
        lines[end:end] = [f"metadata:{newline}", f"  opencode/autoinvoke: true{newline}"]
        return "".join(lines).encode("utf-8")

    start = metadata_lines[0]
    if not re.fullmatch(r"metadata\s*:\s*(?:#.*)?(?:\r?\n)?", lines[start]):
        raise CheckError("OpenCode projection requires metadata to be a YAML mapping")
    stop = end
    for index in range(start + 1, end):
        line = lines[index]
        if line.strip() and not line[0].isspace() and not line.lstrip().startswith("#"):
            stop = index
            break
    keys = []
    for index in range(start + 1, stop):
        match = re.match(r"^(\s+)(?:['\"])?opencode/autoinvoke(?:['\"])?\s*:\s*(.*?)\s*(?:\r?\n)?$", lines[index])
        if match:
            keys.append((index, match.group(1)))
    if len(keys) > 1:
        raise CheckError("OpenCode projection found duplicate metadata.opencode/autoinvoke fields")
    if keys:
        index, indent = keys[0]
        ending = "\r\n" if lines[index].endswith("\r\n") else "\n" if lines[index].endswith("\n") else ""
        lines[index] = f"{indent}opencode/autoinvoke: true{ending}"
    else:
        lines.insert(stop, f"  opencode/autoinvoke: true{newline}")
    return "".join(lines).encode("utf-8")


@lru_cache(maxsize=1)
def opencode_major_version() -> int | None:
    executable = shutil.which("opencode")
    if not executable:
        return None
    try:
        result = subprocess.run(
            [executable, "--version"], capture_output=True, text=True, check=False, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    match = re.search(r"\b(?:v)?(\d+)\.\d+", result.stdout + " " + result.stderr)
    return int(match.group(1)) if match else None


def runtime_projection(root: Path = ROOT, *, opencode_v2: bool | None = None) -> dict[str, bytes]:
    """Return shared Agent Skills files with the minimal OpenCode runtime adapter."""
    if opencode_v2 is None:
        opencode_v2 = opencode_major_version() == 2
    bundles = {item["id"]: item for item in discover(root) if item["lifecycle"] == "skills"}
    result: dict[str, bytes] = {}
    for relative, path in active_projection(root).items():
        content = path.read_bytes()
        parts = PurePosixPath(relative).parts
        if len(parts) == 2 and parts[1] == "SKILL.md":
            invocation = read_json(bundles[parts[0]]["path"] / "metadata.json")["invocation"]
            if opencode_v2:
                content = _opencode_skill_text(content, invocation)
        result[relative] = content
    return result


def desired_hashes(root: Path = ROOT) -> dict[str, str]:
    return {relative: bytes_hash(content) for relative, content in runtime_projection(root).items()}


def runtime_config(root: Path = ROOT) -> dict[str, Path]:
    raw = read_json(root / "config" / "runtime.json")
    required = {"skills", "global_agents", "backups"}
    if not isinstance(raw, dict) or not required <= set(raw) or not all(isinstance(raw.get(k), str) for k in required):
        raise CheckError(f"{root / 'config' / 'runtime.json'}: missing runtime paths")
    return {key: Path(os.path.expanduser(raw[key])) for key in required}


def opencode_runtime_config(root: Path = ROOT) -> dict[str, Path]:
    raw = read_json(root / "config" / "runtime.json")
    required = {"skills", "global_agents", "opencode_agents", "opencode_backups"}
    if not isinstance(raw, dict) or not required <= set(raw) or not all(isinstance(raw.get(key), str) for key in required):
        raise CheckError(f"{root / 'config' / 'runtime.json'}: missing OpenCode runtime paths")
    return {key: _absolute_claude_path(Path(raw[key])) for key in required}


def _absolute_path(path: Path) -> Path:
    return Path(os.path.abspath(os.path.expanduser(str(path))))


def _absolute_claude_path(path: Path) -> Path:
    return _absolute_path(path)


def claude_runtime_config(root: Path = ROOT) -> dict[str, Path]:
    raw = read_json(root / "config" / "runtime.json")
    required = {"skills", "global_agents", "claude_skills", "claude_runtime", "claude_rules", "claude_backups"}
    if not isinstance(raw, dict) or not required <= set(raw) or not all(isinstance(raw.get(key), str) for key in required):
        raise CheckError(f"{root / 'config' / 'runtime.json'}: missing Claude runtime paths")
    config = {key: _absolute_claude_path(Path(raw[key])) for key in required}
    for optional in ("claude_global", "claude_settings", "handoffs"):
        if isinstance(raw.get(optional), str):
            config[optional] = _absolute_claude_path(Path(raw[optional]))
    return config


@dataclass(frozen=True)
class SyncStatus:
    adds: list[str]
    changes: list[str]
    removes: list[str]
    drift: list[str]
    global_changed: bool
    global_drift: bool


def _runtime_hashes(target: Path) -> dict[str, str]:
    if not target.is_dir():
        return {}
    return {path.relative_to(target).as_posix(): file_hash(path) for path in files_under(target) if path.relative_to(target).as_posix() != MARKER}


def external_skill_ids(root: Path) -> set[str]:
    raw = read_json(root / "config" / "runtime.json").get("external_skills", [])
    if not isinstance(raw, list) or any(not isinstance(x, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", x) for x in raw):
        raise CheckError("external_skills must be a list of safe skill IDs")
    if len(raw) != len(set(raw)):
        raise CheckError("duplicate external skill ID")
    names = set(raw)
    owned = {item["id"] for item in discover(root) if item["lifecycle"] == "skills"}
    overlap = sorted(names & owned)
    if overlap:
        raise CheckError("external skill conflicts with EKit ownership: " + ", ".join(overlap))
    return names


def managed_runtime_hashes(root: Path, target: Path) -> dict[str, str]:
    external = external_skill_ids(root)
    return {path: digest for path, digest in _runtime_hashes(target).items() if PurePosixPath(path).parts[0] not in external}


def sync_status(root: Path, target: Path, global_target: Path | None = None) -> SyncStatus:
    desired, current = desired_hashes(root), managed_runtime_hashes(root, target)
    adds = sorted(set(desired) - set(current))
    removes = sorted(set(current) - set(desired))
    changes = sorted(key for key in set(desired) & set(current) if desired[key] != current[key])
    drift: list[str] = []
    global_drift = False
    marker_path = target / MARKER
    if target.exists() and any(target.iterdir()):
        if not marker_path.is_file():
            drift.append("runtime is unmarked")
        else:
            try:
                marker = read_json(marker_path)
                if marker.get("schema") != MARKER_SCHEMA or marker.get("repository") != "elias-agent-skills":
                    drift.append("runtime marker is invalid")
                previous = marker.get("files")
                if not isinstance(previous, dict):
                    drift.append("runtime marker file manifest is invalid"); previous = {}
                for relative, old_hash in previous.items():
                    if not _safe_relative_source_path(relative):
                        drift.append("runtime marker contains an unsafe path")
                        continue
                    if PurePosixPath(relative).parts[0] in external_skill_ids(root):
                        continue
                    path = target / relative
                    if not path.is_file() or file_hash(path) != old_hash:
                        drift.append(relative)
                if global_target is not None:
                    recorded = marker.get("global_agents")
                    if isinstance(recorded, str) and (
                        not global_target.is_file() or file_hash(global_target) != recorded
                    ):
                        global_drift = True
            except CheckError as exc:
                drift.append(str(exc))
    canonical_global = root / "config" / "AGENTS.md"
    global_changed = bool(global_target is not None and (not global_target.is_file() or file_hash(global_target) != file_hash(canonical_global)))
    return SyncStatus(adds, changes, removes, sorted(set(drift)), global_changed, global_drift)


def _assert_safe_target(path: Path, label: str) -> None:
    # Parent-directory symlinks (including macOS /tmp) are ordinary filesystem
    # layout. The managed target itself must be a real file or directory so the
    # atomic rename cannot replace an unexpected link destination.
    if path.is_symlink():
        raise CheckError(f"refusing a symlinked {label}")
    if path.exists() and label == "runtime target" and not path.is_dir():
        raise CheckError("runtime target exists but is not a directory")


def _verify_runtime(root: Path, target: Path, global_target: Path) -> None:
    expected, actual = desired_hashes(root), managed_runtime_hashes(root, target)
    if actual != expected:
        missing = sorted(set(expected) - set(actual)); extra = sorted(set(actual) - set(expected))
        changed = sorted(k for k in set(expected) & set(actual) if expected[k] != actual[k])
        raise CheckError(f"installed runtime verification failed (missing={missing}, changed={changed}, extra={extra})")
    if file_hash(global_target) != file_hash(root / "config" / "AGENTS.md"):
        raise CheckError("installed global AGENTS.md verification failed")
    marker = read_json(target / MARKER)
    if marker.get("files") != expected or marker.get("global_agents") != file_hash(global_target):
        raise CheckError("installed runtime marker verification failed")


def sync_apply(
    root: Path,
    target: Path,
    global_target: Path,
    backup_root: Path,
    *,
    adopt_unmanaged: bool = False,
) -> Path:
    errors = check_repo(root)
    if errors:
        raise CheckError("repository check failed:\n" + "\n".join(errors))
    _assert_safe_target(target, "runtime target"); _assert_safe_target(global_target, "global AGENTS.md target")
    status = sync_status(root, target, global_target)
    if status.drift and not (adopt_unmanaged and status.drift == ["runtime is unmarked"]):
        raise CheckError("runtime drift must be resolved before apply: " + ", ".join(status.drift))
    if status.global_drift:
        raise CheckError("global AGENTS.md was edited after the last sync")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = backup_root / stamp
    backup.mkdir(parents=True, exist_ok=False)
    target.parent.mkdir(parents=True, exist_ok=True); global_target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{target.name}.stage-", dir=target.parent))
    old_runtime = target.parent / f".{target.name}.previous-{stamp}"
    global_stage = global_target.parent / f".{global_target.name}.stage-{stamp}"
    old_global = global_target.parent / f".{global_target.name}.previous-{stamp}"
    had_runtime, had_global = target.exists(), global_target.exists()
    runtime_installed = global_installed = False
    try:
        write_json(backup / "snapshot.json", {
            "schema": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "runtime_existed": had_runtime,
            "global_agents_existed": had_global,
            "runtime_files": _runtime_hashes(target) if had_runtime else {},
            "global_agents": file_hash(global_target) if had_global and global_target.is_file() else None,
        })
        sources, projection = active_projection(root), runtime_projection(root)
        external = external_skill_ids(root)
        external_before = {key: value for key, value in _runtime_hashes(target).items() if PurePosixPath(key).parts[0] in external}
        for skill_id in external:
            source = target / skill_id
            if source.is_symlink() or (source.exists() and not source.is_dir()):
                raise CheckError(f"external skill must be a real directory: {skill_id}")
            if source.exists():
                if any(path.is_symlink() for path in source.rglob("*")):
                    raise CheckError(f"external skill contains a symlink: {skill_id}")
                shutil.copytree(source, stage / skill_id, copy_function=shutil.copy2)
        if set(sources) != set(projection):
            raise CheckError("runtime projection paths disagree with source paths")
        for relative, content in projection.items():
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(sources[relative], destination)
            if destination.read_bytes() != content:
                destination.write_bytes(content)
        manifest = {relative: bytes_hash(projection[relative]) for relative in sorted(projection)}
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
        write_json(stage / MARKER, {"schema": MARKER_SCHEMA, "repository": "elias-agent-skills", "source_commit": commit, "generated_at": datetime.now(timezone.utc).isoformat(), "files": manifest, "global_agents": file_hash(root / "config" / "AGENTS.md")})
        if had_runtime:
            shutil.copytree(target, backup / "skills", copy_function=shutil.copy2, symlinks=True)
            external_after = {key: value for key, value in _runtime_hashes(target).items() if PurePosixPath(key).parts[0] in external}
            if external_after != external_before:
                raise CheckError("external skills changed during sync; retry")
            os.replace(target, old_runtime)
        if had_global:
            shutil.copy2(global_target, backup / "AGENTS.md"); os.replace(global_target, old_global)
        os.replace(stage, target); runtime_installed = True
        shutil.copy2(root / "config" / "AGENTS.md", global_stage); os.replace(global_stage, global_target); global_installed = True
        _verify_runtime(root, target, global_target)
    except Exception:
        if runtime_installed and target.exists(): shutil.rmtree(target)
        if old_runtime.exists(): os.replace(old_runtime, target)
        if global_installed and global_target.exists(): global_target.unlink()
        if old_global.exists(): os.replace(old_global, global_target)
        shutil.rmtree(stage, ignore_errors=True); global_stage.unlink(missing_ok=True)
        raise
    else:
        if old_runtime.exists(): shutil.rmtree(old_runtime)
        old_global.unlink(missing_ok=True)
        return backup


@dataclass(frozen=True)
class ClaudeSyncStatus:
    adds: list[str]
    changes: list[str]
    removes: list[str]
    drift: list[str]
    skill_links_adds: list[str]
    skill_links_changes: list[str]
    skill_links_removes: list[str]
    rule_changed: bool
    conflicts: list[str]
    prerequisites: list[str]
    unsupported: list[str]
    global_link_changed: bool = False


@dataclass(frozen=True)
class OpenCodeSyncStatus:
    changed: bool
    drift: list[str]
    conflicts: list[str]
    prerequisites: list[str]
    routing: dict[str, list[str]]
    limitations: list[str]
    version: int | None


def _claude_hash_text(value: str) -> str:
    return _claude_hash_bytes(value.encode("utf-8"))


def _claude_hash_bytes(value: bytes) -> str:
    return bytes_hash(value)


def _claude_paths_overlap(left: Path, right: Path) -> bool:
    return _paths_overlap(left, right)


def _paths_overlap(left: Path, right: Path) -> bool:
    left_path, right_path = left.resolve(strict=False), right.resolve(strict=False)
    return left_path == right_path or left_path in right_path.parents or right_path in left_path.parents


def _claude_skill_text(source: str, invocation: Sequence[str]) -> str:
    """Keep owned skills model-loadable without changing their body."""
    lines = source.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise CheckError("Claude projection requires SKILL.md frontmatter")
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration as exc:
        raise CheckError("Claude projection found unclosed SKILL.md frontmatter") from exc
    key_pattern = re.compile(r"^\s*disable-model-invocation\s*:")
    found = False
    output = [lines[0]]
    for line in lines[1:end]:
        if key_pattern.match(line):
            if found:
                raise CheckError("Claude projection found duplicate disable-model-invocation fields")
            found = True
        else:
            output.append(line)
    output.extend(lines[end:])
    return "".join(output)


def _invocation_routing(invocation_by_id: dict[str, Sequence[str]]) -> dict[str, list[str]]:
    return {
        "automatic": sorted(
            skill_id for skill_id, invocation in invocation_by_id.items()
            if "automatic" in invocation and "explicit" not in invocation
        ),
        "explicit": sorted(
            skill_id for skill_id, invocation in invocation_by_id.items()
            if "explicit" in invocation
        ),
        "supporting_only": sorted(
            skill_id for skill_id, invocation in invocation_by_id.items()
            if "supporting" in invocation and "automatic" not in invocation and "explicit" not in invocation
        ),
    }


def claude_projection(root: Path = ROOT) -> tuple[dict[str, bytes], dict[str, list[str]]]:
    bundles = {item["id"]: item for item in discover(root) if item["lifecycle"] == "skills"}
    invocation_by_id = {
        skill_id: read_json(item["path"] / "metadata.json")["invocation"]
        for skill_id, item in bundles.items()
    }
    files: dict[str, bytes] = {}
    for relative, source in active_projection(root).items():
        path = PurePosixPath(relative)
        content = source.read_bytes()
        if len(path.parts) == 2 and path.name == "SKILL.md":
            content = _claude_skill_text(content.decode("utf-8"), invocation_by_id[path.parts[0]]).encode("utf-8")
        files[relative] = content
    return files, _invocation_routing(invocation_by_id)


def _claude_rules(global_target: Path, routing: dict[str, list[str]]) -> str:
    def list_ids(values: list[str]) -> str:
        return ", ".join(f"`{skill_id}`" for skill_id in values) if values else "(none)"

    supporting = "\n".join(f"- `{skill_id}`" for skill_id in routing["supporting_only"]) or "- (none)"
    return (
        "# Managed routing for Elias's owned skills\n\n"
        "Generated by `elias-agent-skills`; update the canonical instructions or skill metadata instead of editing this file.\n\n"
        f"`~/.claude/CLAUDE.md` is a managed link to `{global_target.resolve(strict=False)}`, the canonical shared user guidance. Keep its meaning intact. "
        "The skill sources live in the `elias-agent-skills` repository; installed skill files are generated copies.\n\n"
        "For each project, follow its `AGENTS.md`. If Claude has not loaded it through native AGENTS support or a project `CLAUDE.md` import, read the root `AGENTS.md` before work and relevant nested `AGENTS.md` files before editing their scope.\n\n"
        "## Invocation policy\n\n"
        f"- Automatically selectable skills: {list_ids(routing['automatic'])}. These may own a request when relevant.\n"
        f"- Skills requiring explicit invocation: {list_ids(routing['explicit'])}. These are user-requested workflows: load them when Elias names or clearly requests their method in ordinary language or dictation; slash commands are optional. Descriptions and instructions guide request recognition, not a deterministic permission check.\n"
        "- Supporting-only skills must not own a request. Load one only when a separately selected primary skill needs its expertise.\n\n"
        "Claude Code has no native supporting-only invocation mode, so the supporting-only list below is routing guidance, "
        "not a host-enforced restriction. While the `elias-mods` plugin is loaded, its skill guard flags a supporting-only load "
        "that has no owning primary skill. Requested workflows remain model-loadable. The supporting-skill guard only warns unless the plugin's "
        "`skill_guard_refuse` option is on. `claude-sync` reports the remaining gap so it is not mistaken for full parity.\n\n"
        "## Supporting-only skills\n\n"
        f"{supporting}\n"
    )


def _opencode_routing(root: Path) -> dict[str, list[str]]:
    invocation_by_id = {
        item["id"]: read_json(item["path"] / "metadata.json")["invocation"]
        for item in discover(root) if item["lifecycle"] == "skills"
    }
    return _invocation_routing(invocation_by_id)


def opencode_instructions(root: Path = ROOT) -> tuple[bytes, dict[str, list[str]]]:
    routing = _opencode_routing(root)

    def list_ids(values: list[str]) -> str:
        return ", ".join(f"`{skill_id}`" for skill_id in values) if values else "(none)"

    supporting = "\n".join(f"- `{skill_id}`" for skill_id in routing["supporting_only"]) or "- (none)"
    explicit = "\n".join(f"- `{skill_id}`" for skill_id in routing["explicit"]) or "- (none)"
    suffix = (
        "## Managed OpenCode skill routing\n\n"
        "Generated from this repository's activation metadata. Edit the canonical instructions or skill metadata instead of this section.\n\n"
        "Owned skills are discovered directly from the shared `~/.agents/skills` Agent Skills path; this setup does not create a second skill catalog.\n\n"
        f"- Automatic skills may own a request when their descriptions clearly fit: {list_ids(routing['automatic'])}.\n"
        "- Supporting-only skills must not own the request. Load one only when a separately selected primary capability needs its expertise.\n"
        "- Explicit means user-requested: load when Elias names or clearly requests the workflow in ordinary language or dictation; special command syntax is optional.\n\n"
        "When OpenCode V2 is installed, shared-runtime sync enables model loading with `metadata.opencode/autoinvoke: true` for user-requested skills. Request recognition follows descriptions and instructions on every host; it is not a deterministic permission check. OpenCode has no native supporting-only policy; that rule is guidance, not enforced routing.\n\n"
        "### Supporting-only skills\n\n"
        f"{supporting}\n\n"
        "### Explicit-only skills\n\n"
        f"{explicit}\n"
    )
    canonical = (root / "config" / "AGENTS.md").read_bytes()
    ending = b"\n" if not canonical.endswith(b"\n") else b""
    return canonical + ending + b"\n" + suffix.encode("utf-8"), routing


def _opencode_managed_content(body: bytes) -> bytes:
    digest = hashlib.sha256(body).hexdigest().encode("ascii")
    return b"<!-- elias-agent-skills opencode managed v1 sha256:" + digest + b" -->\n" + body


def _opencode_marker_drift(content: bytes) -> str | None:
    match = OPENCODE_FILE_MARKER.match(content)
    if not match:
        if content.startswith(b"<!-- elias-agent-skills opencode managed"):
            return "OpenCode AGENTS.md managed marker is invalid"
        return "OpenCode AGENTS.md is not marked as managed"
    if bytes_hash(content[match.end():]) != "sha256:" + match.group(1).decode("ascii"):
        return "OpenCode AGENTS.md was edited after the last managed sync"
    return None


def _opencode_sync_prerequisites(root: Path, skills_target: Path, global_target: Path) -> list[str]:
    shared = sync_status(root, skills_target, global_target)
    prerequisites: list[str] = []
    if shared.drift:
        prerequisites.append("shared Agent Skills runtime has drift; inspect it and run `python3 scripts/skills.py sync --apply`")
    if shared.adds or shared.changes or shared.removes:
        prerequisites.append("shared Agent Skills runtime needs sync; run `python3 scripts/skills.py sync --apply` first")
    if shared.global_changed or shared.global_drift:
        prerequisites.append("canonical global AGENTS.md needs sync; run `python3 scripts/skills.py sync --apply` first")
    return prerequisites


def opencode_sync_status(
    root: Path,
    agents_target: Path,
    skills_target: Path,
    global_target: Path,
    *,
    backup_root: Path | None = None,
) -> OpenCodeSyncStatus:
    agents_target = _absolute_claude_path(agents_target)
    skills_target = _absolute_claude_path(skills_target)
    global_target = _absolute_claude_path(global_target)
    backup_root = _absolute_claude_path(backup_root) if backup_root else None
    body, routing = opencode_instructions(root)
    desired = _opencode_managed_content(body)
    conflicts: list[str] = []
    drift: list[str] = []
    if agents_target.is_symlink():
        conflicts.append("OpenCode AGENTS.md target must be a regular file, not a symlink")
    elif agents_target.exists() and not agents_target.is_file():
        conflicts.append("OpenCode AGENTS.md target exists but is not a regular file")
    elif agents_target.is_file():
        error = _opencode_marker_drift(agents_target.read_bytes())
        if error == "OpenCode AGENTS.md is not marked as managed":
            conflicts.append("OpenCode AGENTS.md already exists and is not owned by this sync")
        elif error:
            drift.append(error)
    managed_targets = (
        ("OpenCode AGENTS.md", agents_target),
        ("shared Agent Skills runtime", skills_target),
        ("Codex global AGENTS.md", global_target),
        ("canonical AGENTS.md", root / "config" / "AGENTS.md"),
    )
    for index, (left_name, left_path) in enumerate(managed_targets):
        for right_name, right_path in managed_targets[index + 1:]:
            if _paths_overlap(left_path, right_path):
                conflicts.append(f"{left_name} and {right_name} targets must be separate")
    if backup_root:
        if backup_root.is_symlink() or (backup_root.exists() and not backup_root.is_dir()):
            conflicts.append("OpenCode backup path must be a real directory")
        if any(_paths_overlap(backup_root, path) for _, path in managed_targets):
            conflicts.append("OpenCode backup directory must be separate from managed targets")
        if _paths_overlap(backup_root, root.resolve(strict=False)):
            conflicts.append("OpenCode backup directory must be outside the canonical repository")
    if _paths_overlap(agents_target, root.resolve(strict=False)):
        conflicts.append("OpenCode global AGENTS.md target must be outside the canonical repository")
    changed = not agents_target.is_file() or agents_target.read_bytes() != desired
    version = opencode_major_version()
    limitations = []
    if routing["explicit"]:
        limitations.append("User-requested workflow recognition is model-guided through descriptions and instructions, not host-enforced.")
    if routing["supporting_only"]:
        limitations.append("OpenCode has no native supporting-only invocation mode; generated AGENTS.md guidance is not enforced.")
    return OpenCodeSyncStatus(
        changed,
        drift,
        conflicts,
        _opencode_sync_prerequisites(root, skills_target, global_target),
        routing,
        limitations,
        version,
    )


def _verify_opencode(
    root: Path,
    agents_target: Path,
    skills_target: Path,
    global_target: Path,
) -> None:
    expected, _ = opencode_instructions(root)
    actual = agents_target.read_bytes()
    marker = OPENCODE_FILE_MARKER.match(actual)
    if not marker or actual[marker.end():] != expected:
        raise CheckError("OpenCode global AGENTS.md verification failed")
    errors = _opencode_sync_prerequisites(root, skills_target, global_target)
    if errors:
        raise CheckError("OpenCode shared skill runtime verification failed: " + "; ".join(errors))


def opencode_sync_apply(
    root: Path,
    agents_target: Path,
    skills_target: Path,
    global_target: Path,
    backup_root: Path,
) -> Path | None:
    errors = check_repo(root)
    if errors:
        raise CheckError("repository check failed:\n" + "\n".join(errors))
    status = opencode_sync_status(
        root, agents_target, skills_target, global_target, backup_root=backup_root,
    )
    if status.conflicts:
        raise CheckError("OpenCode sync conflict: " + "; ".join(status.conflicts))
    if status.drift:
        raise CheckError("OpenCode runtime drift must be resolved before apply: " + "; ".join(status.drift))
    if status.prerequisites:
        raise CheckError("OpenCode sync prerequisites are not met: " + "; ".join(status.prerequisites))
    if not status.changed:
        return None

    agents_target = _absolute_claude_path(agents_target)
    backup_root = _absolute_claude_path(backup_root)
    body, _ = opencode_instructions(root)
    desired = _opencode_managed_content(body)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    backup = backup_root / stamp
    backup.mkdir(parents=True, exist_ok=False)
    agents_target.parent.mkdir(parents=True, exist_ok=True)
    stage = agents_target.parent / f".{agents_target.name}.stage-{stamp}"
    old = agents_target.parent / f".{agents_target.name}.previous-{stamp}"
    had_target = agents_target.exists()
    installed = False
    try:
        write_json(backup / "snapshot.json", {
            "schema": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "agents_target": str(agents_target),
            "target_existed": had_target,
            "target_hash": file_hash(agents_target) if had_target else None,
            "shared_skills_target": str(skills_target),
        })
        if had_target:
            shutil.copy2(agents_target, backup / "AGENTS.md")
            os.replace(agents_target, old)
        stage.write_bytes(desired)
        os.replace(stage, agents_target)
        installed = True
        _verify_opencode(root, agents_target, skills_target, global_target)
    except Exception:
        if installed and agents_target.exists():
            agents_target.unlink()
        if old.exists():
            os.replace(old, agents_target)
        stage.unlink(missing_ok=True)
        raise
    else:
        old.unlink(missing_ok=True)
        return backup


def opencode_doctor(
    root: Path,
    agents_target: Path,
    skills_target: Path,
    global_target: Path,
    *,
    backup_root: Path | None = None,
) -> list[str]:
    status = opencode_sync_status(
        root, agents_target, skills_target, global_target, backup_root=backup_root,
    )
    errors = check_repo(root)
    errors.extend(status.conflicts)
    errors.extend(status.drift)
    errors.extend(status.prerequisites)
    if status.changed:
        errors.append("OpenCode global AGENTS.md differs from the canonical projection")
    return sorted(set(errors))


def _claude_manifest(target: Path) -> tuple[dict[str, Any] | None, list[str]]:
    if not target.exists():
        return None, []
    if target.is_symlink():
        return None, ["Claude runtime target is a symlink"]
    if not target.is_dir():
        return None, ["Claude runtime target is not a directory"]
    if not any(target.iterdir()):
        return None, []
    marker_path = target / MARKER
    if not marker_path.is_file():
        return None, ["Claude runtime is unmarked"]
    try:
        marker = read_json(marker_path)
    except CheckError as exc:
        return None, [f"invalid Claude runtime marker: {exc}"]
    if not isinstance(marker, dict) or marker.get("schema") != MARKER_SCHEMA or marker.get("repository") != "elias-agent-skills" or marker.get("provider") != "claude-code":
        return None, ["Claude runtime marker is invalid"]
    files = marker.get("files")
    managed_ids = marker.get("active_skill_ids")
    if not isinstance(files, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
        return None, ["Claude runtime marker file manifest is invalid"]
    if not isinstance(managed_ids, list) or not all(isinstance(value, str) and SKILL_ID_RE.fullmatch(value) for value in managed_ids) or len(set(managed_ids)) != len(managed_ids):
        return None, ["Claude runtime marker skill list is invalid"]
    recorded_target = marker.get("runtime_target")
    if not isinstance(recorded_target, str) or Path(recorded_target).resolve(strict=False) != target.resolve(strict=False):
        return None, ["Claude runtime marker target does not match the configured path"]
    errors: list[str] = []
    for relative, expected in files.items():
        if not _safe_relative_source_path(relative):
            errors.append("Claude runtime marker contains an unsafe path")
            continue
        path = target / relative
        if not path.is_file() or file_hash(path) != expected:
            errors.append(f"Claude runtime drift: {relative}")
    actual = _runtime_hashes(target)
    if set(actual) != set(files):
        errors.append("Claude runtime drift: installed files differ from its manifest")
    extra_directories = sorted(_claude_runtime_directories(target) - _claude_expected_directories(files))
    errors.extend(f"Claude runtime drift: unexpected directory {relative}" for relative in extra_directories)
    for path in target.rglob("*"):
        if path.is_symlink():
            errors.append(f"Claude runtime drift: unexpected symlink {path.relative_to(target).as_posix()}")
    if errors:
        return marker, sorted(set(errors))
    return marker, []


def _claude_link_target(path: Path) -> Path | None:
    if not path.is_symlink():
        return None
    return (path.parent / path.readlink()).resolve(strict=False)


def _claude_runtime_directories(target: Path) -> set[str]:
    ignored = {".git", "__pycache__", ".pytest_cache", ".DS_Store"}
    if not target.is_dir():
        return set()
    return {
        path.relative_to(target).as_posix()
        for path in target.rglob("*")
        if path.is_dir() and not path.is_symlink()
        and not any(part in ignored for part in path.relative_to(target).parts)
    }


def _claude_expected_directories(files: dict[str, Any]) -> set[str]:
    result: set[str] = set()
    for relative in files:
        parent = PurePosixPath(relative).parent
        while parent != PurePosixPath("."):
            result.add(parent.as_posix())
            parent = parent.parent
    return result


def _valid_codex_legacy_link(root: Path, codex_target: Path, skill_id: str, link: Path) -> bool:
    marker_path = codex_target / MARKER
    if codex_target.is_symlink() or not marker_path.is_file() or not link.is_symlink():
        return False
    try:
        marker = read_json(marker_path)
    except CheckError:
        return False
    if not isinstance(marker, dict) or marker.get("schema") != MARKER_SCHEMA or marker.get("repository") != "elias-agent-skills":
        return False
    files = marker.get("files")
    if not isinstance(files, dict) or f"{skill_id}/SKILL.md" not in files:
        return False
    expected = {key: value for key, value in files.items() if PurePosixPath(key).parts[0] not in external_skill_ids(root)}
    if managed_runtime_hashes(root, codex_target) != expected:
        return False
    return _claude_link_target(link) == (codex_target / skill_id).resolve(strict=False)


def claude_sync_status(
    root: Path,
    skills_target: Path,
    runtime_target: Path,
    rules_target: Path,
    global_target: Path,
    codex_skills_target: Path,
    *,
    backup_root: Path | None = None,
    global_link: Path | None = None,
) -> ClaudeSyncStatus:
    skills_target = _absolute_claude_path(skills_target)
    runtime_target = _absolute_claude_path(runtime_target)
    rules_target = _absolute_claude_path(rules_target)
    global_target = _absolute_claude_path(global_target)
    codex_skills_target = _absolute_claude_path(codex_skills_target)
    backup_root = _absolute_claude_path(backup_root) if backup_root else None
    desired_content, routing = claude_projection(root)
    desired = {relative: _claude_hash_bytes(content) for relative, content in desired_content.items()}
    current = _runtime_hashes(runtime_target)
    marker, runtime_errors = _claude_manifest(runtime_target)
    adds = sorted(set(desired) - set(current))
    removes = sorted(set(current) - set(desired))
    changes = sorted(path for path in set(desired) & set(current) if desired[path] != current[path])
    conflicts: list[str] = []
    prerequisites: list[str] = []

    if skills_target.is_symlink() or (skills_target.exists() and not skills_target.is_dir()):
        conflicts.append("Claude skills target must be a real directory")
    if runtime_target.is_symlink() or (runtime_target.exists() and not runtime_target.is_dir()):
        conflicts.append("Claude runtime target must be a real directory")
    if rules_target.is_symlink() or (rules_target.exists() and not rules_target.is_file()):
        conflicts.append("Claude rules target must be a regular file")
    targets = (
        ("Claude skills", skills_target),
        ("Claude runtime", runtime_target),
        ("Claude rules", rules_target),
        ("Codex skills", codex_skills_target),
        ("global instructions", global_target),
    )
    for index, (left_name, left_path) in enumerate(targets):
        for right_name, right_path in targets[index + 1:]:
            if _claude_paths_overlap(left_path, right_path):
                conflicts.append(f"{left_name} and {right_name} targets must be separate")
    if backup_root and (backup_root.is_symlink() or (backup_root.exists() and not backup_root.is_dir())):
        conflicts.append("Claude backup path must be a real directory")
    if backup_root and any(_claude_paths_overlap(backup_root, target) for _, target in targets):
        conflicts.append("Claude backup directory must be separate from managed targets")

    previous_ids = set(marker.get("active_skill_ids", [])) if marker else set()
    previous_runtime = runtime_target
    desired_ids = {relative.split("/", 1)[0] for relative in desired}
    link_adds: list[str] = []
    link_changes: list[str] = []
    link_removes: list[str] = []
    if not skills_target.is_symlink() and (not skills_target.exists() or skills_target.is_dir()):
        for skill_id in sorted(desired_ids):
            path = skills_target / skill_id
            if not path.exists() and not path.is_symlink():
                link_adds.append(skill_id)
                continue
            actual_target = _claude_link_target(path)
            expected_target = (runtime_target / skill_id).resolve(strict=False)
            if actual_target == expected_target:
                if skill_id not in previous_ids:
                    conflicts.append(f"Claude skill link is not recorded as managed: {skill_id}")
                continue
            old_target = (previous_runtime / skill_id).resolve(strict=False)
            if skill_id in previous_ids and actual_target == old_target:
                if expected_target != old_target:
                    link_changes.append(skill_id)
                continue
            if _valid_codex_legacy_link(root, codex_skills_target, skill_id, path):
                link_changes.append(skill_id)
                continue
            conflicts.append(f"Claude skill path already exists and is not a recognized managed or Codex legacy link: {skill_id}")
        for skill_id in sorted(previous_ids - desired_ids):
            path = skills_target / skill_id
            if not path.exists() and not path.is_symlink():
                continue
            actual_target = _claude_link_target(path)
            if actual_target == (previous_runtime / skill_id).resolve(strict=False):
                link_removes.append(skill_id)
            else:
                conflicts.append(f"previously managed Claude skill link changed and will not be removed: {skill_id}")

    rule_content = _claude_rules(global_target, routing)
    managed_rule = bool(marker and marker.get("rules_target") == str(rules_target))
    if marker and marker.get("rules_target") != str(rules_target):
        conflicts.append("Claude runtime manifest names a different managed rules path")
    rule_hash = file_hash(rules_target) if rules_target.is_file() and not rules_target.is_symlink() else None
    if rules_target.exists() and not managed_rule:
        conflicts.append("Claude rules target already exists and is not owned by this sync")
    elif managed_rule:
        expected_rule_hash = marker.get("rules_hash")
        if not isinstance(expected_rule_hash, str) or rule_hash != expected_rule_hash:
            runtime_errors.append("Claude rule file drift: managed rules file was edited or removed")
    rule_changed = rule_hash != _claude_hash_text(rule_content)

    if global_target.is_symlink() or not global_target.is_file():
        prerequisites.append("global AGENTS.md must be synced before Claude Code")
    elif file_hash(global_target) != file_hash(root / "config" / "AGENTS.md"):
        prerequisites.append("global AGENTS.md must be synced before Claude Code")

    global_link_changed = False
    if global_link is not None:
        global_link = _absolute_claude_path(global_link)
        if _claude_link_target(global_link) != global_target.resolve(strict=False):
            if global_link.exists() or global_link.is_symlink():
                conflicts.append("Claude global CLAUDE.md exists and is not a link to the global AGENTS.md; move it aside first")
            else:
                global_link_changed = True

    return ClaudeSyncStatus(
        adds, changes, removes, sorted(set(runtime_errors)),
        sorted(link_adds), sorted(link_changes), sorted(link_removes), rule_changed,
        sorted(set(conflicts)), sorted(set(prerequisites)), routing["supporting_only"],
        global_link_changed,
    )


def _verify_claude_runtime(
    root: Path,
    skills_target: Path,
    runtime_target: Path,
    rules_target: Path,
    global_target: Path,
    global_link: Path | None = None,
) -> None:
    expected_content, routing = claude_projection(root)
    expected = {relative: _claude_hash_bytes(content) for relative, content in expected_content.items()}
    actual = _runtime_hashes(runtime_target)
    if actual != expected:
        raise CheckError("installed Claude runtime verification failed")
    expected_rules = _claude_hash_text(_claude_rules(global_target, routing))
    if not rules_target.is_file() or file_hash(rules_target) != expected_rules:
        raise CheckError("installed Claude rules verification failed")
    marker = read_json(runtime_target / MARKER)
    if marker.get("provider") != "claude-code" or marker.get("files") != expected or marker.get("rules_hash") != expected_rules:
        raise CheckError("installed Claude runtime marker verification failed")
    for skill_id in sorted({path.split("/", 1)[0] for path in expected}):
        path = skills_target / skill_id
        if _claude_link_target(path) != (runtime_target / skill_id).resolve(strict=False):
            raise CheckError(f"installed Claude skill link verification failed: {skill_id}")
    if global_link is not None and _claude_link_target(global_link) != global_target.resolve(strict=False):
        raise CheckError("installed Claude global CLAUDE.md link verification failed")


def claude_sync_apply(
    root: Path,
    skills_target: Path,
    runtime_target: Path,
    rules_target: Path,
    global_target: Path,
    codex_skills_target: Path,
    backup_root: Path,
    global_link: Path | None = None,
) -> Path | None:
    skills_target = _absolute_claude_path(skills_target)
    runtime_target = _absolute_claude_path(runtime_target)
    rules_target = _absolute_claude_path(rules_target)
    global_target = _absolute_claude_path(global_target)
    codex_skills_target = _absolute_claude_path(codex_skills_target)
    backup_root = _absolute_claude_path(backup_root)
    errors = check_repo(root)
    if errors:
        raise CheckError("repository check failed:\n" + "\n".join(errors))
    global_link = _absolute_claude_path(global_link) if global_link else None
    status = claude_sync_status(
        root, skills_target, runtime_target, rules_target, global_target, codex_skills_target,
        backup_root=backup_root, global_link=global_link,
    )
    if status.drift:
        raise CheckError("Claude runtime drift must be resolved before apply: " + "; ".join(status.drift))
    if status.conflicts:
        raise CheckError("Claude sync conflict: " + "; ".join(status.conflicts))
    if status.prerequisites:
        raise CheckError("global AGENTS.md must be synced before Claude Code")
    changed = bool(status.adds or status.changes or status.removes or status.skill_links_adds or status.skill_links_changes or status.skill_links_removes or status.rule_changed or status.global_link_changed)
    if not changed:
        return None

    desired_content, routing = claude_projection(root)
    rules_content = _claude_rules(global_target, routing)
    touched_links = sorted(set(status.skill_links_adds + status.skill_links_changes + status.skill_links_removes))
    original_links = {
        skill_id: os.readlink(skills_target / skill_id) if (skills_target / skill_id).is_symlink() else None
        for skill_id in touched_links
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    if backup_root.is_symlink():
        raise CheckError("refusing a symlinked Claude backup directory")
    backup_root.mkdir(parents=True, exist_ok=True)
    backup = backup_root / stamp
    backup.mkdir(parents=True, exist_ok=False)
    had_runtime, had_rules = runtime_target.exists(), rules_target.exists()
    write_json(backup / "snapshot.json", {
        "schema": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "provider": "claude-code",
        "runtime_existed": had_runtime,
        "rules_existed": had_rules,
        "skill_links": original_links,
    })
    if had_runtime:
        shutil.copytree(runtime_target, backup / "runtime", copy_function=shutil.copy2, symlinks=True)
    if had_rules:
        shutil.copy2(rules_target, backup / "rules.md")

    skills_target.parent.mkdir(parents=True, exist_ok=True)
    skills_target.mkdir(parents=True, exist_ok=True)
    runtime_target.parent.mkdir(parents=True, exist_ok=True)
    rules_target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{runtime_target.name}.stage-", dir=runtime_target.parent))
    rules_stage = rules_target.parent / f".{rules_target.name}.stage-{stamp}"
    old_runtime = runtime_target.parent / f".{runtime_target.name}.previous-{stamp}"
    runtime_installed = rules_installed = global_link_installed = False
    links_touched: set[str] = set()
    try:
        source_projection = active_projection(root)
        for relative, content in desired_content.items():
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_projection[relative], destination)
            if destination.read_bytes() != content:
                destination.write_bytes(content)
        manifest = {relative: _claude_hash_bytes(content) for relative, content in sorted(desired_content.items())}
        source_commit = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
        write_json(stage / MARKER, {
            "schema": MARKER_SCHEMA,
            "repository": "elias-agent-skills",
            "provider": "claude-code",
            "source_commit": source_commit,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "runtime_target": str(runtime_target),
            "files": manifest,
            "active_skill_ids": sorted({path.split("/", 1)[0] for path in manifest}),
            "routing": routing,
            "rules_target": str(rules_target),
            "rules_hash": _claude_hash_text(rules_content),
            "global_agents_hash": file_hash(global_target),
        })
        rules_stage.write_text(rules_content, encoding="utf-8")
        if had_runtime:
            os.replace(runtime_target, old_runtime)
        os.replace(stage, runtime_target)
        runtime_installed = True
        os.replace(rules_stage, rules_target)
        rules_installed = True

        desired_ids = sorted({path.split("/", 1)[0] for path in manifest})
        for skill_id in desired_ids:
            if skill_id not in status.skill_links_adds and skill_id not in status.skill_links_changes:
                continue
            path = skills_target / skill_id
            temporary_link = skills_target / f".{skill_id}.stage-{stamp}"
            temporary_link.symlink_to(runtime_target / skill_id)
            links_touched.add(skill_id)
            try:
                os.replace(temporary_link, path)
            finally:
                temporary_link.unlink(missing_ok=True)
        for skill_id in status.skill_links_removes:
            path = skills_target / skill_id
            if path.is_symlink():
                path.unlink()
            links_touched.add(skill_id)
        if status.global_link_changed and global_link is not None:
            global_link.parent.mkdir(parents=True, exist_ok=True)
            global_link.symlink_to(global_target)
            global_link_installed = True
        _verify_claude_runtime(root, skills_target, runtime_target, rules_target, global_target, global_link)
    except Exception:
        if global_link_installed and global_link is not None and global_link.is_symlink():
            global_link.unlink()
        for skill_id in links_touched:
            path = skills_target / skill_id
            if path.is_symlink():
                path.unlink()
            old_target = original_links.get(skill_id)
            if old_target is not None:
                path.symlink_to(old_target)
        if rules_installed and rules_target.exists():
            if had_rules and (backup / "rules.md").is_file():
                shutil.copy2(backup / "rules.md", rules_target)
            else:
                rules_target.unlink()
        if runtime_installed and runtime_target.exists():
            shutil.rmtree(runtime_target)
        if old_runtime.exists():
            os.replace(old_runtime, runtime_target)
        shutil.rmtree(stage, ignore_errors=True)
        rules_stage.unlink(missing_ok=True)
        raise
    else:
        if old_runtime.exists():
            shutil.rmtree(old_runtime)
        return backup


def claude_doctor(
    root: Path,
    skills_target: Path,
    runtime_target: Path,
    rules_target: Path,
    global_target: Path,
    codex_skills_target: Path,
    *,
    backup_root: Path | None = None,
    global_link: Path | None = None,
) -> list[str]:
    status = claude_sync_status(
        root, skills_target, runtime_target, rules_target, global_target, codex_skills_target,
        backup_root=backup_root, global_link=global_link,
    )
    errors = [*status.drift, *status.conflicts, *status.prerequisites]
    if status.adds or status.changes or status.removes:
        errors.append("Claude runtime differs from canonical active skills")
    if status.skill_links_adds or status.skill_links_changes or status.skill_links_removes:
        errors.append("Claude skill links differ from the managed runtime")
    if status.rule_changed:
        errors.append("Claude routing rules differ from canonical invocation metadata")
    if status.global_link_changed:
        errors.append("Claude global CLAUDE.md link is missing")
    return sorted(set(errors))


@dataclass(frozen=True)
class SourceUpdate:
    repository: str
    ref: str
    path: str
    status: str
    detail: str
    pinned_digest: str | None = None
    head_digest: str | None = None


def _git(args: Sequence[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=False)


def _fetch_object(repository: str, revision: str, destination: str, bare: Path) -> str | None:
    result = _git(["fetch", "--quiet", "--depth=1", repository, f"{revision}:refs/check/{destination}"], cwd=bare)
    return None if result.returncode else f"refs/check/{destination}"


def inspect_source_update(source: dict[str, Any]) -> SourceUpdate:
    repository, ref, path = source["repository"], source["ref"], source["path"]
    if not COMMIT_RE.fullmatch(ref):
        return SourceUpdate(repository, ref, path, "unavailable", "source uses a version snapshot rather than a Git commit")
    remote = _git(["ls-remote", repository, "HEAD"])
    if remote.returncode or not remote.stdout.split():
        return SourceUpdate(repository, ref, path, "unavailable", remote.stderr.strip() or "remote HEAD unavailable")
    head = remote.stdout.split()[0]
    with tempfile.TemporaryDirectory(prefix="agent-skills-source-") as temporary:
        bare = Path(temporary)
        initialized = _git(["init", "--bare", "--quiet", str(bare)])
        if initialized.returncode:
            return SourceUpdate(repository, ref, path, "unavailable", initialized.stderr.strip())
        pinned_ref = _fetch_object(repository, ref, "pinned", bare)
        head_ref = _fetch_object(repository, head, "head", bare)
        if not pinned_ref or not head_ref:
            return SourceUpdate(repository, ref, path, "unavailable", "could not fetch the pinned commit and current HEAD")
        pinned_spec = f"{pinned_ref}^{{tree}}" if path == "." else f"{pinned_ref}:{path}"
        head_spec = f"{head_ref}^{{tree}}" if path == "." else f"{head_ref}:{path}"
        pinned = _git(["rev-parse", pinned_spec], cwd=bare)
        current = _git(["rev-parse", head_spec], cwd=bare)
        if pinned.returncode:
            return SourceUpdate(repository, ref, path, "invalid", "recorded path does not exist at the pinned commit")
        pinned_oid = pinned.stdout.strip(); kind = _git(["cat-file", "-t", pinned_oid], cwd=bare).stdout.strip()
        pinned_digest = f"git-{kind}:{pinned_oid}"
        recorded = source.get("digest", "")
        if recorded.startswith(("git-tree:", "git-blob:")) and recorded != pinned_digest:
            return SourceUpdate(repository, ref, path, "invalid", f"recorded digest disagrees with pinned path ({pinned_digest})", pinned_digest)
        if current.returncode:
            return SourceUpdate(repository, ref, path, "review available", "recorded path was removed from current HEAD", pinned_digest)
        head_oid = current.stdout.strip(); head_kind = _git(["cat-file", "-t", head_oid], cwd=bare).stdout.strip()
        head_digest = f"git-{head_kind}:{head_oid}"
        state = "unchanged" if head_digest == pinned_digest else "review available"
        return SourceUpdate(repository, ref, path, state, "exact source path object compared", pinned_digest, head_digest)


def _inspect_source_group(repository: str, sources: list[dict[str, Any]]) -> list[SourceUpdate]:
    """Fetch each repository revision once, then compare all of its recorded paths."""
    results: list[SourceUpdate] = []
    git_sources = [source for source in sources if COMMIT_RE.fullmatch(source["ref"])]
    for source in sources:
        if source not in git_sources:
            results.append(SourceUpdate(
                repository, source["ref"], source["path"], "unavailable",
                "source uses a version snapshot rather than a Git commit",
            ))
    if not git_sources:
        return results
    remote = _git(["ls-remote", repository, "HEAD"])
    if remote.returncode or not remote.stdout.split():
        detail = remote.stderr.strip() or "remote HEAD unavailable"
        return results + [SourceUpdate(repository, source["ref"], source["path"], "unavailable", detail) for source in git_sources]
    head = remote.stdout.split()[0]
    with tempfile.TemporaryDirectory(prefix="agent-skills-source-") as temporary:
        bare = Path(temporary)
        initialized = _git(["init", "--bare", "--quiet", str(bare)])
        if initialized.returncode:
            return results + [SourceUpdate(repository, source["ref"], source["path"], "unavailable", initialized.stderr.strip()) for source in git_sources]
        head_ref = _fetch_object(repository, head, "head", bare)
        pinned_refs = {
            ref: _fetch_object(repository, ref, f"pinned-{index}", bare)
            for index, ref in enumerate(sorted({source["ref"] for source in git_sources}))
        }
        for source in git_sources:
            ref, path = source["ref"], source["path"]
            pinned_ref = pinned_refs[ref]
            if not head_ref or not pinned_ref:
                results.append(SourceUpdate(repository, ref, path, "unavailable", "could not fetch the pinned commit and current HEAD")); continue
            pinned_spec = f"{pinned_ref}^{{tree}}" if path == "." else f"{pinned_ref}:{path}"
            head_spec = f"{head_ref}^{{tree}}" if path == "." else f"{head_ref}:{path}"
            pinned = _git(["rev-parse", pinned_spec], cwd=bare)
            current = _git(["rev-parse", head_spec], cwd=bare)
            if pinned.returncode:
                results.append(SourceUpdate(repository, ref, path, "invalid", "recorded path does not exist at the pinned commit")); continue
            pinned_oid = pinned.stdout.strip(); kind = _git(["cat-file", "-t", pinned_oid], cwd=bare).stdout.strip()
            pinned_digest = f"git-{kind}:{pinned_oid}"
            recorded = source.get("digest", "")
            if recorded.startswith(("git-tree:", "git-blob:")) and recorded != pinned_digest:
                results.append(SourceUpdate(repository, ref, path, "invalid", f"recorded digest disagrees with pinned path ({pinned_digest})", pinned_digest)); continue
            if current.returncode:
                results.append(SourceUpdate(repository, ref, path, "review available", "recorded path was removed from current HEAD", pinned_digest)); continue
            head_oid = current.stdout.strip(); head_kind = _git(["cat-file", "-t", head_oid], cwd=bare).stdout.strip()
            head_digest = f"git-{head_kind}:{head_oid}"
            state = "unchanged" if head_digest == pinned_digest else "review available"
            results.append(SourceUpdate(repository, ref, path, state, "exact source path object compared", pinned_digest, head_digest))
    return results


def source_updates(root: Path = ROOT) -> list[SourceUpdate]:
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for item in discover(root):
        metadata = read_json(item["path"] / "metadata.json")
        for source in metadata.get("sources", []):
            unique[(source["repository"], source["ref"], source["path"], source["digest"])] = source
    grouped: dict[str, list[dict[str, Any]]] = {}
    for source in unique.values():
        grouped.setdefault(source["repository"], []).append(source)
    results: list[SourceUpdate] = []
    for repository, sources in sorted(grouped.items()):
        results.extend(_inspect_source_group(repository, sources))
    return results


def doctor(root: Path, target: Path, global_target: Path, *, probe_tools: bool = True) -> list[str]:
    errors = check_repo(root)
    status = sync_status(root, target, global_target)
    errors.extend(f"runtime drift: {item}" for item in status.drift)
    if status.global_drift: errors.append("global AGENTS.md was edited after the last sync")
    desired, actual = desired_hashes(root), managed_runtime_hashes(root, target)
    for relative in sorted(set(desired) | set(actual)):
        if desired.get(relative) != actual.get(relative): errors.append(f"runtime mismatch: {relative}")
    if not global_target.is_file() or file_hash(global_target) != file_hash(root / "config" / "AGENTS.md"):
        errors.append("global AGENTS.md differs from canonical source")
    if probe_tools:
        tools = read_json(root / "config" / "tools.json")
        bundles = discover(root)
        active_tools = {tool for item in bundles if item["lifecycle"] == "skills" for tool in read_json(item["path"] / "metadata.json").get("dependencies", {}).get("tools", [])}
        inactive_tools = {tool for item in bundles if item["lifecycle"] != "skills" for tool in read_json(item["path"] / "metadata.json").get("dependencies", {}).get("tools", [])}
        for name, definition in tools.items():
            if name in inactive_tools and name not in active_tools: continue
            if definition.get("kind") != "executable": continue
            probe = definition.get("probe", [])
            if not isinstance(probe, list) or not probe or not all(isinstance(v, str) for v in probe): errors.append(f"invalid executable probe for {name}")
            elif shutil.which(probe[0]) is None: errors.append(f"missing executable tool {name}: {probe[0]}")
    return sorted(set(errors))


def command_check(args: argparse.Namespace) -> int:
    errors = check_repo(ROOT)
    if args.list:
        for item in discover(ROOT):
            metadata = read_json(item["path"] / "metadata.json")
            print(f"{item['lifecycle']:<10} {item['group']:<28} {item['id']:<28} {','.join(metadata['invocation'])}")
    if errors:
        print("Check failed:", file=sys.stderr)
        for error in errors: print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Check passed: {len(discover(ROOT))} owned bundle(s)."); return 0


def command_sync(args: argparse.Namespace) -> int:
    try:
        config = runtime_config(ROOT)
        target = Path(args.target).expanduser() if args.target else config["skills"]
        global_target = Path(args.global_target).expanduser() if args.global_target else config["global_agents"]
        backup_root = Path(args.backup_root).expanduser() if args.backup_root else config["backups"]
        errors = check_repo(ROOT)
        if errors: raise CheckError("repository check failed:\n" + "\n".join(errors))
        status = sync_status(ROOT, target, global_target)
        print(f"Target: {target}")
        for label, values in (("add", status.adds), ("change", status.changes), ("remove", status.removes), ("drift", status.drift)):
            print(f"{label}: {len(values)}")
            for value in values: print(f"  {value}")
        print(f"global AGENTS.md: {'change' if status.global_changed else 'unchanged'}")
        if status.global_drift: print("global drift: edited after the last managed sync")
        if not args.apply: return 0
        backup = sync_apply(ROOT, target, global_target, backup_root, adopt_unmanaged=args.adopt_unmanaged)
    except (CheckError, OSError) as exc:
        print(str(exc), file=sys.stderr); return 1
    print(f"Applied. Rollback snapshot: {backup}"); return 0


def command_claude_sync(args: argparse.Namespace) -> int:
    try:
        config = claude_runtime_config(ROOT)
        skills_target = Path(args.skills_target).expanduser() if args.skills_target else config["claude_skills"]
        runtime_target = Path(args.runtime_target).expanduser() if args.runtime_target else config["claude_runtime"]
        rules_target = Path(args.rules_target).expanduser() if args.rules_target else config["claude_rules"]
        global_target = Path(args.global_target).expanduser() if args.global_target else config["global_agents"]
        codex_skills_target = Path(args.codex_skills_target).expanduser() if args.codex_skills_target else config["skills"]
        backup_root = Path(args.backup_root).expanduser() if args.backup_root else config["claude_backups"]
        errors = check_repo(ROOT)
        if errors:
            raise CheckError("repository check failed:\n" + "\n".join(errors))
        global_link = config.get("claude_global")
        status = claude_sync_status(
            ROOT, skills_target, runtime_target, rules_target, global_target,
            codex_skills_target, backup_root=backup_root, global_link=global_link,
        )
        print(f"Claude skills: {skills_target}")
        print(f"Claude generated runtime: {runtime_target}")
        for label, values in (("runtime add", status.adds), ("runtime change", status.changes), ("runtime remove", status.removes), ("runtime drift", status.drift)):
            print(f"{label}: {len(values)}")
            for value in values:
                print(f"  {value}")
        for label, values in (("skill link add", status.skill_links_adds), ("skill link replace", status.skill_links_changes), ("managed skill link remove", status.skill_links_removes)):
            print(f"{label}: {len(values)}")
            for value in values:
                print(f"  {value}")
        print(f"Claude routing rules: {'change' if status.rule_changed else 'unchanged'} ({rules_target})")
        if global_link is not None:
            link_state = "add" if status.global_link_changed else "conflict" if any("CLAUDE.md" in item for item in status.conflicts) else "unchanged"
            print(f"Claude global CLAUDE.md link: {link_state} ({global_link} -> {global_target})")
        print(f"supporting-only limitation: Claude does not natively enforce this invocation class ({len(status.unsupported)} skill(s)); the elias-mods plugin guard warns when loaded, and refuses only with skill_guard_refuse")
        for value in status.unsupported:
            print(f"  {value}")
        for label, values in (("conflict", status.conflicts), ("prerequisite", status.prerequisites)):
            print(f"{label}: {len(values)}")
            for value in values:
                print(f"  {value}")
        if not args.apply:
            return 1 if status.drift or status.conflicts or status.prerequisites else 0
        backup = claude_sync_apply(
            ROOT, skills_target, runtime_target, rules_target, global_target,
            codex_skills_target, backup_root, global_link,
        )
    except (CheckError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if backup is None:
        print("Claude runtime is already in sync.")
    else:
        print(f"Applied. Rollback snapshot: {backup}")
    return 0


def _print_opencode_routing(status: OpenCodeSyncStatus) -> None:
    print(f"OpenCode version: {status.version if status.version is not None else 'not detected'}")
    print(f"Routing: {len(status.routing['automatic'])} automatic, {len(status.routing['supporting_only'])} supporting-only, {len(status.routing['explicit'])} user-requested")
    print("User-requested skills remain model-loadable; descriptions and managed instructions guide request recognition.")
    for name, values in (
        ("Automatic", status.routing["automatic"]),
        ("Supporting-only", status.routing["supporting_only"]),
        ("User-requested", status.routing["explicit"]),
    ):
        print(f"{name} skills: {', '.join(values) if values else '(none)'}")
    for limitation in status.limitations:
        print(f"Routing limitation: {limitation}")


def command_opencode_sync(args: argparse.Namespace) -> int:
    try:
        config = opencode_runtime_config(ROOT)
        agents_target = Path(args.agents_target).expanduser() if args.agents_target else config["opencode_agents"]
        skills_target = Path(args.skills_target).expanduser() if args.skills_target else config["skills"]
        global_target = Path(args.global_target).expanduser() if args.global_target else config["global_agents"]
        backup_root = Path(args.backup_root).expanduser() if args.backup_root else config["opencode_backups"]
        status = opencode_sync_status(
            ROOT, agents_target, skills_target, global_target, backup_root=backup_root,
        )
        print(f"OpenCode global instructions: {agents_target} ({'change' if status.changed else 'unchanged'})")
        print(f"Shared skill path: {skills_target} (no duplicate catalog)")
        for heading, values in (("drift", status.drift), ("conflict", status.conflicts), ("prerequisite", status.prerequisites)):
            print(f"{heading}: {len(values)}")
            for value in values:
                print(f"  {value}")
        _print_opencode_routing(status)
        if not args.apply:
            return 1 if status.drift or status.conflicts or status.prerequisites else 0
        backup = opencode_sync_apply(
            ROOT, agents_target, skills_target, global_target, backup_root,
        )
    except (CheckError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if backup is None:
        print("Already current; no files changed.")
    else:
        print(f"Applied. Rollback snapshot: {backup}")
    return 0


def command_opencode_doctor(_: argparse.Namespace) -> int:
    try:
        config = opencode_runtime_config(ROOT)
        status = opencode_sync_status(
            ROOT, config["opencode_agents"], config["skills"], config["global_agents"],
            backup_root=config["opencode_backups"],
        )
        errors = opencode_doctor(
            ROOT, config["opencode_agents"], config["skills"], config["global_agents"],
            backup_root=config["opencode_backups"],
        )
    except (CheckError, OSError) as exc:
        errors = [str(exc)]
        status = None
    if status:
        _print_opencode_routing(status)
    if shutil.which("opencode") is None:
        print("Live smoke: pending; the OpenCode CLI is not installed.")
    else:
        print("Live smoke: pending; run a fresh OpenCode session to verify discovery and invocation.")
    if errors:
        print("OpenCode doctor found issues:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OpenCode structural checks passed: shared skills and managed global instructions agree with the canonical source.")
    return 0


def command_updates(_: argparse.Namespace) -> int:
    failures = False
    for result in sorted(source_updates(ROOT), key=lambda value: (value.repository, value.path, value.ref)):
        print(f"{result.status:<16} {result.repository}@{result.ref}:{result.path} — {result.detail}")
        failures |= result.status == "invalid"
    return 1 if failures else 0


def codex_handoff_warnings(codex_config: Path, handoffs: Path) -> list[str]:
    """Warn when the Codex sandbox cannot write the shared handoff directory."""
    try:
        import tomllib

        data = tomllib.loads(codex_config.read_text(encoding="utf-8")) if codex_config.is_file() else {}
    except (OSError, ValueError) as exc:
        return [f"Codex config could not be read: {codex_config} ({exc})"]
    if data.get("sandbox_mode") in (None, "danger-full-access"):
        return []
    roots = (data.get("sandbox_workspace_write") or {}).get("writable_roots") or []
    target = _absolute_path(handoffs).resolve(strict=False)
    for root in roots:
        base = _absolute_path(Path(os.path.expanduser(str(root)))).resolve(strict=False)
        if target == base or base in target.parents:
            return []
    rule_path = str(handoffs).replace(str(Path.home()), "~", 1)
    return [f"Codex sandbox cannot write {handoffs}; handoff will fail. Add \"{rule_path}\" to [sandbox_workspace_write] writable_roots in {codex_config}."]


def command_doctor(args: argparse.Namespace) -> int:
    try:
        config = runtime_config(ROOT); errors = doctor(ROOT, config["skills"], config["global_agents"])
    except (CheckError, OSError) as exc:
        errors = [str(exc)]
    raw = read_json(ROOT / "config" / "runtime.json")
    if isinstance(raw.get("handoffs"), str) and isinstance(raw.get("codex_config"), str):
        for warning in codex_handoff_warnings(Path(os.path.expanduser(raw["codex_config"])), Path(os.path.expanduser(raw["handoffs"]))):
            print(f"Warning: {warning}")
    if args.smoke: print("Smoke routing scenarios require a fresh Codex task; structural discovery is checked here.")
    if errors:
        print("Doctor found issues:")
        for error in errors: print(f"- {error}")
        return 1
    print("Doctor passed: source, runtime, global instructions, and executable tools agree."); return 0


def command_capabilities(args: argparse.Namespace) -> int:
    try:
        import capabilities

        report = capabilities.build_report(
            ROOT,
            warning_threshold_tokens=args.catalog_warning_tokens,
            skill_id=args.skill,
        )
    except (CheckError, OSError) as exc:
        print(f"Capability report failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(capabilities.render_report(report))
    return 0


def claude_read_permission_warnings(settings_path: Path, targets: Sequence[Path]) -> list[str]:
    """Warn when Claude settings would prompt before a skill reads its own reference files."""
    return claude_permission_warnings(settings_path, "Read", targets, "skills will prompt before opening their references")


def claude_permission_warnings(settings_path: Path, tool: str, targets: Sequence[Path], consequence: str) -> list[str]:
    """Warn when Claude settings lack a `<tool>(<path>/**)` allow rule covering each target."""
    try:
        settings = read_json(settings_path) if settings_path.is_file() else {}
    except (OSError, ValueError, CheckError):
        return [f"Claude settings could not be read: {settings_path}"]
    permissions = settings.get("permissions") if isinstance(settings, dict) else None
    permissions = permissions if isinstance(permissions, dict) else {}
    if permissions.get("defaultMode") == "bypassPermissions":
        return []
    allowed: list[Path] = []
    for rule in permissions.get("allow") or []:
        if not isinstance(rule, str):
            continue
        if rule == tool:
            return []
        match = re.fullmatch(rf"{tool}\((.+?)(?:/\*\*?)?\)", rule)
        if match:
            allowed.append(_absolute_path(Path(match.group(1)).expanduser()).resolve(strict=False))
    warnings = []
    for target in targets:
        resolved = _absolute_path(target).resolve(strict=False)
        if not any(resolved == base or base in resolved.parents for base in allowed):
            rule_path = str(target).replace(str(Path.home()), "~", 1)
            warnings.append(f"Claude settings do not allow {tool} on {target}; {consequence}. Add `{tool}({rule_path}/**)` to permissions.allow in {settings_path}.")
    return warnings


def command_claude_doctor(_: argparse.Namespace) -> int:
    try:
        config = claude_runtime_config(ROOT)
        errors = claude_doctor(
            ROOT, config["claude_skills"], config["claude_runtime"],
            config["claude_rules"], config["global_agents"], config["skills"],
            backup_root=config["claude_backups"], global_link=config.get("claude_global"),
        )
        status = claude_sync_status(
            ROOT, config["claude_skills"], config["claude_runtime"],
            config["claude_rules"], config["global_agents"], config["skills"],
            backup_root=config["claude_backups"],
        )
    except (CheckError, OSError) as exc:
        errors = [str(exc)]
        status = None
    if status and status.unsupported:
        print(f"Routing limitation: Claude does not natively enforce supporting-only invocation for {len(status.unsupported)} skill(s); the elias-mods plugin guard is warn-only unless skill_guard_refuse is on.")
    if "config" in locals() and "claude_settings" in config:
        for warning in claude_read_permission_warnings(config["claude_settings"], [config["claude_skills"], config["claude_runtime"]]):
            print(f"Warning: {warning}")
        if "handoffs" in config:
            for tool in ("Read", "Edit"):  # Claude applies Edit rules to every file-writing tool
                for warning in claude_permission_warnings(config["claude_settings"], tool, [config["handoffs"]], "handoff and pickup will prompt or fail"):
                    print(f"Warning: {warning}")
    if errors:
        print("Claude doctor found issues:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Claude doctor passed: generated skills, routing rules, and managed links agree with the canonical source.")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    commands = result.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check"); check.add_argument("--list", action="store_true"); check.set_defaults(func=command_check)
    sync = commands.add_parser("sync"); sync.add_argument("--apply", action="store_true"); sync.add_argument("--adopt-unmanaged", action="store_true", help="back up and replace an existing unmarked runtime during the one-time cutover"); sync.add_argument("--target"); sync.add_argument("--global-target"); sync.add_argument("--backup-root"); sync.set_defaults(func=command_sync)
    claude_sync = commands.add_parser("claude-sync", help="preview or apply the Claude Code skills and instruction projection")
    claude_sync.add_argument("--apply", action="store_true")
    claude_sync.add_argument("--skills-target")
    claude_sync.add_argument("--runtime-target")
    claude_sync.add_argument("--rules-target")
    claude_sync.add_argument("--global-target")
    claude_sync.add_argument("--codex-skills-target")
    claude_sync.add_argument("--backup-root")
    claude_sync.set_defaults(func=command_claude_sync)
    opencode_sync = commands.add_parser("opencode-sync", help="preview or apply OpenCode's shared skill and instruction setup")
    opencode_sync.add_argument("--apply", action="store_true")
    opencode_sync.add_argument("--agents-target")
    opencode_sync.add_argument("--skills-target")
    opencode_sync.add_argument("--global-target")
    opencode_sync.add_argument("--backup-root")
    opencode_sync.set_defaults(func=command_opencode_sync)
    updates = commands.add_parser("updates"); updates.set_defaults(func=command_updates)
    doctor_command = commands.add_parser("doctor"); doctor_command.add_argument("--smoke", action="store_true"); doctor_command.set_defaults(func=command_doctor)
    capability_command = commands.add_parser("capabilities", help="report agent routing, tool, orchestration, and skill-catalog status")
    capability_command.add_argument("--skill", help="show tool-dependency impact for one active skill")
    capability_command.add_argument("--catalog-warning-tokens", type=int, help="set a local catalog warning threshold (not a published product limit)")
    capability_command.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    capability_command.set_defaults(func=command_capabilities)
    claude_doctor_command = commands.add_parser("claude-doctor", help="check the installed Claude Code projection")
    claude_doctor_command.set_defaults(func=command_claude_doctor)
    opencode_doctor_command = commands.add_parser("opencode-doctor", help="check OpenCode's shared skills and global instructions")
    opencode_doctor_command.set_defaults(func=command_opencode_doctor)
    return result


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.func(arguments))
