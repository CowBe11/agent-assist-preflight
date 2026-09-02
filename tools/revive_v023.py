#!/usr/bin/env python3
"""One-shot deterministic revival patch for the v0.2.3 maintenance branch.

This script is intentionally temporary. It patches the source and checked-in dist
copy together, adds regression tests, aligns version metadata, and refreshes docs.
The workflow deletes this script before the branch is merged.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER_PATHS = [
    ROOT / "management_webui" / "server.py",
    ROOT / "dist" / "フォルダの中身チェック" / "management_webui" / "server.py",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_server(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        'CANDIDATES_PATH = DATA_ROOT / "glossary_candidates.json"\n',
        'CANDIDATES_PATH = DATA_ROOT / "glossary_candidates.json"\n'
        'GLOSSARY_OVERRIDES_PATH = DATA_ROOT / "glossary_overrides.json"\n'
        'APP_VERSION = "0.2.3"\n'
        '_MAX_REQUEST_BYTES = 1_250_000\n',
        f"{path}: constants",
    )

    text = replace_once(
        text,
        'def write_json(path: Path, payload: object) -> None:\n'
        '    path.parent.mkdir(parents=True, exist_ok=True)\n'
        '    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")\n\n\n'
        'def read_comments() -> list[dict]:',
        'def write_json(path: Path, payload: object) -> None:\n'
        '    path.parent.mkdir(parents=True, exist_ok=True)\n'
        '    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")\n\n\n'
        'def read_glossary_overrides(path: Path = GLOSSARY_OVERRIDES_PATH) -> dict:\n'
        '    """Read locally promoted glossary entries. Invalid files fail closed to an empty override set."""\n'
        '    if not path.exists():\n'
        '        return {}\n'
        '    try:\n'
        '        data = json.loads(path.read_text(encoding="utf-8"))\n'
        '    except (OSError, json.JSONDecodeError):\n'
        '        return {}\n'
        '    return data if isinstance(data, dict) else {}\n\n\n'
        'def apply_glossary_overrides(path: Path = GLOSSARY_OVERRIDES_PATH) -> dict:\n'
        '    """Apply persisted local glossary promotions to the in-memory dictionaries."""\n'
        '    overrides = read_glossary_overrides(path)\n'
        '    for term, entry in overrides.items():\n'
        '        if not isinstance(entry, dict):\n'
        '            continue\n'
        '        ja_text = str(entry.get("ja", "")).strip()\n'
        '        en_text = str(entry.get("en", "")).strip()\n'
        '        if ja_text:\n'
        '            GLOSSARY[str(term)] = ja_text\n'
        '        if en_text:\n'
        '            GLOSSARY_EN[str(term)] = en_text\n'
        '    return overrides\n\n\n'
        'def persist_glossary_entry(term: str, ja_text: str, en_text: str, path: Path = GLOSSARY_OVERRIDES_PATH) -> None:\n'
        '    """Persist one promoted term before removing it from the candidate queue."""\n'
        '    overrides = read_glossary_overrides(path)\n'
        '    overrides[term] = {"ja": ja_text, "en": en_text}\n'
        '    write_json(path, overrides)\n'
        '    if ja_text:\n'
        '        GLOSSARY[term] = ja_text\n'
        '    if en_text:\n'
        '        GLOSSARY_EN[term] = en_text\n\n\n'
        'apply_glossary_overrides()\n\n\n'
        'def read_comments() -> list[dict]:',
        f"{path}: glossary persistence helpers",
    )

    text = replace_once(
        text,
        '        if cid.startswith("cmd") and cid[1:].isdigit():\n'
        '            nums.append(int(cid[1:]))',
        '        if cid.startswith("cmd") and cid[3:].isdigit():\n'
        '            nums.append(int(cid[3:]))',
        f"{path}: command id parsing",
    )

    text = replace_once(
        text,
        ']\n\ndef _matches_any(cmd: str, patterns: list[str]) -> bool:',
        ']\n\n_SHELL_CONTROL_PATTERN = re.compile(r"(?:>>?|<|&&|\\|\\||;|`|\\$\\()")\n\ndef _matches_any(cmd: str, patterns: list[str]) -> bool:',
        f"{path}: shell control pattern",
    )

    text = replace_once(
        text,
        '    elif _matches_any(cmd, _LOW_RISK_PATTERNS):\n'
        '        risk = "low"\n'
        '        summary_ja = "読み取り専用または情報確認のコマンドです。安全です。"\n'
        '        summary_en = "Read-only or informational command. Safe."\n'
        '        ok_to_continue = True\n'
        '        user_attention = "none"',
        '    elif _SHELL_CONTROL_PATTERN.search(cmd):\n'
        '        risk = "medium"\n'
        '        summary_ja = "リダイレクト・パイプ・連結などのシェル制御記号を含みます。見た目が安全なコマンドでも副作用が増えるため確認してください。"\n'
        '        summary_en = "Contains shell redirection, piping, or command chaining. Review it because these operators can add side effects to an otherwise safe-looking command."\n'
        '        ok_to_continue = True\n'
        '        user_attention = "optional"\n'
        '    elif _matches_any(cmd, _LOW_RISK_PATTERNS):\n'
        '        risk = "low"\n'
        '        summary_ja = "読み取り専用または情報確認のコマンドです。安全です。"\n'
        '        summary_en = "Read-only or informational command. Safe."\n'
        '        ok_to_continue = True\n'
        '        user_attention = "none"',
        f"{path}: shell controls before low risk",
    )

    text = replace_once(
        text,
        '    elif "git status" in cmd.lower():',
        '    elif cmd.lower() == "git status":',
        f"{path}: exact git status",
    )

    text = replace_once(
        text,
        '\n\nclass Handler(BaseHTTPRequestHandler):\n    server_version = "AgentAssistManagementWebUI/0.1"',
        '\n\ndef _origin_is_local(origin: str, server_port: int) -> bool:\n'
        '    """Allow CLI/agent clients without Origin and same-localhost browser requests only."""\n'
        '    origin = (origin or "").strip()\n'
        '    if not origin:\n'
        '        return True\n'
        '    try:\n'
        '        parsed = urlparse(origin)\n'
        '        if parsed.scheme not in {"http", "https"}:\n'
        '            return False\n'
        '        if parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:\n'
        '            return False\n'
        '        port = parsed.port if parsed.port is not None else (443 if parsed.scheme == "https" else 80)\n'
        '    except ValueError:\n'
        '        return False\n'
        '    return port == server_port\n\n\n'
        'class RequestBodyTooLarge(ValueError):\n'
        '    pass\n\n\n'
        'class Handler(BaseHTTPRequestHandler):\n'
        '    server_version = f"AgentAssistManagementWebUI/{APP_VERSION}"',
        f"{path}: origin helper and server version",
    )

    text = replace_once(
        text,
        '    def read_body_json(self) -> dict:\n'
        '        length = int(self.headers.get("Content-Length", "0") or "0")\n'
        '        if length <= 0:\n'
        '            return {}\n'
        '        raw_bytes = self.rfile.read(length)',
        '    def read_body_json(self) -> dict:\n'
        '        try:\n'
        '            length = int(self.headers.get("Content-Length", "0") or "0")\n'
        '        except ValueError as exc:\n'
        '            raise ValueError("invalid Content-Length") from exc\n'
        '        if length <= 0:\n'
        '            return {}\n'
        '        if length > _MAX_REQUEST_BYTES:\n'
        '            raise RequestBodyTooLarge(f"request body too large (max {_MAX_REQUEST_BYTES} bytes)")\n'
        '        raw_bytes = self.rfile.read(length)',
        f"{path}: body size guard",
    )

    text = replace_once(
        text,
        '            "version": "0.1.0",',
        '            "version": APP_VERSION,',
        f"{path}: API version",
    )

    text = replace_once(
        text,
        '    def do_POST(self) -> None:  # noqa: N802\n'
        '        parsed = urlparse(self.path)\n'
        '        try:\n'
        '            payload = self.read_body_json()\n'
        '        except Exception as exc:  # noqa: BLE001\n'
        '            self.send_json({"error": str(exc)}, status=400)\n'
        '            return',
        '    def do_POST(self) -> None:  # noqa: N802\n'
        '        parsed = urlparse(self.path)\n'
        '        origin = self.headers.get("Origin", "")\n'
        '        if not _origin_is_local(origin, self.server.server_port):\n'
        '            self.send_json({"ok": False, "error": "cross-site browser request rejected"}, status=403)\n'
        '            return\n'
        '        try:\n'
        '            payload = self.read_body_json()\n'
        '        except RequestBodyTooLarge as exc:\n'
        '            self.send_json({"ok": False, "error": str(exc)}, status=413)\n'
        '            return\n'
        '        except Exception as exc:  # noqa: BLE001\n'
        '            self.send_json({"error": str(exc)}, status=400)\n'
        '            return',
        f"{path}: POST guards",
    )

    text = replace_once(
        text,
        '            entry = candidates.pop(cid)\n'
        '            # Add to GLOSSARY / GLOSSARY_EN\n'
        '            ja_text = entry.get("ja", entry.get("description", ""))\n'
        '            en_text = entry.get("en", entry.get("description", ""))\n'
        '            if ja_text:\n'
        '                GLOSSARY[cid] = ja_text\n'
        '            if en_text:\n'
        '                GLOSSARY_EN[cid] = en_text\n'
        '            write_json(CANDIDATES_PATH, candidates)',
        '            entry = candidates[cid]\n'
        '            ja_text = str(entry.get("ja", entry.get("description", ""))).strip()\n'
        '            en_text = str(entry.get("en", entry.get("description", ""))).strip()\n'
        '            if not ja_text and not en_text:\n'
        '                self.send_json({"ok": False, "error": "candidate has no glossary text"}, status=400)\n'
        '                return\n'
        '            # Persist first so a failed write never destroys the only copy of the candidate.\n'
        '            persist_glossary_entry(cid, ja_text, en_text)\n'
        '            candidates.pop(cid)\n'
        '            write_json(CANDIDATES_PATH, candidates)',
        f"{path}: promotion persistence",
    )

    text = text.replace(
        '            risk_order = {"high": 0, "medium": 1, "low": 2}\n'
        '            sorted_cards = sorted(cards, key=lambda c: (risk_order.get(c.get("risk", "low"), 99), c.get("created_at", ""),), reverse=False)\n'
        '            # First sort by risk priority, then within same risk by newest first\n'
        '            # Simpler: high first, rest by time\n',
        '            # High-risk cards first, then the remaining cards by recency.\n',
    )

    path.write_text(text, encoding="utf-8")


def write_compatibility_launcher() -> None:
    content = textwrap.dedent(
        '''\
        #!/usr/bin/env python3
        """Compatibility launcher for Agent Assist Preflight v0.2.3.

        The maintained WebUI lives in management_webui/server.py. This file remains so
        existing Windows launchers and old instructions keep working without maintaining
        a second, divergent copy of the server implementation.
        """
        from __future__ import annotations

        import sys
        import threading
        import time
        import webbrowser

        VERSION = "0.2.3"


        def main() -> None:
            if "--version" in sys.argv:
                print(f"agent-assist-preflight-standalone {VERSION}")
                return

            def _open_browser() -> None:
                time.sleep(0.8)
                webbrowser.open("http://127.0.0.1:8765/")

            threading.Thread(target=_open_browser, daemon=True).start()
            from management_webui.server import main as webui_main
            webui_main()


        if __name__ == "__main__":
            main()
        '''
    )
    for path in [ROOT / "standalone.py", ROOT / "dist" / "フォルダの中身チェック" / "standalone.py"]:
        path.write_text(content, encoding="utf-8")


def align_versions() -> None:
    pyproject = ROOT / "pyproject.toml"
    text = replace_once(pyproject.read_text(encoding="utf-8"), 'version = "0.1.2"', 'version = "0.2.3"', "pyproject version")
    pyproject.write_text(text, encoding="utf-8")

    checker = ROOT / "preflight_checker.py"
    text = replace_once(checker.read_text(encoding="utf-8"), 'VERSION = "0.1.2"', 'VERSION = "0.2.3"', "CLI version")
    checker.write_text(text, encoding="utf-8")

    version_tests = ROOT / "tests" / "test_preflight_checker.py"
    version_tests.write_text(version_tests.read_text(encoding="utf-8").replace("0.1.2", "0.2.3"), encoding="utf-8")


def update_gitignore() -> None:
    path = ROOT / ".gitignore"
    text = path.read_text(encoding="utf-8")
    if "management_webui/data/glossary_overrides.json" not in text:
        anchor = "management_webui/data/command_card_mode.json\n"
        if anchor not in text:
            raise SystemExit(".gitignore local-state anchor not found")
        text = text.replace(anchor, anchor + "management_webui/data/glossary_overrides.json\n")
    path.write_text(text, encoding="utf-8")


def write_regression_tests() -> None:
    content = textwrap.dedent(
        '''\
        import importlib.util
        import json
        import threading
        import unittest
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

                    body = b"x" * (self.server_mod._MAX_REQUEST_BYTES + 1)
                    too_large = Request(
                        f"http://127.0.0.1:{port}/api/comments",
                        data=body,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self.assertRaises(HTTPError) as ctx:
                        urlopen(too_large, timeout=3)
                    self.assertEqual(ctx.exception.code, 413)
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
        '''
    )
    (ROOT / "tests" / "test_webui_hardening.py").write_text(content, encoding="utf-8")


def refresh_readmes() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace('[日本語 README](README.ja.md) | `v0.1.2` |', '[日本語 README](README.ja.md) | `v0.2.3` |')
    if "actions/workflows/ci.yml/badge.svg" not in text:
        text = text.replace(
            "# Agent Assist Preflight / AIエージェント初心者支援ツール\n",
            "# Agent Assist Preflight / AIエージェント初心者支援ツール\n\n[![CI](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml)\n",
        )
    text = text.replace(
        "A local, read-only safety layer for people using Claude Code, Cursor, Codex, OpenCode, ChatGPT, Hermes, or other AI agents on real projects.",
        "A local preflight and review layer for people using Claude Code, Cursor, Codex, OpenCode, ChatGPT, Hermes, or other AI agents on real projects.",
    )
    text = text.replace(
        "- **read-only**\n- **local-only**\n- **no command execution**\n- **no dependency installation**\n- **no automatic external sending**\n- **no silent browser control**",
        "- **read-only toward inspected projects** — commands found in a target repo are never executed\n- **local-only** — the WebUI binds to localhost\n- **fixed diagnostics only** — the WebUI may run predefined read-only environment checks\n- **no dependency installation**\n- **no automatic external sending**\n- **no silent browser control**",
    )
    readme.write_text(text, encoding="utf-8")

    readme_ja = ROOT / "README.ja.md"
    text = readme_ja.read_text(encoding="utf-8")
    text = text.replace('[English README](README.md) | `v0.2.0 "Control Deck"` / コントロールデッキ |', '[English README](README.md) | `v0.2.3 "Revival"` / リバイバル |')
    if "actions/workflows/ci.yml/badge.svg" not in text:
        text = text.replace(
            "# Agent Assist Preflight / AIエージェント初心者支援ツール\n",
            "# Agent Assist Preflight / AIエージェント初心者支援ツール\n\n[![CI](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml)\n",
        )
    text = text.replace(
        "Claude Code・Cursor・Codex・OpenCode・ChatGPT・Hermes などのAIエージェントとつなげて使える、ローカル専用・読み取り専用の初心者支援ツールです。",
        "Claude Code・Cursor・Codex・OpenCode・ChatGPT・Hermes などのAIエージェントとつなげて使える、ローカル専用の実行前レビュー・初心者支援ツールです。",
    )
    text = text.replace(
        "- **read-only / 読み取り専用**\n- **local-only / ローカル専用**\n- **コマンド実行なし**\n- **依存関係のインストールなし**\n- **外部への自動送信なし**\n- **勝手なブラウザ操作なし**",
        "- **確認対象のプロジェクトには read-only** — README等で見つけたコマンドを勝手に実行しません\n- **local-only / ローカル専用** — WebUIはlocalhostだけで待ち受けます\n- **固定の読み取り診断のみ** — WebUI自身の環境確認では、あらかじめ決めた読み取り系コマンドだけを使います\n- **依存関係のインストールなし**\n- **外部への自動送信なし**\n- **勝手なブラウザ操作なし**",
    )
    readme_ja.write_text(text, encoding="utf-8")

    dist_root = ROOT / "dist" / "フォルダの中身チェック"
    (dist_root / "README.md").write_text(readme.read_text(encoding="utf-8"), encoding="utf-8")
    (dist_root / "README.ja.md").write_text(readme_ja.read_text(encoding="utf-8"), encoding="utf-8")


def refresh_release_board() -> None:
    content = textwrap.dedent(
        '''\
        # Agent Assist Preflight — Release Board

        ## v0.2.3 "Revival" — 2026-09-02

        The maintenance audit has been converted into a tested revival release candidate.

        ### Fixed in Revival

        - [x] Package, CLI, management API, README, and compatibility-launcher versions aligned to `0.2.3`.
        - [x] Command-card IDs correctly parse the `cmdNNNN` suffix instead of reusing `cmd0001`.
        - [x] Promoted glossary candidates persist in local `glossary_overrides.json` and survive WebUI restarts.
        - [x] Local JSON POST bodies are capped at 1.25 MB; oversized requests return HTTP 413.
        - [x] Browser POSTs with a non-local Origin are rejected while CLI/agent clients without Origin remain supported.
        - [x] Shell redirection, pipelines, command chaining, command substitution, and similar control operators cannot inherit a low-risk rating from a safe-looking prefix.
        - [x] The old duplicated `standalone.py` server is replaced by a thin compatibility launcher for the maintained WebUI.
        - [x] Root and checked-in `dist/` WebUI server copies remain synchronized.
        - [x] Regression tests cover the audit findings.
        - [x] CI runs core checks on Python 3.9/3.12 plus the full pytest suite.

        ### Current boundary

        The scanner never executes commands found in an inspected project. The local management WebUI may run fixed read-only environment diagnostics and writes only its own local state. It does not auto-install dependencies, auto-send content to external services, or silently control the browser.

        ## Next — quality and maintainability

        - [ ] Split `management_webui/server.py` by responsibility before the next large feature wave.
        - [ ] Generate `dist/` from source instead of keeping a manually synchronized duplicate.
        - [ ] Expand secret patterns for major cloud/chat providers.
        - [ ] Improve mobile layout and accessibility.
        - [ ] Add traceback highlighting and step-by-step common-error guidance.
        - [ ] Add a small contributor guide and release checklist.

        ## Long term

        - [ ] Local-AI assistance only behind explicit user action, masked text, confirmation UI, read-only tools, and no automatic external send.
        - [ ] Stronger agent / MCP permission boundaries.
        - [ ] Custom review patterns with a beginner-facing explanation for every rule.

        ## Out of scope

        - Full security auditing or malware detection
        - Real-time threat intelligence
        - Automatic remote diagnosis
        - Automatic command repair / execution
        '''
    )
    (ROOT / "RELEASE_BOARD.md").write_text(content, encoding="utf-8")


def main() -> None:
    for path in SERVER_PATHS:
        patch_server(path)
    write_compatibility_launcher()
    align_versions()
    update_gitignore()
    write_regression_tests()
    refresh_readmes()
    refresh_release_board()


if __name__ == "__main__":
    main()
