import assert from 'node:assert/strict';
import { readFile, stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve, relative } from 'node:path';
import { createHash } from 'node:crypto';
import { groupResources } from '../site/catalogue-groups.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const read = async path => JSON.parse(await readFile(join(root, path), 'utf8'));
const registry = await read('catalogue.json');
assert.equal(new Set(registry.packages.map(pack => `${pack.id}:${pack.version}`)).size, registry.packages.length);
const nb2Entry = registry.packages.find(pack => pack.id === 'nb2');
const nb2 = await read(nb2Entry.manifest);
const directory = dirname(nb2Entry.manifest);
const resources = await read(join(directory, 'ressources.json'));
assert.equal(resources.length, nb2.counts.primaryResources);
assert.equal(new Set(resources.map(resource => resource.id)).size, nb2.counts.primaryResources);
assert.equal(groupResources(resources).length, nb2.counts.galleryCards);
const aliases = await read(join(directory, nb2.deduplication.aliases));
assert.equal(aliases.length, nb2.deduplication.mergedResources);
assert.equal(new Set(aliases.map(item => `${item.kind}:${item.previousId}`)).size, aliases.length);
const identities = new Set(resources.map(resource => `${resource.kind}:${resource.id}`));
for (const alias of aliases) {
  assert.ok(identities.has(`${alias.kind}:${alias.resourceId}`));
  assert.ok(!identities.has(`${alias.kind}:${alias.previousId}`));
}
const types = {};
const previews = new Set();
for (const resource of resources) {
  types[resource.kind] = (types[resource.kind] || 0) + 1;
  assert.ok(resource.name && resource.familyPath.length && ['2D', '3D'].includes(resource.dimension));
  assert.ok(['both', 'exterior', 'interior', 'unspecified'].includes(resource.context));
  assert.match(resource.preview, /^apercus\/[a-f0-9]{24}\.png$/);
  previews.add(resource.preview);
}
assert.deepEqual(types, { model3d: 5506, element: 130, tileset: 1225, character: 911, smartTilePreset: 421, borderBlueprint: 229, environmentPreset: 396 });
for (const preview of previews) {
  const data = await readFile(join(root, directory, preview));
  assert.equal(data.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
  assert.ok(resources.filter(resource => resource.preview === preview).every(resource => resource.previewSha256 === createHash('sha256').update(data).digest('hex')));
}
let links = 0;
for (const path of ['index.html', 'ressources.html', ...await Promise.all(registry.packages.map(async entry => join(dirname(entry.manifest), (await read(entry.manifest)).catalogue.gallery)))]) {
  const html = await readFile(join(root, path), 'utf8');
  assert.match(html, /lang="fr"/);
  assert.match(html, /site\/dark.css/);
  assert.match(html, /brand\/avelune-studio.svg/);
  for (const [, url] of html.matchAll(/(?:href|src)="([^"]+)"/g)) {
    if (url.startsWith('#') || /^[a-z]+:/i.test(url)) continue;
    const target = resolve(dirname(join(root, path)), decodeURIComponent(url.split(/[?#]/)[0]));
    assert.ok(!relative(root, target).startsWith('..'), `Lien hors site : ${url}`);
    await stat(target);
    links++;
  }
}
for (const capture of await read('site/media/captures.json')) {
  const data = await readFile(join(root, 'site/media', capture.file));
  assert.equal(createHash('sha256').update(data).digest('hex'), capture.sha256);
  assert.ok(capture.source && capture.context);
}
for (const pack of registry.packages) {
  const manifest = await read(pack.manifest);
  assert.equal(pack.version, manifest.version);
  assert.equal(pack.id, manifest.id);
  assert.ok(pack.presentation.title && pack.presentation.format && pack.presentation.description);
  for (const image of pack.presentation.images) await stat(join(root, dirname(pack.manifest), image));
  assert.match(manifest.archive.url, /^https:\/\/github.com\/yoahnl\/avelune-packages\/releases\/download\//);
  const checksum = await readFile(join(root, dirname(pack.manifest), `${manifest.archive.file}.sha256`), 'utf8');
  assert.equal(checksum.split(/\s+/)[0], manifest.archive.sha256);
}
const frlgEntry = registry.packages.find(pack => pack.id === 'frlg');
const frlg = await read(frlgEntry.manifest);
const frlgResources = await read(join(dirname(frlgEntry.manifest), 'apercus.json'));
assert.equal(frlgResources.length, frlg.counts.standardDecorModels);
for (const resource of frlgResources) {
  assert.equal(createHash('sha256').update(await readFile(join(root, dirname(frlgEntry.manifest), resource.preview))).digest('hex'), resource.previewSha256);
}
console.log(JSON.stringify({ status: 'valid', resources: resources.length, previews: previews.size, localLinks: links, types }));

if (frlg.catalogue.resources) {
  const illustrated = await read(join(dirname(frlgEntry.manifest), frlg.catalogue.resources));
  assert.equal(illustrated.length, frlg.counts.galleryResources);
  assert.equal(new Set(illustrated.map(item => item.id)).size, illustrated.length);
  assert.equal(groupResources(illustrated).length, frlg.counts.galleryCards);
  const known = new Set(illustrated.map(item => item.id));
  for (const resource of illustrated) {
    assert.ok(resource.familyPath.length && resource.dimension === '2D');
    assert.ok(['both', 'exterior', 'interior', 'unspecified'].includes(resource.context));
    for (const id of resource.relatedResourceIds || []) assert.ok(known.has(id));
    for (const key of ['preview', 'rawPreview']) if (resource[key]) {
      assert.ok(!resource[key].includes('..') && !resource[key].startsWith('/'));
      const hash = createHash('sha256').update(await readFile(join(root, dirname(frlgEntry.manifest), resource[key]))).digest('hex');
      assert.equal(hash, resource[key + 'Sha256']);
    }
  }
  console.log(JSON.stringify({ status: 'valid-frlg-gallery', illustratedResources: illustrated.length, cards: frlg.counts.galleryCards }));
}
