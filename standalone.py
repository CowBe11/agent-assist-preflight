#!/usr/bin/env python3
"""Standalone Agent Assist Preflight — beginner support tool.

A single-file distribution that bundles the preflight checker, port conflict
checker, glossary, and WebUI server.  Only Python stdlib is required (3.9+).
Static files (index.html, app.js, styles.css) are read from the sibling
directory ``management_webui/static/`` relative to this script.
"""
from __future__ import annotations

import datetime as _dt
import fnmatch
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import parse_qs, urlparse

# ═══════════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_DIR = Path(__file__).resolve().parent
STATIC_ROOT = SCRIPT_DIR / "management_webui" / "static"
DATA_ROOT = SCRIPT_DIR / "management_webui" / "data"
COMMENTS_PATH = DATA_ROOT / "review_comments.json"

# ═══════════════════════════════════════════════════════════════════════════════
# Preflight checker (from preflight_checker.py)
# ═══════════════════════════════════════════════════════════════════════════════

VERSION = "0.1.0"
DEFAULT_EXTENSIONS = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".ini", ".env.example", ".sh", ".bash", ".ps1", ".py", ".js", ".ts",
    ".mjs", ".cjs", ".dockerfile", "", ".lock"
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}
MAX_FILE_BYTES = 512_000

RISK_RULES = [
    ("destructive_delete", "high", r"\b(rm\s+-rf|del\s+/[fsq]|remove-item\s+.*-recurse|shutil\.rmtree|delete\s+all|drop\s+database|drop\s+table)\b"),
    ("global_install", "high", r"\b(sudo\s+)?(npm|pnpm|yarn|pip|pipx|cargo|brew|apt|apt-get)\s+(install|add)\b|\bcurl\s+[^\n|]+\|\s*(sh|bash)\b"),
    ("secrets_or_auth", "high", r"\b(api[\s_-]?key|secret|token|oauth|client_secret|password|bearer\s+[^\s]+|\.env\b)"),
    ("paid_or_billing", "high", r"\b(billing|paid|subscription|credit card|stripe|pricing|usage-based|quota|credits?)\b"),
    ("daemon_or_cron", "high", r"\b(systemctl|launchctl|crontab|cron|daemon|service\s+install|pm2\s+start|forever\s+start)\b"),
    ("config_mutation", "high", r"\b(hermes\s+config\s+set|mcpServers|claude_desktop_config|settings\.json|config\.yaml|write\s+to\s+.*config)\b"),
    ("remote_code_execution", "high", r"\b(eval\(|exec\(|child_process|subprocess\.(run|popen|call)|os\.system|powershell\s+-enc)\b"),
    ("external_network", "medium", r"\b(https?://|websocket|ws://|wss://|fetch\(|requests\.|axios\.|curl\b|wget\b|openai|anthropic|xai|github api)"),
    ("filesystem_write", "medium", r"\b(write_file|fs\.writeFile|open\([^\n]+['\"]w['\"]|mkdir|touch\b|cp\s+|mv\s+|copy-item|set-content)\b"),
    ("container_or_vm", "medium", r"\b(docker\s+run|docker compose|podman|kubectl|kind\s+(create|delete|get|export|load|build)\b|vagrant)\b"),
    ("ports", "medium", r"\b(port\s*[:=]\s*(8000|9000|9224|9500)|localhost:(8000|9000|9224|9500)|listen\()"),
    ("browser_control", "medium", r"\b(playwright|puppeteer|selenium|chrome devtools|remote debugging|--remote-debugging-port)\b"),
    ("local_read", "low", r"\b(read_file|fs\.readFile|cat\s+|sqlite|markdown|README)\b"),
    ("dry_run_hint", "low", r"\b(dry[- ]?run|--check|--no-write|readonly|read-only|preview)\b"),
]

SEVERITY_SCORE = {"low": 1, "medium": 2, "high": 3}
PRIORITY_BY_SEVERITY = {"low": "note", "medium": "review", "high": "confirm"}
FAIL_ON_SCORE = {"never": 99, "review": 2, "confirm": 3, "medium": 2, "high": 3}

CHECK_HELP = {
    "destructive_delete": {
        "plain_language": "The text includes a delete/reset command that could remove data.",
        "why_it_matters": "Beginners and agents can run these commands in the wrong folder by accident.",
        "beginner_next_step": "Do not run it yet. Ask what folder or data it affects, and look for a dry-run or backup step.",
    },
    "global_install": {
        "plain_language": "The setup may install software globally or run a downloaded install script.",
        "why_it_matters": "Global installs and curl-pipe-shell commands can change your machine outside the project folder.",
        "beginner_next_step": "Prefer a temporary folder, virtual environment, or local install. Ask before using sudo, -g, or curl | sh.",
    },
    "secrets_or_auth": {
        "plain_language": "The text mentions tokens, passwords, API keys, OAuth, or .env files.",
        "why_it_matters": "Secrets can be leaked into logs, shell history, screenshots, commits, or agent context.",
        "beginner_next_step": "Use placeholder values while reading. Do not paste real secrets until you know where they are stored.",
    },
    "paid_or_billing": {
        "plain_language": "The text mentions billing, paid plans, credit cards, pricing, quotas, or credits.",
        "why_it_matters": "A tool may cost money or consume a paid API quota after setup.",
        "beginner_next_step": "Stop and confirm the cost path. Never subscribe or enter payment details through an agent.",
    },
    "daemon_or_cron": {
        "plain_language": "The setup may install or start a background service, daemon, cron job, or process manager.",
        "why_it_matters": "Background tasks can keep running after the terminal closes and may be hard for beginners to find later.",
        "beginner_next_step": "Ask how to stop, disable, and uninstall it before starting it.",
    },
    "config_mutation": {
        "plain_language": "The text may change agent, MCP, Claude, Hermes, or application configuration files.",
        "why_it_matters": "Config changes can affect future agent sessions and other projects, not just this trial.",
        "beginner_next_step": "Back up the config file first and ask what exact file will change.",
    },
    "remote_code_execution": {
        "plain_language": "The text contains code execution patterns such as eval, exec, subprocess, or shell execution.",
        "why_it_matters": "These patterns can run commands on your machine if used carelessly.",
        "beginner_next_step": "Inspect the surrounding code and avoid running it until you understand what command is executed.",
    },
    "external_network": {
        "plain_language": "The text mentions network calls or external web/API access.",
        "why_it_matters": "Network calls may send data outside your machine or depend on external services.",
        "beginner_next_step": "Check what data is sent and whether an offline/local mode exists.",
    },
    "filesystem_write": {
        "plain_language": "The text mentions writing, copying, moving, or creating files.",
        "why_it_matters": "File writes can overwrite work or modify files outside the intended project.",
        "beginner_next_step": "Confirm the target path and use a disposable test folder first.",
    },
    "container_or_vm": {
        "plain_language": "The text mentions Docker, Kubernetes, Vagrant, or similar isolated runtimes.",
        "why_it_matters": "Containers can still mount local folders, use ports, consume disk, and run background services.",
        "beginner_next_step": "Check volume mounts, ports, and cleanup commands before starting it.",
    },
    "ports": {
        "plain_language": "The text mentions local ports used by web apps, agents, or browser-control tools.",
        "why_it_matters": "Port conflicts can break other local tools or expose a local service unexpectedly.",
        "beginner_next_step": "Check whether the port is already used and whether the service binds only to localhost.",
    },
    "browser_control": {
        "plain_language": "The text mentions browser automation or remote browser control.",
        "why_it_matters": "Browser automation can interact with logged-in sessions or local browser data.",
        "beginner_next_step": "Use a separate browser profile and avoid pages with private accounts until you understand the tool.",
    },
    "local_read": {
        "plain_language": "The text mentions reading local files or databases.",
        "why_it_matters": "Reading is usually lower impact, but private files can still appear in logs or reports.",
        "beginner_next_step": "Check which files are read and avoid private folders for first trials.",
    },
    "dry_run_hint": {
        "plain_language": "The text mentions dry-run, preview, read-only, or no-write modes.",
        "why_it_matters": "These modes are often safer first steps when learning a tool.",
        "beginner_next_step": "Try the dry-run or preview mode before any command that changes files or settings.",
    },
}

SECRET_VALUE_PATTERNS = [
    re.compile(r"(?i)(bearer\s+)[^\s`'\"]+"),
    re.compile(
        r"""(?ix)
        (
          "? (?:api[\s_-]?key|client_secret|password|token|secret) "?
          \s*[:=]\s*
        )
        (?:"[^"]*"|'[^']*'|[^\s`'"]+)
        """
    ),
]


def redact_excerpt(text: str) -> str:
    redacted = text[:220]
    for pattern in SECRET_VALUE_PATTERNS:
        redacted = pattern.sub(lambda m: m.group(1) + "[REDACTED]", redacted)
    return redacted


def is_negated_review_match(line: str, match: re.Match[str]) -> bool:
    """Return true only when the matched term is explicitly described as unnecessary."""
    before = line[:match.start()]
    after = line[match.end():]
    clause_before = re.split(r"[.;:!?。！？]", before)[-1]
    if re.search(r"\b(?:no|without)\b", clause_before, re.IGNORECASE) and re.search(
        r"\b(?:required|needed|used|necessary)\b", after, re.IGNORECASE
    ):
        return True
    if re.match(r"\s+(?:is|are)?\s*(?:not|required\s+not)\s+(?:required|needed|used|necessary)\b", after, re.IGNORECASE):
        return True
    return bool(re.search(r"(?:不要|使わない|必要ありません|必要ない)", line))


def _is_excluded(path: Path, root: Optional[Path], patterns: list[str]) -> bool:
    if not patterns:
        return False
    candidates = [path.as_posix()]
    if root is not None:
        try:
            candidates.append(path.relative_to(root).as_posix())
        except ValueError:
            pass
    return any(fnmatch.fnmatch(candidate, pat) for candidate in candidates for pat in patterns)


@dataclass
class Finding:
    file: str
    line: int
    category: str
    severity: str
    priority: str
    excerpt: str
    plain_language: str
    why_it_matters: str
    beginner_next_step: str


def _iter_files(paths: list[Path], extensions: set[str], exclude_patterns: list[str], root: Optional[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if not _is_excluded(path, root, exclude_patterns):
                yield path
            continue
        for cur, dirs, files in os.walk(path):
            cur_path = Path(cur)
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not _is_excluded(cur_path / d, root, exclude_patterns)]
            for name in files:
                p = Path(cur) / name
                if _is_excluded(p, root, exclude_patterns):
                    continue
                suffix = p.suffix.lower()
                if suffix in extensions or name in {"Dockerfile", "Makefile", "README", "LICENSE"}:
                    yield p


def _read_text_for_scan(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        data = path.read_bytes()
        if b"\x00" in data:
            return None
        return data.decode("utf-8", errors="replace")
    except OSError:
        return None


def scan(paths: list[Path], root: Optional[Path] = None, exclude_patterns: Optional[list[str]] = None) -> dict:
    findings: list[Finding] = []
    scanned_files = 0
    skipped_files = 0
    compiled = [(cat, sev, re.compile(pattern, re.IGNORECASE)) for cat, sev, pattern in RISK_RULES]
    extensions = set(DEFAULT_EXTENSIONS)
    exclude_patterns = exclude_patterns or []

    for file_path in _iter_files(paths, extensions, exclude_patterns, root):
        text = _read_text_for_scan(file_path)
        if text is None:
            skipped_files += 1
            continue
        scanned_files += 1
        rel = str(file_path if root is None else file_path.relative_to(root) if file_path.is_relative_to(root) else file_path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            normalized = line.strip()
            if not normalized:
                continue
            for category, severity, regex in compiled:
                match = regex.search(normalized)
                if match:
                    if category in {"secrets_or_auth", "paid_or_billing", "daemon_or_cron"} and is_negated_review_match(normalized, match):
                        continue
                    help_text = CHECK_HELP.get(category, {
                        "plain_language": "This line matched a review check.",
                        "why_it_matters": "It may affect setup or future commands.",
                        "beginner_next_step": "Read the surrounding instructions before running anything.",
                    })
                    findings.append(Finding(
                        rel, line_no, category, severity,
                        PRIORITY_BY_SEVERITY[severity],
                        redact_excerpt(normalized),
                        help_text["plain_language"],
                        help_text["why_it_matters"],
                        help_text["beginner_next_step"],
                    ))

    max_severity = "low" if findings else "low"
    if findings:
        max_severity = max(findings, key=lambda f: SEVERITY_SCORE[f.severity]).severity
    confirm_categories = sorted({f.category for f in findings if f.severity == "high"})
    review_categories = sorted({f.category for f in findings if f.severity == "medium"})
    note_categories = sorted({f.category for f in findings if f.severity == "low"})
    decision = "no_review_items_found"
    headline = "No obvious review items found. Still read the instructions before running commands."
    next_actions = ["Read the README and install instructions before running commands."]
    if confirm_categories:
        decision = "confirm_before_running"
        headline = "Stop and ask before running commands from this project."
        next_actions = [
            "Do not install, paste tokens, edit config, or start services yet.",
            "Read the lines listed below and ask a human to confirm the next command.",
            "Try first in a disposable folder or isolated workspace if you decide to continue.",
        ]
    elif review_categories:
        decision = "review_before_trying"
        headline = "Review these items before trying the project."
        next_actions = [
            "Read the surrounding setup instructions.",
            "Prefer dry-run, preview, local-only, or disposable-workspace steps first.",
        ]

    review_items = [asdict(f) for f in findings]
    return {
        "tool": "agent-assist-preflight",
        "version": VERSION,
        "scanned_files": scanned_files,
        "skipped_files": skipped_files,
        "review_item_count": len(findings),
        "finding_count": len(findings),
        "max_priority": PRIORITY_BY_SEVERITY[max_severity],
        "max_severity": max_severity,
        "decision": decision,
        "beginner_summary": {"headline": headline, "next_actions": next_actions},
        "confirmation_categories": confirm_categories,
        "review_categories": review_categories,
        "note_categories": note_categories,
        "review_items": review_items,
        "findings": review_items,
        "human_approval_categories": confirm_categories,
        "limitations": [
            "read-only text-pattern helper; it does not prove a project is safe",
            "does not execute commands, install dependencies, or inspect runtime behavior",
            "false positives and false negatives are expected",
        ],
    }



# ---------------------------------------------------------------------------
# Basic Tool Checker — read-only environment discovery for beginners + agents
# ---------------------------------------------------------------------------

_TOOL_SPECS = [
    {
        "id": "python",
        "label": "Python",
        "commands": ["python3", "python"],
        "windows_commands": ["python", "py"],
        "version_args": ["--version"],
        "beginner": "Pythonは、AIツールや小さな自動化ツールを動かすためによく使われる道具です。",
        "agent": "Python作業は、エージェントが実際に動いている側（Windows/WSL）にあるPythonを使う必要があります。仮想環境があるかも確認してください。",
    },
    {
        "id": "node",
        "label": "Node.js",
        "commands": ["node"],
        "windows_commands": ["node"],
        "version_args": ["--version"],
        "beginner": "Node.jsは、JavaScript製の開発ツールやWebアプリを動かすためによく使われます。",
        "agent": "npm作業をするエージェントがWSL内で動いているなら、Windows側だけでなくWSL側のnodeも必要です。",
    },
    {
        "id": "npm",
        "label": "npm",
        "commands": ["npm"],
        "windows_commands": ["npm"],
        "version_args": ["--version"],
        "beginner": "npmは、Node.js用の部品を入れる道具です。知らない部品を入れる前に、何が入るか確認してください。",
        "agent": "npm install はファイル追加やネットワークアクセスを伴います。勝手に実行せず、ユーザー確認と作業フォルダ確認を先にしてください。",
    },
    {
        "id": "git",
        "label": "Git",
        "commands": ["git"],
        "windows_commands": ["git"],
        "version_args": ["--version"],
        "beginner": "Gitは、ファイルの変更履歴を記録する道具です。元に戻す・差分を見る・GitHubに置く時に使います。",
        "agent": "git操作は差分確認に便利ですが、commit/push/checkout/resetは状態を変えます。実行前に目的を説明してください。",
    },
    {
        "id": "gh",
        "label": "GitHub CLI",
        "commands": ["gh"],
        "windows_commands": ["gh"],
        "version_args": ["--version"],
        "beginner": "GitHub CLIは、ターミナルからGitHubを操作する道具です。ログインが必要なことがあります。",
        "agent": "gh はGitHubアカウントや認証状態に触れます。ログイン、repo作成、PR作成、pushはユーザー確認後にしてください。",
    },
    {
        "id": "powershell",
        "label": "PowerShell",
        "commands": ["powershell.exe", "pwsh", "powershell"],
        "windows_commands": ["powershell", "pwsh"],
        "version_args": ["--version"],
        "beginner": "PowerShellはWindowsの命令画面です。Windows側のポートやアプリ確認に使うことがあります。",
        "agent": "WSLからWindows側を調べる時はpowershell.exeが入口になります。設定変更や停止コマンドは確認なしで実行しないでください。",
    },
    {
        "id": "wsl",
        "label": "WSL",
        "commands": ["wsl.exe", "wsl"],
        "windows_commands": ["wsl"],
        "version_args": ["--version"],
        "beginner": "WSLはWindowsの中でLinuxを動かす仕組みです。Windows側とWSL側で入っている道具が違うことがあります。",
        "agent": "WSL内エージェントはWindowsにあるnode/npm/gitを直接使えない場合があります。どちら側で作業しているか明示してください。",
    },
    {
        "id": "docker",
        "label": "Docker",
        "commands": ["docker"],
        "windows_commands": ["docker"],
        "version_args": ["--version"],
        "beginner": "Dockerは小さな実験用の箱でソフトを動かす道具です。ただしフォルダ共有やポート公開が起きることがあります。",
        "agent": "docker run/compose はイメージ取得、ポート公開、volumeマウント、常駐を伴います。勝手に起動せず確認してください。",
    },
]


def _short_output(text: str, limit: int = 160) -> str:
    return " ".join((text or "").strip().split())[:limit]


def _run_version(command: str, args: list[str]) -> str:
    try:
        proc = subprocess.run([command, *args], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=5)
    except Exception:
        return ""
    return _short_output(proc.stdout or proc.stderr)


def _find_local_command(commands: list[str]) -> dict:
    for command in commands:
        path = shutil.which(command)
        if path:
            return {"present": True, "command": command, "path": path}
    return {"present": False, "command": commands[0] if commands else "", "path": ""}


def _windows_tool_snapshot() -> dict:
    if not shutil.which("powershell.exe"):
        return {"available": False, "tools": {}, "error": "powershell.exe not found from this runtime"}
    names = sorted({cmd for spec in _TOOL_SPECS for cmd in spec["windows_commands"]})
    ps_names = ",".join("'" + name.replace("'", "''") + "'" for name in names)
    script = (
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8;"
        f"$names=@({ps_names});"
        "foreach($name in $names){"
        "$cmd=Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1;"
        "if($cmd){ Write-Output ($name + '|' + $cmd.Source) }"
        "}"
    )
    try:
        proc = subprocess.run(["powershell.exe", "-NoProfile", "-Command", script], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=8)
    except Exception as exc:
        return {"available": False, "tools": {}, "error": str(exc)[:120]}
    tools = {}
    for line in (proc.stdout or "").splitlines():
        if "|" not in line:
            continue
        name, path = line.split("|", 1)
        tools[name.strip().lower()] = {"present": True, "command": name.strip(), "path": path.strip()}
    return {"available": True, "tools": tools, "error": _short_output(proc.stderr)}


def scan_basic_tools() -> dict:
    """Check common setup tools on current runtime and Windows side. Read-only."""
    windows = _windows_tool_snapshot()
    uname_release = ""
    if hasattr(os, "uname"):
        try:
            uname_release = os.uname().release.lower()
        except OSError:
            uname_release = ""
    running_side = "wsl" if "microsoft" in uname_release or shutil.which("wsl.exe") else "current"
    tools = []
    for spec in _TOOL_SPECS:
        local = _find_local_command(spec["commands"])
        if local["present"]:
            local["version"] = _run_version(local["command"], spec["version_args"])
        else:
            local["version"] = ""
        win_match = {"present": False, "command": spec["windows_commands"][0], "path": "", "version": ""}
        if windows.get("available"):
            for command in spec["windows_commands"]:
                found = windows.get("tools", {}).get(command.lower())
                if found:
                    win_match = {**found, "version": ""}
                    break
        # Avoid running many Windows tools just to get versions; path presence is enough for side check.
        agent_present = local["present"]
        if local["present"] and win_match["present"]:
            status = "both"
            status_ja = "Windows側にもWSL/エージェント側にもあります"
        elif local["present"]:
            status = "agent_only"
            status_ja = "エージェントが使う側にはあります"
        elif win_match["present"]:
            status = "windows_only"
            status_ja = "Windows側にはありますが、エージェント側では見つかりません"
        else:
            status = "missing"
            status_ja = "見つかりません"
        agent_note = spec["agent"]
        if status == "windows_only":
            agent_note += " Windows側だけにある状態なので、WSLで動くエージェントがこの道具を使う作業をすると失敗する可能性があります。勝手にインストールせず、まずユーザーに確認してください。"
        elif status == "missing":
            agent_note += " 見つからない場合は、インストール手順を提案するだけにして、実際のインストールはユーザー確認後にしてください。"
        tools.append({
            "id": spec["id"],
            "label": spec["label"],
            "status": status,
            "status_ja": status_ja,
            "present": local["present"] or win_match["present"],
            "current_side": local,
            "windows_side": win_match,
            "agent_can_use": agent_present,
            "run_command": local["command"] if local["present"] else spec["commands"][0],
            "beginner_explanation": spec["beginner"],
            "agent_caution": agent_note,
        })
    missing_for_agent = [t["label"] for t in tools if not t["agent_can_use"]]
    windows_only = [t["label"] for t in tools if t["status"] == "windows_only"]
    lines = ["基本道具を読み取り専用で確認しました。"]
    if windows_only:
        lines.append("Windows側だけで見つかった道具があります: " + ", ".join(windows_only))
    if missing_for_agent:
        lines.append("エージェント側で見つからない道具があります: " + ", ".join(missing_for_agent))
    lines.append("不足があっても、この画面はインストールや設定変更を行いません。")
    return {
        "ok": True,
        "running_side": running_side,
        "windows_probe_available": bool(windows.get("available")),
        "windows_probe_error": windows.get("error", ""),
        "tools": tools,
        "summary": "\n".join(lines),
    }

# ═══════════════════════════════════════════════════════════════════════════════
# Port Conflict Checker — read-only port ownership listing
# ---------------------------------------------------------------------------

_PORT_DESCRIPTIONS = {
    1234: "ローカルLLMサーバー系で使われることがある（LM Studioなど）",
    3000: "開発サーバー系で使われることがある（Node.js、React、Next.jsなど）",
    3001: "開発サーバーの代替ポートで使われることがある",
    5000: "開発サーバー系で使われることがある（Flask、Expressなど）",
    5173: "Vite（開発サーバー）で使われることがある",
    50021: "VOICEVOX系で使われることがある",
    50022: "VOICEVOXの代替ポート",
    7860: "Stable Diffusion WebUI / Gradioで使われることがある",
    8000: "開発サーバー系で使われることがある",
    8060: "Godot Editorで使われることがある",
    8080: "開発サーバー系で使われることがある",
    8088: "llama.cpp / LM Studioで使われることがある",
    8089: "llama.cppの代替ポート",
    8188: "ComfyUIで使われることがある",
    8189: "ComfyUIの代替ポート",
    8642: "Hermes Desktopで使われることがある",
    8765: "Agent Assist Preflight WebUI（このツール自身）",
    9000: "ComfyUIやその他ツールで使われることがある",
    9222: "Chrome DevTools Protocol（ブラウザ自動操作）で使われることがある",
    9224: "Chrome DevTools Protocolの代替ポート",
    9500: "Godot AI MCPで使われることがある",
    11434: "Ollama（ローカルLLM）で使われることがある",
}


def scan_port_owners() -> dict:
    """List all listening ports with process info. Read-only, no connections."""
    if not shutil.which("powershell.exe"):
        return {"ok": False, "error": "Windows PowerShellが必要です", "ports": []}

    # Get listening connections with process info
    script = (
        "Get-NetTCPConnection -State Listen | "
        "Select-Object LocalAddress, LocalPort, OwningProcess | "
        "Sort-Object LocalPort | "
        "ForEach-Object { "
        "$proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; "
        "Write-Output ($_.LocalAddress + '|' + $_.LocalPort + '|' + $_.OwningProcess + '|' + "
        "($proc.ProcessName -replace '\\|','') + '|' + ($proc.Path -replace '\\|','')) }"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command", script],
            check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=10,
        )
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:100], "ports": []}

    ports = []
    seen = set()
    for line in (proc.stdout or "").strip().splitlines():
        parts = line.strip().split("|")
        if len(parts) < 4:
            continue
        addr = parts[0]
        try:
            port_num = int(parts[1])
        except ValueError:
            continue
        pid = parts[2]
        proc_name = parts[3] or "不明"
        exe_path = parts[4] if len(parts) > 4 else ""

        key = (addr, port_num)
        if key in seen:
            continue
        seen.add(key)

        # Determine visibility
        if addr in ("127.0.0.1", "::1", "[::1]"):
            visibility = "local"
            visibility_ja = "自分だけ"
        elif addr in ("0.0.0.0", "::", "[::]"):
            visibility = "all"
            visibility_ja = "外から見える可能性"
        else:
            visibility = "specific"
            visibility_ja = f"特定のアドレス（{addr}）"

        # Beginner description
        desc = _PORT_DESCRIPTIONS.get(port_num, "")
        is_known = bool(desc)
        if not desc:
            desc = "見慣れない待ち受け — 何のソフトか確認してみてください"
        is_self = port_num == 8765

        ports.append({
            "address": addr,
            "port": port_num,
            "pid": pid,
            "process_name": proc_name,
            "exe_path": exe_path,
            "visibility": visibility,
            "visibility_ja": visibility_ja,
            "description": desc,
            "is_known": is_known,
            "is_self": is_self,
        })

    # Generate summary
    local_count = sum(1 for p in ports if p["visibility"] == "local")
    all_count = sum(1 for p in ports if p["visibility"] == "all")
    summary_lines = [f"{len(ports)}個のポートがLISTEN中です。"]
    if all_count > 0:
        summary_lines.append(f"⚠️ {all_count}個は外から見える可能性があります（0.0.0.0）。")
    summary_lines.append("ポートを止めるときは、まずそのソフトを通常方法で終了してください。")

    return {
        "ok": True,
        "ports": ports,
        "total": len(ports),
        "local_count": local_count,
        "external_count": all_count,
        "summary": "\n".join(summary_lines),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Glossary (70+ terms)
# ═══════════════════════════════════════════════════════════════════════════════

GLOSSARY = {
    "sudo": "パソコンの管理者権限で命令を実行すること。ふだんは安全のため制限されている操作も、sudoをつけると実行できてしまうので注意。",
    "apt": "インターネットからソフトを探してきて、自動でインストールしてくれる道具。スマホの「App Store」の文字だけバージョン。",
    "brew": "主にMacで使われる、ソフトの自動インストール道具。Homebrewとも呼ばれる。",
    "pip": "Pythonで使う部品を、ネットから取ってきて追加する道具。便利だが、知らない部品を入れると危険なコードが混ざることもある。",
    "npm": "Node.jsで使う部品を、ネットから取ってきて追加する道具。便利だが、知らない部品を入れると危険なコードが混ざることもある。",
    "curl": "インターネット上のURLにアクセスする命令。ファイルをダウンロードしたり、Webサービスにデータを送ったりできる。確認ウインドウが出た時に中身を確認せず実行する使い方は危険。",
    "wget": "インターネットからファイルをダウンロードする命令。curlと似ているが、wgetはダウンロードだけに特化している。",
    "eval": "文字列をプログラムとして実行する命令。便利な場面もあるが、悪意のある文字列を渡されると危険な命令まで実行されることがある。初心者は基本的に避けた方がいい。",
    "exec": "別のプログラムや命令を呼び出して実行する仕組み。便利だが、外から受け取った文字をそのまま実行すると、危険な命令まで動いてしまうことがある。",
    "subprocess": "パソコンの中で、別のプログラムを新しく動かす仕組み。何を動かすか次第で危険にもなる。",
    "shell": "ターミナルに入力された命令を受け取って、実際にパソコンへ伝えるプログラム。bash、zsh、PowerShellなどがある。",
    "chmod": "ファイルにつける「鍵」の設定を変える命令。「見るだけ」「編集できる」「実行できる」の3つの鍵を、自分・仲間・他人それぞれに配れる。",
    "chown": "ファイルの「持ち主」を変える命令。「このファイルはAさんのものだけど、Bさんのものにする」みたいに変更できる。",
    "rm": "ファイルを削除する。ゴミ箱には入らず、復元が難しい。",
    "mv": "ファイルを移動・リネームする。",
    "cp": "ファイルを複製する。",
    "crontab": "「毎日朝7時に自動でバックアップをとる」みたいに、決まった時間に決まった命令を自動実行するタイマー機能。",
    "systemd": "Linuxの中で、裏方でずっと動いているプログラムの電源を入れたり切ったりする管理人。",
    "daemon": "パソコンの裏側で、必要なときに備えて待ち続けるプログラム。",
    "OAuth": "「Googleでログイン」のように、別のサービスのアカウントを使ってログインしたり、必要な権限だけを許可したりする仕組み。便利だが、怪しいアプリに許可を出すと、許可した範囲の情報を使われることがある。",
    "APIキー": "ネット上のサービスを使うための「秘密の合言葉」。これを知られると、あなたの利用枠や料金で勝手に使われることがある。",
    "認証トークン": "ログイン済みであることを証明するデジタルな鍵。APIキーと同じく、他人に見せたりチャットに貼ったりすると悪用されることがある。",
    "AIのトークン": "AIが文章を読むときの細かい単位。日本語では1文字や短い単語のかけらのように分かれることがある。AIの料金や処理量は、このトークン数で決まることが多い。",
    ".env": "パスワード、APIキー、設定値などを入れておくことが多い設定ファイル。便利だけど、秘密情報が入ることがあるので、他人に送ったりネットに公開したりしない。",
    "quota": "ネットのサービスを使える回数や量の上限。たとえば「1か月に1000回まで」のような制限。超えると一時的に使えなくなったり、追加料金が必要になったりする。",
    "credits": "ネットのサービスを使うための「チケット」や「コイン」。使うたびに減っていく。ゼロになると使えなくなったり、追加購入が必要になったりする。",
    "docker": "パソコンの中に「小さな実験用の箱」を作って、その中でソフトを動かす仕組み。箱の中に分けられるので本体を汚しにくい。ただし、設定によってはパソコン本体のファイルにも触れるので注意。",
    "kubernetes": "たくさんのDockerの箱を、まとめて自動で管理する仕組み。「箱が壊れたら新しいのを自動で用意する」みたいなことをしてくれる。",
    "localhost": "自分自身のパソコンのこと。インターネットには出ていかず、自分のパソコンの中だけで完結している。",
    "CDP": "Chromeブラウザを、プログラムから遠隔操作するための通り道。ボタンを自動で押させたり、画面の中身を読み取ったりできる。",
    "Playwright": "Webブラウザ（Chromeなど）をプログラムで自動操作する道具。ボタンを自動で押したり、画面に文字が表示されているか確認したりできる。",
    "MCP": "AIアプリやAIエージェントが、外部ツールとやり取りするための共通ルール。たとえば、AIがファイルを読んだり、カレンダーを確認したり、別のソフトを操作したりする入口になる。ただし、使える機能や安全性はMCPサーバーごとの設定による。",
    "MCPサーバー": "AIに機能を貸し出す側のプログラム。たとえば「ファイルを読む」「ブラウザを操作する」「VOICEVOXを使う」などの機能を、AIから呼び出せるようにする。",
    "MCPクライアント": "MCPサーバーに接続して機能を使う側のアプリ。AIエージェントや開発ツールがこれにあたる。",
    "MCP対応": "そのソフトやツールが、MCP経由でAIから使える可能性があるという意味。ただし、対応しているだけで自動的に安全に接続されるわけではない。",
    "dry-run": "実際には変更せず、何が起きるかを表示だけする試運転モード。",
    "venv": "Pythonの「実験用の部屋」。プロジェクトごとに別の部屋を作って、それぞれに別の部品を入れられる。部屋を分ければ、部品同士がケンカしない。",
    "volume": "Dockerの箱と、自分のパソコンのフォルダをつなぐ「窓」。窓を通して、箱の中からパソコンのファイルを読んだり書いたりできる。",
    "port": "パソコンの中にある「通信用のドア」。番号がついていて、ドアごとに違う仕事（Webを見る、メールを送るなど）を担当する。",
    "常駐": "ふつう、黒い画面（ターミナル）を閉じると、その画面で動かしていたプログラムも一緒に終わる。でも「常駐」は、画面を閉じても裏で動き続ける。",
    "バックグラウンド": "画面には表示されず、裏で動き続けること。",
    "CLI": "文字を打ってソフトやパソコンを操作する方式。ボタンをクリックする代わりに、命令文を入力して動かす。",
    "GUI": "ボタンやウィンドウで操作する、いつもの見た目の方式。マウスでクリックするやり方。",
    "OSS": "設計図が公開されているソフト。誰でも中身を見たり、改造したりできる。無料で使えるものが多い。",
    "README": "プロジェクトフォルダの一番上にある説明書。最初に読むべきファイル。",
    "MITライセンス": "ソフトの使い方を決めるライセンスのひとつ。かなり自由度が高く、条件を守れば、使う・改造する・配布する・販売することができる。",
    "リポジトリ": "ソースコードや変更履歴をまとめて管理する場所。GitHub上にあることも多いが、自分のパソコンの中にもリポジトリは作れる。",
    "commit": "Gitでファイルの変更を「この状態で保存」と記録すること。",
    "push": "Gitで、手元のcommitをGitHubにアップロードすること。",
    "clone": "Gitで、サーバー上のプロジェクトを手元にコピーすること。",
    "PR": "Pull Request。GitHubで「この修正を取り込んでほしい」と提案すること。",
    "issue": "GitHubなどで、不具合・要望・作業メモを記録するための相談チケット。",
    "CI": "プログラムを変更するたびに、自動で「ちゃんと動くかな？」と確認してくれる仕組み。壊れてたらすぐ教えてくれるので安心。",
    "バイブコーディング": "AIに「こういうの作って」と言ってコードを生成してもらう開発スタイル。",
    "WSL": "Windowsパソコンの中でLinuxを動かせるようにする仕組み。わざわざ別のパソコンを用意しなくても、Windowsの中にLinuxの世界を作れる。",
    "パス": "ファイルやフォルダの住所。C:\\Users\\... や /home/... のような文字列。",
    "ターミナル": "CLIを使うための画面。黒い画面に文字を打つタイプのアプリ。",
    "エージェント": "自分で考えて、自分で動くAIプログラム。たとえば「カレンダーを見て、空いてる日を教えて」と頼むと、自分でカレンダーを開いて調べてくれる。",
    "Git": "ファイルの変更履歴を記録する道具。「いつ、何を変えたか」を残せるので、前の状態に戻したり、複数人で作業したりしやすくなる。",
    "GitHub": "Gitで管理しているプロジェクトをネット上に置けるサービス。コード置き場、作業メモ、公開ページとしてよく使われる。",
    "branch": "Gitで作業を分けるための枝。安全に別案を試したり、修正作業を本体と分けたりできる。",
    "merge": "分けて作業していた変更を、元の流れに合体させること。",
    "fork": "他人のリポジトリを、自分用にコピーして改造できるようにすること。",
    "dependency": "そのソフトが動くために必要な別の部品。依存関係が足りないと、インストールや起動で失敗することがある。",
    "package": "ソフトや部品をひとまとめにしたもの。npmやpipで入れる部品もパッケージと呼ばれる。",
    "PATH": "パソコンが命令を探しに行く場所のリスト。PATHに登録されていないと、インストール済みのソフトでも「見つからない」と言われることがある。",
    "環境変数": "パソコンやプログラムに渡す設定値。APIキーや実行モードなどを入れることが多い。.envファイルに書かれることもある。",
    "JSON": "データを { \"name\": \"Taro\" } のような形で書く形式。APIや設定ファイルでよく使われる。",
    "YAML": "設定ファイルでよく使われる書き方。見た目は読みやすいが、空白の数がズレると壊れやすい。",
    "log": "プログラムが何をしたかを記録したメモ。エラーの原因を探すときにとても役立つ。",
    "error": "プログラムがうまく動かなかったという知らせ。怖いものではなく、「どこで困っているか」を教えてくれるヒント。",
    "warning": "すぐ止まるほどではないが、注意した方がいいという知らせ。",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Server utilities
# ═══════════════════════════════════════════════════════════════════════════════

def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _read_comments() -> list[dict]:
    if not COMMENTS_PATH.exists():
        _write_json(COMMENTS_PATH, [])
    try:
        data = json.loads(COMMENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def _next_comment_id(comments: list[dict]) -> str:
    nums = []
    for item in comments:
        cid = str(item.get("id", ""))
        if cid.startswith("c") and cid[1:].isdigit():
            nums.append(int(cid[1:]))
    return f"c{(max(nums) if nums else 0) + 1:04d}"


def _run_preflight(target: Path) -> dict:
    """Run the preflight checker in-process (no subprocess needed)."""
    try:
        report = scan([target], target if target.is_dir() else None)
        return {"ok": True, "returncode": 0, "target": str(target), "report": report}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "target": str(target)}


def _run_preflight_for_text(filename: str, content: str) -> dict:
    if len(content.encode("utf-8", errors="replace")) > 1_000_000:
        return {"ok": False, "error": "text file is too large for this simple trial view (limit: 1MB)"}
    safe_name = Path(filename or "dropped-text.txt").name
    safe_name = re.sub(r"[^A-Za-z0-9._ -]", "_", safe_name).strip(" .") or "dropped-text.txt"
    if Path(safe_name).suffix.lower() not in {".txt", ".md", ".markdown", ".rst", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".sh"}:
        safe_name += ".txt"
    with tempfile.TemporaryDirectory(prefix="agent-assist-drop-") as tmp:
        target = Path(tmp) / safe_name
        target.write_text(content, encoding="utf-8", errors="replace")
        result = _run_preflight(target)
        result["source"] = "dropped_text_file"
        result["display_name"] = safe_name
        return result


def _windows_path_to_wsl(path_text: str) -> str:
    text = path_text.strip()
    if re.match(r"^[A-Za-z]:\\", text) and shutil.which("wslpath"):
        proc = subprocess.run(["wslpath", "-u", text], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=5)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return text


def _pick_folder_dialog() -> dict:
    try:
        if shutil.which("powershell.exe"):
            script = r'''
Add-Type -AssemblyName System.Windows.Forms
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$dialog = New-Object System.Windows.Forms.OpenFileDialog
$dialog.Title = 'Agent Assist Preflightで確認するフォルダまたはテキストファイルを選んでください'
$dialog.Filter = 'すべてのファイル (*.*)|*.*'
$dialog.CheckFileExists = $false
$dialog.CheckPathExists = $true
$dialog.ValidateNames = $false
$dialog.FileName = 'このフォルダを選択'
if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) {
  $selected = $dialog.FileName
  if ([System.IO.Path]::GetFileName($selected) -eq 'このフォルダを選択') {
    Write-Output ([System.IO.Path]::GetDirectoryName($selected))
  } else {
    Write-Output $selected
  }
}
'''
            proc = subprocess.run(
                ["powershell.exe", "-NoProfile", "-STA", "-Command", script],
                check=False, text=True, encoding="utf-8", errors="replace", capture_output=True,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                raw = proc.stdout.strip().splitlines()[-1]
                selected = _windows_path_to_wsl(raw)
                return {"ok": True, "path": selected, "raw_path": raw, "dialog": "open-file-dialog"}
            return {"ok": False, "cancelled": True, "error": proc.stderr.strip() or "path selection was cancelled"}
        script = "import tkinter as tk; from tkinter import filedialog; root=tk.Tk(); root.withdraw(); print(filedialog.askopenfilename() or filedialog.askdirectory())"
        proc = subprocess.run(["python3", "-c", script], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return {"ok": True, "path": proc.stdout.strip(), "dialog": "tk"}
        return {"ok": False, "cancelled": True, "error": proc.stderr.strip() or "path selection was cancelled"}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP Handler
# ═══════════════════════════════════════════════════════════════════════════════

class Handler(BaseHTTPRequestHandler):
    server_version = "AgentAssistPreflightStandalone/0.1"

    def log_message(self, format: str, *args: object) -> None:
        # Suppress noisy request logs in the beginner console
        pass

    def _send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            self._send_json({
                "project": "Agent Assist Preflight (Standalone)",
                "root": str(SCRIPT_DIR),
                "docs": [],
                "comments": _read_comments(),
            })
            return
        if parsed.path == "/api/doc":
            self._send_json({"id": "readme-ja", "path": "", "content": "standalone モードでは外部ドキュメントは不要です。"})
            return
        if parsed.path == "/api/sample-report":
            fixture = SCRIPT_DIR / "tests" / "fixtures" / "danger"
            if fixture.exists():
                self._send_json(_run_preflight(fixture))
            else:
                self._send_json({"ok": False, "error": "sample fixture not found"})
            return
        if parsed.path == "/api/pick-folder":
            self._send_json(_pick_folder_dialog())
            return
        if parsed.path == "/api/glossary":
            self._send_json(GLOSSARY)
            return
        if parsed.path == "/api/port-owners":
            self._send_json(scan_port_owners())
            return
        if parsed.path == "/api/tool-basics":
            self._send_json(scan_basic_tools())
            return
        self._serve_static(parsed.path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        try:
            payload = self._read_body_json()
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        if parsed.path == "/api/scan":
            raw_target = str(payload.get("target_path", "")).strip()
            if not raw_target:
                self._send_json({"ok": False, "error": "target_path is required"}, status=400)
                return
            target = Path(raw_target).expanduser()
            if not target.is_absolute():
                target = (SCRIPT_DIR / target).resolve()
            if not target.exists():
                self._send_json({"ok": False, "error": "path does not exist", "target": str(target)}, status=404)
                return
            self._send_json(_run_preflight(target))
            return
        if parsed.path == "/api/scan-text":
            filename = str(payload.get("filename", "dropped-text.txt"))
            content = payload.get("content", "")
            if not isinstance(content, str) or not content.strip():
                self._send_json({"ok": False, "error": "text file content is required"}, status=400)
                return
            self._send_json(_run_preflight_for_text(filename, content))
            return
        if parsed.path == "/api/comments":
            text = str(payload.get("text", "")).strip()
            if not text:
                self._send_json({"error": "text is required"}, status=400)
                return
            comments = _read_comments()
            now = utc_now()
            item = {
                "id": _next_comment_id(comments),
                "created_at": now,
                "updated_at": now,
                "section": str(payload.get("section", "未指定")).strip() or "未指定",
                "priority": str(payload.get("priority", "review")),
                "status": "open",
                "text": text,
                "beginner_reaction": str(payload.get("beginner_reaction", "")).strip(),
                "owner_note": "",
            }
            comments.insert(0, item)
            _write_json(COMMENTS_PATH, comments)
            self._send_json({"ok": True, "comment": item, "comments": comments}, status=201)
            return
        if parsed.path.startswith("/api/comments/"):
            cid = parsed.path.rsplit("/", 1)[-1]
            comments = _read_comments()
            for item in comments:
                if item.get("id") == cid:
                    if "status" in payload:
                        item["status"] = str(payload["status"])
                    if "owner_note" in payload:
                        item["owner_note"] = str(payload["owner_note"])
                    item["updated_at"] = utc_now()
                    _write_json(COMMENTS_PATH, comments)
                    self._send_json({"ok": True, "comment": item, "comments": comments})
                    return
            self._send_json({"error": "comment not found"}, status=404)
            return
        self._send_json({"error": "not found"}, status=404)

    def _serve_static(self, path: str) -> None:
        if path in ("", "/"):
            target = STATIC_ROOT / "index.html"
        else:
            rel = Path(path.lstrip("/"))
            target = (STATIC_ROOT / rel).resolve()
            if not str(target).startswith(str(STATIC_ROOT.resolve()) + os.sep):
                self.send_response(403)
                self.end_headers()
                return
        if not target.exists() or not target.is_file():
            self.send_response(404)
            self.end_headers()
            return
        body = target.read_bytes()
        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        if target.suffix in {".html", ".css", ".js"}:
            content_type += "; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


# ═══════════════════════════════════════════════════════════════════════════════
# Main entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    # Force UTF-8 stdout/stderr for Windows cp932 consoles
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    host = "127.0.0.1"
    port = 8765

    # Check that static files exist
    index_html = STATIC_ROOT / "index.html"
    if not index_html.exists():
        print("=" * 60)
        print("  ❌ エラー: WebUIのファイルが見つかりませんでした。")
        print()
        print(f"  期待するパス: {STATIC_ROOT}")
        print()
        print("  このファイル (standalone.py) の近くに")
        print("  management_webui/static/ フォルダが必要です。")
        print("=" * 60)
        sys.exit(1)

    # Ensure data directory exists
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if not COMMENTS_PATH.exists():
        _write_json(COMMENTS_PATH, [])

    # Start server
    httpd = ThreadingHTTPServer((host, port), Handler)

    # Print startup banner
    root_path = str(SCRIPT_DIR)
    print("=" * 60)
    print("  🌱 バイブコーディング初心者支援ツール を起動しました！")
    print()
    print("  👉 ブラウザが自動で開きます。開かない場合は下のURLをコピー：")
    print(f"     http://{host}:{port}/")
    print()
    print(f"  📁 このツールのフォルダ：")
    print(f"     {root_path}")
    print()
    print("  この画面を閉じるとツールも終了します。")
    print("  終了するときは Ctrl+C を押してください。")
    print("=" * 60)

    # Open browser after a short delay
    def _open_browser():
        time.sleep(0.8)
        webbrowser.open(f"http://{host}:{port}/")

    threading.Thread(target=_open_browser, daemon=True).start()

    # Serve until Ctrl+C
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  👋 ツールを終了しました。また使ってください！")
        httpd.server_close()


if __name__ == "__main__":
    main()
