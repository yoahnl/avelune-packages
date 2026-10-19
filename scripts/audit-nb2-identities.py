import argparse
import collections
import json
from pathlib import Path
import time
import zipfile

from nb2_identity import glb_identity, png_identity


parser = argparse.ArgumentParser()
parser.add_argument('snapshot', type=Path)
parser.add_argument('archive', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
catalog = json.loads(args.snapshot.read_text())['catalog']
results = {}
start = time.monotonic()
with zipfile.ZipFile(args.archive) as archive:
    for index, file in enumerate(catalog['files']):
        path = file['archivePath']
        if path in results:
            continue
        data = archive.read(path)
        if path.endswith('.glb'):
            signature, method = glb_identity(data)
        elif path.endswith('.png'):
            signature, method = png_identity(data), 'exact-rgba'
        else:
            signature, method = file['rawSha256'], 'byte-exact'
        results[path] = {'signature': signature, 'method': method}
        if index % 250 == 0:
            print(json.dumps({'files': index + 1, 'seconds': round(time.monotonic() - start)}), flush=True)
args.output.write_text(json.dumps(results, ensure_ascii=False, separators=(',', ':')))
print(json.dumps({'complete': len(results), 'methods': dict(collections.Counter(value['method'] for value in results.values())), 'seconds': round(time.monotonic() - start)}), flush=True)
