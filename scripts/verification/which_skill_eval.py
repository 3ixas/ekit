#!/usr/bin/env python3
"""Run every routing case through `which-skill` in fresh Claude and Codex sessions.

Local and opt-in: it makes real model calls, so CI never runs it. For each case in
`evals/routing.json` it starts a non-interactive session in an isolated workspace
that holds this checkout's active bundles, hides the globally installed copies,
asks `which-skill` which skill should own the case's request, and parses the answer.

A case passes when the `Owner` line names the case's owner exactly. When that owner
declares an `authority_stop` in its metadata, the `Stops at` line must also name the
case's labelled boundary (keyword overlap); failures are listed for human review.

Exits 0 with a skip message for each missing CLI, and 1 when any case fails or errors.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import skills  # noqa: E402

HOSTS = ("claude", "codex")
SKILL_ID = "which-skill"
NO_FIT = "(no skill)"
LABELS = ("owner", "brings in", "say", "stops at", "also worth naming")
STOPWORDS = frozenset(
    "with that this from have been will when only must such than then into over also each unless "
    "without their they them these those other more most some what which while would about after "
    "before being does doing both same your".split()
)
# Boundary keywords that must overlap with the case label: all of them for a short label, else this many.
BOUNDARY_MIN_SHARED = 3
# Share of the owner's catalogue boundary keywords a faithful `Stops at` line must carry.
CATALOGUE_MIN_SHARE = 0.25
CATALOGUE_MIN_SHARED = 2

_LABEL_PREFIX = r"^[\s>*_`#-]*"
_OWNER_RE = re.compile(_LABEL_PREFIX + r"owner[\s*_`]*:[\s*_`]*([a-z0-9][a-z0-9-]*)", re.I | re.M)
_LABEL_LINE_RE = re.compile(
    _LABEL_PREFIX + "(?:" + "|".join(re.escape(label) for label in LABELS) + r")[\s*_`]*:", re.I
)
QUOTA_RE = re.compile(r"hit your .{0,20}limit|usage limit|rate limit|quota", re.I)
_STOPS_RE = re.compile(_LABEL_PREFIX + r"stops at[\s*_`]*:[\s*_`]*(.*)", re.I)


class QuotaError(RuntimeError):
    """Raised when a host CLI refuses a session due to a usage or rate limit."""


@dataclass
class Outcome:
    host: str
    index: int
    request: str
    expected: str
    status: str = "pass"  # pass | fail | error
    owner: str | None = None
    other_owners: list[str] = field(default_factory=list)
    stops_at: str = ""
    boundary_checked: bool = False
    boundary_label: str = ""
    shared_keywords: list[str] = field(default_factory=list)
    reason: str = ""
    output_file: str = ""


def stem(word: str) -> str:
    """Crude suffix strip so merge/merging and deploy/deployment/deploys compare equal."""
    for suffix in ("ation", "ment", "ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            word = word[: -len(suffix)]
            break
    return word[:-1] if word.endswith("e") and len(word) > 4 else word


def keywords(text: str) -> set[str]:
    return {stem(word) for word in re.findall(r"[a-z]{4,}", text.lower()) if word not in STOPWORDS}


def parse_recommendation(text: str) -> tuple[list[str], str]:
    """Return every `Owner` id in order and the `Stops at` text of the first block."""
    owners = [match.group(1).lower() for match in _OWNER_RE.finditer(text)]
    lines = text.splitlines()
    first_owner = next((i for i, line in enumerate(lines) if _OWNER_RE.match(line)), None)
    stops = ""
    if first_owner is not None:
        for i in range(first_owner, len(lines)):
            if i > first_owner and _OWNER_RE.match(lines[i]):
                break
            match = _STOPS_RE.match(lines[i])
            if not match:
                continue
            parts = [match.group(1).strip()]
            for follow in lines[i + 1:]:
                if not follow.strip() or _LABEL_LINE_RE.match(follow):
                    break
                parts.append(follow.strip())
            stops = " ".join(part for part in parts if part)
            break
    return owners, stops


def boundary_overlap(label: str, stops_at: str) -> tuple[bool, list[str]]:
    wanted = keywords(label)
    shared = sorted(wanted & keywords(stops_at))
    return len(shared) >= min(BOUNDARY_MIN_SHARED, len(wanted)), shared


def catalogue_overlap(declared: str, stops_at: str) -> tuple[bool, list[str]]:
    wanted = keywords(declared)
    shared = sorted(wanted & keywords(stops_at))
    return len(shared) >= CATALOGUE_MIN_SHARED and len(shared) >= CATALOGUE_MIN_SHARE * len(wanted), shared


def judge(
    host: str,
    index: int,
    case: dict,
    answer: str,
    declared_stop: str,
) -> Outcome:
    """Judge one answer; `declared_stop` is the owner's metadata `authority_stop`, or empty."""
    outcome = Outcome(host, index, case["request"], case.get("owner") or NO_FIT)
    owners, stops = parse_recommendation(answer)
    outcome.stops_at = stops
    if case.get("no_fit"):
        # A no-fit case passes on a plain "no skill applies" answer: no Owner line at all.
        if owners:
            outcome.status, outcome.owner = "fail", owners[0]
            outcome.reason = f"owner {owners[0]!r}, expected no skill to apply"
        return outcome
    if not owners:
        outcome.status, outcome.reason = "fail", "no Owner line in the answer"
        return outcome
    outcome.owner, outcome.other_owners = owners[0], owners[1:]
    if outcome.owner != case["owner"]:
        outcome.status = "fail"
        outcome.reason = f"owner {outcome.owner!r}, expected {case['owner']!r}"
        return outcome
    if declared_stop:
        # The case label may describe request-specific behaviour rather than the authority
        # boundary, so the owner's declared stop also counts as the labelled boundary.
        outcome.boundary_checked = True
        outcome.boundary_label = case["authority_stop"]
        label_ok, shared = boundary_overlap(case["authority_stop"], stops)
        declared_ok, declared_shared = catalogue_overlap(declared_stop, stops)
        outcome.shared_keywords = sorted(set(shared) | set(declared_shared))
        if not (label_ok or declared_ok):
            outcome.status = "fail"
            outcome.reason = "Stops at does not name the labelled boundary" if stops else "no Stops at line"
    return outcome


def prompt_for(request: str) -> str:
    return (
        "Use the which-skill skill. Which EKit skill should I use for this request? "
        "Answer in the which-skill recommendation shape and do not start any work.\n\n"
        f"Request: {request}"
    )


def prepare_workspace(root: Path) -> Path:
    """Give the session this checkout's active bundles, as a host synced from it would list them."""
    workspace = Path(tempfile.mkdtemp(prefix="which-skill-eval-", dir=root))
    bundles = [bundle for bundle in skills.discover(REPOSITORY_ROOT) if bundle["lifecycle"] == "skills"]
    for parent in (".claude/skills", ".agents/skills"):
        for bundle in bundles:
            shutil.copytree(
                bundle["path"], workspace / parent / bundle["id"],
                ignore=shutil.ignore_patterns("metadata.json", "evals"),
            )
    subprocess.run(["git", "init", "-q"], cwd=workspace, check=True, capture_output=True)
    return workspace


def ask(host: str, prompt: str, workspace: Path, model: str | None, timeout: int, scratch: Path) -> str:
    if host == "claude":
        # The prompt precedes --allowedTools, or Claude reads it as a tool name.
        # Project settings only: an installed personal skill would shadow the workspace copy.
        command = [
            "claude", "-p", prompt, "--setting-sources", "project",
            "--no-session-persistence", "--allowedTools", "Read", "Skill",
        ]
        if model:
            command += ["--model", model]
        result = subprocess.run(
            command, cwd=workspace, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout
        )
        answer = result.stdout
    else:
        last_message = scratch / "last-message.txt"
        command = [
            "codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
            "--output-last-message", str(last_message),
        ]
        if model:
            command += ["-m", model]
        # An empty HOME hides the installed ~/.agents/skills; CODEX_HOME keeps the sign-in and config.
        home = scratch / "home"
        home.mkdir(exist_ok=True)
        codex_home = os.environ.get("CODEX_HOME") or str(Path.home() / ".codex")
        result = subprocess.run(
            [*command, prompt], cwd=workspace, stdin=subprocess.DEVNULL, capture_output=True, text=True,
            timeout=timeout, env={**os.environ, "HOME": str(home), "CODEX_HOME": codex_home},
        )
        answer = last_message.read_text(encoding="utf-8") if last_message.exists() else result.stdout
    if result.returncode != 0 and not answer.strip():
        stderr_tail = result.stderr.strip()[-400:]
        if QUOTA_RE.search(stderr_tail):
            raise QuotaError(f"{host} refused the session: {stderr_tail[:200]}")
        raise RuntimeError(f"{host} exited {result.returncode}: {stderr_tail}")
    if QUOTA_RE.search(answer) and not _OWNER_RE.search(answer):
        raise QuotaError(f"{host} refused the session: {answer.strip()[:200]}")
    return answer


def run_case(
    host: str,
    index: int,
    case: dict,
    declared_stop: str,
    args: argparse.Namespace,
    output: Path,
    workspace: Path,
    scratch_root: Path,
    stop_event: threading.Event,
) -> Outcome:
    transcript = output / f"{host}-{index:02d}.txt"
    if stop_event.is_set():
        reason = f"{host} skipped after quota/rate limit"
        outcome = Outcome(host, index, case["request"], case.get("owner") or NO_FIT, "error", reason=reason)
        transcript.write_text(f"ERROR: {reason}\n", encoding="utf-8")
        outcome.output_file = str(transcript)
        return outcome
    scratch = Path(tempfile.mkdtemp(prefix=f"{host}-{index}-", dir=scratch_root))
    try:
        answer = ask(host, prompt_for(case["request"]), workspace, args.model.get(host), args.timeout, scratch)
    except QuotaError as error:
        stop_event.set()
        outcome = Outcome(host, index, case["request"], case.get("owner") or NO_FIT, "error", reason=str(error))
        transcript.write_text(f"ERROR: {error}\n", encoding="utf-8")
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as error:
        outcome = Outcome(host, index, case["request"], case.get("owner") or NO_FIT, "error", reason=str(error))
        transcript.write_text(f"ERROR: {error}\n", encoding="utf-8")
    else:
        transcript.write_text(answer, encoding="utf-8")
        outcome = judge(host, index, case, answer, declared_stop)
    outcome.output_file = str(transcript)
    return outcome


def load_cases(only: list[str] | None) -> tuple[list[tuple[int, dict, str]], dict[str, str]]:
    cases = json.loads((REPOSITORY_ROOT / "evals" / "routing.json").read_text(encoding="utf-8"))
    declared = {
        bundle["id"]: skills.read_json(bundle["path"] / "metadata.json").get("authority_stop") or ""
        for bundle in skills.discover(REPOSITORY_ROOT)
    }
    selected = [
        (index, case, declared.get(case.get("owner"), ""))
        for index, case in enumerate(cases)
        if not only or case.get("owner") in only or str(index) in only
    ]
    return selected, declared


def report(outcomes: list[Outcome], hosts: list[str]) -> str:
    lines = []
    for host in hosts:
        mine = [item for item in outcomes if item.host == host]
        counts = {status: sum(1 for item in mine if item.status == status) for status in ("pass", "fail", "error")}
        checked = [item for item in mine if item.boundary_checked]
        boundary = sum(1 for item in checked if item.status == "pass")
        lines.append(
            f"{host}: {counts['pass']}/{len(mine)} pass, {counts['fail']} fail, {counts['error']} error; "
            f"boundary check {boundary}/{len(checked)}"
        )
    lines.append("")
    lines.append("case  owner                      " + "  ".join(f"{host:<6}" for host in hosts) + "  request")
    for index in sorted({item.index for item in outcomes}):
        row = [item for item in outcomes if item.index == index]
        cells = {item.host: item.status.upper() for item in row}
        lines.append(
            f"{index:<4}  {row[0].expected:<25}  "
            + "  ".join(f"{cells.get(host, '-'):<6}" for host in hosts)
            + f"  {row[0].request[:70]}"
        )
    failures = [item for item in outcomes if item.status != "pass"]
    if failures:
        lines += ["", "Failures for human review:"]
        for item in sorted(failures, key=lambda value: (value.index, value.host)):
            lines.append(f"- case {item.index} on {item.host} [{item.status}]: {item.reason}")
            lines.append(f"    request: {item.request}")
            if item.boundary_checked:
                lines.append(f"    labelled boundary: {item.boundary_label}")
                lines.append(f"    Stops at: {item.stops_at or '(missing)'}")
                lines.append(f"    shared keywords: {', '.join(item.shared_keywords) or 'none'}")
            lines.append(f"    transcript: {item.output_file}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--host", choices=(*HOSTS, "all"), default="all")
    parser.add_argument("--only", nargs="*", help="run only these case indexes or owner skill ids")
    parser.add_argument("--jobs", type=int, default=2, help="concurrent sessions per host")
    parser.add_argument("--timeout", type=int, default=300, help="seconds allowed per session")
    parser.add_argument("--claude-model")
    parser.add_argument("--codex-model")
    parser.add_argument("--output-dir", type=Path, help="keep raw answers and results.json here")
    args = parser.parse_args(argv)
    args.model = {"claude": args.claude_model, "codex": args.codex_model}

    wanted = list(HOSTS) if args.host == "all" else [args.host]
    hosts = []
    for host in wanted:
        if shutil.which(host):
            hosts.append(host)
        else:
            print(f"Skipping {host}: `{host}` CLI not found on PATH.")
    if not hosts:
        print("No host CLI available; skipping the which-skill behavioural eval.")
        return 0

    cases, _ = load_cases(args.only)
    if not cases:
        print("No routing case matches --only.", file=sys.stderr)
        return 2
    output = args.output_dir or Path(tempfile.mkdtemp(prefix="which-skill-eval-results-"))
    output.mkdir(parents=True, exist_ok=True)
    print(f"Running {len(cases)} cases on {', '.join(hosts)}; answers in {output}", flush=True)

    outcomes: list[Outcome] = []
    stop_events = {host: threading.Event() for host in hosts}
    with tempfile.TemporaryDirectory(prefix="which-skill-eval-") as scratch_root:
        workspace = prepare_workspace(Path(scratch_root))
        with ThreadPoolExecutor(max_workers=max(1, args.jobs) * len(hosts)) as pool:
            futures = [
                pool.submit(
                    run_case, host, index, case, declared, args, output, workspace, Path(scratch_root), stop_events[host]
                )
                for host in hosts
                for index, case, declared in cases
            ]
            for future in futures:
                outcomes.append(future.result())

    (output / "results.json").write_text(
        json.dumps([item.__dict__ for item in outcomes], indent=2), encoding="utf-8"
    )
    print(report(outcomes, hosts))
    return 0 if all(item.status == "pass" for item in outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
