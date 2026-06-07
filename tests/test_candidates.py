"""Test that glossary_candidates.json can be loaded."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "management_webui" / "data"
CANDIDATES_PATH = DATA_DIR / "glossary_candidates.json"


def test_candidates_file_exists():
    """glossary_candidates.json should exist."""
    assert CANDIDATES_PATH.exists(), f"File not found: {CANDIDATES_PATH}"


def test_candidates_is_valid_json():
    """Should be valid JSON."""
    content = CANDIDATES_PATH.read_text(encoding="utf-8")
    data = json.loads(content)
    assert isinstance(data, dict), f"Expected dict, got {type(data)}"


def test_candidates_have_entries():
    """Should have at least 1 entry."""
    content = CANDIDATES_PATH.read_text(encoding="utf-8")
    data = json.loads(content)
    assert len(data) >= 1, f"Expected >=1 candidate, got {len(data)}"


def test_candidates_entry_format():
    """Each entry should have required fields."""
    content = CANDIDATES_PATH.read_text(encoding="utf-8")
    data = json.loads(content)
    for term, entry in data.items():
        assert isinstance(entry, dict), f"Entry '{term}' is not a dict"
        assert "ja" in entry, f"Entry '{term}' missing 'ja'"
        assert "en" in entry, f"Entry '{term}' missing 'en'"
        assert "pri" in entry, f"Entry '{term}' missing 'pri'"
        assert "cat" in entry, f"Entry '{term}' missing 'cat'"
