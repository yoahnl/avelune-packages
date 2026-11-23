---
name: avelune-packages
description: Use when working on Avelune Packages, its shared website and galleries, a .aveluneassets library, resource classification, duplicate assets, or a package release for FRLG, NB2 or another universe.
---

# Avelune Packages

Conserver une bibliothèque prête à utiliser dans Studio et un site commun cohérent entre univers. Les demandes explicites de l’utilisateur priment sur ces conventions ; ce skill ne donne aucune autorisation de commit, push, publication ou suppression.

## Retrouver le bon espace de travail

- Dépôt de livraison : chercher le dépôt dont `origin` est `yoahnl/avelune-packages`. Sur ce Mac : `/Users/karim/Project/Avelune Package`.
- Moteur et API d’édition : dépôt distinct `/Users/karim/Project/pokemonProject`. Ne pas y déplacer le site ou y corriger un problème sans lien avec la tâche.
- Lire le `README.md`, `catalogue.json`, les manifestes actifs et l’état Git avant toute modification. Une version trouvée dans un dossier local peut être un chantier d’une autre conversation. Sa présence ne l’autorise pas à devenir la version publiée.
- Ne pas recopier les versions, totaux et qualifications de ce skill ou d’un ancien chat : les relire dans les données actuelles, puis vérifier les preuves utiles.

## Cohérence du site

- Garder **un seul site GitHub Pages**, une page d’accueil et un registre commun pour tous les packs. Adresse actuelle : `https://yoahnl.github.io/avelune-packages/`.
- Garder le **dark mode**, l’identité Avelune officielle et les libellés en français. Réutiliser `site/styles.css`, `site/dark.css`, leurs variables CSS et les composants/espacements existants. Éviter les thèmes et les copies de styles propres à chaque pack.
- Logo : `site/brand/avelune-studio.svg` ; favicon : `site/favicon.svg`. Ne pas les redessiner, recolorer ou remplacer par un logo généré. Les sources officielles fournies sont sous `/Users/karim/Project/pokemonProject autre dossiers/Avelune_Studio_Identite_Complete/` sur ce Mac ; ce chemin n’est pas une dépendance du site publié.
- Réutiliser la recherche, le bouton **Filtres** ouvrant son panneau, les familles/sous-familles, les contextes intérieur/extérieur/mixte, le format 2D/3D, la pagination et les fiches détaillées. Garder les états vides, la réinitialisation, le clavier et les liens de retour vers l’accueil.
- `site/home.js` génère les cartes depuis `catalogue.json`. Avant d’ajouter un univers, inspecter aussi ses métriques, les cartes de secours et titres de `index.html`, et `scripts/check-site.mjs` : certaines branches sont encore spécifiques à FRLG/NB2. Adapter ce qui concerne le nouveau pack, sans refonte générale automatique.
- Lire `manifest.catalogue.gallery` pour trouver la galerie active ; ne pas supposer qu’elle s’appelle toujours `galerie.html`.
- Séparer disponibilité et qualification : `published` ne prouve ni import ni rendu. L’accueil actuel affiche « Import vérifié » dans sa branche non publiée ; ne pas réutiliser cette conclusion pour un nouveau candidat sans preuve, et aligner le libellé avec les qualifications quand cette carte est modifiée.
- Conserver les liens compatibles avec le sous-chemin GitHub Pages `/avelune-packages/`. Aucun chemin machine ou `localhost` dans la livraison publique.

## Ressources et classement

- Pour les packs Pokémon actuels, le périmètre est **la création des cartes** : extérieur et intérieur. Ne pas y ajouter les combats ou l’interface du jeu sans demande explicite.
- Livrer des définitions natives éditables et leur fermeture de dépendances. Un gros modèle de carte n’est pas l’équivalent de terrains, paths, bordures et éléments modulaires réutilisables.
- Préserver les familles et sous-familles, les variantes, les noms précis et les contextes. Une ressource graphique 2D employée dans une scène 3D reste identifiée correctement ; ne pas convertir ou redimensionner implicitement les données.
- Les aperçus doivent venir des ressources réelles. Identifier une première frame ou un module représentatif ; ne pas faire passer cette image pour une preuve de toute l’animation ou de tous les assemblages.
- Distinguer **regroupement de galerie** et **fusion dans le pack**. Une même miniature peut réunir plusieurs variantes/outils sur une fiche avec un sélecteur explicite ; les filtres doivent retrouver chaque membre.
- Ne fusionner des ressources que si leur équivalence sémantique est prouvée. Préserver les différences de géométrie orientée, textures/UV/échantillonnage, couleur, animation, échelle, pivot, collisions, rampe et rôle SmartTile. Relire les règles effectives de `scripts/nb2_identity.py` et `scripts/deduplicate-nb2.py`, plutôt que supposer une égalité binaire ou visuelle suffisante. Vérifier les références remappées, la couverture et l’idempotence ; conserver les correspondances et anciennes appellations.
- Modifier un projet Studio via ses API canoniques, avec contrôle de révision et sauvegarde/réouverture. Lire les consignes MCP du dépôt moteur quand ce périmètre est concerné. L’édition des fichiers de publication du site n’est pas une mutation de projet Studio.

### Arborescence logique des assets

- Organiser les ressources en **familles et sous-familles sémantiques**, selon leur nature et leur usage pour construire une carte. Chaque branche doit avoir un sens clair pour l’utilisateur : par exemple `Bâtiments / Portes`, `Objets / Assises` ou `Relief / Rochers`. Adapter la profondeur et le nombre de familles au contenu réel ; ne pas figer ceux d’un pack particulier.
- Réutiliser une famille pertinente avant d’en créer une autre. Créer une sous-famille seulement si elle aide concrètement à retrouver ou choisir des ressources ; éviter les catégories fourre-tout, redondantes ou ultra spécifiques qui répètent le nom d’un seul asset.
- Ne pas transformer automatiquement les noms de fichiers, atlas, cartes sources, lieux, lots d’extraction ou identifiants techniques en catégories. Garder la provenance, les variantes et les précisions propres à une ressource dans ses métadonnées. Les contextes intérieur/extérieur/mixte restent des filtres indépendants.
- Vérifier le contenu réel avant de classer : un bâtiment entier reste un bâtiment même si son nom mentionne la pierre ; les rochers et falaises appartiennent au relief. Une même règle de classement doit s’appliquer aux ressources comparables, dans Studio comme dans la galerie.
- Ne pas livrer de catégories orphelines ou vides dans l’arborescence du pack. Chaque sous-famille doit avoir un parent valide et un contenu utile, directement ou dans ses descendants ; les seuls composants techniques masqués ne justifient pas une branche visible.
- Séparer cette arborescence de navigation des groupes techniques utilisés par les terrains, paths, bordures et SmartTiles. Un reclassement visuel ne doit pas modifier leurs banques de motifs, règles, dépendances ou comportement de dessin.
- Avant livraison, contrôler l’arbre complet, ses parents, ses effectifs et les ressources réellement rangées sous chaque branche. Vérifier sa concordance entre le pack importé dans Studio et la galerie ; des totaux corrects ne suffisent pas à prouver un classement cohérent.

## Version et publication, seulement si demandées

1. Préparer une nouvelle version candidate sous `packages/<univers>/<version>/`. Figer les fichiers et empreintes du lot, puis les recontrôler avant commit et déploiement pour repérer les écritures concurrentes. Ne pas remplacer silencieusement l’archive d’une release existante. Conserver provenance et sources ; exclure ROM, projets privés, secrets, caches et preuves locales de la publication.
2. Inspecter le format et les exigences actuels dans le manifeste et les API canoniques. Qualifier le pack reconstruit : inspection, import dans un projet vierge, validation et réouverture stricte. Séparer ces résultats de la revue graphique et des tests Player/appareils.
3. Aligner manifeste, registre, inventaires, aperçus, checksum et limites. Compter séparément ressources principales, motifs, fichiers médias et fiches de galerie. Ne pas qualifier le pack d’exhaustif à partir du seul nombre d’assets trouvés.
4. Les archives `.aveluneassets` et éventuels ZIP vont dans les **GitHub Releases**, pas dans Git ni dans `dist/`. Le dépôt contient les fiches et le site. `scripts/build-site.mjs` ne publie que les versions et galeries actives.
5. Après les vérifications et les actions Git autorisées, publier la release dédiée, retélécharger son archive intégralement et comparer taille/SHA-256 au manifeste et au fichier `.sha256`. Lire le flux en streaming lorsque possible pour éviter une copie inutile sur le SSD.
6. Vérifier les conditions effectives d’activation des boutons. L’accueil lit `published` dans le registre ; la galerie NB2 lit aussi celui du manifeste : les activer ensemble seulement après cette preuve. Le manifeste FRLG actuel n’a pas ce champ et sa galerie utilise un lien direct ; ne pas inventer une condition déjà implémentée ou modifier l’ancienne version pour satisfaire une checklist. Pour une nouvelle galerie, adopter une activation explicite cohérente avec le registre. Vérifier les boutons et téléchargements sur le site effectivement déployé. Un push réussi ne prouve pas le déploiement : vérifier le run `.github/workflows/pages.yml` et son URL.

Une autorisation ancienne pour une autre livraison n’est pas une permission générale. Ne pas changer la visibilité du dépôt, les accès ou l’authentification sans autorisation correspondante. En cas de refus, diagnostiquer la cause et l’état distant avant toute reprise ; ne pas créer plusieurs releases ou exports concurrents.

## Vérifier et laisser un espace propre

Dans le dépôt de livraison :

```bash
npm test
npm run check
npm run build
```

- Pour une modification de comparaison NB2 : `cd scripts && python3 -m unittest test_nb2_identity.py`, puis les contrôles sémantiques adaptés aux archives réellement modifiées. Les scripts Dart de qualification utilisent l’environnement du moteur ; ne pas supposer que Node seul suffit pour reconstruire un pack.
- Pour une modification visuelle : contrôler ordinateur et mobile, sous-chemin de déploiement, logo, lisibilité, recherche/filtres, variantes, pagination, images et liens de téléchargement. Réutiliser le serveur de prévisualisation s’il existe ; ne pas en ouvrir un par conversation.
- Surveiller l’espace libre avant les archives, extractions ou QA lourdes. Réutiliser les fichiers, supprimer uniquement les temporaires identifiés de la tâche et fermer ses propres navigateurs/applications de test. Ne pas arrêter les outils d’une autre conversation ni fermer l’aperçu demandé par l’utilisateur.
- Décrire les changements, commandes et résultats frais, liens/empreintes et limites. Conserver les modifications concurrentes hors commit et rendre compte de l’état Git réel. Enregistrer les preuves dans le contexte Notion existant `POST-WLD-ASSET-PACK-001` quand la tâche relève de ce chantier, sans élargir la bêta ni marquer `DONE` soi-même.

## Garder ces consignes fiables

Mettre à jour ce fichier quand une décision utilisateur change une convention durable. Ne pas dupliquer ces règles dans plusieurs skills ou transformer les erreurs historiques en interdictions universelles. Les instructions du dépôt et les installations locales renvoient à ce même fichier.
