#!/usr/bin/env python3
"""
DOM Clobbering Lab server.

Serves the static lab from ./public and provides a tiny "attacker" collector:

  POST /collect        store an exfiltrated payload, return {"ok": true}
  GET  /collect?...    same (used by image beacons), returns {"ok": true}
  GET  /collect.json   list of collected entries
  POST /reset          wipe the collector log

Legit (non-logged) endpoints used by the simulated victims:
  POST /api/checkout, POST /api/upload, GET /api/analytics/ping

Only stdlib. Runs on http://127.0.0.1:8000 by default.
"""
import json
import os
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(BASE, "public")
LOG_PATH = os.path.join(BASE, "collect.log")
LOCK = threading.Lock()

LEGIT_RESPONSES = {
    "/api/checkout": {"ok": True, "orderId": "ORD-7781"},
    "/api/upload": {"ok": True, "stored": True},
    "/api/analytics/ping": {"ok": True},
}


def read_log(limit=300):
    if not os.path.exists(LOG_PATH):
        return []
    entries = []
    with open(LOG_PATH, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries[-limit:]


def append_log(entry):
    with LOCK:
        with open(LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC, **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))

    def _send_json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)

        if url.path == "/collect.json":
            return self._send_json(read_log())

        if url.path == "/collect":
            append_log({
                "id": os.urandom(4).hex(),
                "ts": time.time(),
                "method": "GET",
                "path": url.path,
                "query": url.query,
                "body": "",
                "ua": self.headers.get("User-Agent", ""),
            })
            return self._send_json({"ok": True})

        if url.path in LEGIT_RESPONSES:
            return self._send_json(LEGIT_RESPONSES[url.path])

        if url.path == "/":
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b""

        if url.path == "/reset":
            with LOCK:
                open(LOG_PATH, "w").close()
            return self._send_json({"ok": True})

        if url.path == "/collect":
            append_log({
                "id": os.urandom(4).hex(),
                "ts": time.time(),
                "method": "POST",
                "path": url.path,
                "query": url.query,
                "body": raw.decode("utf-8", "replace")[:8000],
                "ua": self.headers.get("User-Agent", ""),
            })
            return self._send_json({"ok": True})

        if url.path in LEGIT_RESPONSES:
            return self._send_json(LEGIT_RESPONSES[url.path])

        self.send_error(404, "Not found")


def main():
    port = int(os.environ.get("PORT", sys.argv[1] if len(sys.argv) > 1 else 8000))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("\n  DOM Clobbering Lab")
    print("  ------------------")
    print("  Lab       : http://127.0.0.1:%d/" % port)
    print("  Collector : http://127.0.0.1:%d/attacker.html" % port)
    print("  Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  bye\n")


if __name__ == "__main__":
    main()
