import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import preflight_checker

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "preflight_checker.py"
STANDALONE_SCRIPT = ROOT / "standalone.py"


def run_checker(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, text=True, capture_output=True)


class PreflightCheckerTests(unittest.TestCase):
    def test_safe_fixture_json(self):
        result = run_checker("tests/fixtures/safe", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertIn(data["decision"], {"no_review_items_found", "review_before_trying"})
        self.assertEqual(data["confirmation_categories"], [])

    def test_danger_fixture_asks_for_confirmation_without_security_language(self):
        result = run_checker("tests/fixtures/danger", "--format", "json", "--fail-on", "confirm")
        self.assertEqual(result.returncode, 2)
        data = json.loads(result.stdout)
        self.assertEqual(data["decision"], "confirm_before_running")
        self.assertIn("global_install", data["confirmation_categories"])
        self.assertIn("secrets_or_auth", data["confirmation_categories"])
        self.assertIn("daemon_or_cron", data["confirmation_categories"])
        self.assertEqual(data["beginner_summary"]["headline"], "Stop and ask before running commands from this project.")
        self.assertIn("plain_language", data["review_items"][0])
        self.assertIn("why_it_matters", data["review_items"][0])
        self.assertIn("beginner_next_step", data["review_items"][0])
        self.assertNotIn("security scanner", result.stdout.lower())

    def test_markdown_output_explains_warnings_in_plain_language(self):
        result = run_checker("tests/fixtures/danger", "--format", "markdown")
        self.assertEqual(result.returncode, 0)
        self.assertIn("# Agent Assist Preflight Notes", result.stdout)
        self.assertIn("## Plain-language summary", result.stdout)
        self.assertIn("## What the review items mean", result.stdout)
        self.assertIn("This is not a security scanner", result.stdout)
        self.assertIn("What this means", result.stdout)
        self.assertIn("Beginner next step", result.stdout)

    def test_exclude_pattern_skips_danger_fixture(self):
        result = run_checker("tests/fixtures", "--format", "json", "--exclude", "danger/**", "--fail-on", "high")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        files = {finding["file"] for finding in data["findings"]}
        self.assertNotIn("danger/README.md", files)

    def test_secret_values_are_redacted(self):
        tmp = ROOT / "tests" / "fixtures" / "tmp_secret.md"
        tmp.write_text("Use API_KEY=demo-secret-value and bearer demo.bearer.value", encoding="utf-8")
        try:
            result = run_checker(str(tmp), "--format", "json")
        finally:
            tmp.unlink(missing_ok=True)
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("demo-secret-value", result.stdout)
        self.assertNotIn("demo.bearer.value", result.stdout)
        self.assertIn("[REDACTED]", result.stdout)

    def test_quoted_and_json_secret_values_are_redacted(self):
        samples = [
            'API_KEY="quoted-secret"',
            '"api_key": "json-secret"',
            "TOKEN='single-quoted-secret'",
        ]
        for sample in samples:
            with self.subTest(sample=sample):
                redacted = preflight_checker.redact_excerpt(sample)
                self.assertIn("[REDACTED]", redacted)
                self.assertNotIn("secret", redacted)

    def test_negation_does_not_hide_required_secret_or_paid_subscription(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "README.md"
            candidate.write_text(
                "No free trial; a paid subscription and API key are required.\n",
                encoding="utf-8",
            )
            report = preflight_checker.scan([candidate])

        categories = {item["category"] for item in report["review_items"]}
        self.assertIn("paid_or_billing", categories)
        self.assertIn("secrets_or_auth", categories)

    def test_cli_outputs_utf8_even_when_windows_console_encoding_is_cp932(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "README.md"
            candidate.write_text("📖 API key is required.\n", encoding="utf-8")
            env = {**os.environ, "PYTHONIOENCODING": "cp932"}
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(candidate), "--format", "json"],
                cwd=ROOT,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertIn("📖", result.stdout.decode("utf-8"))

    def test_version_metadata_matches_release(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")

        self.assertEqual(preflight_checker.VERSION, "0.2.3")
        self.assertIn('version = "0.2.3"', pyproject)

    def test_cli_version_flag_does_not_require_paths(self):
        result = run_checker("--version")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "agent-assist-preflight 0.2.3")

    def test_standalone_version_flag_exits_without_starting_server(self):
        result = subprocess.run(
            [sys.executable, str(STANDALONE_SCRIPT), "--version"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=5,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "agent-assist-preflight-standalone 0.2.3")


if __name__ == "__main__":
    unittest.main()
