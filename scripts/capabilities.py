"""Build a read-only compatibility report for the owned skills and agent hosts."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

import skills


def _tool_health(
    name: str,
    definition: dict[str, Any],
    *,
    which: Callable[[str], str | None],
    run: Callable[..., subprocess.CompletedProcess[str]],
) -> dict[str, str]:
    kind = definition.get("kind")
    if kind in {"connector", "workspace-runtime"}:
        return {
            "status": "unverified",
            "detail": "Availability is supplied by the host/session tool catalog and cannot be inspected by this repository CLI.",
        }
    if kind != "executable":
        return {"status": "unverified", "detail": "The tool has no supported availability probe."}

    probe = definition.get("probe")
    if not isinstance(probe, list) or not probe or not all(isinstance(part, str) for part in probe):
        return {"status": "unverified", "detail": "The executable probe is not configured correctly."}
    executable = which(probe[0])
    if executable is None:
        return {
            "status": "missing",
            "detail": f"Required executable is not on PATH: {probe[0]}; do not claim workflows requiring {name} succeeded.",
        }
    if name != "github":
        return {"status": "available", "detail": f"Executable is present: {probe[0]} (the workflow itself is not exercised)."}

    # Capture all CLI output and report only a normalized status. In particular,
    # never surface account details, credential-helper output, or token strings.
    try:
        result = run([executable, *probe[1:]], capture_output=True, text=True, check=False, timeout=8)
    except (OSError, subprocess.TimeoutExpired):
        return {"status": "unverified", "detail": "GitHub CLI authentication could not be checked safely."}
    if result.returncode == 0:
        return {"status": "available", "detail": "GitHub CLI authentication check succeeded; raw command output was withheld."}
    return {
        "status": "unverified",
        "detail": "GitHub CLI check did not establish whether access is available; a sandbox may hide the host keyring, so rerun in a host/keyring-enabled context if needed. Raw command output was withheld.",
    }


def _catalog(root: Path, catalog_config: dict[str, Any], override: int | None) -> dict[str, Any]:
    divisor = catalog_config.get("chars_per_estimated_token", 4)
    if not isinstance(divisor, int) or isinstance(divisor, bool) or divisor < 1:
        raise skills.CheckError("config/agent-capabilities.json: chars_per_estimated_token must be a positive integer")
    descriptors: list[str] = []
    for item in skills.discover(root):
        if item["lifecycle"] != "skills":
            continue
        metadata = skills.frontmatter(item["path"] / "SKILL.md")
        descriptors.append(f"{metadata.get('name', item['id'])} {metadata.get('description', '')}".strip())
    characters = sum(len(descriptor) for descriptor in descriptors)
    estimated_tokens = (characters + divisor - 1) // divisor
    configured_threshold = catalog_config.get("warning_threshold_tokens")
    threshold = override if override is not None else configured_threshold
    if threshold is not None and (not isinstance(threshold, int) or isinstance(threshold, bool) or threshold < 1):
        raise skills.CheckError("catalog warning threshold must be a positive integer")
    if threshold is None:
        status = "unverified"
        message = "No local warning threshold is set, and no numeric limit was found in the public guidance reviewed."
    elif estimated_tokens >= threshold:
        status = "warning"
        message = "Estimated discovery metadata has reached the configured local warning threshold; this is not a product limit."
    else:
        status = "within-local-threshold"
        message = "Estimated discovery metadata is below the configured local warning threshold."
    return {
        "skill_count": len(descriptors),
        "description_characters": characters,
        "estimated_tokens": estimated_tokens,
        "estimate_method": f"ceil(character count / {divisor}); approximate only",
        "warning_threshold_tokens": threshold,
        "status": status,
        "message": message,
        "official_limit_note": catalog_config.get("limit_note", "No numeric host limit is recorded."),
    }


def build_report(
    root: Path = skills.ROOT,
    *,
    warning_threshold_tokens: int | None = None,
    skill_id: str | None = None,
    which: Callable[[str], str | None] = shutil.which,
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    """Return host support, local tool prerequisites, routing, and catalog evidence."""
    root = Path(root)
    manifest = skills.read_json(root / "config" / "agent-capabilities.json")
    if not isinstance(manifest, dict) or manifest.get("schema") != 1:
        raise skills.CheckError("config/agent-capabilities.json: expected schema 1")
    agents = manifest.get("agents")
    if not isinstance(agents, dict) or set(agents) != {"codex", "claude-code", "opencode"}:
        raise skills.CheckError("config/agent-capabilities.json: expected Codex, Claude Code, and OpenCode entries")

    tools = skills.read_json(root / "config" / "tools.json")
    if not isinstance(tools, dict):
        raise skills.CheckError("config/tools.json: expected an object")
    if any(not isinstance(definition, dict) for definition in tools.values()):
        raise skills.CheckError("config/tools.json: every tool definition must be an object")
    tool_health = {name: _tool_health(name, definition, which=which, run=run) for name, definition in sorted(tools.items())}
    bundles = [item for item in skills.discover(root) if item["lifecycle"] == "skills"]
    by_id = {item["id"]: item for item in bundles}
    if skill_id is not None and skill_id not in by_id:
        raise skills.CheckError(f"unknown active skill: {skill_id}")
    selected = [by_id[skill_id]] if skill_id else bundles

    host_reports: list[dict[str, Any]] = []
    for agent_id, agent in agents.items():
        if not isinstance(agent, dict):
            raise skills.CheckError(f"config/agent-capabilities.json: {agent_id} must be an object")
        routing = agent.get("routing", {})
        orchestration = agent.get("orchestration", {})
        if not isinstance(routing, dict) or not isinstance(orchestration, dict):
            raise skills.CheckError(f"config/agent-capabilities.json: invalid routing/orchestration for {agent_id}")
        host_tool_health = {name: dict(result) for name, result in tool_health.items()}
        entrypoint_config = agent.get("entrypoint", {})
        if not isinstance(entrypoint_config, dict):
            raise skills.CheckError(f"config/agent-capabilities.json: invalid entrypoint for {agent_id}")
        if entrypoint_config.get("kind") == "executable":
            command = entrypoint_config.get("command")
            if not isinstance(command, str) or not command:
                raise skills.CheckError(f"config/agent-capabilities.json: missing entrypoint command for {agent_id}")
            entrypoint_status = "available" if which(command) is not None else "missing"
            entrypoint_detail = (
                f"Host CLI executable is present: {command}."
                if entrypoint_status == "available"
                else f"Host CLI executable is not on PATH: {command}."
            )
        else:
            entrypoint_status = "unverified"
            entrypoint_detail = entrypoint_config.get("detail", "The active agent session cannot be inspected by this CLI.")

        issue_tracker = orchestration.get("issue_tracker")
        if isinstance(issue_tracker, dict):
            github_status = host_tool_health.get("github", {"status": "unverified"})["status"]
            if entrypoint_status == "missing":
                issue_tracker_status = "missing"
                issue_tracker_detail = f"{agent.get('label', agent_id)} is not installed, so its issue-tracker workflow cannot run from this host."
            else:
                issue_tracker_status = "unverified"
                issue_tracker_detail = (
                    f"The host session's issue-tracker permission and operation are not exercised by this report. "
                    f"The separate local GitHub CLI check is {github_status} and does not establish host-session access."
                )
            orchestration = {
                **orchestration,
                "issue_tracker": {
                    **issue_tracker,
                    "status": issue_tracker_status,
                    "detail": issue_tracker_detail,
                },
            }
        workflow_impacts: dict[str, list[str]] = {"missing": [], "unverified": []}
        routing_impacts: dict[str, list[str]] = {
            "unsupported": [],
            "conditional": [],
            "unverified": [],
            "missing": [],
        }
        for item in selected:
            metadata = skills.read_json(item["path"] / "metadata.json")
            dependencies = metadata.get("dependencies", {}).get("tools", [])
            missing = [name for name in dependencies if host_tool_health.get(name, {"status": "missing"})["status"] == "missing"]
            unverified = [name for name in dependencies if host_tool_health.get(name, {"status": "unverified"})["status"] == "unverified"]
            if missing:
                workflow_impacts["missing"].append(f"{item['id']} ({', '.join(sorted(missing))})")
            if unverified:
                workflow_impacts["unverified"].append(f"{item['id']} ({', '.join(sorted(unverified))})")
            for mode in metadata.get("invocation", []):
                mapping = routing.get(mode)
                if not isinstance(mapping, dict):
                    routing_impacts["unsupported"].append(f"{item['id']} ({mode}; no host mapping)")
                    continue
                status = mapping.get("status", "unverified")
                if status in routing_impacts:
                    routing_impacts[status].append(f"{item['id']} ({mode})")

        host_reports.append({
            "id": agent_id,
            "label": agent.get("label", agent_id),
            "sources": agent.get("sources", []),
            "entrypoint": {"status": entrypoint_status, "detail": entrypoint_detail},
            "routing": routing,
            "orchestration": orchestration,
            "tools": host_tool_health,
            "skill_dependency_impacts": workflow_impacts,
            "skill_routing_impacts": routing_impacts,
            "scope_note": "Product support is distinct from live integration visibility: this CLI cannot inspect the agent's active session tool catalog or permission state.",
        })

    catalog_config = manifest.get("catalog", {})
    if not isinstance(catalog_config, dict):
        raise skills.CheckError("config/agent-capabilities.json: catalog must be an object")
    return {
        "report_schema": 1,
        "catalog": _catalog(root, catalog_config, warning_threshold_tokens),
        "skill_filter": skill_id,
        "agents": host_reports,
    }


def render_report(report: dict[str, Any]) -> str:
    catalog = report["catalog"]
    lines = [
        "Agent capability report (read-only)",
        f"Codex skill catalog: {catalog['skill_count']} skills; approximately {catalog['estimated_tokens']:,} discovery tokens ({catalog['description_characters']:,} characters).",
        f"Catalog status: {catalog['status']} — {catalog['message']}",
        "Tool availability is checked on this host; app/session connector visibility and permissions remain unverified by this CLI.",
        "Do not claim a tool, integration, or delegated action succeeded without a returned result; use a documented fallback or report the limitation.",
    ]
    if report.get("skill_filter"):
        lines.append(f"Workflow filter: {report['skill_filter']}")
    for agent in report["agents"]:
        lines.append("")
        lines.append(agent["label"])
        lines.append(f"  Agent entrypoint: {agent['entrypoint']['status']} — {agent['entrypoint']['detail']}")
        route_items = [f"{name}={detail['status']}" for name, detail in agent["routing"].items()]
        lines.append("  Routing: " + ", ".join(route_items))
        for name, detail in agent["routing"].items():
            if detail.get("status") in {"unsupported", "conditional", "unverified"}:
                lines.append(f"    {name}: {detail.get('detail', 'No verified native control.')}")
                if detail.get("fallback"):
                    lines.append(f"      Fallback: {detail['fallback']}")
        orchestration = ", ".join(f"{name}={detail['status']}" for name, detail in agent["orchestration"].items())
        lines.append("  Orchestration: " + orchestration)
        for name, detail in agent["orchestration"].items():
            if detail.get("status") in {"unsupported", "conditional", "unverified", "missing"}:
                lines.append(f"    {name}: {detail.get('detail', 'No verified host support.')}")
        for name in ("github", "stitch", "browser"):
            detail = agent["tools"].get(name, {"status": "unverified", "detail": "No probe is configured."})
            lines.append(f"  {name}: {detail['status']} — {detail['detail']}")
        key_tools = {"github", "stitch", "browser"}
        other_tools = {name: detail for name, detail in agent["tools"].items() if name not in key_tools}
        local_available = sorted(name for name, detail in other_tools.items() if detail["status"] == "available")
        local_missing = sorted(name for name, detail in other_tools.items() if detail["status"] == "missing")
        local_unverified = sum(detail["status"] == "unverified" for detail in other_tools.values())
        if local_available:
            lines.append("  Local executable probes available: " + ", ".join(local_available))
        if local_missing:
            lines.append("  Local executable probes missing: " + ", ".join(local_missing))
        if local_unverified:
            lines.append(f"  Other host-provided or workspace capabilities unverified: {local_unverified}")
        impacts = agent["skill_dependency_impacts"]
        for status in ("missing", "unverified"):
            entries = impacts[status]
            if entries:
                lines.append(f"  Skills with {status} tool dependencies: {len(entries)}")
                if report.get("skill_filter"):
                    lines.append("    " + "; ".join(entries))
        route_impacts = agent["skill_routing_impacts"]
        for status in ("unsupported", "conditional", "unverified", "missing"):
            entries = route_impacts[status]
            if entries:
                lines.append(f"  Skills with {status} invocation mappings: {len(entries)} — " + ", ".join(entries))
        if agent.get("sources"):
            lines.append("  Evidence: " + ", ".join(agent["sources"]))
    return "\n".join(lines)
