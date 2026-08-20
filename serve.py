"""
Range-capable HTTP server for hadeeth_id local development.
Supports HTTP/1.1 Range requests (bytes=start-end), required
for the NDJSON byte-offset lookup system to work efficiently.

Usage:
    py serve.py            # starts on port 8000
    py serve.py 9000       # starts on custom port

Open http://localhost:8000
"""

import http.server
import os
import sys
import socketserver


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP request handler with RFC 7233 Range request support."""

    def send_head(self):
        path = self.translate_path(self.path)

        # Directory listing fallback to parent
        if os.path.isdir(path):
            return super().send_head()

        # Open file
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None

        fs = os.fstat(f.fileno())
        file_size = fs.st_size
        ctype = self.guess_type(path)

        # Parse Range header
        range_header = self.headers.get('Range')
        if range_header and range_header.startswith('bytes='):
            try:
                ranges_str = range_header[6:]          # strip 'bytes='
                range_part = ranges_str.split(',')[0].strip()
                start_str, end_str = range_part.split('-')

                start = int(start_str) if start_str.strip() else 0
                end   = int(end_str)   if end_str.strip()   else file_size - 1

                start = max(0, min(start, file_size - 1))
                end   = max(start, min(end, file_size - 1))

                content_length = end - start + 1
                f.seek(start)

                self.send_response(206, 'Partial Content')
                self.send_header('Content-Type', ctype)
                self.send_header('Content-Range',
                                 'bytes {}-{}/{}'.format(start, end, file_size))
                self.send_header('Content-Length', str(content_length))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Last-Modified',
                                 self.date_time_string(fs.st_mtime))
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.end_headers()
                return f

            except (ValueError, AttributeError) as exc:
                print('Range parse error: {}, serving full file'.format(exc))
                f.seek(0)

        # Full file response
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(file_size))
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Last-Modified', self.date_time_string(fs.st_mtime))
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        try:
            while True:
                buf = source.read(65536)  # 64 KB chunks
                if not buf:
                    break
                outputfile.write(buf)
        except (BrokenPipeError, ConnectionResetError):
            pass  # client disconnected mid-transfer — normal for range requests

    def log_message(self, fmt, *args):
        # Compact log: show status + path only
        if args and len(args) >= 2:
            status = str(args[1])
            raw    = str(args[0])
            path   = raw.split('"')[1] if '"' in raw else raw
            is_range = (self.headers.get('Range') or '') if hasattr(self, 'headers') else ''
            tag  = ' [RANGE]' if is_range else ''
            print('  {}{}  {}'.format(status, tag, path))
        else:
            super().log_message(fmt, *args)


class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')

    handler = RangeHTTPRequestHandler
    handler.extensions_map.update({
        '.ndjson': 'application/x-ndjson',
        '.json':   'application/json',
        '.html':   'text/html',
        '.js':     'application/javascript',
        '.css':    'text/css',
        '.woff2':  'font/woff2',
    })

    with ThreadedServer(('', port), handler) as httpd:
        print('')
        print('  hadeeth.id dev server')
        print('  URL  : http://localhost:{}'.format(port))
        print('  Range: ENABLED (206 Partial Content)')
        print('  Mode : Threaded')
        print('  Stop : Ctrl+C')
        print('')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\n  Stopped.')
