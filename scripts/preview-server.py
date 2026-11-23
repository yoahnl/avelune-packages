from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
allowed = {task['id'] for task in json.loads((root / 'local-records/nb2-preview-tasks.json').read_text())}
destination = root / 'packages/nb2/0.8.0/apercus'

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(root), **kwargs)

    def log_message(self, *args):
        pass

    def do_POST(self):
        match = re.fullmatch(r'/__render-output/([a-f0-9]{24})', self.path)
        size = int(self.headers.get('Content-Length', '0'))
        if not match or match[1] not in allowed or size < 8 or size > 2097152:
            self.send_error(400)
            return
        data = self.rfile.read(size)
        if not data.startswith(b'\x89PNG\r\n\x1a\n'):
            self.send_error(400)
            return
        path = destination / (match[1] + '.png')
        if path.exists() and path.read_bytes() != data:
            self.send_error(409)
            return
        if not path.exists():
            with path.open('xb') as file:
                file.write(data)
        self.send_response(201)
        self.end_headers()

print('Preview ready: http://127.0.0.1:56841', flush=True)
ThreadingHTTPServer(('127.0.0.1', 56841), Handler).serve_forever()
