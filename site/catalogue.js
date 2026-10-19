import { groupResources, matchesResource } from './catalogue-groups.js';

const $ = id => document.getElementById(id);
const labels = { model3d: 'Modèle 3D', element: 'Élément de décor', tileset: 'Feuille de ressources', character: 'Personnage', smartTilePreset: 'Pinceau', borderBlueprint: 'Bordure', environmentPreset: 'Environnement' };
const contexts = { exterior: 'Extérieur', interior: 'Intérieur', both: 'Intérieur & extérieur', unspecified: 'Tous contextes' };
const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
const format = value => new Intl.NumberFormat('fr-FR').format(value);
const pageSize = 48;
const parameters = new URLSearchParams(location.search);
const state = Object.fromEntries(['q', 'family', 'kind', 'context', 'dimension', 'sort'].map(key => [key, parameters.get(key) || (key === 'sort' ? 'selection' : '')]));
let page = Math.max(1, Math.trunc(Number(parameters.get('page'))) || 1);
let resources = [], filtered = [], groups = [], packManifest;
const featured = ['rp_cca5a28be2d3194c12e96bdb323b319971c1c170e7848a54', 'rp_c53c38d3f63a2bbb1bf67b2fad9cca603f35fea8e3fdfa87', 'rp_99b2783ab4e0aa7d53c13ad1e4aafdfc6467b7d96daadab1', 'rp_52c0000e82b7e5aaa116e13263dbcd40217e1ab563ebd321', 'rp_b6d9d14028a8af06ba047c61bdecd5d23deacf4ab5a859be'];

function node(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function syncUrl() {
  const next = new URLSearchParams();
  for (const [key, value] of Object.entries(state)) if (value && !(key === 'sort' && value === 'selection')) next.set(key, value);
  if (page > 1) next.set('page', page);
  history.replaceState(null, '', location.pathname + (next.size ? '?' + next : '') + location.hash);
}

function card(group) {
  const resource = group.representative;
  const button = node('button', 'resource-card');
  button.type = 'button';
  button.title = resource.name;
  const picture = node('span', 'resource-picture');
  const image = document.createElement('img');
  image.src = resource.preview;
  image.alt = '';
  image.loading = 'lazy';
  image.width = 256;
  image.height = 224;
  image.addEventListener('error', () => { image.remove(); picture.append(node('span', 'quiet', 'Aperçu indisponible')); }, { once: true });
  picture.append(image, node('span', 'dimension', resource.dimension));
  const copy = node('span', 'resource-copy');
  copy.append(node('span', 'resource-family', resource.family), node('h3', '', resource.name), node('span', 'resource-meta', `${labels[resource.kind]} · ${contexts[resource.context]}`));
  if (group.resources.length > 1) copy.append(node('span', 'resource-meta', `${format(group.resources.length)} variantes et outils à consulter`));
  button.append(picture, copy);
  button.addEventListener('click', () => openResource(resource, group));
  return button;
}

function openResource(resource, group = groupResources(resources).find(item => item.resources.some(value => value.id === resource.id))) {
  const container = $('resource-detail');
  const layout = node('div', 'detail-layout');
  const picture = node('div', 'detail-picture');
  const image = document.createElement('img');
  image.src = resource.preview;
  image.alt = resource.name;
  picture.append(image);
  const copy = node('div', 'detail-copy');
  const title = node('h2', '', resource.name);
  title.id = 'detail-title';
  copy.append(node('span', 'tag', `${resource.dimension} · ${labels[resource.kind]}`), title, node('p', 'family-trail', resource.familyPath.join(' / ')));
  if (group && group.resources.length > 1) {
    const label = node('label', 'variant-picker', 'Variantes et outils associés');
    const select = document.createElement('select');
    for (const variant of group.resources) {
      const option = node('option', '', `${labels[variant.kind]} · ${variant.name}`);
      option.value = variant.id;
      select.append(option);
    }
    select.value = resource.id;
    select.addEventListener('change', () => {
      openResource(group.resources.find(item => item.id === select.value), group);
      container.querySelector('.variant-picker select').focus();
    });
    label.append(select);
    copy.append(label);
  }
  if (resource.description) copy.append(node('p', '', resource.description));
  copy.append(node('p', 'detail-note', resource.previewScope === 'module' ? 'Aperçu fixe d’un module représentatif. Dessinez avec ce pinceau dans Studio pour obtenir les raccords et les variations.' : 'Aperçu fixe de la ressource. Les animations et le comportement se consultent dans Studio.'));
  const definitions = node('dl');
  const fields = [['Contexte', contexts[resource.context]], ['Version du pack', packManifest.version]];
  if (resource.triangles !== undefined && resource.triangles !== null) fields.push(['Triangles', format(resource.triangles)]);
  for (const [label, value] of fields) { const wrapper = node('div'); wrapper.append(node('dt', '', label), node('dd', '', value)); definitions.append(wrapper); }
  copy.append(definitions);
  if (resource.sourceCount > 1) {
    const details = document.createElement('details');
    details.append(node('summary', '', `${format(resource.sourceCount)} définitions source regroupées`));
    const list = document.createElement('ul');
    for (const name of resource.sourceNames) list.append(node('li', '', name));
    details.append(list);
    copy.append(details);
  }
  layout.append(picture, copy);
  container.replaceChildren(layout);
  history.replaceState(null, '', location.pathname + location.search + '#resource=' + encodeURIComponent(resource.id));
  if (!$('resource-dialog').open) $('resource-dialog').showModal();
}

function render() {
  filtered = resources.filter(resource => matchesResource(resource, state, normalize));
  if (state.sort === 'name') filtered.sort((a, b) => a.name.localeCompare(b.name, 'fr'));
  else if (state.sort === 'family') filtered.sort((a, b) => a.familyPath.join().localeCompare(b.familyPath.join(), 'fr') || a.name.localeCompare(b.name, 'fr'));
  else filtered.sort((a, b) => (featured.includes(a.id) ? featured.indexOf(a.id) : 100) - (featured.includes(b.id) ? featured.indexOf(b.id) : 100));
  groups = groupResources(filtered);
  const pages = Math.max(1, Math.ceil(groups.length / pageSize));
  page = Math.max(1, Math.min(pages, page));
  $('resource-grid').replaceChildren(...groups.slice((page - 1) * pageSize, page * pageSize).map(card));
  $('resource-grid').setAttribute('aria-busy', 'false');
  $('result-count').textContent = `${format(groups.length)} fiche${groups.length > 1 ? 's' : ''} · ${format(filtered.length)} ressources sur ${format(resources.length)}`;
  $('empty-state').hidden = filtered.length > 0;
  $('pagination').hidden = filtered.length === 0;
  $('previous').disabled = page <= 1;
  $('next').disabled = page >= pages;
  $('page-label').textContent = `${page} / ${pages}`;
  const chips = [];
  const filterLabels = { family: state.family, kind: labels[state.kind], context: state.context === 'both' ? 'Ressources mixtes' : contexts[state.context], dimension: state.dimension };
  for (const key of ['family', 'kind', 'context', 'dimension']) if (state[key]) {
    const chip = node('button', 'filter-chip', filterLabels[key]);
    chip.append(node('span', '', '×'));
    chip.setAttribute('aria-label', 'Retirer le filtre ' + filterLabels[key]);
    chip.addEventListener('click', () => { state[key] = ''; $(key).value = ''; page = 1; render(); });
    chips.push(chip);
  }
  $('active-filters').replaceChildren(...chips);
  $('filter-count').textContent = chips.length ? `(${chips.length})` : '';
  syncUrl();
}

function reset(includeSearch) {
  for (const key of ['family', 'kind', 'context', 'dimension']) { state[key] = ''; $(key).value = ''; }
  if (includeSearch) { state.q = ''; $('search').value = ''; }
  page = 1;
  render();
}

try {
  const [resourceResponse, manifestResponse] = await Promise.all([fetch('ressources.json'), fetch('package.json')]);
  if (!resourceResponse.ok || !manifestResponse.ok) throw new Error('Catalogue indisponible');
  resources = await resourceResponse.json();
  const manifest = await manifestResponse.json();
  packManifest = manifest;
  if (resources.length !== manifest.counts.primaryResources) throw new Error('Inventaire incomplet');
  for (const resource of resources) resource.search = normalize([resource.name, resource.description, ...resource.familyPath, ...(resource.sourceNames || [])].join(' '));
  const paths = new Set();
  for (const resource of resources) for (let i = 1; i <= resource.familyPath.length; i++) paths.add(resource.familyPath.slice(0, i).join(' / '));
  for (const path of [...paths].sort((a, b) => a.localeCompare(b, 'fr'))) { const option = node('option', '', path); option.value = path; $('family').append(option); }
  $('search').value = state.q;
  for (const key of ['family', 'kind', 'context', 'dimension', 'sort']) {
    $(key).value = state[key];
    if ($(key).value !== state[key]) { state[key] = key === 'sort' ? 'selection' : ''; $(key).value = state[key]; }
    $(key).addEventListener('change', () => { state[key] = $(key).value; page = 1; render(); });
  }
  if (manifest.published === true) {
    for (const button of document.querySelectorAll('[data-download]')) { const link = node('a', 'button dark', 'Télécharger le pack ↓'); link.href = manifest.archive.url; button.replaceWith(link); }
    $('resource-grid').dataset.published = 'true';
    for (const note of document.querySelectorAll('[data-download-note]')) note.textContent = `Version ${manifest.version} · ${format(Math.round(manifest.archive.bytes / 1000000))} Mo · téléchargement depuis GitHub Releases`;
  }
  render();
  if (location.hash.startsWith('#resource=')) { const selected = resources.find(resource => resource.id === decodeURIComponent(location.hash.slice(10))); if (selected) openResource(selected); }
} catch (error) {
  $('result-count').textContent = 'Le catalogue ne peut pas être chargé.';
  const message = node('p', 'alert', 'Rechargez la page ou téléchargez l’inventaire CSV pour consulter les ressources.');
  $('resource-grid').replaceWith(message);
}

let debounce;
$('search').addEventListener('input', () => { clearTimeout(debounce); debounce = setTimeout(() => { state.q = $('search').value; page = 1; render(); }, 160); });
$('filter-open').addEventListener('click', () => $('filter-dialog').showModal());
$('reset-filters').addEventListener('click', () => reset(false));
$('reset-empty').addEventListener('click', () => reset(true));
for (const direction of ['previous', 'next']) $(direction).addEventListener('click', () => { page += direction === 'next' ? 1 : -1; render(); $('catalogue-title').scrollIntoView({ behavior: 'instant', block: 'start' }); });
for (const button of document.querySelectorAll('[data-close]')) button.addEventListener('click', () => $(button.dataset.close).close());
$('resource-dialog').addEventListener('close', () => history.replaceState(null, '', location.pathname + location.search));
for (const dialog of document.querySelectorAll('dialog')) dialog.addEventListener('click', event => { if (event.target === dialog && (event.clientX < dialog.getBoundingClientRect().left || event.clientX > dialog.getBoundingClientRect().right || event.clientY < dialog.getBoundingClientRect().top || event.clientY > dialog.getBoundingClientRect().bottom)) dialog.close(); });
