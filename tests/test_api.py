"""Test main API endpoints return 200 and expected structure."""

import json
import sys
import threading
import time
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import urlopen, Request
from urllib.error import URLError

import pytest

SERVER_DIR = Path(__file__).resolve().parents[1] / "management_webui"
sys.path.insert(0, str(SERVER_DIR))

import importlib.util
spec = importlib.util.spec_from_file_location("server", SERVER_DIR / "server.py")
server_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_mod)

Handler = server_mod.Handler
PORT = 18765
BASE = f"http://127.0.0.1:{PORT}"


@pytest.fixture(scope="module")
def server():
    """Start a test server on a high port."""
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    time.sleep(0.3)  # Let it bind
    yield
    httpd.shutdown()


def test_api_index(server):
    """GET /api should return 200 with valid JSON."""
    resp = urlopen(f"{BASE}/api")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert isinstance(data, dict)


def test_api_glossary_ja(server):
    """GET /api/glossary should return glossary dict."""
    resp = urlopen(f"{BASE}/api/glossary")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert isinstance(data, dict)
    assert len(data) >= 144


def test_api_glossary_en(server):
    """GET /api/glossary?lang=en should return EN glossary."""
    resp = urlopen(f"{BASE}/api/glossary?lang=en")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert isinstance(data, dict)
    assert len(data) >= 144


def test_api_glossary_candidates(server):
    """GET /api/glossary-candidates should return candidates dict."""
    resp = urlopen(f"{BASE}/api/glossary-candidates")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert isinstance(data, dict)
    assert len(data) >= 1


def test_api_state(server):
    """GET /api/state should return project state."""
    resp = urlopen(f"{BASE}/api/state")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert "project" in data
    assert data["project"] == "Agent Assist Preflight"


def test_api_port_owners(server):
    """GET /api/port-owners should return port data."""
    resp = urlopen(f"{BASE}/api/port-owners")
    assert resp.status == 200
    data = json.loads(resp.read().decode())
    assert "ok" in data or "ports" in data
