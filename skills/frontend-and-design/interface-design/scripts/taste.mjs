#!/usr/bin/env node
// Resolve a compatible local runtime without changing the user's shell or installing anything.
import { existsSync, readdirSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const commands = new Set(['draw', 'assets', 'lint', 'inspect', 'scenes']);
const [command, ...args] = process.argv.slice(2);
if (!commands.has(command)) {
  console.error('Usage: node taste.mjs draw|assets|lint|inspect|scenes [upstream arguments]');
  process.exit(2);
}
const candidates = process.env.TASTE_NODE ? [process.env.TASTE_NODE] : [process.execPath];
if (!process.env.TASTE_NODE) {
  const nvm = join(homedir(), '.nvm/versions/node');
  if (existsSync(nvm)) for (const version of readdirSync(nvm).sort((a, b) => b.localeCompare(a, undefined, { numeric: true }))) candidates.push(join(nvm, version, 'bin/node'));
  candidates.push(join(homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'));
}
const node = candidates.find((candidate) => {
  const result = spawnSync(candidate, ['--version'], { encoding: 'utf8', timeout: 5000 });
  return result.status === 0 && Number(result.stdout.match(/^v(\d+)\./)?.[1]) >= 22;
});
if (!node) {
  console.log(JSON.stringify({ status: 'unavailable', error: 'Taste requires an existing Node 22+ executable. Set TASTE_NODE; nothing was installed.' }));
  process.exit(2);
}
const script = resolve(dirname(fileURLToPath(import.meta.url)), '../assets/taste-toolkit/scripts', `${command}.mjs`);
const result = spawnSync(node, [script, ...args], { stdio: 'inherit', env: process.env });
if (result.error || result.signal) {
  console.error(JSON.stringify({ status: 'unavailable', error: result.error?.message || `Interrupted: ${result.signal}` }));
  process.exit(2);
}
process.exit(result.status ?? 2);
