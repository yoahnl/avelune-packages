import argparse
import collections
import copy
import json
from pathlib import Path

from nb2_identity import digest


SECTIONS = [('tileset', 'tilesets'), ('model3d', 'models3d'), ('element', 'elements'), ('character', 'characters'), ('environmentPreset', 'environmentPresets')]
SMART = [('smartTileAtlas', 'atlases'), ('smartTileMaterial', 'materials'), ('smartTileAnimation', 'animations'), ('smartTilePreset', 'presets'), ('smartTilePattern', 'patterns')]
FIELDS = {'modelId': 'model3d', 'sourceModelId': 'model3d', 'elementId': 'element', 'sourceElementId': 'element', 'tilesetId': 'tileset', 'atlasId': 'smartTileAtlas', 'animationId': 'smartTileAnimation', 'materialId': 'smartTileMaterial', 'centerMaterialId': 'smartTileMaterial', 'defaultMaterialId': 'smartTileMaterial', 'sourceSmartTilePresetId': 'smartTilePreset'}
EDGES = {'northEdge', 'northEastCorner', 'eastEdge', 'southEastCorner', 'southEdge', 'southWestCorner', 'westEdge', 'northWestCorner'}
IGNORED = {'id', 'name', 'sortOrder', 'categoryId', 'folderId', 'description'}


def rewrite(value, mappings):
    if isinstance(value, list):
        return [rewrite(item, mappings) for item in value]
    if not isinstance(value, dict):
        return value
    result = {}
    for key, item in value.items():
        kind = FIELDS.get(key, 'smartTileMaterial' if key in EDGES else None)
        if kind and isinstance(item, str):
            result[key] = mappings.get(kind, {}).get(item, item)
        elif key == 'allowedMaterialIds':
            result[key] = list(dict.fromkeys(mappings.get('smartTileMaterial', {}).get(id, id) for id in item))
        else:
            result[key] = rewrite(item, mappings)
    return result


def semantic(kind, item, files, identities):
    if kind == 'smartTileMaterial':
        return digest([kind, item])
    value = copy.deepcopy(item)
    if kind == 'model3d':
        source = files[value.pop('sourceAssetId')]
        value.pop('relativePath')
        value.pop('inspection')
        value['content'] = identities[source['archivePath']]['signature']
    elif kind == 'tileset':
        value.pop('relativePath')
    if kind == 'borderBlueprint':
        value = value['latestPublished']['definition']

    def normalize(obj):
        if isinstance(obj, list):
            return [normalize(x) for x in obj]
        if not isinstance(obj, dict):
            return obj
        out = {}
        for key, item in obj.items():
            if key in IGNORED or key == 'tags' and kind == 'environmentPreset':
                continue
            if key in {'assetId', 'sourceAssetId'} and isinstance(item, str) and item in files:
                out[key] = identities[files[item]['archivePath']]['signature']
            else:
                out[key] = normalize(item)
        return out

    return digest([kind, normalize(value)])


def common_parent(entries, family_by_id):
    trails = []
    for entry in entries:
        current = entry.get('familyId')
        trail = []
        while current in family_by_id:
            trail.insert(0, current)
            current = family_by_id[current].get('parentId')
        trails.append(trail)
    common = []
    for parts in zip(*trails):
        if len(set(parts)) != 1:
            break
        common.append(parts[0])
    return common[-1] if common else entries[0].get('familyId')


def deduplicate(snapshot, identities):
    catalog = copy.deepcopy(snapshot['catalog'])
    if catalog['dynamicDependencies']:
        raise ValueError('Dynamic dependencies require a dedicated reference audit')
    files = {f['id']: f for f in catalog['files']}
    metadata = {(e['resourceKind'], e['resourceId']): e for e in catalog['resourceLibraryCatalog']['entries']}
    families = {f['id']: f for f in catalog['resourceLibraryCatalog']['families']}
    mappings = {}
    groups = {}
    signatures = {}
    counts = {}
    new_metadata = {}

    def process(kind, items):
        grouped = collections.defaultdict(list)
        for item in items:
            transformed = rewrite(item, mappings)
            fingerprint = semantic(kind, transformed, files, identities)
            signatures[kind + ':' + item['id']] = fingerprint
            grouped[fingerprint].append(transformed)
        mapping = {}
        kept = []
        for fingerprint, members in grouped.items():
            representative = members[0]
            canonical = representative['id']
            groups[kind + ':' + canonical] = [item['id'] for item in members]
            for item in members:
                mapping[item['id']] = canonical
            if kind == 'environmentPreset':
                for index, entry in enumerate(representative['palette']):
                    entry['tags'] = sorted(set().union(*(set(m['palette'][index].get('tags', [])) for m in members)))
            classified = [metadata[kind, m['id']] for m in members if (kind, m['id']) in metadata]
            if classified:
                entry = copy.deepcopy(classified[0])
                contexts = {e.get('placementContext', 'unspecified') for e in classified}
                if 'both' in contexts or {'interior', 'exterior'} <= contexts:
                    entry['placementContext'] = 'both'
                elif contexts != {'unspecified'}:
                    entry['placementContext'] = next(v for v in contexts if v != 'unspecified')
                entry['resourceId'] = canonical
                entry['familyId'] = common_parent(classified, families)
                if len(members) > 1:
                    entry['description'] = ((entry.get('description') or '') + f' Ressource réutilisable : {len(members)} définitions source équivalentes regroupées.').strip()[:2000]
                new_metadata[kind, canonical] = entry
            kept.append(representative)
        mappings[kind] = mapping
        counts[kind] = {'before': len(items), 'after': len(kept), 'removed': len(items) - len(kept)}
        return kept

    for kind, key in SECTIONS[:2]:
        catalog[key] = process(kind, catalog[key])
    for kind, key in SMART[:3]:
        catalog['smartTileCatalog'][key] = process(kind, catalog['smartTileCatalog'][key])
    for kind, key in SECTIONS[2:]:
        catalog[key] = process(kind, catalog[key])
    for kind, key in SMART[3:]:
        catalog['smartTileCatalog'][key] = process(kind, catalog['smartTileCatalog'][key])
    catalog['borderCatalog']['records'] = process('borderBlueprint', catalog['borderCatalog']['records'])
    catalog['resourceLibraryCatalog']['entries'] = list(new_metadata.values())
    catalog['extras']['smartTilePatternIds'] = [p['id'] for p in catalog['smartTileCatalog']['patterns']]
    for origin in catalog['provenance']:
        unique = {}
        for resource in origin['resources']:
            kind = resource['resourceKind']
            item = {**resource, 'id': mappings.get(kind, {}).get(resource['id'], resource['id'])}
            unique[kind, item['id']] = item
        origin['resources'] = list(unique.values())
    used = set()
    paths = set()

    def references(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {'sourceAssetId', 'assetId'} and isinstance(item, str):
                    used.add(item)
                if key == 'relativeAssetPath' and isinstance(item, str):
                    paths.add(item)
                references(item)
        elif isinstance(value, list):
            for item in value:
                references(item)

    for key in ['tilesets', 'models3d', 'characters', 'borderCatalog']:
        references(catalog[key])
    catalog['files'] = [f for f in catalog['files'] if f['id'] in used or f['logicalPath'] in paths]
    audit = {'sourceSha256': snapshot['archiveSha256'], 'counts': counts, 'mappings': mappings, 'groups': groups, 'signatures': signatures, 'filesBefore': len(files), 'filesAfter': len(catalog['files']), 'policy': 'Exact rational oriented surfaces and affine UV/normal/color fields; exact RGBA and sampling; animated GLBs byte-exact; native settings preserved. No screenshot-based merging.'}
    return catalog, audit


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('snapshot', type=Path)
    parser.add_argument('identities', type=Path)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('audit', type=Path)
    args = parser.parse_args()
    snapshot = json.loads(args.snapshot.read_text())
    catalog, audit = deduplicate(snapshot, json.loads(args.identities.read_text()))
    args.catalog.write_text(json.dumps(catalog, ensure_ascii=False, separators=(',', ':')))
    args.audit.write_text(json.dumps(audit, ensure_ascii=False, separators=(',', ':')))
    print(json.dumps({'counts': audit['counts'], 'filesBefore': audit['filesBefore'], 'filesAfter': audit['filesAfter']}, ensure_ascii=False))
