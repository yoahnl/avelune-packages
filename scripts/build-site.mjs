import { cp, mkdir, rm, readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { join, relative } from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const output = join(root, 'dist');
await rm(output, { recursive: true, force: true });
await mkdir(output);
const registry = JSON.parse(await readFile(join(root, 'catalogue.json'), 'utf8'));
const activeVersions = new Map(registry.packages.map(pack => [pack.id, pack.version]));
const galleryPaths = new Set(await Promise.all(registry.packages.map(async pack => {
  const manifest = JSON.parse(await readFile(join(root, pack.manifest), 'utf8'));
  return join('packages', pack.id, pack.version, manifest.catalogue.gallery);
})));
for (const entry of ['index.html', 'ressources.html', 'site', 'packages', 'catalogue.json']) {
  await cp(join(root, entry), join(output, entry), { recursive: true, filter: source => {
    const path = relative(root, source);
    const parts = path.split('/');
    if (parts[0] === 'packages' && parts.length >= 3 && activeVersions.get(parts[1]) !== parts[2]) return false;
    if (parts[0] === 'packages' && parts.length === 4 && source.endsWith('.html') && !galleryPaths.has(path)) return false;
    return !/\.(aveluneassets|zip)$/.test(source) && !source.endsWith('.DS_Store') && !source.endsWith('.receipt.json');
  } });
}
console.log('Site statique préparé dans dist/. Aucun cache, source de travail ou package binaire inclus.');
