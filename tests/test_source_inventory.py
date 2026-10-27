"""Provenance maintenance must stay within the downloaded checkout."""
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts/source_inventory.py"


def fixture(parent):
    root = parent / "source"
    (root / "docs/provenance").mkdir(parents=True)
    (root / "docs/provenance/retained-sources.json").write_text(json.dumps({
        "method_snapshots": [], "bundled_assets": [], "sources": []}))
    (root / "licenses").mkdir()
    (root / "licenses/mit-fixture.txt").write_text("reviewed new terms\n")
    for owner in ("a-clean", "z-indirect"):
        bundle = root / "skills/group" / owner
        (bundle / "references/licenses").mkdir(parents=True)
        (bundle / "references/licenses/mit-fixture.txt").write_text("original internal bytes\n")
        (bundle / "metadata.json").write_text(json.dumps({"id": owner, "sources": [{
            "repository": "https://example.test/upstream", "ref": "a" * 40,
            "path": "method.md", "digest": "git-blob:" + "b" * 40,
            "use": "copied", "license": "mit-fixture", "changes": "local adaptation"}]}))
        (bundle / "NOTICE.txt").write_text("references/licenses/mit-fixture.txt\n")
    return root


def snapshot(parent):
    return {str(p.relative_to(parent)): p.read_bytes()
            for p in parent.rglob("*") if p.is_file()}


def run(root, mode="refresh-metadata"):
    return subprocess.run([sys.executable, str(SCRIPT), mode, "--root", str(root)],
                          capture_output=True, text=True)


class SourceInventoryTests(unittest.TestCase):
    def test_reviewed_refresh_updates_only_inventory_and_portable_notices(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = pathlib.Path(temp)
            root = fixture(parent)
            unrelated = parent / "unrelated.txt"
            unrelated.write_text("preserve unrelated content\n")
            before = snapshot(parent)
            result = run(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(run(root, "check").returncode, 0)
            expected_changes = {
                "source/docs/provenance/retained-sources.json",
                "source/skills/group/a-clean/references/licenses/mit-fixture.txt",
                "source/skills/group/z-indirect/references/licenses/mit-fixture.txt"}
            after = snapshot(parent)
            self.assertEqual({p for p in before if before[p] != after[p]}, expected_changes)
            self.assertEqual(unrelated.read_text(), "preserve unrelated content\n")

    def test_indirected_refresh_is_rejected_before_any_internal_or_external_write(self):
        components = ("root", "companion", "internal-companion", "companion-parent",
                      "references", "bundle", "metadata", "notice", "canonical-licence",
                      "canonical-parent", "inventory", "inventory-parent", "docs", "lifecycle")
        for component in components:
            with self.subTest(component=component), tempfile.TemporaryDirectory() as temp:
                parent = pathlib.Path(temp)
                root = fixture(parent)
                bundle = root / "skills/group/z-indirect"
                selected = {
                    "root": root,
                    "companion": bundle / "references/licenses/mit-fixture.txt",
                    "internal-companion": bundle / "references/licenses/mit-fixture.txt",
                    "companion-parent": bundle / "references/licenses",
                    "references": bundle / "references",
                    "bundle": bundle,
                    "metadata": bundle / "metadata.json",
                    "notice": bundle / "NOTICE.txt",
                    "canonical-licence": root / "licenses/mit-fixture.txt",
                    "canonical-parent": root / "licenses",
                    "inventory": root / "docs/provenance/retained-sources.json",
                    "inventory-parent": root / "docs/provenance",
                    "docs": root / "docs",
                    "lifecycle": root / "skills"}[component]
                target = (root / "internal-target.txt" if component == "internal-companion"
                          else parent / "outside-target")
                if selected.is_dir():
                    shutil.copytree(selected, target)
                    shutil.rmtree(selected)
                else:
                    shutil.copy2(selected, target)
                    selected.unlink()
                selected.symlink_to(target, target_is_directory=target.is_dir())
                before = snapshot(parent)
                result = run(root)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(snapshot(parent), before,
                                 "rejected refresh changed existing internal/external bytes")
