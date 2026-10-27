"""Technical CLI checks; no design benchmark or generated comparison builds."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
OWNER = ROOT / 'skills/frontend-and-design/interface-design'
TOOLKIT = OWNER / 'assets/taste-toolkit'
LAUNCHER = OWNER / 'scripts/taste.mjs'
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node unavailable')
class TasteToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.env = {**os.environ, 'TASTE_SKILL_TMP': str(self.root)}
        self.env.pop('TASTE_SKILL_HISTORY', None)

    def cli(self, *args, env=None, timeout=60):
        return subprocess.run([NODE, str(LAUNCHER), *args], cwd=self.root,
                              env={**self.env, **(env or {})}, text=True,
                              capture_output=True, timeout=timeout)

    def policy(self, exceptions):
        (self.root / 'DESIGN.md').write_text('# Approved design\nViolet, hairlines, quiet typography.\n')
        folder = self.root / '.taste-skill'
        folder.mkdir(exist_ok=True)
        (folder / 'policy.json').write_text(json.dumps({
            'version': 1, 'designContract': '../DESIGN.md', 'exceptions': exceptions,
        }))

    def test_seeded_page_draw_saved_reuse_and_project_history(self):
        args = ('draw', '--sector', 'personal-portfolio', '--brief', 'A portfolio',
                '--sections', 'work,about,contact', '--direction', 'name-as-monument', '--seed', '42')
        result = self.cli(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        sheet = json.loads((self.root / '.taste-skill/direction.json').read_text())
        self.assertEqual(sheet['seed'], 42)
        self.assertEqual(sheet['direction']['id'], 'name-as-monument')
        self.assertTrue((self.root / '.taste-skill/history.json').is_file())
        shown = self.cli('draw', '--show')
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertIn(sheet['direction']['name'], shown.stdout)
        # Separate project, same seed and constraints, no shared draw history.
        second = self.root / 'second'; second.mkdir()
        result = subprocess.run([NODE, str(LAUNCHER), *args], cwd=second, env=self.env, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        other = json.loads((second / '.taste-skill/direction.json').read_text())
        for key in ['direction', 'hero', 'type', 'palette', 'sections']:
            self.assertEqual(sheet[key], other[key])

    def test_options_read_only_and_app_draw(self):
        result = self.cli('draw', '--app', '--kind', 'finance', '--brief', 'Shared budget', '--seed', '42', '--options', '3')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / '.taste-skill').exists())
        result = self.cli('draw', '--app', '--kind', 'finance', '--brief', 'Shared budget', '--seed', '42')
        self.assertEqual(result.returncode, 0, result.stderr)
        sheet = json.loads((self.root / '.taste-skill/direction.json').read_text())
        self.assertEqual(sheet['kind'], 'app')
        self.assertTrue(sheet['screens'])
        self.assertEqual(self.cli('draw', '--show').returncode, 0)

    def test_policy_keeps_violet_and_hairlines_visible_without_failure(self):
        self.policy({'palette-purple': 'Approved brand', 'hairline': 'Approved separators'})
        (self.root / 'index.html').write_text('<style>h1 { color:#6366f1; border-bottom:1px solid black; }</style><h1>Example</h1>')
        result = self.cli('lint', 'index.html', '--json')
        self.assertEqual(result.returncode, 0, result.stderr)
        findings = json.loads(result.stdout)['findings']
        for rule in ['palette-purple', 'hairline']:
            found = [f for f in findings if f['id'] == rule]
            self.assertTrue(found)
            self.assertTrue(all(f['level'] == 'INFO' and f['category'] == 'aesthetic' and f['exception'] for f in found))

    def test_policy_rejects_unknown_functional_or_missing_contract(self):
        for exceptions in [{'broken-image': 'Ignore'}, {'invented-rule': 'Ignore'}]:
            self.policy(exceptions)
            (self.root / 'index.html').write_text('<h1>Example</h1>')
            self.assertEqual(self.cli('lint', 'index.html', '--json').returncode, 2)
        (self.root / 'DESIGN.md').unlink()
        self.assertEqual(self.cli('lint', 'index.html', '--json').returncode, 2)

    def test_lint_specific_policy_is_accepted_by_both_clis(self):
        self.policy({'framework-colour': 'Approved project framework tokens'})
        (self.root / 'index.html').write_text('<h1>Fixture</h1>')
        self.assertEqual(self.cli('lint', 'index.html', '--json').returncode, 0)
        result = self.cli('inspect', 'http://127.0.0.1:1', '--json', env={'CHROME_PATH': '/nonexistent/chrome'})
        self.assertEqual(result.returncode, 2)
        report = json.loads(result.stdout)
        self.assertIn('browser executable', report['error'])
        self.assertNotIn('policy rule', report['error'])

    def test_missing_runtime_and_browser_report_unavailable(self):
        result = self.cli('draw', '--list', 'directions', env={'TASTE_NODE': '/nonexistent/node'})
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['status'], 'unavailable')
        (self.root / 'index.html').write_text('<h1>Example</h1>')
        result = self.cli('inspect', 'http://127.0.0.1:1', '--json', env={'CHROME_PATH': '/nonexistent/chrome'})
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'unavailable')

    def test_network_failure_is_unavailable_not_empty_success(self):
        shim = self.root / 'offline.mjs'
        shim.write_text("globalThis.fetch = async () => { throw new Error('offline fixture'); };\n")
        result = self.cli('assets', 'ceramics', '--source', 'openverse', '--json', env={'NODE_OPTIONS': f'--import={shim}'})
        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'unavailable')
        self.assertTrue(report['sources'][0]['error'])

    def test_shipped_resources_and_no_competing_entrypoint(self):
        manifest = json.loads((TOOLKIT / 'provenance.json').read_text())
        self.assertEqual(len(manifest['files']), 39)
        for entry in manifest['files']:
            self.assertTrue((TOOLKIT / entry['local_path']).is_file(), entry)
        self.assertFalse(list(TOOLKIT.rglob('SKILL.md')))
        self.assertFalse((TOOLKIT / 'library/scenes.json').exists())
        result = self.cli('draw', '--list', 'scenes')
        self.assertIn('No scene library yet', result.stdout)

    def test_asset_download_records_credit_and_refuses_other_licences(self):
        shim = self.root / 'asset-service.mjs'
        shim.write_text("""const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lXkAAAAASUVORK5CYII=', 'base64');
globalThis.fetch = async (url) => String(url).includes('api.openverse.org')
 ? Response.json({id:'fixture',title:'Ceramic study',creator:'Fixture Artist',license:'by',license_version:'4.0',foreign_landing_url:'https://example.org/source',url:'https://example.org/fixture.png',width:1,height:1})
 : new Response(png, {headers:{'content-type':'image/png'}});
""")
        result = self.cli('assets', '--get', 'openverse:fixture', env={'NODE_OPTIONS': f'--import={shim}'})
        self.assertEqual(result.returncode, 0, result.stderr)
        credits = json.loads((self.root / 'assets/credits.json').read_text())
        self.assertEqual(credits[0]['creator'], 'Fixture Artist')
        self.assertEqual(credits[0]['licenseCode'], 'by')
        self.assertEqual(credits[0]['page'], 'https://example.org/source')
        self.assertTrue((self.root / credits[0]['file']).read_bytes().startswith(b'\x89PNG'))
        result = self.cli('assets', '--credits')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Fixture Artist', result.stdout)
        shim.write_text(shim.read_text().replace("license:'by'", "license:'by-nc'"))
        result = self.cli('assets', '--get', 'openverse:fixture', env={'NODE_OPTIONS': f'--import={shim}'})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(json.loads((self.root / 'assets/credits.json').read_text())), 1)

    def test_profile_sweep_preserves_active_foreign_and_unowned_profiles(self):
        module = (TOOLKIT / 'scripts/lib/cdp.mjs').as_uri()
        script = """import {mkdirSync,writeFileSync,existsSync} from 'node:fs';
import {join} from 'node:path'; import {hostname} from 'node:os';
import {sweepProfiles} from MODULE;
for (const name of ['active','foreign','unowned','dead']) {
 const p = join(process.cwd(),'ad-chrome-'+name); mkdirSync(p);
 if(name !== 'unowned') writeFileSync(join(p,'taste-skill-owner.json'),JSON.stringify({host:name === 'foreign' ? 'another-machine' : hostname(),pid:name === 'active' ? process.pid : 2147483647,chrome:2147483647}));
}
sweepProfiles(process.cwd());
console.log(JSON.stringify(Object.fromEntries(['active','foreign','unowned','dead'].map(n => [n,existsSync(join(process.cwd(),'ad-chrome-'+n))]))));
""".replace('MODULE', json.dumps(module))
        result = subprocess.run([NODE, '--input-type=module', '-e', script], cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {'active': True, 'foreign': True, 'unowned': True, 'dead': False})

    @unittest.skipUnless(os.environ.get('TASTE_BROWSER_TESTS') == '1', 'Set TASTE_BROWSER_TESTS=1 for real Chromium fixture checks')
    def test_real_browser_defects_survive_style_exceptions_and_cleanup(self):
        self.policy({'palette-purple': 'Approved brand', 'hairline': 'Approved separators',
                     'few-pictures': 'Type specimen', 'still-page': 'Quiet specimen'})
        (self.root / 'index.html').write_text('''<!doctype html><html lang="en"><head><title>Fixture</title>
<style>body{margin:24px;font:18px Arial;color:#111;background:white}h1{font-size:60px;line-height:1.1;color:#6366f1;border-bottom:1px solid black}.wide{width:2400px}.crop{height:26px;overflow:hidden}p{max-width:600px}</style></head>
<body><h1>Fixture</h1><p>This is a technical fixture with deliberate geometry defects.</p>
<div class="crop"><h2 style="margin:0;font-size:50px;transform:translateY(-22px)">Clipped title</h2></div>
<div class="wide">Accidental page overflow</div><img src="/missing-image.png" alt="Broken fixture"><p>End of fixture.</p></body></html>''')
        result = self.cli('inspect', 'index.html', '--widths', '1440,390', '--json', timeout=100)
        self.assertEqual(result.returncode, 1, result.stderr + result.stdout[:500])
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'measured')
        ids = {f['id'] for f in report['findings']}
        self.assertTrue({'overflow', 'broken-image', 'clipped-text'} <= ids, ids)
        for finding in report['findings']:
            if finding['id'] in {'palette-purple', 'hairline'}:
                self.assertEqual(finding['level'], 'INFO')
            if finding['id'] in {'overflow', 'broken-image', 'clipped-text'}:
                self.assertEqual(finding['category'], 'functional')
        self.assertTrue(report['images'])
        self.assertFalse(list(self.root.glob('ad-chrome-*')))
        (self.root / 'broken-probe.html').write_text('<h1>Probe fixture</h1><script>document.createRange = () => { throw new Error("required probe unavailable"); };</script>')
        result = self.cli('inspect', 'broken-probe.html', '--widths', '390', '--json', timeout=40)
        self.assertEqual(result.returncode, 2, result.stderr + result.stdout[:500])
        self.assertEqual(json.loads(result.stdout)['status'], 'unavailable')
        self.assertFalse(list(self.root.glob('ad-chrome-*')))



if __name__ == '__main__':
    unittest.main()
