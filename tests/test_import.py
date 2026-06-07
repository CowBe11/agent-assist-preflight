"""Test that server.py can be imported and its key data structures are valid."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SERVER_DIR = PROJECT_ROOT / "management_webui"
sys.path.insert(0, str(SERVER_DIR))

import importlib.util
spec = importlib.util.spec_from_file_location("server", SERVER_DIR / "server.py")
server_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_mod)


def test_glossary_exists():
    """GLOSSARY dict should be defined and non-empty."""
    assert hasattr(server_mod, "GLOSSARY"), "GLOSSARY not found in server.py"
    assert isinstance(server_mod.GLOSSARY, dict), "GLOSSARY should be a dict"
    assert len(server_mod.GLOSSARY) >= 144, f"GLOSSARY has {len(server_mod.GLOSSARY)} entries, expected >= 144"


def test_glossary_en_exists():
    """GLOSSARY_EN dict should exist and be non-empty."""
    assert hasattr(server_mod, "GLOSSARY_EN"), "GLOSSARY_EN not found"
    assert isinstance(server_mod.GLOSSARY_EN, dict), "GLOSSARY_EN should be a dict"
    assert len(server_mod.GLOSSARY_EN) >= 100, f"GLOSSARY_EN has {len(server_mod.GLOSSARY_EN)} entries, expected >= 100"
