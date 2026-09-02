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
