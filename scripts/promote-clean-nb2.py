import hashlib
import json
import os
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
name = 'NB2-Bibliotheque-modulaire-0.9.0.aveluneassets'
source = root / 'local-records' / name
target = root / 'packages/nb2/0.9.0' / name
inspection = json.loads((root / 'local-records/nb2-mcp-inspection.json').read_text())
assert inspection['snapshot']['state'] == 'succeeded'
expected = inspection['result']['archiveRawSha256']
assert hashlib.file_digest(source.open('rb'), 'sha256').hexdigest() == expected
if target.exists():
    previous = hashlib.file_digest(target.open('rb'), 'sha256').hexdigest()
    assert previous in {'67bed385b36171cf80d2a9bd01ae2c8c302994953c8d4bbe1fffdd0342250983', expected}
temporary = target.with_name(target.name + '.qualified')
assert not temporary.exists()
shutil.copyfile(source, temporary)
os.replace(temporary, target)
for suffix in ['.sha256', '.receipt.json']:
    shutil.copyfile(source.with_name(name + suffix), target.with_name(name + suffix))
print(json.dumps({'promoted': str(target), 'sha256': expected, 'bytes': target.stat().st_size}))
