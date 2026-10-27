// Owned policy: DESIGN.md governs intentional aesthetic exceptions; measurements stay visible.
import { existsSync, readFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { RULE_IDS } from './rules.mjs';

const policyRules = new Set([...RULE_IDS, 'copy', 'cta-copy', 'default-font', 'h-screen', 'em-dash', 'transition-all', 'ease-in', 'scale-zero', 'bounce', 'framework-colour']);

const functional = new Set(['broken-image', 'overflow', 'clipped-text', 'covered-text', 'reduced-hidden', 'font-fallback', 'scene-not-started']);
const heuristic = new Set(['contrast', 'focal-point', 'empty-screens', 'empty-middle', 'blank-gap', 'lopsided', 'off-centre', 'ragged-edges', 'unused-canvas', 'below-fold', 'panel-void', 'hero-void', 'one-sided-bleed', 'pinned-over-picture', 'long-pin', 'side-scroll', 'scene-not-live', 'scene-heavy', 'many-scenes']);

export function category(id) {
  return functional.has(id) ? 'functional' : heuristic.has(id) ? 'heuristic' : 'aesthetic';
}

export function loadPolicy(args) {
  const index = args.indexOf('--policy');
  if (index >= 0 && (!args[index + 1] || args[index + 1].startsWith('--'))) throw new Error('--policy requires a JSON file');
  const path = resolve(index >= 0 ? args.splice(index, 2)[1] : '.taste-skill/policy.json');
  if (!existsSync(path)) {
    if (index >= 0) throw new Error(`Policy not found: ${path}`);
    return { path: null, exceptions: {}, designContract: null };
  }
  const policy = JSON.parse(readFileSync(path, 'utf8'));
  if (policy?.version !== 1 || typeof policy.designContract !== 'string' || !policy.designContract.trim()
      || !policy.exceptions || Array.isArray(policy.exceptions) || typeof policy.exceptions !== 'object') throw new Error('Policy requires version:1, designContract and an exceptions object');
  const designContract = resolve(dirname(path), policy.designContract);
  if (!existsSync(designContract)) throw new Error(`Design contract not found: ${designContract}`);
  for (const [id, reason] of Object.entries(policy.exceptions)) {
    if (!policyRules.has(id)) throw new Error(`Unknown policy rule: ${id}`);
    if (category(id) === 'functional') throw new Error(`Functional diagnostic cannot be waived: ${id}`);
    if (typeof reason !== 'string' || !reason.trim()) throw new Error(`Exception ${id} requires the recorded design reason`);
  }
  return { path, designContract, exceptions: policy.exceptions };
}

export function applyPolicy(findings, policy, allowances = []) {
  return findings.map((finding) => {
    const kind = category(finding.id);
    const reason = policy.exceptions[finding.id]
      || (kind !== 'functional' && allowances.includes(finding.id) ? 'Explicit --allow or direction-sheet allowance; reconcile with DESIGN.md.' : null);
    return { ...finding, category: kind, upstreamLevel: finding.level,
      requiresConfirmation: kind === 'heuristic' || ['overflow', 'clipped-text', 'covered-text'].includes(finding.id),
      ...(reason ? { level: 'INFO', exception: reason } : kind === 'heuristic' ? { level: 'WARN' } : {}) };
  });
}
