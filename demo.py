"""Serve the offline coursework demo on loopback; never call a model API."""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from experiment import DEFAULT_MODEL, build_prompt
from verify_claim import verify_parameter_binding

ROOT = Path(__file__).resolve().parent
ASSETS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/demo.css": ("demo.css", "text/css; charset=utf-8"),
    "/demo.js": ("demo.js", "text/javascript; charset=utf-8"),
}


class DemoHandler(BaseHTTPRequestHandler):
    def local_request(self):
        allowed = {
            f"127.0.0.1:{self.server.server_port}",
            f"localhost:{self.server.server_port}",
        }
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        return host in allowed and (origin is None or origin == f"http://{host}")

    def respond(self, status, content, content_type="application/json"):
        payload = content.encode("utf-8") if isinstance(content, str) else content
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if not self.local_request():
            self.respond(403, '{"error":"Local demo requests only"}')
            return
        if self.path in ASSETS:
            filename, content_type = ASSETS[self.path]
            self.respond(200, (ROOT / "demo" / filename).read_bytes(), content_type)
        elif self.path == "/api/cases":
            cases = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
            self.respond(200, json.dumps({
                "model": DEFAULT_MODEL,
                "cases": [{"id": key, **value, "prompt": build_prompt(value)} for key, value in cases.items()],
            }))
        else:
            self.respond(404, '{"error":"Not found"}')

    def do_POST(self):
        if not self.local_request():
            self.respond(403, '{"error":"Local demo requests only"}')
            return
        if self.path != "/api/verify-sqlite":
            self.respond(404, '{"error":"Not found"}')
            return
        if self.headers.get("Transfer-Encoding") or self.headers.get("Content-Length", "0") != "0":
            self.respond(400, '{"error":"This check accepts no user input"}')
            return
        self.respond(200, json.dumps(verify_parameter_binding()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("Choose a port from 1 to 65535")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), DemoHandler)
    print(f"AI Security Agents coursework demo: http://127.0.0.1:{args.port}", flush=True)
    print("Offline prompts and local SQLite verification. No Gemini requests.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
