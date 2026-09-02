#!/usr/bin/env python3
"""Adjust the generated HTTP 413 regression test to send headers only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tests" / "test_webui_hardening.py"
text = path.read_text(encoding="utf-8")

text = text.replace(
    "from http.server import ThreadingHTTPServer\n",
    "from http.client import HTTPConnection\nfrom http.server import ThreadingHTTPServer\n",
    1,
)

start_marker = '            body = b"x" * (self.server_mod._MAX_REQUEST_BYTES + 1)\n'
end_marker = '            self.assertEqual(ctx.exception.code, 413)\n'
start = text.find(start_marker)
if start < 0:
    raise SystemExit("generated 413 test start not found")
end = text.find(end_marker, start)
if end < 0:
    raise SystemExit("generated 413 test end not found")
end += len(end_marker)

new = '''            conn = HTTPConnection("127.0.0.1", port, timeout=3)
            conn.request(
                "POST",
                "/api/comments",
                body=None,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(self.server_mod._MAX_REQUEST_BYTES + 1),
                },
            )
            response = conn.getresponse()
            try:
                self.assertEqual(response.status, 413)
                response.read()
            finally:
                conn.close()
'''
path.write_text(text[:start] + new + text[end:], encoding="utf-8")
