import argparse
import csv
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument('snapshot', type=Path)
parser.add_argument('archive', type=Path)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
target = root / 'packages/nb2/0.8.0'
target.mkdir(parents=True, exist_ok=True)
local = root / 'local-records/nb2-media'
local.mkdir(parents=True, exist_ok=True)
snapshot = json.loads(args.snapshot.read_text())
assert snapshot['archiveSha256'] == '9935b447fa30ad649c5021dfed30f89126fb65887f27e4984a9917fc7a16a21b'
with args.archive.open('rb') as source:
    assert hashlib.file_digest(source, 'sha256').hexdigest() == snapshot['archiveSha256']
c = snapshot['catalog']
files = {file['id']: file for file in c['files']}
models = {item['id']: item for item in c['models3d']}
tilesets = {item['id']: item for item in c['tilesets']}
elements = {item['id']: item for item in c['elements']}
atlases = {item['id']: item for item in c['smartTileCatalog']['atlases']}
families = {item['id']: item for item in c['resourceLibraryCatalog']['families']}
metadata = {(item['resourceKind'], item['resourceId']): item for item in c['resourceLibraryCatalog']['entries']}
tasks = {}

def family_path(id):
    trail = []
    visited = set()
    while id and id in families:
        assert id not in visited
        visited.add(id)
        item = families[id]
        trail.insert(0, item['name'])
        id = item.get('parentId')
    return trail

def picture(asset, crop=None):
    if asset not in files:
        return None
    file = files[asset]
    return {'source': 'local-records/nb2-media/' + Path(file['archivePath']).name,
            'kind': 'model' if file['mediaType'] == 'model/gltf-binary' or file['archivePath'].endswith('.glb') else 'image',
            'crop': crop}

def from_tileset(id, frame=None):
    tile = tilesets.get(id)
    if not tile:
        return None
    source = tile.get('source', {})
    asset = source.get('assetId')
    crop = None
    if frame:
        width = source.get('tileWidth', 32)
        height = source.get('tileHeight', 32)
        crop = [frame.get('x', 0) * width, frame.get('y', 0) * height,
                frame['width'] * width, frame['height'] * height]
    return picture(asset, crop)

def from_model(id):
    model = models.get(id)
    return picture(model['sourceAssetId']) if model else None

def from_element(id):
    element = elements.get(id)
    if not element:
        return None
    frame = element.get('frames', [{}])[0]
    return from_tileset(frame.get('tilesetId') or element.get('tilesetId'), frame.get('source'))

def source_part(part):
    source = part.get('source', part)
    if source.get('kind') == 'model3d':
        return from_model(source['modelId'])
    frame = source.get('frame')
    if frame and frame.get('atlasId') in atlases:
        atlas = atlases[frame['atlasId']]
        return from_tileset(atlas['tilesetId'], frame.get('source'))
    return None

def preview(kind, item):
    if kind == 'model3d':
        return from_model(item['id'])
    if kind == 'tileset':
        return from_tileset(item['id'])
    if kind == 'element':
        return from_element(item['id'])
    if kind == 'character':
        animation = next((a for a in item['animations'] if a['state'] == 'idle' and a['direction'] == 'south'), item['animations'][0])
        frame = animation['frames'][0]['source']
        return picture(animation['sourceAssetId'], [frame['x'], frame['y'], frame['width'], frame['height']])
    if kind == 'smartTilePreset':
        for rule in item.get('rules', []):
            for candidate in rule.get('candidates', []):
                for part in candidate.get('parts', []):
                    found = source_part(part)
                    if found:
                        return found
    if kind == 'environmentPreset':
        for entry in item.get('palette', []):
            found = from_model(entry.get('modelId')) or from_element(entry.get('modelId'))
            if found:
                return found
    if kind == 'borderBlueprint':
        for part in item['latestPublished']['definition'].get('primitives', []):
            found = from_model(part.get('sourceModelId')) or from_element(part.get('sourceElementId'))
            if found:
                return found
    return None

groups = [('model3d', c['models3d']), ('element', c['elements']), ('tileset', c['tilesets']),
          ('character', c['characters']), ('smartTilePreset', c['smartTileCatalog']['presets']),
          ('borderBlueprint', c['borderCatalog']['records']), ('environmentPreset', c['environmentPresets'])]
rows = []
for kind, items in groups:
    for item in items:
        entry = metadata[(kind, item['id'])]
        descriptor = preview(kind, item)
        image = None
        if descriptor:
            key = hashlib.sha256(json.dumps(descriptor, sort_keys=True).encode()).hexdigest()[:24]
            tasks[key] = {'id': key, **descriptor}
            image = f'apercus/{key}.png'
        trail = family_path(entry.get('familyId'))
        name = item.get('name') or item.get('latestPublished', {}).get('definition', {}).get('name') or item['id']
        row = {'id': item['id'], 'name': name, 'kind': kind, 'family': trail[-1] if trail else 'Autres ressources',
               'familyPath': trail, 'context': entry.get('placementContext', 'unspecified'),
               'dimension': '3D' if descriptor and descriptor['kind'] == 'model' else '2D',
               'description': entry.get('description', ''), 'preview': image,
               'previewScope': 'module' if kind in ['smartTilePreset', 'borderBlueprint', 'environmentPreset'] else 'resource'}
        if kind == 'model3d':
            row['triangles'] = item.get('inspection', {}).get('triangleCount')
            row['animations'] = len(item.get('inspection', {}).get('animations', []))
        rows.append(row)
assert len(rows) == 9974 and len({row['id'] for row in rows}) == 9974
with zipfile.ZipFile(args.archive) as archive:
    for file in files.values():
        destination = local / Path(file['archivePath']).name
        if not destination.exists():
            destination.write_bytes(archive.read(file['archivePath']))
        with destination.open('rb') as stream:
            assert hashlib.file_digest(stream, 'sha256').hexdigest() == file['rawSha256']
(root / 'local-records/nb2-preview-tasks.json').write_text(json.dumps(list(tasks.values()), ensure_ascii=False))
(target / 'ressources.json').write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')))
with (target / 'catalogue.csv').open('w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'nom', 'type', 'famille', 'sous_familles', 'contexte', 'dimension', 'description'])
    for row in rows:
        writer.writerow([row['id'], row['name'], row['kind'], row['familyPath'][0] if row['familyPath'] else '', ' / '.join(row['familyPath'][1:]), row['context'], row['dimension'], row['description']])
archive_name = 'NB2-Bibliotheque-modulaire-0.8.0.aveluneassets'
manifest = {
    'schema': 'avelune.package-registry.entry.v1', 'id': 'nb2', 'name': 'Pokémon Noir et Blanc 2 — Bibliothèque modulaire',
    'version': '0.8.0', 'scope': 'map-graphics', 'qualification': 'import-verified-graphical-audit-pending',
    'release': 'https://github.com/yoahnl/avelune-packages/releases/tag/nb2-v0.8.0', 'published': False,
    'archive': {'file': archive_name, 'bytes': snapshot['archiveBytes'], 'sha256': snapshot['archiveSha256'],
        'url': f'https://github.com/yoahnl/avelune-packages/releases/download/nb2-v0.8.0/{archive_name}', 'formatVersion': 2},
    'catalogue': {'csv': 'catalogue.csv', 'inventory': 'inventaire.json', 'gallery': 'galerie.html', 'resources': 'ressources.json'},
    'requires': {'partitionedCatalog': True, 'smartTileSchema': 9},
    'counts': {'primaryResources': 9974, 'models3d': 6391, 'characters': 912, 'tilesets': 1233, 'elements': 136,
        'smartTilePresets': 421, 'borderBlueprints': 280, 'environmentPresets': 601, 'smartTilePatterns': 4013, 'mediaFiles': 7624},
    'limitations': ['Exhaustivité de toutes les cartes et variantes du jeu non certifiée.', 'Qualification visuelle de chaque assemblage et appareils physiques non réalisée.']}
(target / 'package.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
(target / (archive_name + '.sha256')).write_text(snapshot['archiveSha256'] + '  ' + archive_name + '\n')
inventory = {'schema': 'avelune.nb2.delivery.v1', 'archive': manifest['archive'], 'counts': manifest['counts'],
    'contexts': {'exterior': 2930, 'interior': 958, 'both': 6086}, 'families': len(families),
    'qualification': manifest['qualification'], 'source': 'Export canonique NB2 0.8.0 ; réimport vierge et réouverture stricte vérifiés.'}
(target / 'inventaire.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'resources': len(rows), 'uniquePreviewTasks': len(tasks), 'noPreview': sum(row['preview'] is None for row in rows)}))
