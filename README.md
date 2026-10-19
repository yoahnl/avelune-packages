# Avelune Packages

Catalogue des bibliothèques de ressources importables dans Avelune Studio.

**[Parcourir le site Avelune Packages](https://yoahnl.github.io/avelune-packages/)** — un seul catalogue en dark mode pour les bibliothèques 2D et 3D.

Les archives `.aveluneassets` sont disponibles dans les **Releases**. Git conserve les fiches, les inventaires, les empreintes et les aperçus. Cloner le dépôt ne télécharge pas les archives des packages.

## Packages disponibles

| Univers | Version | Périmètre | État | Téléchargement |
| --- | --- | --- | --- | --- |
| Pokémon Rouge Feu et Vert Feuille | 1.9.4 | Cartes et décors | Import complet vérifié ; correctifs graphiques, classement et variantes contrôlés ; événements à configurer | [Release FRLG 1.9.4](https://github.com/yoahnl/avelune-packages/releases/tag/frlg-v1.9.4) |
| Pokémon Noir et Blanc 2 | 0.9.0 | Bibliothèque modulaire de cartes 2D/3D | Doublons équivalents regroupés ; exhaustivité graphique non certifiée | [Release NB2 0.9.0](https://github.com/yoahnl/avelune-packages/releases/tag/nb2-v0.9.0) |

Le [registre JSON](catalogue.json) répertorie les versions, les fichiers et leurs empreintes. Le [dossier FRLG 1.9.4](packages/frlg/1.9.4/) contient les fiches CSV, l’inventaire, les aperçus et la qualification.

## Importer un package

1. Télécharger le fichier `.aveluneassets` depuis sa release.
2. Vérifier son empreinte avec le fichier `.sha256` fourni : `shasum -a 256 -c FRLG-Cartes-Decors-1.9.4.aveluneassets.sha256`.
3. Ouvrir un projet dans Avelune Studio, sélectionner le package et examiner le plan d’import.
4. Importer, enregistrer et rouvrir le projet.

FRLG 1.9.4 nécessite une version de Studio intégrant le catalogue partitionné, le schéma SmartTile 9 et le correctif canonique d’import des familles prédéfinies, ainsi que les correctifs FRLG du 19 octobre 2026. Voir `qualification.json` dans la livraison. Un ancien binaire Studio n’est pas qualifié par les vérifications de cette version.

La [galerie FRLG](https://yoahnl.github.io/avelune-packages/packages/frlg/1.9.4/bibliotheque.html) présente 792 fiches pour 793 décors standards et 1 011 ressources illustrées, avec les états de portes associés. L’inventaire CSV complet couvre aussi les terrains, chemins, bordures, environnements et composants.

## Contenu FRLG 1.9.4

| Ressources standards | Quantité |
| --- | ---: |
| Décors | 793 |
| Terrains | 106 |
| Chemins, dont les hautes herbes | 150 |
| Surfaces de forêt | 5 |
| Modèles de bordures | 7 |
| Environnements standards | 74 |

Le package inclut aussi 8 309 composants de décors, 64 pinceaux composants, 9 environnements composants et 493 images support. Les raccords et assemblages utilisent 9 791 motifs et 944 animations SmartTile publiées. Les 10 010 ressources principales possèdent une description et un contexte d’usage.

L’import complet dans un projet vide et la réouverture stricte ont été vérifiés : 10 010 ressources principales, 9 791 motifs et 515 fichiers médias contrôlés par taille et SHA-256. La version 1.9.4 restaure le panneau vert de la porte de Chen, assemble les trois états cohérents de la paroi d’ascenseur et fournit ses deux sens d’animation. Le fauteuil propre est renommé et rangé dans les assises ; les compositions avec fond restent des composants. Six alias de portes équivalents sont remappés, huit chemins de familles sont regroupés et les descriptions des modes de pose sont précisées. Les variantes d’ancrage, de collision, de palette et d’animation utiles sont conservées.

Les façades et les portes sont des ressources séparées. La galerie montre leur assemblage fermé et permet de consulter la façade seule et les états associés. Le passage, les collisions et le déclenchement de l’animation de porte se configurent dans le projet : le package ne les lie pas automatiquement.

**La comparaison source→pack couvre les cellules des 421 définitions natives hors prototypes ; elle ne certifie pas à elle seule chaque assemblage entier, événement ou geste de dessin.** Les contrôles réalisés ne constituent pas une certification de chaque assemblage et animation dans Studio et le Player. La qualification L7 et les appareils physiques iOS/Android restent à vérifier.

## Ajouter un package ou une version

Créer un dossier `packages/<univers>/<version>/` avec son `package.json`, son inventaire, son catalogue et ses empreintes, puis ajouter cette version à `catalogue.json`. Renseigner sa présentation : titre, région, format, description et trois aperçus relatifs au manifeste. L’accueil lit ce registre pour générer ses cartes et ses compteurs ; le build conserve seulement les versions actives. Publier les archives dans une release dédiée, par exemple `<univers>-v<version>`, vérifier leur empreinte après téléversement, puis activer `published` dans le registre et le manifeste.

Les sources de préparation, les projets d’audit et les preuves détaillées restent dans l’espace de travail d’audit séparé. Ce dépôt rassemble les livraisons des packages.

## Site et galerie NB2

La page d’accueil `index.html` présente les deux univers. La [galerie NB2](packages/nb2/0.9.0/galerie.html) permet de rechercher les 8 818 ressources, de filtrer par famille, type, contexte et dimension, puis de consulter leur fiche. Les 3 981 motifs de dessin sont comptés séparément des ressources principales. Les 6 467 fiches regroupent les ressources qui partagent un aperçu, avec accès explicite aux variantes et outils. Ce regroupement visuel ne fusionne pas les variantes dans le package.

Le pack 0.9.0 fusionne 1 156 définitions principales et 32 motifs équivalents. La comparaison conserve les surfaces orientées, les champs UV et les couleurs exacts, les textures et leur échantillonnage, les animations, les collisions, les pivots, les échelles et les profils de rampe. Les rôles de matériaux SmartTile restent distincts. Les anciennes appellations restent recherchables et `regroupements.json` documente leurs correspondances. Le pack 0.8.0 reste une référence locale et n’est pas inclus dans le nouveau build du site.

La release [NB2 0.9.0](https://github.com/yoahnl/avelune-packages/releases/tag/nb2-v0.9.0) fournit `NB2-Bibliotheque-modulaire-0.9.0.aveluneassets` et son fichier `.sha256`. Le téléchargement public complet a été vérifié : 202 738 463 octets, SHA-256 `7987e5b5613cce58c424237f993e97d4e060f312fae5b112b514a9f2db118d8f`. Les boutons du site sont activés après cette vérification. L’archive binaire reste hors Git.

L’accueil et les deux galeries partagent le même thème sombre. Le logo `site/brand/avelune-studio.svg` et le favicon sont les SVG officiels fournis pour Avelune Studio, conservés sans recoloration. La galerie FRLG du site est `bibliotheque.html` ; l’ancienne galerie autonome reste incluse dans sa livraison hors ligne historique.

Pour afficher le site localement :

```bash
npm run dev
```

Ouvrir `http://127.0.0.1:56841`. Le catalogue utilise des fichiers JSON locaux ; ouvrir directement la galerie avec une URL `file://` ne suffit pas.

```bash
npm run check
npm test
npm run build
```

Ces commandes utilisent uniquement Node.js et ne nécessitent aucune installation de dépendances. Le build prépare `dist/` avec les pages, les inventaires et les aperçus ; il exclut les archives, les caches et les fichiers de travail. Le workflow `.github/workflows/pages.yml` publie ce dossier lors des changements du site sur `main`, ou sur déclenchement manuel. Dans les réglages GitHub Pages du dépôt, choisir **GitHub Actions** comme source.

La dépendance de développement Three.js sert uniquement à préparer les aperçus 3D. Elle n’est ni chargée par le site public, ni nécessaire au build du site. Les sources et les fichiers intermédiaires de préparation restent dans `local-records/`, ignoré par Git.
