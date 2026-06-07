"""Test glossary data loading from server.py."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = PROJECT_ROOT / "management_webui"
sys.path.insert(0, str(SERVER_DIR))

import importlib.util
spec = importlib.util.spec_from_file_location("server", SERVER_DIR / "server.py")
server_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_mod)


def test_glossary_is_dict_of_strings():
    """GLOSSARY values should all be strings."""
    for key, val in server_mod.GLOSSARY.items():
        assert isinstance(val, str), f"GLOSSARY['{key}'] is not a string: {type(val)}"


def test_glossary_en_is_dict_of_strings():
    """GLOSSARY_EN values should all be strings."""
    for key, val in server_mod.GLOSSARY_EN.items():
        assert isinstance(val, str), f"GLOSSARY_EN['{key}'] is not a string: {type(val)}"


def test_glossary_has_common_terms():
    """Common security terms should be present."""
    common = {"sudo", "chmod", "rm", "docker", "pip", "MCP", "JSON"}
    found = common & set(server_mod.GLOSSARY.keys())
    assert found, f"None of the expected common terms found in GLOSSARY: {common}"
