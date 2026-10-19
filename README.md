# Avelune Packages

Catalogue des bibliothèques de ressources importables dans Avelune Studio.

Les archives `.aveluneassets` sont disponibles dans les **Releases**. Git conserve les fiches, les inventaires, les empreintes et les aperçus. Cloner le dépôt ne télécharge pas les archives des packages.

## Packages disponibles

| Univers | Version | Périmètre | État | Téléchargement |
| --- | --- | --- | --- | --- |
| Pokémon Rouge Feu et Vert Feuille | 1.8.1 | Cartes et décors | Import complet vérifié ; audit graphique exhaustif en cours | [Release FRLG 1.8.1](https://github.com/yoahnl/avelune-packages/releases/tag/frlg-v1.8.1) |
| Pokémon Noir et Blanc 2 | 0.9.0 | Bibliothèque modulaire de cartes 2D/3D | Doublons équivalents regroupés ; exhaustivité graphique non certifiée | Release à publier |

Le [registre JSON](catalogue.json) répertorie les versions, les fichiers et leurs empreintes. Le [dossier FRLG 1.8.1](packages/frlg/1.8.1/) contient les fiches CSV, l’inventaire et les aperçus.

## Importer un package

1. Télécharger le fichier `.aveluneassets` depuis sa release.
2. Vérifier son empreinte avec le fichier `.sha256` fourni : `shasum -a 256 -c FRLG-Cartes-Decors-1.8.1.aveluneassets.sha256`.
3. Ouvrir un projet dans Avelune Studio, sélectionner le package et examiner le plan d’import.
4. Importer, enregistrer et rouvrir le projet.

FRLG 1.8.1 nécessite une version de Studio intégrant le catalogue partitionné, le schéma SmartTile 9 et les correctifs FRLG du 19 octobre 2026. Un ancien binaire Studio n’est pas qualifié par les vérifications de cette version.

Pour parcourir la galerie hors ligne, télécharger `FRLG-Catalogue-1.8.1.zip`, extraire le dossier et ouvrir `galerie.html`.

## Contenu FRLG 1.8.1

| Ressources standards | Quantité |
| --- | ---: |
| Décors | 930 |
| Terrains | 106 |
| Chemins, dont les hautes herbes | 150 |
| Surfaces de forêt | 5 |
| Modèles de bordures | 7 |
| Environnements et dispersions | 83 |

Le package inclut aussi 8 088 composants de décors, 64 pinceaux composants et 429 images support. Les raccords et assemblages utilisent 9 791 motifs et 944 animations publiées. Les 9 862 ressources principales possèdent une description et un contexte d’usage.

L’export, l’import complet dans un projet vide, les références de médias et la réouverture ont été vérifiés. Cinq paires de doublons statiques strictement équivalents ont été fusionnées en conservant les variantes utiles.

**L’exhaustivité graphique de toutes les cartes et variantes FRLG reste à auditer.** Les contrôles réalisés ne constituent pas une certification de chaque assemblage et animation dans Studio et le Player. La qualification L7 et les appareils physiques iOS/Android restent à vérifier.

## Ajouter un package ou une version

Créer un dossier `packages/<univers>/<version>/` avec son `package.json`, son inventaire, son catalogue et ses empreintes, puis ajouter cette version à `catalogue.json`. Publier les archives dans une release dédiée, par exemple `<univers>-v<version>`, et vérifier leur empreinte après téléversement.

Les sources de préparation, les projets d’audit et les preuves détaillées restent dans l’espace de travail d’audit séparé. Ce dépôt rassemble les livraisons des packages.

## Site et galerie NB2

La page d’accueil `index.html` présente les deux univers. La [galerie NB2](packages/nb2/0.9.0/galerie.html) permet de rechercher les 8 818 ressources, de filtrer par famille, type, contexte et dimension, puis de consulter leur fiche. Les 3 981 motifs de dessin sont comptés séparément des ressources principales. Les 6 467 fiches regroupent les ressources qui partagent un aperçu, avec accès explicite aux variantes et outils. Ce regroupement visuel ne fusionne pas les variantes dans le package.

Le pack 0.9.0 fusionne 1 156 définitions principales et 32 motifs équivalents. La comparaison conserve les surfaces orientées, les champs UV et les couleurs exacts, les textures et leur échantillonnage, les animations, les collisions, les pivots, les échelles et les profils de rampe. Les rôles de matériaux SmartTile restent distincts. Les anciennes appellations restent recherchables et `regroupements.json` documente leurs correspondances. Le pack 0.8.0 reste une référence locale et n’est pas inclus dans le nouveau build du site.

Le téléchargement NB2 reste explicitement désactivé tant que sa release n’est pas publiée. Publier l’archive sous le nom `NB2-Bibliotheque-modulaire-0.9.0.aveluneassets`, avec son fichier `.sha256`, dans la release `nb2-v0.9.0`. Après vérification du téléchargement et de son empreinte, passer `published` à `true` dans le manifeste NB2 et le registre. Ne pas ajouter l’archive binaire dans Git.

Pour afficher le site localement :

```bash
npm run dev
```

Ouvrir `http://127.0.0.1:56841`. Le catalogue utilise des fichiers JSON locaux ; ouvrir directement la galerie avec une URL `file://` ne suffit pas.

```bash
npm run check
npm run build
```

Ces commandes utilisent uniquement Node.js et ne nécessitent aucune installation de dépendances. Le build prépare `dist/` avec les pages, les inventaires et les aperçus ; il exclut les archives, les caches et les fichiers de travail. Le workflow `.github/workflows/pages.yml` publie ce dossier lors des changements du site sur `main`, ou sur déclenchement manuel. Dans les réglages GitHub Pages du dépôt, choisir **GitHub Actions** comme source.

La dépendance de développement Three.js sert uniquement à préparer les aperçus 3D. Elle n’est ni chargée par le site public, ni nécessaire au build du site. Les sources et les fichiers intermédiaires de préparation restent dans `local-records/`, ignoré par Git.
