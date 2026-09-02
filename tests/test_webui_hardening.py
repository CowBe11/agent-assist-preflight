import importlib.util
import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "management_webui" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("preflight_hardened_server", SERVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WebUIHardeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_mod = load_server_module()

    def test_command_card_id_uses_cmd_numeric_suffix(self):
        cards = [{"id": "cmd0001"}, {"id": "cmd0012"}, {"id": "noise"}]
        self.assertEqual(self.server_mod.next_command_card_id(cards), "cmd0013")

    def test_shell_redirection_is_not_low_risk(self):
        result = self.server_mod.assess_command_risk("echo hello > output.txt")
        self.assertEqual(result["risk"], "medium")
        self.assertEqual(result["user_attention"], "optional")

    def test_shell_chaining_cannot_be_downgraded_by_git_status_summary(self):
        result = self.server_mod.assess_command_risk("git status; touch marker.txt")
        self.assertEqual(result["risk"], "medium")

    def test_origin_guard_allows_agents_and_same_localhost_only(self):
        self.assertTrue(self.server_mod._origin_is_local("", 8765))
        self.assertTrue(self.server_mod._origin_is_local("http://127.0.0.1:8765", 8765))
        self.assertTrue(self.server_mod._origin_is_local("http://localhost:8765", 8765))
        self.assertFalse(self.server_mod._origin_is_local("https://example.com", 8765))
        self.assertFalse(self.server_mod._origin_is_local("http://127.0.0.1:9999", 8765))

    def test_glossary_promotion_survives_reload(self):
        term = "revival-test-term"
        old_ja = self.server_mod.GLOSSARY.pop(term, None)
        old_en = self.server_mod.GLOSSARY_EN.pop(term, None)
        try:
            with TemporaryDirectory() as tmp:
                path = Path(tmp) / "overrides.json"
                self.server_mod.persist_glossary_entry(term, "再起動後も残る", "Survives restart", path)
                self.server_mod.GLOSSARY.pop(term, None)
                self.server_mod.GLOSSARY_EN.pop(term, None)
                self.server_mod.apply_glossary_overrides(path)
                self.assertEqual(self.server_mod.GLOSSARY[term], "再起動後も残る")
                self.assertEqual(self.server_mod.GLOSSARY_EN[term], "Survives restart")
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIn(term, data)
        finally:
            self.server_mod.GLOSSARY.pop(term, None)
            self.server_mod.GLOSSARY_EN.pop(term, None)
            if old_ja is not None:
                self.server_mod.GLOSSARY[term] = old_ja
            if old_en is not None:
                self.server_mod.GLOSSARY_EN[term] = old_en

    def test_cross_site_post_is_rejected_and_oversize_body_is_413(self):
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), self.server_mod.Handler)
        port = httpd.server_port
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            bad_origin = Request(
                f"http://127.0.0.1:{port}/api/comments",
                data=b"{}",
                headers={"Content-Type": "application/json", "Origin": "https://example.com"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(bad_origin, timeout=3)
            self.assertEqual(ctx.exception.code, 403)

            conn = HTTPConnection("127.0.0.1", port, timeout=3)
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
        finally:
            httpd.shutdown()
            httpd.server_close()

    def test_api_and_server_report_current_version(self):
        self.assertEqual(self.server_mod.APP_VERSION, "0.2.3")
        self.assertIn("0.2.3", self.server_mod.Handler.server_version)

    def test_standalone_is_now_a_thin_compatibility_launcher(self):
        source = (ROOT / "standalone.py").read_text(encoding="utf-8")
        self.assertIn("from management_webui.server import main as webui_main", source)
        self.assertNotIn("class Handler(BaseHTTPRequestHandler)", source)


if __name__ == "__main__":
    unittest.main()
