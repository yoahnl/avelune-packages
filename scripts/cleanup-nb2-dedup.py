import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
records = root / 'local-records'
proof = json.loads((records / 'nb2-clean-import-proof.json').read_text())
delivery = json.loads((records / 'nb2-clean-delivery.json').read_text())
owner = json.loads((records / 'nb2-qa-ownership.json').read_text())
assert proof['canonicalImport'] and proof['strictReopen']
assert proof['sourceSha256'] == delivery['sha256']
for field in ['releaseArchive', 'libraryArchive']:
    with Path(delivery[field]).open('rb') as stream:
        assert hashlib.file_digest(stream, 'sha256').hexdigest() == delivery['sha256']
processes = subprocess.check_output(['ps', '-eo', 'pid=,uid=,command='], text=True)
assert 'scripts/qualify-clean-nb2.dart' not in processes
assert 'cliDaemon.js nb2-dedup-qa' not in processes
before = shutil.disk_usage(root).free
qa = Path(owner['projectRoot'])
assert qa == Path('/Users/karim/Project/pokemonProject/apps/unys_3d_sources/nb2-dedup-import-20261019')
targets = [qa, records / 'npm-dedup-qa-cache', records / 'NB2-Bibliotheque-modulaire-0.9.0.aveluneassets', records / 'NB2-Bibliotheque-modulaire-0.9.0.aveluneassets.sha256', records / 'NB2-Bibliotheque-modulaire-0.9.0.aveluneassets.receipt.json']
deleted = []
for target in targets:
    if not target.exists():
        continue
    assert not target.is_symlink()
    if target.is_dir():
        open_files = subprocess.run(['lsof', '-t', '+D', str(target)], capture_output=True, text=True)
        assert not open_files.stdout.strip(), (str(target), open_files.stdout)
        files = [f for f in target.rglob('*') if f.is_file()]
        assert all(f.stat().st_uid == os.getuid() for f in files)
        size = sum(f.stat().st_size for f in files)
        shutil.rmtree(target)
    else:
        size = target.stat().st_size
        target.unlink()
    deleted.append({'path': str(target), 'logicalBytes': size})
receipt = root / 'packages/nb2/0.9.0/NB2-Bibliotheque-modulaire-0.9.0.aveluneassets.receipt.json'
data = json.loads(receipt.read_text())
receipt.write_text(json.dumps({'archiveBytes': data['archiveBytes'], 'sha256': data['sha256'], 'canonicalBuilder': True, 'canonicalInspection': True, 'canonicalImport': True, 'strictReopen': True}, indent=2) + '\n')
report = {'deleted': deleted, 'logicalBytesRemoved': sum(entry['logicalBytes'] for entry in deleted), 'freeBytesBefore': before, 'freeBytesAfter': shutil.disk_usage(root).free, 'sourcesPreserved': True, 'proofsPreserved': True, 'oldPackPreserved': True, 'userPreviewKeptRunning': True}
(records / 'nb2-dedup-cleanup.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
