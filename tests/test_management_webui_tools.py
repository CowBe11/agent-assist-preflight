import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "management_webui" / "server.py"


def load_server_module():
    spec = importlib.util.spec_from_file_location("management_webui_server", SERVER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BasicToolCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = load_server_module()

    def test_basic_tool_checker_returns_all_expected_tools(self):
        data = self.server.scan_basic_tools()
        self.assertTrue(data["ok"])
        self.assertIn("summary", data)
        self.assertIn("running_side", data)
        tool_ids = {item["id"] for item in data["tools"]}
        self.assertEqual(tool_ids, {"python", "node", "npm", "git", "gh", "powershell", "wsl", "docker"})

    def test_basic_tool_checker_schema_is_agent_readable(self):
        data = self.server.scan_basic_tools()
        for item in data["tools"]:
            with self.subTest(tool=item["id"]):
                self.assertIn(item["status"], {"both", "agent_only", "windows_only", "missing"})
                self.assertIsInstance(item["agent_can_use"], bool)
                self.assertIsInstance(item["current_side"], dict)
                self.assertIsInstance(item["windows_side"], dict)
                self.assertIn("beginner_explanation", item)
                self.assertIn("agent_caution", item)
                self.assertIn("run_command", item)

    def test_windows_subprocesses_request_utf8_with_replacement(self):
        completed = self.server.subprocess.CompletedProcess([], 0, stdout="", stderr="")
        with (
            patch.object(self.server.shutil, "which", return_value="powershell.exe"),
            patch.object(self.server.subprocess, "run", return_value=completed) as run,
        ):
            self.server._windows_tool_snapshot()
        self.assertEqual(run.call_args.kwargs["encoding"], "utf-8")
        self.assertEqual(run.call_args.kwargs["errors"], "replace")

    def test_url_card_ids_do_not_repeat_after_history_is_trimmed(self):
        cards = [{"id": f"u{number:04d}"} for number in range(2, 22)]
        self.assertEqual(self.server.next_url_card_id(cards), "u0022")

    def test_url_card_status_endpoint_is_documented_as_post(self):
        server_source = SERVER.read_text(encoding="utf-8")
        self.assertIn('"POST /api/url-card/<id>"', server_source)
        self.assertNotIn('"PATCH /api/url-card/<id>"', server_source)

    def test_url_validation_requires_a_hostname(self):
        self.assertEqual(self.server._validate_url("https://"), (False, "url must include a hostname"))
        self.assertEqual(self.server._validate_url("https://example.com"), (True, ""))

    def test_distribution_webui_server_matches_source(self):
        distributed = ROOT / "dist" / "フォルダの中身チェック" / "management_webui" / "server.py"
        self.assertEqual(distributed.read_text(encoding="utf-8"), SERVER.read_text(encoding="utf-8"))

    def test_webui_renders_all_review_items(self):
        app_js = (ROOT / "management_webui" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertNotIn("items.slice(0, 5)", app_js)
        self.assertIn("items.map((item, index)", app_js)

    def test_term_annotation_uses_one_pass_to_avoid_rewriting_tooltip_html(self):
        app_js = (ROOT / "management_webui" / "static" / "app.js").read_text(encoding="utf-8")
        annotation = app_js.split("function annotateTerms(text) {", 1)[1].split("\n}", 1)[0]
        self.assertNotIn("for (const term of terms)", annotation)
        self.assertIn("const pattern =", annotation)

    def test_dashboard_exposes_operational_controls(self):
        index_html = (ROOT / "management_webui" / "static" / "index.html").read_text(encoding="utf-8")
        expected_ids = [
            "dashScanForm",
            "dashTargetPathInput",
            "dashPickFolderBtn",
            "dashTextInput",
            "dashTextDropZone",
            "dashTextFileInput",
            "dashCliInput",
            "dashPortOwnersBtn",
            "dashToolBasicsBtn",
            "dashGlossarySearch",
            "dashWorkbenchOutput",
        ]
        for element_id in expected_ids:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', index_html)

    def test_dashboard_js_has_direct_action_handlers(self):
        app_js = (ROOT / "management_webui" / "static" / "app.js").read_text(encoding="utf-8")
        expected_functions = [
            "async function runDashboardScan",
            "async function runDashboardTextScan",
            "async function scanDashboardTextFile",
            "function setupDashboardDropZone",
            "function runDashboardCliCheck",
            "async function runDashboardPortOwners",
            "async function runDashboardToolBasics",
            "function renderDashboardGlossary",
            "function bindDashboardControls",
        ]
        for function_name in expected_functions:
            with self.subTest(function_name=function_name):
                self.assertIn(function_name, app_js)

    def test_dashboard_picker_reuses_shared_path_selection_flow(self):
        app_js = (ROOT / "management_webui" / "static" / "app.js").read_text(encoding="utf-8")
        self.assertIn("async function pickFolderForInputs(", app_js)
        dashboard_picker = app_js.split("async function pickDashboardFolder()", 1)[1].split("\n}", 1)[0]
        self.assertIn("pickFolderForInputs(", dashboard_picker)

    def test_windows_picker_uses_topmost_owner_window(self):
        server_source = SERVER.read_text(encoding="utf-8")
        self.assertIn("$owner = New-Object System.Windows.Forms.Form", server_source)
        self.assertIn("$owner.TopMost = $true", server_source)
        self.assertIn("$dialog.ShowDialog($owner)", server_source)


if __name__ == "__main__":
    unittest.main()
