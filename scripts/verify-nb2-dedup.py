import importlib.util
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dedup', root / 'scripts/deduplicate-nb2.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
source = json.loads((root / 'local-records/nb2-dedup-source.json').read_text())
catalog = json.loads((root / 'local-records/nb2-deduplicated-catalog.json').read_text())
identities = json.loads((root / 'local-records/nb2-file-identities.json').read_text())
audit = json.loads((root / 'local-records/nb2-dedup-audit.json').read_text())
files = {f['id']: f for f in source['catalog']['files']}
assert source['archiveSha256'] == audit['sourceSha256']
sections = [(kind, source['catalog'][key], catalog[key]) for kind, key in module.SECTIONS]
sections += [(kind, source['catalog']['smartTileCatalog'][key], catalog['smartTileCatalog'][key]) for kind, key in module.SMART]
sections += [('borderBlueprint', source['catalog']['borderCatalog']['records'], catalog['borderCatalog']['records'])]
compared = 0
for kind, before, after in sections:
    kept = {item['id']: item for item in after}
    mapping = audit['mappings'][kind]
    assert set(mapping) == {item['id'] for item in before}
    assert set(mapping.values()) == set(kept)
    for item in before:
        transformed = module.rewrite(item, audit['mappings'])
        selected = kept[mapping[item['id']]]
        assert module.semantic(kind, transformed, files, identities) == module.semantic(kind, selected, files, identities), (kind, item['id'])
        compared += 1
second, result = module.deduplicate({**source, 'catalog': catalog}, identities)
assert second == catalog
assert not any(count['removed'] for count in result['counts'].values())
for kind, key in [('model3d', 'models3d'), ('element', 'elements'), ('character', 'characters')]:
    item = source['catalog'][key][0]
    baseline = module.semantic(kind, item, files, identities)
    for field, value in ({'scale': 2, 'pivot': {'x': 1, 'y': 0, 'z': 0}, 'collisionBounds': {'min': {'x': -1, 'y': 0, 'z': -1}, 'max': {'x': 1, 'y': 1, 'z': 1}}, 'rampProfile': {'direction': 'north', 'width': 1}} if kind == 'model3d' else {'frameWidth': 17} if kind == 'character' else {'collisionProfile': {'kind': 'blocked'}}).items():
        assert module.semantic(kind, {**item, field: value}, files, identities) != baseline, (kind, field)
report = {'status': 'valid', 'sourceDefinitionsCompared': compared, 'allFormerDefinitionsCovered': True, 'allMappedSemanticsPreserved': True, 'secondPassChanges': 0, 'nativeVariantFieldsProtected': True, 'counts': audit['counts']}
(root / 'local-records/nb2-dedup-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
