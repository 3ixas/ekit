#!/usr/bin/env python3
"""Export selected active skills for review; never install or project globals."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def checked_source(path: Path, root: Path) -> None:
    """Reject indirection both at a source root and anywhere below it."""
    if root.is_symlink():
        raise ValueError(f'symlink checkout root: {root}')
    if not path.is_relative_to(root) or not path.resolve().is_relative_to(root):
        raise ValueError(f'source escapes checkout: {path}')
    current = root
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'symlink source component: {current}')


def checked_tree(source: Path, root: Path) -> None:
    checked_source(source, root)
    for path in source.rglob('*'):
        checked_source(path, root)


def copy_directory(source: Path, target: Path, root: Path) -> None:
    checked_tree(source, root)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))


def export(root: Path, output: Path, requested: list[str], revision: str) -> dict:
    if output == root or output.is_relative_to(root):
        raise ValueError('output must be outside the source checkout')
    if output.exists():
        raise ValueError(f'output already exists: {output}')
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('revision must be the full 40-character downloaded commit SHA')
    checked_source(root / 'skills', root)
    catalog = {}
    for metadata in sorted((root / 'skills').glob('*/*/metadata.json')):
        checked_source(metadata, root)
        data = json.loads(metadata.read_text())
        skill_id = data['id']
        if skill_id in catalog:
            raise ValueError(f'duplicate active skill id: {skill_id}')
        catalog[skill_id] = (metadata.parent, data)
    selected = set()
    pending = list(requested)
    while pending:
        skill_id = pending.pop()
        if skill_id in selected:
            continue
        if skill_id not in catalog:
            raise ValueError(f'not an active skill or missing dependency: {skill_id}')
        selected.add(skill_id)
        pending.extend(catalog[skill_id][1].get('dependencies', {}).get('skills', []))
    licences = set()
    tools = set()
    mentions = set()
    for skill_id in selected:
        source, metadata = catalog[skill_id]
        checked_tree(source, root)
        tools.update(metadata.get('dependencies', {}).get('tools', []))
        for record in metadata.get('sources', []):
            licence = record['license']
            if not re.fullmatch(r'[a-z0-9][a-z0-9.-]*', licence):
                raise ValueError(f'invalid licence identifier: {licence}')
            if not (root / 'licenses' / f'{licence}.txt').is_file():
                raise ValueError(f'missing licence companion: {licence}')
            licences.add(licence)
        for text in source.rglob('*.md'):
            mentions.update(set(re.findall(r'`([a-z][a-z0-9-]+)`', text.read_text())) & catalog.keys())
    checked_tree(root / 'licenses', root)
    if (root / 'docs').exists():
        checked_tree(root / 'docs', root)
    for name in ('LICENSE', 'LICENSE_SCOPE.md', 'THIRD_PARTY_NOTICES.md'):
        checked_source(root / name, root)
    if not (root / 'THIRD_PARTY_NOTICES.md').is_file():
        raise ValueError('missing THIRD_PARTY_NOTICES.md')
    # Build only a new review directory, never an installation destination.
    output.mkdir(parents=True)
    for skill_id in sorted(selected):
        source, _ = catalog[skill_id]
        target = output / source.relative_to(root)
        target.parent.mkdir(parents=True, exist_ok=True)
        copy_directory(source, target, root)
    (output / 'licenses').mkdir()
    for companion in sorted((root / 'licenses').glob('*.txt')):
        if companion.is_symlink():
            raise ValueError(f'symlink licence companion: {companion}')
        shutil.copy2(companion, output / 'licenses' / companion.name)
    for name in ('LICENSE', 'LICENSE_SCOPE.md', 'THIRD_PARTY_NOTICES.md'):
        if (root / name).is_file():
            shutil.copy2(root / name, output / name)
    if (root / 'docs').is_dir():
        copy_directory(root / 'docs', output / 'docs', root)
    manifest = {
        'schema_version': 1,
        'revision': revision,
        'revision_evidence': 'Operator-supplied downloaded revision; file hashes identify actual exported bytes. No network verification is performed.',
        'requested': sorted(set(requested)),
        'skills': sorted(selected),
        'tools_requiring_host_verification': sorted(tools),
        'instruction_mentions_requiring_review': sorted(mentions - selected),
        'conditional_review': 'Mentions are a heuristic, not a complete dependency parser. Read instructions and local companions, then rerun with --include for required conditional owners.',
        'installation': 'Review only. No personal globals, credentials, managed markers or plugin installation are applied.',
        'files': {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(output.rglob('*')) if p.is_file()},
    }
    (output / 'bundle-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('skills', nargs='+')
    parser.add_argument('--include', action='append', default=[], help='Additional conditionally required active skill ID; repeat as needed')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--revision', required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = export(args.root.resolve(), args.output_dir.resolve(), args.skills + args.include, args.revision)
    except (ValueError, OSError, KeyError, json.JSONDecodeError) as exc:
        parser.exit(1, f'{exc}\n')
    print(json.dumps({k: manifest[k] for k in ('revision', 'skills', 'tools_requiring_host_verification', 'instruction_mentions_requiring_review')}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
