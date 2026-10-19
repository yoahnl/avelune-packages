# Avelune Packages

Catalogue des bibliothèques de ressources importables dans Avelune Studio.

Les archives `.aveluneassets` sont disponibles dans les **Releases**. Git conserve les fiches, les inventaires, les empreintes et les aperçus. Cloner le dépôt ne télécharge pas les archives des packages.

## Packages disponibles

| Univers | Version | Périmètre | État | Téléchargement |
| --- | --- | --- | --- | --- |
| Pokémon Rouge Feu et Vert Feuille | 1.8.1 | Cartes et décors | Import complet vérifié ; audit graphique exhaustif en cours | [Release FRLG 1.8.1](https://github.com/yoahnl/avelune-packages/releases/tag/frlg-v1.8.1) |

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
