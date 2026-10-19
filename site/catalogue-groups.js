export function groupResources(resources) {
  const groups = new Map();
  for (const resource of resources) {
    const key = resource.appearanceGroup || resource.id;
    if (!groups.has(key)) groups.set(key, { id: key, representative: resource, resources: [] });
    groups.get(key).resources.push(resource);
  }
  return [...groups.values()];
}

export function matchesResource(resource, state, normalize) {
  const term = normalize(state.q.trim());
  const path = resource.familyPath.join(' / ');
  return (!term || resource.search.includes(term)) && (!state.kind || resource.kind === state.kind) && (!state.dimension || resource.dimension === state.dimension) && (!state.context || resource.context === state.context || state.context !== 'both' && resource.context === 'both') && (!state.family || path === state.family || path.startsWith(state.family + ' / '));
}
