const $ = id => document.getElementById(id);
const node = (tag, className, text) => {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text) result.textContent = text;
  return result;
};
const normalize = value => value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase();
const contexts = { interior: 'Intérieur', exterior: 'Extérieur', both: 'Intérieur & extérieur' };
const params = new URLSearchParams(location.search);
let resources = [];
let page = 1;
const state = { q: params.get('q') || '', family: params.get('family') || '', context: params.get('context') || '' };
const size = 48;

function openResource(resource) {
  const layout = node('div', 'detail-layout');
  const picture = node('div', 'detail-picture');
  const image = node('img');
  image.src = resource.preview;
  image.alt = resource.name;
  picture.append(image);
  const copy = node('div', 'detail-copy');
  const title = node('h2', '', resource.name);
  title.id = 'detail-title';
  copy.append(node('span', 'tag', contexts[resource.placementContext] || 'Contexte à préciser'), title, node('p', 'family-trail', resource.family), node('p', '', resource.description), node('p', 'detail-note', `${resource.nativeDimensionsPx.join(' × ')} px · ${resource.frameCount} frame(s). L’aperçu montre la première frame.`));
  layout.append(picture, copy);
  $('resource-detail').replaceChildren(layout);
  $('resource-dialog').showModal();
}

function render() {
  const query = normalize(state.q.trim());
  const filtered = resources.filter(resource => (!state.family || resource.family === state.family) && (!state.context || resource.placementContext === state.context || resource.placementContext === 'both') && (!query || normalize(`${resource.name} ${resource.family} ${resource.description}`).includes(query)));
  const pages = Math.max(1, Math.ceil(filtered.length / size));
  page = Math.min(page, pages);
  $('result-count').textContent = `${filtered.length} décor(s) sur ${resources.length} · inventaire complet dans le CSV`;
  $('empty-state').hidden = filtered.length > 0;
  $('pagination').hidden = pages < 2;
  $('previous').disabled = page === 1;
  $('next').disabled = page === pages;
  $('page-label').textContent = `Page ${page} / ${pages}`;
  $('active-filters').textContent = [state.family, contexts[state.context]].filter(Boolean).join(' · ');
  $('resource-grid').replaceChildren(...filtered.slice((page - 1) * size, page * size).map(resource => {
    const card = node('button', 'resource-card');
    const picture = node('span', 'resource-picture');
    const image = node('img');
    image.src = resource.preview;
    image.alt = '';
    image.loading = 'lazy';
    picture.append(image, node('span', 'dimension', '2D'));
    const copy = node('span', 'resource-copy');
    copy.append(node('span', 'resource-family', resource.family), node('h3', '', resource.name), node('span', 'resource-meta', contexts[resource.placementContext]));
    card.append(picture, copy);
    card.addEventListener('click', () => openResource(resource));
    return card;
  }));
  const params = new URLSearchParams(Object.entries(state).filter(([, value]) => value));
  history.replaceState(null, '', location.pathname + (params.size ? `?${params}` : ''));
}

function reset() {
  state.q = state.family = state.context = '';
  for (const key of Object.keys(state)) $(key === 'q' ? 'search' : key).value = '';
  page = 1;
  render();
}

try {
  const response = await fetch('apercus.json');
  if (!response.ok) throw new Error('Catalogue indisponible');
  resources = await response.json();
  for (const family of [...new Set(resources.map(resource => resource.family))].sort((a, b) => a.localeCompare(b, 'fr'))) {
    const option = node('option', '', family);
    option.value = family;
    $('family').append(option);
  }
  $('search').value = state.q;
  for (const key of ['family', 'context']) {
    $(key).value = state[key];
    if ($(key).value !== state[key]) state[key] = '';
    $(key).addEventListener('change', () => { state[key] = $(key).value; page = 1; render(); });
  }
  render();
} catch {
  $('result-count').textContent = 'Impossible de charger la galerie. Vous pouvez télécharger l’inventaire CSV ci-dessus.';
}
$('search').addEventListener('input', () => { state.q = $('search').value; page = 1; render(); });
$('filter-open').addEventListener('click', () => $('filter-dialog').showModal());
$('reset-empty').addEventListener('click', reset);
$('reset-filters').addEventListener('click', reset);
for (const direction of ['previous', 'next']) $(direction).addEventListener('click', () => { page += direction === 'next' ? 1 : -1; render(); $('catalogue-title').scrollIntoView({ block: 'start' }); });
for (const button of document.querySelectorAll('[data-close]')) button.addEventListener('click', () => $(button.dataset.close).close());
