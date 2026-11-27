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
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import skills  # noqa: E402

HOSTS = ("claude", "codex")
SUBSETS = ("sample", "explicit", "boundary")
CANARY_THRESHOLD = 5
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
_NO_FIT_RE = re.compile(
    r"\bno\b.{0,30}\bskill\b|\bask normally\b|\bdoes not apply\b|\bdoesn['’]t apply\b|\bnone of the\b",
    re.I,
)
_STOPS_RE = re.compile(_LABEL_PREFIX + r"stops at[\s*_`]*:[\s*_`]*(.*)", re.I)


class QuotaError(RuntimeError):
    """Raised when a host CLI refuses a session due to a usage or rate limit."""


class ResumeError(ValueError):
    """Raised when --resume cannot safely reuse an existing results.json."""


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
    declared_boundary: str = ""
    shared_keywords: list[str] = field(default_factory=list)
    reason: str = ""
    output_file: str = ""
    model: str | None = None

    @classmethod
    def from_dict(cls, raw: object) -> Outcome:
        if not isinstance(raw, dict):
            raise ResumeError("Cannot resume: malformed outcome entry in results.json.")
        host = raw.get("host")
        index = raw.get("index")
        request = raw.get("request")
        expected = raw.get("expected")
        status = raw.get("status")
        if (
            not isinstance(host, str)
            or not isinstance(index, int)
            or isinstance(index, bool)
            or not isinstance(request, str)
            or not isinstance(expected, str)
            or status not in ("pass", "fail", "error")
        ):
            raise ResumeError("Cannot resume: outcome entry in results.json is missing required fields.")
        other_owners = raw.get("other_owners", [])
        shared_keywords = raw.get("shared_keywords", [])
        if not isinstance(other_owners, list) or not all(isinstance(v, str) for v in other_owners):
            raise ResumeError("Cannot resume: invalid other_owners in results.json.")
        if not isinstance(shared_keywords, list) or not all(isinstance(v, str) for v in shared_keywords):
            raise ResumeError("Cannot resume: invalid shared_keywords in results.json.")
        owner = raw.get("owner")
        if owner is not None and not isinstance(owner, str):
            raise ResumeError("Cannot resume: invalid owner in results.json.")
        model = raw.get("model")
        if model is not None and not isinstance(model, str):
            raise ResumeError("Cannot resume: invalid model in results.json.")
        stops_at = raw.get("stops_at", "")
        boundary_checked = raw.get("boundary_checked", False)
        boundary_label = raw.get("boundary_label", "")
        declared_boundary = raw.get("declared_boundary", "")
        reason = raw.get("reason", "")
        output_file = raw.get("output_file", "")
        if (
            not isinstance(stops_at, str)
            or not isinstance(boundary_checked, bool)
            or not isinstance(boundary_label, str)
            or not isinstance(declared_boundary, str)
            or not isinstance(reason, str)
            or not isinstance(output_file, str)
        ):
            raise ResumeError("Cannot resume: invalid optional field in results.json.")
        return cls(
            host=host,
            index=index,
            request=request,
            expected=expected,
            status=status,
            owner=owner,
            other_owners=list(other_owners),
            stops_at=stops_at,
            boundary_checked=boundary_checked,
            boundary_label=boundary_label,
            declared_boundary=declared_boundary,
            shared_keywords=list(shared_keywords),
            reason=reason,
            output_file=output_file,
            model=model,
        )


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
    if not answer.strip():
        outcome.status, outcome.reason = "fail", "empty answer"
        return outcome
    owners, stops = parse_recommendation(answer)
    outcome.stops_at = stops
    if case.get("no_fit"):
        # A no-fit case passes on a plain "no skill applies" answer: no Owner line at all.
        if owners:
            outcome.status, outcome.owner = "fail", owners[0]
            outcome.reason = f"owner {owners[0]!r}, expected no skill to apply"
        elif not _NO_FIT_RE.search(answer):
            outcome.status, outcome.reason = "fail", "answer did not state that no skill applies"
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
        outcome.declared_boundary = declared_stop
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
    claude_files, _ = skills.claude_projection(REPOSITORY_ROOT)
    shared_files = skills.runtime_projection(REPOSITORY_ROOT, opencode_v2=False)
    for parent, projected in ((".claude/skills", claude_files), (".agents/skills", shared_files)):
        for relative, content in projected.items():
            destination = workspace / parent / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
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
    if result.returncode != 0:
        detail = (result.stderr.strip() or answer.strip())[-400:]
        if QUOTA_RE.search(result.stderr) or QUOTA_RE.search(answer):
            raise QuotaError(f"{host} refused the session: {detail[:200]}")
        raise RuntimeError(f"{host} exited {result.returncode}: {detail}")
    if QUOTA_RE.search(answer) and not _OWNER_RE.search(answer):
        raise QuotaError(f"{host} refused the session: {answer.strip()[:200]}")
    return answer


def _skipped_outcome(
    host: str,
    index: int,
    case: dict,
    output: Path,
    reason: str,
    model: str | None = None,
) -> Outcome:
    transcript = output / f"{host}-{index:02d}.txt"
    outcome = Outcome(host, index, case["request"], case.get("owner") or NO_FIT, "error", reason=reason, model=model)
    transcript.write_text(f"ERROR: {reason}\n", encoding="utf-8")
    outcome.output_file = str(transcript)
    return outcome


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
    model = args.model.get(host)
    if stop_event.is_set():
        return _skipped_outcome(host, index, case, output, f"{host} skipped after quota/rate limit", model=model)
    scratch = Path(tempfile.mkdtemp(prefix=f"{host}-{index}-", dir=scratch_root))
    try:
        answer = ask(host, prompt_for(case["request"]), workspace, model, args.timeout, scratch)
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
    outcome.model = model
    return outcome


def _declared_stops() -> dict[str, str]:
    return {
        bundle["id"]: skills.read_json(bundle["path"] / "metadata.json").get("authority_stop") or ""
        for bundle in skills.discover(REPOSITORY_ROOT)
    }


def compute_fingerprint(declared: dict[str, str] | None = None) -> str:
    """SHA-256 of the evaluated inputs: projected which-skill bundle, routing cases, and declared stops."""
    digest = hashlib.sha256()

    def add(label: str, data: bytes) -> None:
        label_bytes = label.encode("utf-8")
        digest.update(f"{len(label_bytes)}:".encode("ascii") + label_bytes + b"\0")
        digest.update(f"{len(data)}:".encode("ascii") + data + b"\n")

    add("evals/routing.json", (REPOSITORY_ROOT / "evals" / "routing.json").read_bytes())

    claude_files, _ = skills.claude_projection(REPOSITORY_ROOT)
    shared_files = skills.runtime_projection(REPOSITORY_ROOT, opencode_v2=False)
    prefix = f"{SKILL_ID}/"
    for kind, projected in (("claude", claude_files), ("shared", shared_files)):
        for relative in sorted(key for key in projected if key.startswith(prefix)):
            add(f"{kind}:{relative}", projected[relative])

    if declared is None:
        declared = _declared_stops()
    add("declared_stops", json.dumps(declared, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def load_results(
    results_path: Path,
    expected_fingerprint: str,
    host_models: dict[str, str | None] | None = None,
) -> dict[tuple[str, int], Outcome]:
    if not results_path.exists():
        return {}
    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ResumeError(f"Cannot resume: failed to read {results_path}: {error}") from error
    if (
        not isinstance(data, dict)
        or not isinstance(data.get("fingerprint"), str)
        or not isinstance(data.get("outcomes"), list)
    ):
        raise ResumeError(
            f"Cannot resume: {results_path} has no valid input fingerprint (legacy or malformed results.json). "
            "Use a new --output-dir or remove results.json."
        )
    stored_fingerprint = data["fingerprint"]
    if stored_fingerprint != expected_fingerprint:
        raise ResumeError(
            f"Cannot resume: input fingerprint mismatch in {results_path} "
            f"(stored {stored_fingerprint[:12]}, current {expected_fingerprint[:12]}). "
            "Inputs changed; use a new --output-dir or remove results.json."
        )
    loaded: dict[tuple[str, int], Outcome] = {}
    for entry in data["outcomes"]:
        outcome = Outcome.from_dict(entry)
        loaded[(outcome.host, outcome.index)] = outcome
    if host_models:
        for host, wanted_model in host_models.items():
            stored_models = {item.model for item in loaded.values() if item.host == host}
            if stored_models and stored_models != {wanted_model}:
                found = ", ".join(repr(model or "(default)") for model in sorted(stored_models, key=lambda v: v or ""))
                expected = repr(wanted_model or "(default)")
                raise ResumeError(
                    f"Cannot resume: {host} model mismatch in {results_path} "
                    f"(stored {found}, current {expected}). "
                    f"Pass matching --{host}-model or use a new --output-dir."
                )
    return loaded


def save_results(
    results_path: Path,
    fingerprint: str,
    outcomes_by_key: dict[tuple[str, int], Outcome],
) -> None:
    ordered = [
        outcomes_by_key[key].__dict__
        for key in sorted(outcomes_by_key, key=lambda pair: (pair[1], pair[0]))
    ]
    payload = json.dumps({"fingerprint": fingerprint, "outcomes": ordered}, indent=2) + "\n"
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=results_path.parent,
            prefix=".results-",
            suffix=".tmp",
            delete=False,
        ) as handle:
            tmp_path = Path(handle.name)
            handle.write(payload)
        os.replace(tmp_path, results_path)
    except BaseException:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise


def select_subset(cases: list[dict], declared: dict[str, str], subset: str) -> list[int]:
    """Return deterministic routing.json indexes for a named iteration subset."""
    if subset == "explicit":
        return [index for index, case in enumerate(cases) if case.get("explicit")]
    if subset == "boundary":
        return [
            index
            for index, case in enumerate(cases)
            if declared.get(case.get("owner"), "") or case.get("no_fit")
        ]
    if subset == "sample":
        seen_explicit: set[str] = set()
        seen_auto_boundary: set[str] = set()
        selected: list[int] = []
        for index, case in enumerate(cases):
            owner = case.get("owner") or ""
            if case.get("no_fit"):
                selected.append(index)
            elif case.get("explicit"):
                if owner not in seen_explicit:
                    seen_explicit.add(owner)
                    selected.append(index)
            elif declared.get(owner, "") and owner not in seen_auto_boundary:
                seen_auto_boundary.add(owner)
                selected.append(index)
        return selected
    raise ValueError(f"Unknown subset: {subset!r}")


def load_cases(
    only: list[str] | None,
    subset: str | None = None,
) -> tuple[list[tuple[int, dict, str]], dict[str, str]]:
    if only and subset is not None:
        raise ValueError("--only and --subset cannot be used together.")
    cases = json.loads((REPOSITORY_ROOT / "evals" / "routing.json").read_text(encoding="utf-8"))
    declared = _declared_stops()
    if subset is not None:
        wanted_indexes = set(select_subset(cases, declared, subset))
        selected = [
            (index, case, declared.get(case.get("owner"), ""))
            for index, case in enumerate(cases)
            if index in wanted_indexes
        ]
        return selected, declared
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
                if item.declared_boundary:
                    lines.append(f"    declared boundary: {item.declared_boundary}")
                lines.append(f"    Stops at: {item.stops_at or '(missing)'}")
                lines.append(f"    shared keywords: {', '.join(item.shared_keywords) or 'none'}")
            lines.append(f"    transcript: {item.output_file}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--host", choices=(*HOSTS, "all"), default="all")
    selector = parser.add_mutually_exclusive_group()
    selector.add_argument("--only", nargs="+", help="run only these case indexes or owner skill ids")
    selector.add_argument(
        "--subset",
        choices=SUBSETS,
        help="run a deterministic iteration slice: sample (explicit primaries + boundary + no-fit), explicit, or boundary",
    )
    parser.add_argument("--jobs", type=int, default=2, help="concurrent sessions per host")
    parser.add_argument("--timeout", type=int, default=300, help="seconds allowed per session")
    parser.add_argument("--claude-model")
    parser.add_argument("--codex-model")
    parser.add_argument("--output-dir", type=Path, help="keep raw answers and results.json here")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip cases that already passed in --output-dir/results.json when the input fingerprint matches",
    )
    parser.add_argument(
        "--no-canary",
        action="store_true",
        help=f"skip the 1-case-per-host canary before fanning out runs with more than {CANARY_THRESHOLD} pending cases",
    )
    args = parser.parse_args(argv)
    args.model = {"claude": args.claude_model, "codex": args.codex_model}

    if args.resume and not args.output_dir:
        print("--resume requires --output-dir.", file=sys.stderr)
        return 2

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

    cases, declared = load_cases(args.only, args.subset)
    if not cases:
        selector_flag = "--subset" if args.subset else "--only"
        print(f"No routing case matches {selector_flag}.", file=sys.stderr)
        return 2

    fingerprint = compute_fingerprint(declared)
    output = args.output_dir or Path(tempfile.mkdtemp(prefix="which-skill-eval-results-"))
    results_path = output / "results.json"

    saved_outcomes: dict[tuple[str, int], Outcome] = {}
    if args.resume:
        try:
            saved_outcomes = load_results(
                results_path,
                fingerprint,
                host_models={host: args.model.get(host) for host in hosts},
            )
        except ResumeError as error:
            print(str(error), file=sys.stderr)
            return 2

    output.mkdir(parents=True, exist_ok=True)

    reused_count = 0
    pending_by_host: dict[str, list[tuple[int, dict, str]]] = {host: [] for host in hosts}
    for index, case, declared_stop in cases:
        for host in hosts:
            prior = saved_outcomes.get((host, index)) if args.resume else None
            if prior is not None and prior.status == "pass" and prior.model == args.model.get(host):
                reused_count += 1
            else:
                pending_by_host[host].append((index, case, declared_stop))

    total_pending = sum(len(items) for items in pending_by_host.values())
    if args.resume and reused_count:
        if total_pending == 0:
            print(
                f"Resuming in {output}: all {reused_count} selected case(s) already passed; nothing to run.",
                flush=True,
            )
        else:
            print(
                f"Resuming in {output}: reusing {reused_count} passed case(s), "
                f"running {total_pending} remaining across {', '.join(hosts)}",
                flush=True,
            )
    else:
        print(f"Running {len(cases)} cases on {', '.join(hosts)}; answers in {output}", flush=True)

    def record_outcomes(*items: Outcome) -> None:
        for item in items:
            saved_outcomes[(item.host, item.index)] = item
        save_results(results_path, fingerprint, saved_outcomes)

    if total_pending > 0:
        stop_events = {host: threading.Event() for host in hosts}
        per_host_workers = max(1, args.jobs)
        with tempfile.TemporaryDirectory(prefix="which-skill-eval-") as scratch_root:
            workspace = prepare_workspace(Path(scratch_root))
            pools = {host: ThreadPoolExecutor(max_workers=per_host_workers) for host in hosts}

            def submit(host: str, index: int, case: dict, declared_stop: str) -> Future[Outcome]:
                return pools[host].submit(
                    run_case,
                    host,
                    index,
                    case,
                    declared_stop,
                    args,
                    output,
                    workspace,
                    Path(scratch_root),
                    stop_events[host],
                )

            canary_futures: dict[Future[Outcome], tuple[str, list[tuple[int, dict, str]]]] = {}
            in_flight: set[Future[Outcome]] = set()
            interrupted = False
            try:
                for host in hosts:
                    host_pending = pending_by_host[host]
                    if not host_pending:
                        continue
                    if not args.no_canary and len(host_pending) > CANARY_THRESHOLD:
                        canary_item, rest = host_pending[0], host_pending[1:]
                        print(
                            f"Running canary case {canary_item[0]} on {host} "
                            f"before fanning out {len(rest)} remaining case(s).",
                            flush=True,
                        )
                        future = submit(host, *canary_item)
                        canary_futures[future] = (host, rest)
                        in_flight.add(future)
                    else:
                        for index, case, declared_stop in host_pending:
                            in_flight.add(submit(host, index, case, declared_stop))

                while in_flight:
                    done, in_flight = wait(in_flight, return_when=FIRST_COMPLETED)
                    for future in done:
                        outcome = future.result()
                        if future in canary_futures:
                            host, rest = canary_futures.pop(future)
                            if outcome.status == "error":
                                reason = (
                                    f"{host} skipped after quota/rate limit"
                                    if stop_events[host].is_set()
                                    else f"{host} skipped after canary error: {outcome.reason}"
                                )
                                skipped = [
                                    _skipped_outcome(host, index, case, output, reason, model=args.model.get(host))
                                    for index, case, _declared_stop in rest
                                ]
                                record_outcomes(outcome, *skipped)
                            else:
                                record_outcomes(outcome)
                                for index, case, declared_stop in rest:
                                    in_flight.add(submit(host, index, case, declared_stop))
                        else:
                            record_outcomes(outcome)
            except BaseException:
                interrupted = True
                for event in stop_events.values():
                    event.set()
                for future in in_flight:
                    future.cancel()
                raise
            finally:
                for pool in pools.values():
                    pool.shutdown(wait=not interrupted, cancel_futures=interrupted)

    save_results(results_path, fingerprint, saved_outcomes)
    run_outcomes = [
        saved_outcomes[(host, index)]
        for index, _case, _declared_stop in cases
        for host in hosts
    ]
    print(report(run_outcomes, hosts))
    return 0 if all(item.status == "pass" for item in run_outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())
