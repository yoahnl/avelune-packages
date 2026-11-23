import collections
import copy
import csv
import hashlib
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
source = root / 'packages/nb2/0.8.0'
target = root / 'packages/nb2/0.9.0'
catalog = json.loads((root / 'local-records/nb2-deduplicated-catalog.json').read_text())
audit = json.loads((root / 'local-records/nb2-dedup-audit.json').read_text())
old = json.loads((source / 'ressources.json').read_text())
old_by_id = {row['id']: row for row in old}
metadata = {(e['resourceKind'], e['resourceId']): e for e in catalog['resourceLibraryCatalog']['entries']}
families = {f['id']: f for f in catalog['resourceLibraryCatalog']['families']}
receipt = json.loads(next(target.glob('*.receipt.json')).read_text())
rows = []
preview_cache = {}
sections = [('model3d', catalog['models3d']), ('element', catalog['elements']), ('tileset', catalog['tilesets']), ('character', catalog['characters']), ('smartTilePreset', catalog['smartTileCatalog']['presets']), ('borderBlueprint', catalog['borderCatalog']['records']), ('environmentPreset', catalog['environmentPresets'])]
aliases = []
for kind, items in sections:
    for item in items:
        row = copy.deepcopy(old_by_id[item['id']])
        entry = metadata[kind, item['id']]
        family = entry.get('familyId')
        trail = []
        while family in families:
            trail.insert(0, families[family]['name'])
            family = families[family].get('parentId')
        row['familyPath'] = trail
        row['family'] = trail[-1]
        row['context'] = entry.get('placementContext', 'unspecified')
        row['description'] = entry.get('description', '')
        members = audit['groups'][kind + ':' + row['id']]
        row['sourceNames'] = sorted({old_by_id[id]['name'] for id in members})
        row['sourceCount'] = len(members)
        for id in members:
            if id != row['id']:
                aliases.append({'kind': kind, 'previousId': id, 'resourceId': row['id'], 'previousName': old_by_id[id]['name'], 'previousFamily': old_by_id[id]['familyPath']})
        previous = row['preview']
        if previous not in preview_cache:
            raw = (source / previous).read_bytes()
            hash = hashlib.sha256(raw).hexdigest()
            relative = 'apercus/' + hash[:24] + '.png'
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                destination.write_bytes(raw)
            preview_cache[previous] = (relative, hash)
        row['preview'], row['previewSha256'] = preview_cache[previous]
        row['appearanceGroup'] = hashlib.sha256(json.dumps([trail[0], row['dimension'], row['previewSha256']]).encode()).hexdigest()[:24]
        rows.append(row)

counts = collections.Counter(row['kind'] for row in rows)
manifest = json.loads((source / 'package.json').read_text())
manifest['version'] = '0.9.0'
manifest['release'] = manifest['release'].replace('0.8.0', '0.9.0')
manifest['qualification'] = 'canonical-package-inspected-import-pending'
manifest['archive']['file'] = manifest['archive']['file'].replace('0.8.0', '0.9.0')
manifest['archive']['url'] = manifest['archive']['url'].replace('0.8.0', '0.9.0')
manifest['archive']['bytes'] = receipt['archiveBytes']
manifest['archive']['sha256'] = receipt['sha256']
mapping = {'model3d': 'models3d', 'element': 'elements', 'tileset': 'tilesets', 'character': 'characters', 'smartTilePreset': 'smartTilePresets', 'borderBlueprint': 'borderBlueprints', 'environmentPreset': 'environmentPresets'}
for kind, key in mapping.items():
    manifest['counts'][key] = counts[kind]
manifest['counts']['primaryResources'] = len(rows)
manifest['counts']['smartTilePatterns'] = len(catalog['smartTileCatalog']['patterns'])
manifest['counts']['mediaFiles'] = len(catalog['files'])
manifest['counts']['galleryCards'] = len({row['appearanceGroup'] for row in rows})
manifest['deduplication'] = {'previousVersion': '0.8.0', 'previousResources': len(old), 'mergedResources': len(old) - len(rows), 'mergedPatterns': audit['counts']['smartTilePattern']['removed'], 'aliases': 'regroupements.json', 'sourceSha256': audit['sourceSha256']}
(target / 'package.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(target / 'ressources.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
(target / 'regroupements.json').write_text(json.dumps(aliases, ensure_ascii=False, separators=(',', ':')))
(target / 'inventaire.json').write_text(json.dumps({'schema': 'avelune.nb2.delivery.v1', 'archive': manifest['archive'], 'counts': manifest['counts'], 'deduplication': manifest['deduplication'], 'byKind': audit['counts'], 'qualification': manifest['qualification']}, ensure_ascii=False, indent=2) + '\n')
with (target / 'catalogue.csv').open('w', newline='') as stream:
    writer = csv.writer(stream)
    writer.writerow(['id', 'nom', 'type', 'famille', 'sous_familles', 'contexte', 'dimension', 'description', 'definitions_sources_regroupees'])
    for row in rows:
        writer.writerow([row['id'], row['name'], row['kind'], row['familyPath'][0], ' / '.join(row['familyPath'][1:]), row['context'], row['dimension'], row['description'], row['sourceCount']])
html = (source / 'galerie.html').read_text().replace('0.8.0', '0.9.0').replace('9 974', f'{len(rows):,}'.replace(',', ' ')).replace('6 391', f'{counts["model3d"]:,}'.replace(',', ' ')).replace('4 013', f'{len(catalog["smartTileCatalog"]["patterns"]):,}'.replace(',', ' ')).replace('221,7 Mo', f'{receipt["archiveBytes"] / 1e6:.1f}'.replace('.', ',') + ' Mo')
html = html.replace('L’export, le réimport dans un projet vierge et la réouverture stricte ont été vérifiés, dont les 280 bordures et les 421 brouillons SmartTile.', 'Le pack est reconstruit et contrôlé avec les outils canoniques Avelune. Les doublons équivalents ont été fusionnés et les vraies différences de données conservées. Le résultat du réimport est indiqué dans la fiche d’inventaire.')
html = html.replace('<div id="active-filters"', '<p class="quiet">Les ressources qui partagent le même aperçu sont réunies sur une fiche. Ouvrez-la pour choisir une variante ou son outil de dessin : aucune variante n’est masquée par les filtres.</p>\n      <div id="active-filters"')
(target / 'galerie.html').write_text(html)
index = (root / 'index.html').read_text()
for match in set(re.findall(r'packages/nb2/0\.8\.0/(apercus/[a-f0-9]+\.png)', index)):
    raw = (source / match).read_bytes()
    relative = 'apercus/' + hashlib.sha256(raw).hexdigest()[:24] + '.png'
    destination = target / relative
    if not destination.exists():
        destination.write_bytes(raw)
    index = index.replace('packages/nb2/0.8.0/' + match, 'packages/nb2/0.9.0/' + relative)
index = index.replace('packages/nb2/0.8.0/galerie.html', 'packages/nb2/0.9.0/galerie.html').replace('VERSION 0.8.0', 'VERSION 0.9.0').replace('9 974', '8 818').replace('4 013', '3 981')
(root / 'index.html').write_text(index)
registry = json.loads((root / 'catalogue.json').read_text())
for item in registry['packages']:
    if item['id'] == 'nb2':
        item.update({'version': '0.9.0', 'manifest': 'packages/nb2/0.9.0/package.json', 'release': manifest['release'], 'qualification': manifest['qualification'], 'published': False})
(root / 'catalogue.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'resources': len(rows), 'galleryCards': manifest['counts']['galleryCards'], 'aliases': len(aliases), 'previews': len({row['preview'] for row in rows}), 'trees': {'resources': sum(row['familyPath'][0] == 'Arbres' for row in rows), 'cards': len({row['appearanceGroup'] for row in rows if row['familyPath'][0] == 'Arbres'})}}, ensure_ascii=False))
