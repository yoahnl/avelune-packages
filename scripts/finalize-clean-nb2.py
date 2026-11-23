import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
target = root / 'packages/nb2/0.9.0'
proof = json.loads((root / 'local-records/nb2-clean-import-proof.json').read_text())
manifest = json.loads((target / 'package.json').read_text())
assert proof['canonicalImport'] and proof['strictReopen']
assert proof['sourceSha256'] == manifest['archive']['sha256']
for key, value in proof['counts'].items():
    assert manifest['counts'][key] == value, (key, value, manifest['counts'][key])
archive = target / manifest['archive']['file']
with archive.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == proof['sourceSha256']
original = root / 'packages/nb2/0.8.0/NB2-Bibliotheque-modulaire-0.8.0.aveluneassets'
with original.open('rb') as stream:
    assert hashlib.file_digest(stream, 'sha256').hexdigest() == '9935b447fa30ad649c5021dfed30f89126fb65887f27e4984a9917fc7a16a21b'
manifest['qualification'] = 'import-verified-graphical-audit-pending'
(target / 'package.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
inventory = json.loads((target / 'inventaire.json').read_text())
inventory['qualification'] = manifest['qualification']
inventory['verification'] = {'canonicalInspection': True, 'canonicalImport': True, 'strictReopen': True, 'counts': proof['counts'], 'sourceSha256': proof['sourceSha256'], 'physicalDeviceTest': False, 'allAssetGpuReview': False}
(target / 'inventaire.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + '\n')
registry = json.loads((root / 'catalogue.json').read_text())
for item in registry['packages']:
    if item['id'] == 'nb2':
        item['qualification'] = manifest['qualification']
(root / 'catalogue.json').write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
html = (target / 'galerie.html').read_text()
html = html.replace('Le pack est reconstruit et contrôlé avec les outils canoniques Avelune. Les doublons équivalents ont été fusionnés et les vraies différences de données conservées. Le résultat du réimport est indiqué dans la fiche d’inventaire.', 'L’inspection canonique, l’import complet dans un projet vierge et la réouverture stricte ont été vérifiés. Les 8 818 ressources et les 3 981 motifs sont retrouvés après réouverture. Les doublons équivalents ont été fusionnés et les différences de données conservées.')
(target / 'galerie.html').write_text(html)
delivery = Path('/Users/karim/Project/avelune project/nb2_bibliotheque_modulaire/library/NB2 — Bibliothèque modulaire — 0.9.0.aveluneassets')
if delivery.exists():
    with delivery.open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == proof['sourceSha256']
else:
    temporary = delivery.with_name(delivery.name + '.partial')
    assert not temporary.exists()
    shutil.copyfile(archive, temporary)
    temporary.rename(delivery)
delivery.with_name(delivery.name + '.sha256').write_text(proof['sourceSha256'] + '  ' + delivery.name + '\n')
record = {'status': 'verified', 'version': manifest['version'], 'sha256': proof['sourceSha256'], 'bytes': archive.stat().st_size, 'releaseArchive': str(archive), 'libraryArchive': str(delivery), 'counts': manifest['counts'], 'verification': inventory['verification'], 'published': manifest['published'], 'oldArchivePreserved': True}
(root / 'local-records/nb2-clean-delivery.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(record, ensure_ascii=False))
