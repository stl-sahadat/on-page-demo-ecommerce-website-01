import os
import sys
import gzip
import http.server
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = int(os.environ.get('PORT', 5000))
DIRECTORY = os.path.abspath(os.path.dirname(__file__))

COMPRESSIBLE_TYPES = {
    'text/html', 'text/css', 'application/javascript', 'application/json',
    'image/svg+xml', 'text/plain', 'text/xml'
}

class FastRequestHandler(SimpleHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # 1. Add Keep-Alive
        self.send_header('Connection', 'keep-alive')

        # 2. Add Caching Headers
        path = self.translate_path(self.path)
        ext = os.path.splitext(path)[1].lower()

        if ext in ['.webp', '.png', '.jpg', '.jpeg', '.svg', '.gif', '.ico', '.woff', '.woff2', '.ttf']:
            self.send_header('Cache-Control', 'public, max-age=604800, immutable')
        elif ext in ['.css', '.js']:
            self.send_header('Cache-Control', 'public, max-age=86400')
        elif ext in ['.html', ''] or self.path == '/':
            self.send_header('Cache-Control', 'no-cache, must-revalidate')

        super().end_headers()

    def do_GET(self):
        # Handle Gzip compression for compressible static text/code
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            path = os.path.join(path, 'index.html')

        if not os.path.isfile(path):
            super().do_GET()
            return

        ctype = self.guess_type(path)
        accept_encoding = self.headers.get('Accept-Encoding', '')

        # Check if compressible
        is_compressible = any(ctype.startswith(t) for t in COMPRESSIBLE_TYPES)
        should_gzip = is_compressible and 'gzip' in accept_encoding

        if should_gzip:
            try:
                with open(path, 'rb') as f:
                    content = f.read()

                # Compress content
                compressed = gzip.compress(content, compresslevel=6)

                self.send_response(200)
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Encoding', 'gzip')
                self.send_header('Content-Length', str(len(compressed)))
                self.end_headers()
                self.wfile.write(compressed)
                return
            except Exception as e:
                pass

        super().do_GET()

def run():
    server = ThreadingHTTPServer(('', PORT), FastRequestHandler)
    print(f'Fast Multi-Threaded Gzip Server running on port {PORT} for {DIRECTORY}')
    server.serve_forever()

if __name__ == '__main__':
    run()
