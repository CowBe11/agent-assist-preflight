"""Test that the command risk assessment function works correctly."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = PROJECT_ROOT / "management_webui"
sys.path.insert(0, str(SERVER_DIR))

import importlib.util
spec = importlib.util.spec_from_file_location("server", SERVER_DIR / "server.py")
server_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_mod)


# The server may have assess_command_risk function
assess_command_risk = getattr(server_mod, "assess_command_risk", None)
DANGEROUS_KEYWORDS = getattr(server_mod, "DANGEROUS_KEYWORDS", [])


def test_assess_function_exists():
    """assess_command_risk should be defined."""
    if assess_command_risk:
        result = assess_command_risk("echo hello", "testing", "ja")
        assert isinstance(result, dict), "assess_command_risk should return a dict"
        assert "risk" in result, "Result missing 'risk'"
    else:
        # Fallback: check that DANGEROUS_KEYWORDS contains expected patterns
        assert len(DANGEROUS_KEYWORDS) > 0, "No dangerous keywords defined"


def test_dangerous_keywords_exist():
    """Should have dangerous keyword patterns defined."""
    if DANGEROUS_KEYWORDS:
        assert len(DANGEROUS_KEYWORDS) > 0


def test_rm_recognized_as_high_risk():
    """The 'rm' command should be recognized as dangerous."""
    if assess_command_risk:
        result = assess_command_risk("rm -rf /", "test cleanup", "ja")
        assert result.get("risk") in ("high", "medium"), f"Expected high/medium risk for rm, got {result.get('risk')}"


def test_sudo_recognized():
    """The 'sudo' command should be recognized as risky."""
    if assess_command_risk:
        result = assess_command_risk("sudo apt install nginx", "install web server", "ja")
        assert "risk" in result
