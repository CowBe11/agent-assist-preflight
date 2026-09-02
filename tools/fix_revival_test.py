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
old = '''                    body = b"x" * (self.server_mod._MAX_REQUEST_BYTES + 1)
                    too_large = Request(
                        f"http://127.0.0.1:{port}/api/comments",
                        data=body,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self.assertRaises(HTTPError) as ctx:
                        urlopen(too_large, timeout=3)
                    self.assertEqual(ctx.exception.code, 413)
'''
new = '''                    conn = HTTPConnection("127.0.0.1", port, timeout=3)
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
if old not in text:
    raise SystemExit("generated 413 test block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
