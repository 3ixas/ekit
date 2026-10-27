#!/usr/bin/env python3
"""Check retained source hashes/notices; refresh owned metadata after reviewed edits."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from skill_bundle import checked_source

EXCLUDED_OWNERS = {"documents", "pdf", "slides", "spreadsheets", "data-analysis", "data-visualization"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata_sources(root: Path) -> list[dict]:
    rows = []
    for lifecycle in ("skills", "candidates", "paused"):
        checked_source(root / lifecycle, root)
        for path in sorted((root / lifecycle).glob("*/*/metadata.json")):
            checked_source(path, root)
            metadata = json.loads(path.read_text())
            if metadata["id"] in EXCLUDED_OWNERS:
                continue
            for source in metadata["sources"]:
                if not re.fullmatch(r"[a-z0-9][a-z0-9.-]*", source["license"]):
                    raise ValueError(f"invalid licence identifier: {source['license']}")
                disposition = "retained under recorded upstream terms; preserve companions"
                if source["use"] == "informed-by":
                    disposition = "reference-only; no copying grant asserted"
                elif source["license"].startswith("declared-mit-"):
                    disposition = "retained under pinned README MIT declaration, supplied attribution and accompanying standard terms"
                elif any(word in source["license"] for word in ("unlicensed", "proprietary", "restricted")):
                    disposition = "publication-blocker: permission/notice evidence unresolved"
                rows.append({"bundle": str(path.parent.relative_to(root)),
                             **{key: value for key, value in source.items() if key != "bundle"},
                             "notice": "references/licenses/" + source["license"] + ".txt",
                             "disposition": disposition})
    return rows


def check_bodies(root: Path, inventory: dict) -> None:
    for section, path_key, hash_key in (("method_snapshots", "path", "local_file_sha256"),
                                       ("bundled_assets", "local", "local_sha256")):
        for row in inventory[section]:
            path = root / row[path_key]
            checked_source(path, root)
            if not path.is_file() or digest(path) != row[hash_key]:
                raise ValueError(f"{path}: retained bytes changed; review source comparison and update the explicit record")


def run(root: Path, refresh: bool) -> None:
    # Reject an aliased chosen checkout before canonicalising system path aliases.
    if root.is_symlink():
        raise ValueError(f"symlink checkout root: {root}")
    root = root.resolve()
    checked_source(root, root)
    path = root / "docs/provenance/retained-sources.json"
    checked_source(path, root)
    inventory = json.loads(path.read_text())
    check_bodies(root, inventory)
    sources = metadata_sources(root)
    writes = {}
    # Validate every input, existing ancestor and destination before any write.
    for row in sources:
        source = root / "licenses" / (row["license"] + ".txt")
        companion = root / row["bundle"] / row["notice"]
        notice = root / row["bundle"] / "NOTICE.txt"
        for candidate in (source, companion, notice):
            checked_source(candidate, root)
        if companion.exists() and not companion.is_file():
            raise ValueError(f"not a regular companion file: {companion}")
        for parent in companion.parents:
            if parent == root:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"not a companion directory: {parent}")
        terms = source.read_bytes()
        if not notice.is_file() or row["notice"] not in notice.read_text():
            raise ValueError(f"{notice}: missing companion pointer; update it before refresh")
        writes[companion] = terms
    if refresh:
        inventory["sources"] = sources
        for companion, terms in writes.items():
            companion.parent.mkdir(parents=True, exist_ok=True)
            companion.write_bytes(terms)
        path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n")
    if inventory["sources"] != sources:
        raise ValueError("owned metadata inventory drift; review changes then run refresh-metadata")
    for companion, terms in writes.items():
        if not companion.is_file() or companion.read_bytes() != terms:
            raise ValueError(f"{companion}: missing or stale portable notice")
    print(f"Source inventory passed: {len(sources)} source records; retained bodies and portable notices match.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "refresh-metadata"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        run(args.root, args.mode == "refresh-metadata")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
