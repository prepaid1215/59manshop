#!/usr/bin/env python3
"""Local static preview; a larger request queue supports concurrent browser QA."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class PreviewServer(ThreadingHTTPServer):
    request_queue_size = 128
    daemon_threads = True
    allow_reuse_address = True


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


if __name__ == '__main__':
    root = Path(__file__).resolve().parent.parent
    server = PreviewServer(('127.0.0.1', 8765), partial(QuietHandler, directory=str(root)))
    print('Preview: http://127.0.0.1:8765', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
