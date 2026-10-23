const translations = {
  en: {
    'skip': 'Skip to content', 'nav.discover': 'Discover', 'nav.resources': 'Resources', 'nav.news': 'News', 'menu': 'Menu',
    'hero.eyebrow': 'A WORLD OF IDEAS. AN ADVENTURE OF YOUR OWN.', 'hero.line1': 'Your region.', 'hero.line2': 'Your story.', 'hero.line3': 'Your Pokémon adventure.',
    'hero.description': 'Create your RPG in 2D or 3D with Avelune, a visual editor for building your world and telling your stories.', 'hero.primary': 'Try Avelune Studio', 'hero.secondary': 'See Avelune in action', 'hero.caption': 'Bourg Geon · 3D creation in Avelune Studio',
    'studio.eyebrow': 'MAKE ROOM FOR YOUR IMAGINATION', 'studio.title1': 'It all starts with ', 'studio.title2': 'an idea.', 'studio.caption': 'The HGSS demonstration project, open in Avelune Studio. Select the image to enlarge it.',
    'studio.feature1': 'Your world, in 2D or 3D', 'studio.description1': 'Build towns, routes and interiors in 2D pixel art or with 3D scenery. Bring your region together, one detail at a time.',
    'studio.feature2': 'An adventure to create', 'studio.description2': 'Give your characters a voice, write their conversations and connect the events that shape your story.',
    'captures.eyebrow': 'A LOOK INSIDE AVELUNE', 'captures.title1': 'From your first map ', 'captures.title2': 'to your first adventure.', 'captures.intro': '2D and 3D projects created with Avelune. Discover their worlds and the tools that bring them to life.',
    'tab.world': 'A 2D world', 'tab.studio': 'A 3D world', 'tab.dialogue': 'Tell a story', 'tab.play': 'Test your adventure',
    'world.title': 'The charm of 2D.', 'world.description': 'Forests, rivers and paths take shape in pixel art. The Bond Bridge map shows 2D world creation in Avelune Studio.', 'world.caption': 'Bond Bridge · A 2D Kanto map in Avelune Studio.',
    'world3d.title': 'Give your ideas another dimension.', 'world3d.description': 'Create 3D scenes too. Work with scenery, terrain and animations in the same visual workspace.', 'world3d.caption': 'Bourg Geon · The 3D HGSS demonstration project in Avelune Studio.',
    'dialogue.title': 'Every character has a story.', 'dialogue.description': 'Write conversations in the dialogue editor, connect your scenes and preview the exchange as you create.', 'dialogue.caption': 'The dialogue editor, with a conversation from the Clairbois demonstration project.',
    'play.title': 'Step into your adventure.', 'play.description': 'Launch a playtest from Studio to explore your scenes. See how the places you create feel from the player’s perspective.', 'play.caption': 'The HGSS demonstration project, running in Studio’s playtest mode.', 'capture.enlarge': 'Enlarge the capture',
    'resources.eyebrow': 'PIECES FOR YOUR NEXT WORLD', 'resources.title1': 'Your ideas. ', 'resources.title2': 'A whole library.', 'resources.intro': 'Browse the existing resource libraries and find scenery for your next map.',
    'resources.nb2': 'Black & White 2', 'resources.nb2.description': '3D models, scenery and modular brushes. Explore the Unova library.', 'resources.frlg': 'FireRed & LeafGreen', 'resources.frlg.description': 'The pixel-art charm of Kanto. Discover its scenery, terrain and paths.', 'resources.explore': 'Explore the library', 'resources.all': 'Browse all resources',
    'start.eyebrow': 'YOUR NEXT ADVENTURE STARTS HERE', 'start.title1': 'Give your ideas ', 'start.title2': 'somewhere to grow.', 'start.description': 'Download Avelune Studio, explore the editor and start shaping your RPG. Avelune is under active development.', 'start.download': 'Download Studio', 'start.platforms': 'Published builds for macOS, Windows and Linux. Download details and release notes are available on GitHub.',
    'faq.specialization': 'Is Avelune designed for Pokémon RPGs?', 'faq.specialization.answer': 'Yes. Avelune currently focuses on Pokémon RPG creation, with visual tools for maps, stories and dedicated Pokémon data.',
    'faq.captures': 'Are these real software captures?', 'faq.captures.answer': 'Yes. The captures show Bond Bridge in 2D, Bourg Geon in 3D, the dialogue editor and Avelune Studio’s playtest mode. Select an image to see the full capture.',
    'faq.resources': 'Where can I find resources?', 'faq.resources.answer': 'The Avelune Packages catalogue contains the libraries, previews and import instructions. You can explore it before downloading a package.', 'faq.resources.link': 'Open the catalogue',
    'news.title': 'An adventure in the making.', 'news.description': 'Follow Studio’s published versions and see what is changing with each release.', 'news.link': 'See the latest releases',
    'footer.independent': 'An independent community project, unaffiliated with Nintendo, GAME FREAK or The Pokémon Company. Pokémon and the game graphics belong to their respective owners.', 'footer.source': 'Website source', 'lightbox.close': 'Close'
  }
};

const originalText = new Map([...document.querySelectorAll('[data-i18n]')].map(element => [element, element.textContent]));
const languageButtons = [...document.querySelectorAll('[data-language]')];
let language = 'fr';

function setLanguage(nextLanguage) {
  language = nextLanguage === 'en' ? 'en' : 'fr';
  document.documentElement.lang = language;
  for (const [element, text] of originalText) element.textContent = translations[language]?.[element.dataset.i18n] ?? text;
  for (const button of languageButtons) button.setAttribute('aria-pressed', String(button.dataset.language === language));
  document.title = language === 'en' ? 'Avelune — Create your own Pokémon adventure' : 'Avelune — Créez votre propre aventure Pokémon';
  document.querySelector('meta[name="description"]').content = language === 'en'
    ? 'Create your RPG in 2D or 3D with Avelune, a visual editor specializing in Pokémon. Explore Studio, real software captures and resources.'
    : 'Créez votre RPG en 2D ou en 3D avec Avelune, un éditeur visuel spécialisé Pokémon. Découvrez Studio, ses captures réelles et ses ressources.';
  document.querySelector('.av-menu').setAttribute('aria-label', language === 'en' ? 'Toggle navigation' : 'Ouvrir ou fermer la navigation');
  document.querySelector('.av-nav').setAttribute('aria-label', language === 'en' ? 'Main navigation' : 'Navigation principale');
  document.querySelector('[role="tablist"]').setAttribute('aria-label', language === 'en' ? 'Explore Avelune' : 'Découvrir Avelune');
  const url = new URL(window.location.href);
  if (language === 'en') url.searchParams.set('lang', 'en');
  else url.searchParams.delete('lang');
  window.history.replaceState({}, '', url);
}

for (const button of languageButtons) button.addEventListener('click', () => setLanguage(button.dataset.language));
if (new URLSearchParams(window.location.search).get('lang') === 'en') setLanguage('en');

const menuButton = document.querySelector('.av-menu');
const navigation = document.querySelector('.av-nav');
function closeMenu() {
  menuButton.setAttribute('aria-expanded', 'false');
  navigation.classList.remove('av-nav-open');
}
menuButton.addEventListener('click', () => {
  const expanded = menuButton.getAttribute('aria-expanded') !== 'true';
  menuButton.setAttribute('aria-expanded', String(expanded));
  navigation.classList.toggle('av-nav-open', expanded);
});
for (const link of navigation.querySelectorAll('a')) link.addEventListener('click', closeMenu);
document.addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });

const tabs = [...document.querySelectorAll('.av-tab')];
function selectTab(tab) {
  for (const candidate of tabs) {
    const selected = candidate === tab;
    candidate.setAttribute('aria-selected', String(selected));
    candidate.tabIndex = selected ? 0 : -1;
    document.getElementById(candidate.getAttribute('aria-controls')).hidden = !selected;
  }
}
for (const [index, tab] of tabs.entries()) {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    selectTab(tabs[next]);
    tabs[next].focus();
  });
}

const lightbox = document.querySelector('.av-lightbox');
const lightboxImage = lightbox.querySelector('img');
const lightboxTitle = lightbox.querySelector('.av-lightbox-title');
for (const button of document.querySelectorAll('[data-capture]')) {
  button.addEventListener('click', () => {
    const source = document.getElementById(button.dataset.capture);
    const image = source.querySelector('img');
    lightboxImage.src = image.src;
    lightboxImage.alt = image.alt;
    lightboxTitle.textContent = source.querySelector('figcaption').textContent;
    lightbox.showModal();
  });
}
lightbox.querySelector('.av-close').addEventListener('click', () => lightbox.close());
lightbox.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
