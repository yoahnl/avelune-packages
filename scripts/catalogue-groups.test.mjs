import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';
import { groupResources, matchesResource } from '../site/catalogue-groups.js';

const resources = JSON.parse(await readFile(new URL('../packages/nb2/0.9.0/ressources.json', import.meta.url), 'utf8'));
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
for (const resource of resources) resource.search = normalize([resource.name, resource.description, ...resource.familyPath, ...resource.sourceNames].join(' '));
const empty = { q: '', family: '', kind: '', dimension: '', context: '' };

test('each retained native definition remains available exactly once in gallery groups', () => {
  const groups = groupResources(resources);
  assert.equal(groups.length, 6467);
  assert.deepEqual(groups.flatMap(group => group.resources.map(resource => resource.id)).sort(), resources.map(resource => resource.id).sort());
  for (const group of groups) assert.equal(new Set(group.resources.map(resource => resource.previewSha256)).size, 1);
});

test('trees use two pages of appearance sheets while retaining every technical variant and brush', () => {
  const trees = resources.filter(resource => resource.familyPath[0] === 'Arbres');
  assert.equal(trees.length, 521);
  assert.equal(groupResources(trees).length, 90);
  assert.equal(Math.ceil(groupResources(trees).length / 48), 2);
});

test('every family and kind filter includes every matching member, even inside shared appearance groups', () => {
  for (const family of new Set(resources.map(resource => resource.familyPath[0]))) {
    for (const kind of new Set(resources.map(resource => resource.kind))) {
      const expected = resources.filter(resource => resource.familyPath[0] === family && resource.kind === kind);
      const actual = groupResources(resources.filter(resource => matchesResource(resource, { ...empty, family, kind }, normalize))).flatMap(group => group.resources);
      assert.deepEqual(actual.map(resource => resource.id).sort(), expected.map(resource => resource.id).sort());
    }
  }
});

test('mixed contexts remain searchable from interior and exterior', () => {
  for (const resource of resources.filter(item => item.context === 'both')) {
    assert.ok(matchesResource(resource, { ...empty, context: 'interior' }, normalize));
    assert.ok(matchesResource(resource, { ...empty, context: 'exterior' }, normalize));
  }
});

test('former names remain searchable after merging', () => {
  for (const resource of resources.filter(item => item.sourceCount > 1)) {
    assert.ok(matchesResource(resource, { ...empty, q: resource.sourceNames.at(-1) }, normalize));
  }
});

test('family prefixes do not accidentally match a different family', () => {
  const resource = { familyPath: ['Arbres B'], search: '', kind: 'model3d', context: 'exterior', dimension: '3D' };
  assert.equal(matchesResource(resource, { ...empty, family: 'Arbres' }, normalize), false);
});
