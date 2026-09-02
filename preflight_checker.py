#!/usr/bin/env python3
"""Read-only preflight assistant for agent/tool setup notes.

This helper reads README/config-style text before a human or AI agent runs
commands from a new project. It produces plain-language review notes and
beginner next steps. It is not a sandbox and never executes candidate commands.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Optional

VERSION = "0.2.3"
DEFAULT_EXTENSIONS = {
    ".md", ".txt", ".json", ".jsonl", ".yaml", ".yml", ".toml",
    ".ini", ".env.example", ".sh", ".bash", ".ps1", ".py", ".js", ".ts",
    ".mjs", ".cjs", ".dockerfile", "", ".lock"
}
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next"}
MAX_FILE_BYTES = 512_000

# Extension note for vibe-coding/new contributors:
# Keep this file easy to modify, but do not add a new review category unless you
# can explain it to a beginner. For any check that can trigger a pause, update
# CHECK_HELP with: what this means, why it matters, and beginner next step.
# If a future change would execute commands, install packages, alter configs, or
# send network requests, stop and require explicit user confirmation first.
RISK_RULES = [
    # High: must ask before acting.
    ("destructive_delete", "high", r"\b(rm\s+-rf|del\s+/[fsq]|remove-item\s+.*-recurse|shutil\.rmtree|delete\s+all|drop\s+database|drop\s+table)\b"),
    ("global_install", "high", r"\b(sudo\s+)?(npm|pnpm|yarn|pip|pipx|cargo|brew|apt|apt-get)\s+(install|add)\b|\bcurl\s+[^\n|]+\|\s*(sh|bash)\b"),
    ("secrets_or_auth", "high", r"\b(api[\s_-]?key|secret|token|oauth|client_secret|password|bearer\s+[^\s]+|\.env\b)"),
    ("paid_or_billing", "high", r"\b(billing|paid|subscription|credit card|stripe|pricing|usage-based|quota|credits?)\b"),
    ("daemon_or_cron", "high", r"\b(systemctl|launchctl|crontab|cron|daemon|service\s+install|pm2\s+start|forever\s+start)\b"),
    ("config_mutation", "high", r"\b(hermes\s+config\s+set|mcpServers|claude_desktop_config|settings\.json|config\.yaml|write\s+to\s+.*config)\b"),
    ("remote_code_execution", "high", r"\b(eval\(|exec\(|child_process|subprocess\.(run|popen|call)|os\.system|powershell\s+-enc)\b"),
    # Medium: inspect before trying.
    ("external_network", "medium", r"\b(https?://|websocket|ws://|wss://|fetch\(|requests\.|axios\.|curl\b|wget\b|openai|anthropic|xai|github api)"),
    ("filesystem_write", "medium", r"\b(write_file|fs\.writeFile|open\([^\n]+['\"]w['\"]|mkdir|touch\b|cp\s+|mv\s+|copy-item|set-content)\b"),
    ("container_or_vm", "medium", r"\b(docker\s+run|docker compose|podman|kubectl|kind\s+(create|delete|get|export|load|build)\b|vagrant)\b"),
    ("ports", "medium", r"\b(port\s*[:=]\s*(8000|9000|9224|9500)|localhost:(8000|9000|9224|9500)|listen\()"),
    ("browser_control", "medium", r"\b(playwright|puppeteer|selenium|chrome devtools|remote debugging|--remote-debugging-port)\b"),
    # Low: often fine, but useful context.
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
    """Redact likely secret values before placing text in reports."""
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


def is_excluded(path: Path, root: Optional[Path], patterns: list[str]) -> bool:
    if not patterns:
        return False
    candidates = [path.as_posix()]
    if root is not None:
        try:
            candidates.append(path.relative_to(root).as_posix())
        except ValueError:
            pass
    return any(fnmatch.fnmatch(candidate, pattern) for candidate in candidates for pattern in patterns)

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


def iter_files(paths: list[Path], extensions: set[str], exclude_patterns: list[str], root: Optional[Path]) -> Iterable[Path]:
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if not is_excluded(path, root, exclude_patterns):
                yield path
            continue
        for cur, dirs, files in os.walk(path):
            cur_path = Path(cur)
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not is_excluded(cur_path / d, root, exclude_patterns)]
            for name in files:
                p = Path(cur) / name
                if is_excluded(p, root, exclude_patterns):
                    continue
                suffix = p.suffix.lower()
                if suffix in extensions or name in {"Dockerfile", "Makefile", "README", "LICENSE"}:
                    yield p


def read_text(path: Path) -> Optional[str]:
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

    for file_path in iter_files(paths, extensions, exclude_patterns, root):
        text = read_text(file_path)
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
                    # Avoid the most common false positive in docs: "no token required".
                    # This does not prove safety; it only prevents negative wording from
                    # being treated as a hard approval gate.
                    if category in {"secrets_or_auth", "paid_or_billing", "daemon_or_cron"} and is_negated_review_match(normalized, match):
                        continue
                    help_text = CHECK_HELP.get(category, {
                        "plain_language": "This line matched a review check.",
                        "why_it_matters": "It may affect setup or future commands.",
                        "beginner_next_step": "Read the surrounding instructions before running anything.",
                    })
                    findings.append(Finding(
                        rel,
                        line_no,
                        category,
                        severity,
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
        "finding_count": len(findings),  # compatibility for older CI/scripts
        "max_priority": PRIORITY_BY_SEVERITY[max_severity],
        "max_severity": max_severity,  # compatibility for older CI/scripts
        "decision": decision,
        "beginner_summary": {
            "headline": headline,
            "next_actions": next_actions,
        },
        "confirmation_categories": confirm_categories,
        "review_categories": review_categories,
        "note_categories": note_categories,
        "review_items": review_items,
        "findings": review_items,  # compatibility for older CI/scripts
        "human_approval_categories": confirm_categories,  # compatibility for older CI/scripts
        "limitations": [
            "read-only text-pattern helper; it does not prove a project is safe",
            "does not execute commands, install dependencies, or inspect runtime behavior",
            "false positives and false negatives are expected",
        ],
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Agent Assist Preflight Notes",
        "",
        "This is not a security scanner and does not decide whether a project is safe.",
        "It is a read-only helper that turns setup text into review notes before you run commands.",
        "",
        f"- tool: {report['tool']} {report['version']}",
        f"- scanned_files: {report['scanned_files']}",
        f"- skipped_files: {report['skipped_files']}",
        f"- review_item_count: {report['review_item_count']}",
        f"- max_priority: {report['max_priority']}",
        f"- decision: {report['decision']}",
        "",
        "## Plain-language summary",
        "",
        report["beginner_summary"]["headline"],
        "",
        "### Suggested next steps",
        "",
    ]
    for action in report["beginner_summary"]["next_actions"]:
        lines.append(f"- {action}")
    lines.append("")

    if report["confirmation_categories"]:
        lines.append("## Confirm before running")
        lines.append("")
        for cat in report["confirmation_categories"]:
            lines.append(f"- {cat}")
        lines.append("")
    if report["review_categories"]:
        lines.append("## Review before trying")
        lines.append("")
        for cat in report["review_categories"]:
            lines.append(f"- {cat}")
        lines.append("")

    lines.append("## What the review items mean")
    lines.append("")
    if not report["review_items"]:
        lines.append("No obvious review items found. This is not a guarantee; read the instructions before running commands.")
    else:
        for idx, item in enumerate(report["review_items"], start=1):
            excerpt = item["excerpt"].replace("`", "'")
            lines.extend([
                f"### {idx}. {item['category']} ({item['priority']})",
                "",
                f"- Location: `{item['file']}:{item['line']}`",
                f"- Matched text: `{excerpt}`",
                f"- What this means: {item['plain_language']}",
                f"- Why it matters: {item['why_it_matters']}",
                f"- Beginner next step: {item['beginner_next_step']}",
                "",
            ])

    lines.append("## Limitations")
    lines.append("")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only preflight assistant for README/config setup notes.")
    parser.add_argument("--version", action="version", version=f"agent-assist-preflight {VERSION}")
    parser.add_argument("paths", nargs="+", help="Files or directories to scan")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", help="Optional output file. Parent directory must already be writable by the user.")
    parser.add_argument("--exclude", action="append", default=[], help="Glob pattern to exclude. Can be repeated, e.g. --exclude 'tests/fixtures/danger/**'.")
    parser.add_argument("--fail-on", choices=["never", "review", "confirm", "medium", "high"], default="never", help="Exit non-zero if max priority reaches this level. medium/high are kept as compatibility aliases.")
    args = parser.parse_args(argv)

    input_paths = [Path(p).resolve() for p in args.paths]
    common_root = input_paths[0] if len(input_paths) == 1 and input_paths[0].is_dir() else None
    report = scan(input_paths, common_root, args.exclude)
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n" if args.format == "json" else render_markdown(report)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stdout.write(output)

    threshold = args.fail_on
    if threshold != "never" and SEVERITY_SCORE[report["max_severity"]] >= FAIL_ON_SCORE[threshold] and report["review_item_count"]:
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
