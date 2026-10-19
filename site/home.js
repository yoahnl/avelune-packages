for (const link of document.querySelectorAll('a[href^="#"]')) {
  link.addEventListener('click', event => {
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    history.replaceState(null, '', link.getAttribute('href'));
  });
}

const element = (tag, className, text) => {
  const result = document.createElement(tag);
  if (className) result.className = className;
  if (text) result.textContent = text;
  return result;
};
const number = value => new Intl.NumberFormat('fr-FR').format(value);

try {
  const response = await fetch(new URL('../catalogue.json', import.meta.url));
  if (!response.ok) throw new Error('Registre indisponible');
  const registry = await response.json();
  const cards = await Promise.all(registry.packages.map(async pack => {
    const manifestUrl = new URL(`../${pack.manifest}`, import.meta.url);
    const response = await fetch(manifestUrl);
    if (!response.ok) throw new Error('Fiche indisponible');
    const manifest = await response.json();
    const presentation = pack.presentation;
    const card = element('article', `library-card ${pack.id}-card`);
    const picture = element('div', 'library-picture');
    picture.append(element('span', 'version', `VERSION ${manifest.version}`));
    const images = element('div', 'library-images');
    for (const source of presentation.images) {
      const image = element('img');
      image.src = new URL(source, manifestUrl).href;
      image.alt = '';
      image.loading = 'lazy';
      images.append(image);
    }
    picture.append(images, element('span', 'picture-word', presentation.region));
    const body = element('div', 'library-body');
    const tags = element('div', 'tag-row');
    tags.append(element('span', 'tag', presentation.format), element('span', 'status', pack.published ? '● Disponible' : '● Import vérifié'));
    const metrics = element('div', 'library-metrics');
    metrics.append(element('span', '', `${number(manifest.counts.primaryResources)} ressources`));
    metrics.append(element('span', '', pack.id === 'nb2' ? `${number(manifest.counts.smartTilePatterns)} motifs` : `${number(manifest.counts.standardDecorModels)} décors en galerie`));
    const actions = element('div', 'library-actions');
    const explore = element('a', 'button dark full', 'Explorer la bibliothèque ↗');
    explore.href = new URL(manifest.catalogue.gallery, manifestUrl).href;
    actions.append(explore);
    if (pack.published) {
      const download = element('a', 'button light', 'Télécharger ↓');
      download.href = manifest.archive.url;
      download.setAttribute('aria-label', `Télécharger ${presentation.title} ${manifest.version}`);
      actions.append(download);
    }
    body.append(tags, element('h3', '', presentation.title), element('p', '', presentation.description), metrics, actions);
    card.append(picture, body);
    return { card, count: manifest.counts.primaryResources };
  }));
  document.querySelector('.library-grid').replaceChildren(...cards.map(item => item.card));
  document.querySelector('[data-universe-count]').textContent = number(cards.length);
  document.querySelector('[data-resource-count]').textContent = number(cards.reduce((sum, item) => sum + item.count, 0));
} catch {
  document.querySelector('.library-grid').insertAdjacentText('afterend', 'Le registre ne répond pas. Les liens directs des bibliothèques restent disponibles ci-dessus.');
}
