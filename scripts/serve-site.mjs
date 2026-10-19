import { createServer } from 'node:http';
import { createReadStream } from 'node:fs';
import { stat, realpath } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { extname, join, relative, resolve } from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.png': 'image/png', '.svg': 'image/svg+xml', '.csv': 'text/csv; charset=utf-8' };
const server = createServer(async (request, response) => {
  if (!['GET', 'HEAD'].includes(request.method)) { response.writeHead(405).end(); return; }
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const parts = pathname.split('/');
    if (parts.some(part => part.startsWith('.') && part !== '' || ['local-records', 'node_modules', 'scripts', 'output'].includes(part))) { response.writeHead(404).end(); return; }
    let path = resolve(root, '.' + pathname);
    if (relative(root, path).startsWith('..')) { response.writeHead(404).end(); return; }
    let info = await stat(path);
    if (info.isDirectory()) { path = join(path, 'index.html'); info = await stat(path); }
    if (!info.isFile() || relative(root, await realpath(path)).startsWith('..')) { response.writeHead(404).end(); return; }
    response.writeHead(200, { 'Content-Type': types[extname(path)] || 'application/octet-stream', 'Content-Length': info.size, 'Cache-Control': 'no-cache', 'X-Content-Type-Options': 'nosniff' });
    if (request.method === 'HEAD') { response.end(); return; }
    const stream = createReadStream(path);
    stream.on('error', () => response.destroy());
    stream.pipe(response);
  } catch { response.writeHead(404).end(); }
});
server.listen(56841, '127.0.0.1', () => console.log('Avelune Packages : http://127.0.0.1:56841'));
for (const signal of ['SIGTERM', 'SIGINT']) process.on(signal, () => { server.close(() => process.exit()); server.closeAllConnections(); });
