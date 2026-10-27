"""A downloaded checkout exports complete review bundles without installation."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'skill_bundle.py'


class SkillBundleTests(unittest.TestCase):
    def test_downloaded_source_retains_dependency_assets_notices_and_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / 'source'
            for name, deps in [('primary', ['support']), ('support', [])]:
                bundle = root / 'skills' / 'group' / name
                (bundle / 'assets').mkdir(parents=True)
                (bundle / 'SKILL.md').write_text('Use `conditional` when a chart is needed.\n')
                (bundle / 'metadata.json').write_text(json.dumps({'id': name, 'dependencies': {'skills': deps, 'tools': ['renderer']}, 'sources': [{'license': 'apache-2.0-fixture'}]}))
                (bundle / 'assets' / 'fixture.txt').write_text('complete asset\n')
            conditional = root / 'skills' / 'group' / 'conditional'
            conditional.mkdir()
            (conditional / 'SKILL.md').write_text('Conditional branch\n')
            (conditional / 'metadata.json').write_text(json.dumps({'id': 'conditional', 'dependencies': {'skills': [], 'tools': []}, 'sources': []}))
            (root / 'licenses').mkdir()
            (root / 'licenses' / 'apache-2.0-fixture.txt').write_text('retain this notice\n')
            (root / 'THIRD_PARTY_NOTICES.md').write_text('source terms\n')
            (root / 'LICENSE_SCOPE.md').write_text('upstream exceptions\n')
            (root / 'config').mkdir()
            (root / 'config/AGENTS.md').write_text('PRIVATE GLOBALS\n')
            (root / 'AGENTS.md').write_text('source instructions\n')
            (root / 'CLAUDE.md').write_text('source instructions\n')
            out = pathlib.Path(temp) / 'review'
            command = [sys.executable, str(SCRIPT), '--root', str(root), '--revision', 'a' * 40, '--output-dir', str(out), 'primary']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out / 'bundle-manifest.json').read_text())
            self.assertEqual(manifest['skills'], ['primary', 'support'])
            self.assertEqual(manifest['revision'], 'a' * 40)
            self.assertEqual((out / 'skills/group/support/assets/fixture.txt').read_text(), 'complete asset\n')
            self.assertEqual((out / 'licenses/apache-2.0-fixture.txt').read_text(), 'retain this notice\n')
            self.assertIn('conditional', manifest['instruction_mentions_requiring_review'])
            self.assertFalse((out / 'config').exists())
            self.assertFalse((out / 'AGENTS.md').exists())
            self.assertFalse((out / 'CLAUDE.md').exists())
            self.assertEqual((out / 'LICENSE_SCOPE.md').read_text(), 'upstream exceptions\n')
            # Never overwrite the reviewer's existing work.
            repeated = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(repeated.returncode, 0)
            self.assertEqual((out / 'licenses/apache-2.0-fixture.txt').read_text(), 'retain this notice\n')
            conditional_out = pathlib.Path(temp) / 'conditional-review'
            with_condition = [sys.executable, str(SCRIPT), '--root', str(root), '--revision', 'a' * 40,
                              '--output-dir', str(conditional_out), '--include', 'conditional', 'primary']
            conditional_result = subprocess.run(with_condition, capture_output=True, text=True)
            self.assertEqual(conditional_result.returncode, 0, conditional_result.stderr)
            self.assertEqual(json.loads((conditional_out / 'bundle-manifest.json').read_text())['skills'],
                             ['conditional', 'primary', 'support'])

    def test_symlinked_source_roots_cannot_export_outside_checkout_contents(self):
        for boundary in ('group', 'bundle', 'docs', 'licenses'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as temp:
                root = pathlib.Path(temp) / 'source'
                bundle = root / 'skills/group/primary'
                bundle.mkdir(parents=True)
                (bundle / 'SKILL.md').write_text('Primary\n')
                (bundle / 'metadata.json').write_text(json.dumps({'id': 'primary', 'sources': [{'license': 'apache-2.0-fixture'}]}))
                (root / 'licenses').mkdir()
                (root / 'licenses/apache-2.0-fixture.txt').write_text('notice\n')
                (root / 'docs').mkdir()
                (root / 'docs/guide.md').write_text('outside content must not travel through a symlink\n')
                (root / 'THIRD_PARTY_NOTICES.md').write_text('terms\n')
                source = {'group': root / 'skills/group', 'bundle': bundle,
                          'docs': root / 'docs', 'licenses': root / 'licenses'}[boundary]
                outside = pathlib.Path(temp) / 'outside'
                source.rename(outside)
                source.symlink_to(outside, target_is_directory=True)
                output = pathlib.Path(temp) / 'review'
                result = subprocess.run([sys.executable, str(SCRIPT), '--root', str(root), '--revision', 'b' * 40,
                                         '--output-dir', str(output), 'primary'], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertFalse(output.exists())
