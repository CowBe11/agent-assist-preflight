#!/usr/bin/env python3
"""Local-only management WebUI for Agent Assist Preflight.

This server intentionally uses only Python stdlib. It binds to 127.0.0.1,
serves a static review dashboard, and stores beginner review comments in a
local JSON file. It does not execute project commands.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import mimetypes
import os
import re
import shutil
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = Path(__file__).resolve().parent
STATIC_ROOT = WEB_ROOT / "static"
DATA_ROOT = WEB_ROOT / "data"
COMMENTS_PATH = DATA_ROOT / "review_comments.json"
URL_CARDS_PATH = DATA_ROOT / "url_cards.json"
COMMAND_CARDS_PATH = DATA_ROOT / "command_cards.json"
CANDIDATES_PATH = DATA_ROOT / "glossary_candidates.json"

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


GLOSSARY_EN = {
    "sudo": "Running a command with administrator privileges. Normally restricted operations can be executed with sudo, so be careful.",
    "apt": "A tool that searches for and automatically installs software from the internet. Like a text-only App Store.",
    "brew": "An automatic software installer mainly used on Mac. Also called Homebrew.",
    "pip": "A tool that fetches and adds Python components from the internet. Convenient, but unknown packages may contain dangerous code.",
    "npm": "A tool that fetches and adds Node.js components from the internet. Convenient, but unknown packages may contain dangerous code.",
    "curl": "A command that accesses URLs on the internet. Can download files or send data to web services. Running without checking contents is dangerous.",
    "wget": "A command that downloads files from the internet. Similar to curl, but specialized for downloading only.",
    "eval": "A command that executes a string as a program. Useful but dangerous with untrusted input. Beginners should avoid it.",
    "exec": "A mechanism that calls and executes another program. Convenient but can run dangerous commands from untrusted input.",
    "subprocess": "A mechanism for starting new programs inside your computer. Whether it's dangerous depends on what it runs.",
    "shell": "A program that receives terminal commands and passes them to the computer. Examples: bash, zsh, PowerShell.",
    "chmod": "Changes file permission settings. Assigns read/write/execute permissions to user/group/others.",
    "chown": "Changes the owner of a file.",
    "rm": "Deletes files. They don't go to trash and are difficult to recover.",
    "mv": "Moves or renames files.",
    "cp": "Copies files.",
    "crontab": "A timer that automatically runs commands at set times.",
    "systemd": "A Linux manager that starts and stops background programs.",
    "daemon": "A program that waits in the background, ready to respond when needed.",
    "OAuth": "Logging in using another service's account (e.g. 'Sign in with Google'). Granting access to untrusted apps can expose your data.",
    "API Key": "A secret passphrase for online services. If discovered, others could use your account or credits.",
    "Auth Token": "A digital key proving you are logged in. Don't share or paste in chats.",
    "AI Token": "The smallest unit AI uses to read text. Pricing and processing are often based on token count.",
    ".env": "A settings file for passwords, API keys, and config values. May contain secrets — don't share or publish.",
    "quota": "The maximum usage limit for an online service. Exceeding it may block access or require extra payment.",
    "credits": "Tickets or coins for online services. They decrease with use.",
    "docker": "Creates isolated 'sandboxes' to run software. Keeps things separated but can still affect your files.",
    "kubernetes": "Manages many Docker containers automatically.",
    "localhost": "Your own computer. Doesn't connect to the internet.",
    "CDP": "A channel for remotely controlling Chrome from programs.",
    "Playwright": "A tool for automating web browsers from programs.",
    "MCP": "A common protocol for AI apps to interact with external tools. Capabilities depend on each MCP server.",
    "MCP Server": "A program that lends capabilities to AI (e.g. 'read files', 'control browser').",
    "MCP Client": "An app that connects to MCP servers. AI agents and dev tools are examples.",
    "MCP Compatible": "May be usable via MCP. Compatibility doesn't guarantee safety.",
    "dry-run": "Shows what would happen without making changes.",
    "venv": "A Python sandbox per project. Keeps components from conflicting.",
    "volume": "A window connecting Docker to your computer's folders.",
    "port": "A numbered communication door in your computer, each handling different tasks.",
    "Resident": "Programs that keep running in the background even after closing the terminal.",
    "Background": "Running behind the scenes without being displayed on screen.",
    "CLI": "Operating software by typing text commands.",
    "GUI": "Operating with buttons and windows using a mouse.",
    "OSS": "Software with publicly available source code. Free to view, modify, and use.",
    "README": "The explanation file at the top of a project folder. Read it first.",
    "MIT License": "A very permissive software license. Use, modify, distribute, and sell freely.",
    "Repository": "A place managing source code and change history.",
    "commit": "In Git, recording changes as 'saved at this state.'",
    "push": "In Git, uploading commits to GitHub.",
    "clone": "In Git, copying a project from server to local machine.",
    "PR": "Pull Request. Proposing changes to be included.",
    "issue": "A ticket for bugs, requests, or work notes.",
    "CI": "Automatic checks that run on every code change.",
    "Vibe Coding": "Asking AI to generate code for you.",
    "WSL": "Running Linux inside Windows without a separate machine.",
    "Path": "The address of a file or folder (e.g. C:\\Users\\... or /home/...).",
    "Terminal": "The text-based screen for typing CLI commands.",
    "Agent": "An AI program that thinks and acts autonomously.",
    "Git": "Records file change history. Track changes, revert, and collaborate.",
    "GitHub": "Hosts Git projects online. Used as code repo, notes, and public pages.",
    "branch": "A Git branch for separating work safely.",
    "merge": "Combining separate changes back into the main flow.",
    "fork": "Copying someone's repo to modify it yourself.",
    "dependency": "Required components for software to work.",
    "package": "A bundle of software or components.",
    "PATH": "Where your computer searches for commands. Unregistered = 'not found'.",
    "Environment Variables": "Config values passed to programs. Often for API keys or modes.",
    "JSON": "A data format like { name: Taro }. Common in APIs and configs.",
    "YAML": "A config format. Easy to read but breaks with wrong spacing.",
    "log": "A record of what a program did. Useful for debugging.",
    "error": "A notification that something didn't work. A clue, not a threat.",
    "warning": "A notice that deserves attention but isn't critical.",
}


DOCS = {
    "official-plan": {"path": ROOT / "docs" / "official-plan.md", "kind": "review-desk", "label": "共同レビュー用・公開前に整理"},
    "readme-ja": {"path": ROOT / "README.ja.md", "kind": "public", "label": "公開向け"},
    "readme": {"path": ROOT / "README.md", "kind": "public", "label": "公開向け"},
    "beginner-guide": {"path": ROOT / "docs" / "beginner-guide.md", "kind": "public", "label": "公開向け"},
    "limitations": {"path": ROOT / "docs" / "limitations.md", "kind": "public", "label": "公開向け"},
    "review-check-design": {"path": ROOT / "docs" / "review-check-design.md", "kind": "maintainer", "label": "保守者向け"},
    "rule-design": {"path": ROOT / "docs" / "rule-design.md", "kind": "maintainer", "label": "保守者向け"},
}


def utc_now() -> str:
    return _dt.datetime.now(_dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_comments() -> list[dict]:
    if not COMMENTS_PATH.exists():
        write_json(COMMENTS_PATH, [])
    try:
        data = json.loads(COMMENTS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


_BLOCKED_SCHEMES = {"javascript", "data", "file", "vbscript"}
_MAX_URL_CARDS = 20

def _validate_url(url: str) -> tuple[bool, str]:
    """Validate URL for safety. Returns (ok, error_message)."""
    if not url or not isinstance(url, str):
        return False, "url is required"
    url = url.strip()
    if len(url) > 2048:
        return False, "url too long (max 2048)"
    # Check scheme
    for scheme in _BLOCKED_SCHEMES:
        if url.lower().startswith(scheme + ":"):
            return False, f"blocked scheme: {scheme}:"
    # Must be http or https
    if not url.lower().startswith(("http://", "https://")):
        return False, "url must start with http:// or https://"
    try:
        if not urlparse(url).hostname:
            return False, "url must include a hostname"
    except ValueError:
        return False, "url is invalid"
    return True, ""

def read_url_cards() -> list[dict]:
    if not URL_CARDS_PATH.exists():
        write_json(URL_CARDS_PATH, [])
    try:
        data = json.loads(URL_CARDS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []

def next_url_card_id(cards: list[dict]) -> str:
    nums = []
    for item in cards:
        cid = str(item.get("id", ""))
        if cid.startswith("u") and cid[1:].isdigit():
            nums.append(int(cid[1:]))
    return f"u{(max(nums) if nums else 0) + 1:04d}"

# ── Command Confirmation Cards ──

_MAX_COMMAND_CARDS = 20

def read_command_cards() -> list[dict]:
    if not COMMAND_CARDS_PATH.exists():
        write_json(COMMAND_CARDS_PATH, [])
    try:
        data = json.loads(COMMAND_CARDS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []

def next_command_card_id(cards: list[dict]) -> str:
    nums = []
    for item in cards:
        cid = str(item.get("id", ""))
        if cid.startswith("cmd") and cid[1:].isdigit():
            nums.append(int(cid[1:]))
    return f"cmd{(max(nums) if nums else 0) + 1:04d}"

# ── Risk assessment for command confirmation ──

# Low-risk patterns: read-only, informational commands
_LOW_RISK_PATTERNS = [
    r'^git\s+(status|log|diff|branch|stash\s+list|remote\s+-v|config\s+--list)$',
    r'^(python|python3)\s+--version$',
    r'^(node|npm)\s+(-v|--version)$',
    r'^pip\s+(show|list|freeze)',
    r'^(ls|dir)\b',
    r'^pwd$', r'^cd\b', r'^echo\b',
    r'^(whoami|hostname|date|which|where|type)\b',
    r'^(cat|head|tail)\s+(?!.*\.env|.*secret|.*token|.*credential|.*password|.*key\b)',
    r'^(wc|du|df)\b',
]

# High-risk patterns: destructive, privilege escalation, remote execution
_HIGH_RISK_PATTERNS = [
    r'\brm\s+.*-r[^a-z]*f',    # rm -rf
    r'\bdel\s+/[sq]',           # Windows destructive
    r'Remove-Item\s+.*-Recurse',  # PowerShell destructive
    r'\bsudo\b',
    r'\bcurl\b.*\|\s*(ba)?sh',    # curl | sh
    r'\bwget\b.*\|\s*(ba)?sh',    # wget | sh
    r'\bchmod\s+.*777\b',
    r'\bchmod\s+-R\b',
    r'\bgit\s+reset\s+--hard\b',
    r'\bgit\s+clean\s+-fd\b',
    r'\bgit\s+push\s+.*--force\b',
    r'\b(\$HOME|~/\.ssh|~/\.env|/etc/)\b',
    r'\bdocker\s+rm\b',
    r'\bdocker\s+system\s+prune\b',
    r'\bnpm\s+(unpublish|deprecate)\b',
    r'\bDROP\s+(TABLE|DATABASE)\b',
    r'\bDELETE\s+FROM\b',
]

def _matches_any(cmd: str, patterns: list[str]) -> bool:
    import re as _re
    for p in patterns:
        if _re.search(p, cmd, _re.IGNORECASE):
            return True
    return False

def assess_command_risk(command: str, reason: str = "", lang: str = "ja") -> dict:
    """Assess command risk and return structured guidance. Read-only — no execution."""
    cmd = command.strip()

    # Check high-risk first
    if _matches_any(cmd, _HIGH_RISK_PATTERNS):
        risk = "high"
        summary_ja = "⚠️ 危険な操作です。削除・権限変更・リモート実行の可能性があります。続ける前に必ず確認してください。"
        summary_en = "⚠️ Dangerous operation. May delete files, change permissions, or execute remote code. Must be reviewed before continuing."
        ok_to_continue = False
        user_attention = "required"
    elif _matches_any(cmd, _LOW_RISK_PATTERNS):
        risk = "low"
        summary_ja = "読み取り専用または情報確認のコマンドです。安全です。"
        summary_en = "Read-only or informational command. Safe."
        ok_to_continue = True
        user_attention = "none"
    else:
        risk = "medium"
        summary_ja = "ファイルやパッケージを変更する可能性があるコマンドです。一度確認することをおすすめします。"
        summary_en = "May modify files or packages. Review recommended."
        ok_to_continue = True
        user_attention = "optional"

    # More detailed summaries for specific command types
    if "pip install" in cmd.lower():
        summary_ja = "Pythonのパッケージをインターネットからダウンロードしてインストールします。"
        summary_en = "Downloads and installs a Python package from the internet."
    elif "npm install" in cmd.lower() or "npm i " in cmd.lower():
        summary_ja = "Node.jsのパッケージをインストールします。package.jsonに依存関係が追加されます。"
        summary_en = "Installs Node.js packages. Dependencies are added to package.json."
    elif "git pull" in cmd.lower():
        summary_ja = "リモートリポジトリから最新の変更を取得してマージします。"
        summary_en = "Fetches and merges the latest changes from the remote repository."
    elif "git push" in cmd.lower():
        summary_ja = "ローカルのコミットをリモートリポジトリに送信します。"
        summary_en = "Pushes local commits to the remote repository."
    elif "python" in cmd.lower() and cmd.lower().endswith(".py"):
        summary_ja = "Pythonスクリプトを実行します。スクリプトの内容によってはファイル作成やネットワーク通信が発生します。"
        summary_en = "Runs a Python script. May create files or access network depending on content."
    elif "git status" in cmd.lower():
        risk = "low"; summary_ja = "現在の変更状態を表示するだけの安全なコマンドです。"; summary_en = "Shows current change status only. Safe."
        ok_to_continue = True; user_attention = "none"
    elif "npm run dev" in cmd.lower() or "npm start" in cmd.lower():
        risk = "medium"
        summary_ja = "開発サーバーを起動します。ローカルポートを使用し、ネットワークアクセスが発生することがあります。"
        summary_en = "Starts a development server. Will use local ports and may access the network."

    return {
        "risk": risk,
        "summary": summary_ja if lang == "ja" else summary_en,
        "summary_ja": summary_ja,
        "summary_en": summary_en,
        "ok_to_continue": ok_to_continue,
        "user_attention": user_attention,
    }

def explain_command(command: str, lang: str = "ja") -> str:
    """Return a beginner-friendly explanation using glossary-like keyword parsing."""
    cmd_lower = command.lower().strip()
    parts = []
    for keyword, (ja_desc, en_desc) in [
        ("pip", ("pipはPythonのパッケージ管理ツールです。インターネットからPythonの部品をダウンロードしてインストールします。", "pip is Python's package manager. It downloads and installs Python components from the internet.")),
        ("install", ("install（インストール）は、新しいソフトウェアや部品をあなたのPCに追加することです。", "install means adding new software or components to your PC.")),
        ("npm", ("npmはNode.js用のパッケージ管理ツールです。npm installで部品を追加します。", "npm is Node.js's package manager. npm install adds components.")),
        ("sudo", ("sudoは管理者権限でコマンドを実行します。システム全体に影響する可能性があるので注意が必要です。", "sudo runs commands with administrator privileges. It can affect the entire system, so be careful.")),
        ("curl", ("curlはインターネットからデータをダウンロードするコマンドです。curl | sh のようにパイプで実行する形は特に注意が必要です。", "curl downloads data from the internet. Be especially careful with curl | sh patterns.")),
        ("git", ("gitはファイルの変更履歴を管理するツールです。cloneでコピー、pullで更新、commitで保存します。", "git manages file change history. clone copies, pull updates, commit saves.")),
        ("docker", ("dockerはアプリを小さな箱（コンテナ）の中で動かすツールです。ポート公開やフォルダ共有に注意。", "docker runs apps in small containers. Watch for port exposure and folder sharing.")),
        ("chmod", ("chmodはファイルの権限を変更するコマンドです。+xで実行可能にします。", "chmod changes file permissions. +x makes a file executable.")),
        ("rm", ("rmはファイルやフォルダを削除するコマンドです。-rfをつけると強制的に削除します。取り消せません。", "rm deletes files and folders. -rf forces deletion. This cannot be undone.")),
        ("wget", ("wgetはcurlと同じく、インターネットからファイルをダウンロードするコマンドです。", "wget, like curl, downloads files from the internet.")),
    ]:
        if keyword in cmd_lower:
            parts.append(ja_desc if lang == "ja" else en_desc)
    if not parts:
        return (
            "このコマンドについてはまだ詳しい説明がありません。実行前に、何をするコマンドか調べてみてください。"
            if lang == "ja" else
            "We don't have a detailed explanation for this command yet. Please look up what it does before running it."
        )
    return "\n\n".join(parts)

# ── Command card mode config ──

COMMAND_MODE_PATH = DATA_ROOT / "command_card_mode.json"
_DEFAULT_MODE = "smart"
_VALID_MODES = ("silent", "smart", "strict", "off")

def read_command_mode() -> str:
    if COMMAND_MODE_PATH.exists():
        try:
            data = json.loads(COMMAND_MODE_PATH.read_text(encoding="utf-8"))
            mode = str(data.get("mode", _DEFAULT_MODE))
            return mode if mode in _VALID_MODES else _DEFAULT_MODE
        except (json.JSONDecodeError, KeyError):
            pass
    return _DEFAULT_MODE

def next_comment_id(comments: list[dict]) -> str:
    nums = []
    for item in comments:
        cid = str(item.get("id", ""))
        if cid.startswith("c") and cid[1:].isdigit():
            nums.append(int(cid[1:]))
    return f"c{(max(nums) if nums else 0) + 1:04d}"


def safe_doc(doc_id: str) -> tuple[str, str]:
    if doc_id not in DOCS:
        raise KeyError(doc_id)
    meta = DOCS[doc_id]
    path = meta["path"]
    return str(path.relative_to(ROOT)), read_text(path) if path.exists() else ""


def run_preflight(target: Path) -> dict:
    """Run this project's read-only preflight checker against a local path.

    The target path is passed as an argv item, never through a shell. The checker
    reads text files only and does not execute candidate project commands.
    """
    cmd = ["python3", str(ROOT / "preflight_checker.py"), str(target), "--format", "json"]
    try:
        proc = subprocess.run(cmd, cwd=str(ROOT), check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=20)
        if proc.returncode not in (0, 1, 2):
            return {"ok": False, "error": proc.stderr or proc.stdout, "returncode": proc.returncode}
        return {"ok": True, "returncode": proc.returncode, "target": str(target), "report": json.loads(proc.stdout)}
    except Exception as exc:  # noqa: BLE001 - shown in local management UI
        return {"ok": False, "error": str(exc), "target": str(target)}


def run_preflight_for_text(filename: str, content: str) -> dict:
    """Scan one dropped text file without requiring the user to know its path."""
    if len(content.encode("utf-8", errors="replace")) > 1_000_000:
        return {"ok": False, "error": "text file is too large for this simple trial view (limit: 1MB)"}
    safe_name = Path(filename or "dropped-text.txt").name
    safe_name = re.sub(r"[^A-Za-z0-9._ -]", "_", safe_name).strip(" .") or "dropped-text.txt"
    if Path(safe_name).suffix.lower() not in {".txt", ".md", ".markdown", ".rst", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".sh"}:
        safe_name += ".txt"
    with tempfile.TemporaryDirectory(prefix="agent-assist-drop-") as tmp:
        target = Path(tmp) / safe_name
        target.write_text(content, encoding="utf-8", errors="replace")
        result = run_preflight(target)
        result["source"] = "dropped_text_file"
        result["display_name"] = safe_name
        return result


def windows_path_to_wsl(path_text: str) -> str:
    """Convert a Windows path from a native dialog into a WSL path when possible."""
    text = path_text.strip()
    if re.match(r"^[A-Za-z]:\\", text) and shutil.which("wslpath"):
        proc = subprocess.run(["wslpath", "-u", text], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True, timeout=5)
        if proc.returncode == 0 and proc.stdout.strip():
            return proc.stdout.strip()
    return text


def pick_folder_dialog() -> dict:
    """Open a familiar Windows "Open" dialog and return a local path.

    The old FolderBrowserDialog looks alien and intimidating. On WSL/Windows,
    use the normal Explorer-style OpenFileDialog instead. It can select a file
    directly; for a folder, the user navigates into the folder and clicks Open
    with the placeholder filename "このフォルダを選択".
    """
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
$owner = New-Object System.Windows.Forms.Form
$owner.TopMost = $true
$owner.ShowInTaskbar = $false
$owner.StartPosition = 'CenterScreen'
$owner.Width = 1
$owner.Height = 1
$owner.Add_Shown({ $owner.Activate() })
if ($dialog.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) {
  $selected = $dialog.FileName
  if ([System.IO.Path]::GetFileName($selected) -eq 'このフォルダを選択') {
    Write-Output ([System.IO.Path]::GetDirectoryName($selected))
  } else {
    Write-Output $selected
  }
}
$owner.Dispose()
'''
            proc = subprocess.run(
                ["powershell.exe", "-NoProfile", "-STA", "-Command", script],
                check=False,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                raw = proc.stdout.strip().splitlines()[-1]
                selected = windows_path_to_wsl(raw)
                return {"ok": True, "path": selected, "raw_path": raw, "dialog": "open-file-dialog"}
            return {"ok": False, "cancelled": True, "error": proc.stderr.strip() or "path selection was cancelled"}
        script = "import tkinter as tk; from tkinter import filedialog; root=tk.Tk(); root.withdraw(); print(filedialog.askopenfilename() or filedialog.askdirectory())"
        proc = subprocess.run(["python3", "-c", script], check=False, text=True, encoding="utf-8", errors="replace", capture_output=True)
        if proc.returncode == 0 and proc.stdout.strip():
            return {"ok": True, "path": proc.stdout.strip(), "dialog": "tk"}
        return {"ok": False, "cancelled": True, "error": proc.stderr.strip() or "path selection was cancelled"}
    except Exception as exc:  # noqa: BLE001 - shown in local management UI
        return {"ok": False, "error": str(exc)}


def sample_report() -> dict:
    return run_preflight(ROOT / "tests/fixtures/danger")



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
        "version_args": ["-Command", "$PSVersionTable.PSVersion.ToString()"],
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
        proc = subprocess.run([command, *args], check=False, capture_output=True, timeout=5)
    except Exception:
        return ""
    raw = proc.stdout or proc.stderr
    # Try common encodings — Windows tools often output cp932 on Japanese systems
    for enc in ("utf-8", "utf-16", "cp932", "shift_jis"):
        try:
            decoded = raw.decode(enc)
            if "\ufffd" not in decoded:
                return _short_output(decoded)
        except (UnicodeDecodeError, LookupError):
            continue
    # Last resort: replace undecodable bytes
    return _short_output(raw.decode("utf-8", errors="replace"))


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

# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Auto Diagnostic — one-touch environment scan for the dashboard
# ---------------------------------------------------------------------------

def scan_auto_diagnostic(lang: str = "ja") -> dict:
    """Run tools + ports checks in one call. Designed for dashboard auto-load."""
    tools_result = scan_basic_tools()
    ports_result = scan_port_owners()

    # Simplify tools for dashboard display
    tools_compact = []
    for t in tools_result.get("tools", []):
        tools_compact.append({
            "label": t["label"],
            "id": t["id"],
            "status": t["status"],
            "present": t["present"],
            "agent_can_use": t["agent_can_use"],
            "beginner": t["beginner_explanation"],
            "version": t.get("current_side", {}).get("version", ""),
            "run_command": t.get("run_command", ""),
        })

    # Simplify ports for dashboard display
    ports_compact = []
    for p in ports_result.get("ports", []):
        ports_compact.append({
            "port": p["port"],
            "process": p["process_name"],
            "visibility": p["visibility"],
            "is_known": p["is_known"],
            "is_self": p["is_self"],
            "description": p["description"],
        })

    # Build a beginner-friendly summary
    running_side = tools_result.get("running_side", "current")
    tool_ok = sum(1 for t in tools_compact if t["agent_can_use"])
    tool_total = len(tools_compact)
    tool_missing = [t["label"] for t in tools_compact if not t["agent_can_use"]]
    tool_win_only = [t["label"] for t in tools_compact if t["status"] == "windows_only"]

    port_count = ports_result.get("total", 0)
    port_external = ports_result.get("external_count", 0)
    port_unknown = sum(1 for p in ports_compact if not p["is_known"] and not p["is_self"])

    summary_ja_lines = []
    summary_en_lines = []

    # Title
    summary_ja_lines.append("起動時おまかせ診断を読み取り専用で実行しました。")
    summary_en_lines.append("Startup auto-diagnostic completed in read-only mode.")

    # Tools
    if tool_missing:
        summary_ja_lines.append(f"⚠️ エージェント側で見つからない道具: {', '.join(tool_missing)}")
        summary_en_lines.append(f"⚠️ Tools not found on agent side: {', '.join(tool_missing)}")
    if tool_win_only:
        summary_ja_lines.append(f"💡 Windows側だけにある道具（WSLエージェントから使えないかも）: {', '.join(tool_win_only)}")
        summary_en_lines.append(f"💡 Tools on Windows only (may not be usable from WSL agent): {', '.join(tool_win_only)}")
    if tool_ok == tool_total:
        summary_ja_lines.append("✅ 基本道具はすべてエージェント側で使えます。")
        summary_en_lines.append("✅ All basic tools are available on the agent side.")

    # Ports
    if port_external > 0:
        summary_ja_lines.append(f"⚠️ {port_external}個のポートが外から見える状態です。")
        summary_en_lines.append(f"⚠️ {port_external} ports may be externally visible.")
    else:
        summary_ja_lines.append("✅ 外から見えるポートはありません。")
        summary_en_lines.append("✅ No externally visible ports found.")

    if port_unknown > 0:
        summary_ja_lines.append(f"🔍 用途不明のポートが{port_unknown}個あります。")
        summary_en_lines.append(f"🔍 {port_unknown} unidentified ports are listening.")

    # Running side
    if running_side == "wsl":
        summary_ja_lines.append("ℹ️ WSL環境で動作しています。Windows側とWSL側で道具が違うことがあります。")
        summary_en_lines.append("ℹ️ Running in WSL. Tools may differ between Windows and WSL sides.")

    summary_ja_lines.append("不足があっても、この画面はインストールや設定変更を行いません。")
    summary_en_lines.append("Even if tools are missing, this tool does not install or change settings.")

    return {
        "ok": True,
        "running_side": running_side,
        "tools": tools_compact,
        "ports": ports_compact,
        "tool_ok": tool_ok,
        "tool_total": tool_total,
        "tool_missing": tool_missing,
        "tool_win_only": tool_win_only,
        "port_count": port_count,
        "port_external": port_external,
        "port_unknown": port_unknown,
        "summary": "\n".join(summary_ja_lines if lang == "ja" else summary_en_lines),
        "summary_ja": "\n".join(summary_ja_lines),
        "summary_en": "\n".join(summary_en_lines),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentAssistManagementWebUI/0.1"

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"[{utc_now()}] {self.address_string()} {fmt % args}")

    def send_json(self, payload: object, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length <= 0:
            return {}
        raw_bytes = self.rfile.read(length)
        # Try UTF-8 first (modern tools, Hermes, curl)
        # Fall back to cp932/shift_jis for Windows PowerShell etc.
        raw = None
        for enc in ("utf-8", "cp932", "shift_jis", "utf-8-sig"):
            try:
                raw = raw_bytes.decode(enc)
                break
            except (UnicodeDecodeError, LookupError):
                continue
        if raw is None:
            raw = raw_bytes.decode("utf-8", errors="replace")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload


    def _get_lang(self, parsed) -> str:
        qs = parse_qs(parsed.query)
        lang = qs.get("lang", ["ja"])[0]
        return lang if lang in ("ja", "en") else "ja"

    def _send_api_index(self) -> None:
        self.send_json({
            "name": "Agent Assist Preflight",
            "version": "0.1.0",
            "description": "Read-only preflight assistant for beginners and AI agents. Scans local folders/text and produces plain-language review notes.",
            "description_ja": "初心者とAIエージェント向けの読み取り専用プリフライトアシスタント。ローカルフォルダ/テキストをスキャンして平易なレビューノートを生成します。",
            "endpoints": {
                "GET /api": {"description": "This index. Lists all available endpoints.", "agent_hint": "Start here to discover capabilities."},
                "GET /api/state": {"description": "Project info, doc list, comments.", "params": {}},
                "GET /api/doc": {"description": "Read a document by ID.", "params": {"id": "doc id (e.g. readme, readme-ja, beginner-guide)"}},
                "GET /api/glossary": {"description": "Glossary terms with plain-language explanations.", "params": {"lang": "ja (default) or en"}},
                "GET /api/port-owners": {"description": "List all listening ports with process info and AI/MCP tool candidates.", "params": {"lang": "ja (default) or en"}, "agent_hint": "Use this before starting dev servers to check for port conflicts."},
                "GET /api/tool-basics": {"description": "Check common dev tools (Python, Node, Git, etc.) on both Windows and WSL/agent side.", "params": {"lang": "ja (default) or en"}, "agent_hint": "Run this before assuming a tool is available. Check agent_can_use field."},
                "GET /api/sample-report": {"description": "Run preflight on test fixture. Returns example output format."},
                "POST /api/scan": {"description": "Scan a local folder's text files for review items.", "body": {"target_path": "absolute or relative path to folder/file"}, "agent_hint": "Main entry point. Returns decision, review_items with plain_language explanations."},
                "POST /api/scan-text": {"description": "Scan a single text string for review items.", "body": {"filename": "virtual filename", "content": "text to scan"}, "agent_hint": "Use when you have text content but no local path."},
                "POST /api/comments": {"description": "Add a customization request ticket.", "body": {"text": "request text", "section": "target section", "priority": "confirm|review|note"}},
                "POST /api/comments/<id>": {"description": "Update a ticket status.", "body": {"status": "open|accepted|fixed|parked"}},
                "POST /api/url-card": {"description": "Send a URL to the user as a browser handoff card. The user sees the URL with a reason and can choose to open, copy, or dismiss. Never auto-opens.", "body": {"url": "http/https URL to share", "reason": "why the agent wants the user to open this (shown to user)"}, "agent_hint": "Use this instead of trying to open a browser directly. Safer and works across WSL/Windows. Blocked: javascript:, data:, file:."},
                "GET /api/url-cards": {"description": "List pending URL handoff cards (not yet opened/dismissed by user)."},
                "POST /api/url-card/<id>": {"description": "Update URL card status.", "body": {"status": "opened|copied|dismissed"}},
                "GET /api/auto-diagnostic": {"description": "One-touch environment scan (tools + ports). Runs on dashboard load — no user action needed.", "params": {"lang": "ja (default) or en"}, "agent_hint": "Run this on first contact to understand the machine state."},
                "POST /api/check-command": {"description": "Ask the user to confirm a command before running. Returns risk level, summary, and whether WebUI review is required. Low-risk commands pass through; high-risk commands require user approval in WebUI.", "body": {"command": "the shell command to run", "reason": "why the agent wants to run this"}, "agent_hint": "Call this before running any command with side effects. Check ok_to_continue — if false, wait for user to approve via the card_url before executing. If true, you may proceed (but the user can still review later)."},                "GET /api/check-commands": {"description": "List all command confirmation cards sorted by risk (high first, then newest)."},                "GET /api/check-commands/pending": {"description": "List only high-risk pending command cards that require user attention."},                "GET /api/command-card-mode": {"description": "Get current command card mode (silent/smart/strict/off)."},                "POST /api/command-card-mode": {"description": "Set command card mode.", "body": {"mode": "silent|smart|strict|off"}},
            },
            "agent_workflow": {
                "recommended_first_steps": [
                    "GET /api/tool-basics?lang=en — check what tools are available on this machine",
                    "GET /api/port-owners?lang=en — check for port conflicts before starting servers",
                    "POST /api/scan — scan the target project folder",
                    "GET /api/glossary?lang=en — look up terms to explain to beginner users",
                ],
                "principles": [
                    "This tool is read-only for scanning. It does not install, modify, or execute anything.",
                    "All review items include plain_language, why_it_matters, and beginner_next_step fields.",
                    "Use these fields to explain risks to beginners in simple language before running commands.",
                    "Do not auto-install tools. Report missing tools and let the user decide.",
                    "Do not auto-run dangerous commands. Use the review_items as conversation starters.",
                ],
                "browser_handoff": {
                    "summary": "AI agents can send URLs to the user's browser through the URL card system. The agent POSTs a URL+reason to /api/url-card; the user sees a card in the WebUI with 'Open', 'Copy', and 'Dismiss' buttons. The agent never opens a browser directly.",
                    "why_it_matters": [
                        "Agents running in WSL/Linux cannot open the Windows user's browser directly.",
                        "Auto-opening URLs feels invasive and can be dangerous (tracking pixels, drive-by downloads).",
                        "URL cards keep the user in control: they see the URL, the agent's reason, and decide what to do.",
                        "Blocked URL schemes (javascript:, data:, file:) prevent XSS and local file leaks.",
                        "Works across the WSL/Windows boundary without extra setup."
                    ],
                    "example_agent_workflow": "1. Agent fetches a GitHub README\n2. Agent wants to show the user a reference page\n3. Agent POSTs to /api/url-card with the URL and a plain-language reason\n4. User sees the card in the preflight WebUI\n5. User clicks 'Open' → page opens in their default browser\n6. No copy-paste, no WSLg Chrome, no terminal needed."
                }
            }
        })

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api":
            self._send_api_index()
            return
        if parsed.path == "/api/state":
            docs = []
            for doc_id, meta in DOCS.items():
                path = meta["path"]
                docs.append({
                    "id": doc_id,
                    "path": str(path.relative_to(ROOT)),
                    "exists": path.exists(),
                    "kind": meta["kind"],
                    "label": meta["label"],
                })
            self.send_json({"project": "Agent Assist Preflight", "root": str(ROOT), "docs": docs, "comments": read_comments()})
            return
        if parsed.path == "/api/doc":
            doc_id = parse_qs(parsed.query).get("id", ["official-plan"])[0]
            try:
                rel, content = safe_doc(doc_id)
            except KeyError:
                self.send_json({"error": "unknown doc id"}, status=404)
                return
            self.send_json({"id": doc_id, "path": rel, "content": content})
            return
        if parsed.path == "/api/sample-report":
            self.send_json(sample_report())
            return
        if parsed.path == "/api/pick-folder":
            self.send_json(pick_folder_dialog())
            return
        if parsed.path == "/api/glossary":
            lang = self._get_lang(parsed)
            self.send_json(GLOSSARY_EN if lang == "en" else GLOSSARY)
            return
        if parsed.path == "/api/glossary-candidates":
            if CANDIDATES_PATH.exists():
                self.send_json(json.loads(CANDIDATES_PATH.read_text(encoding="utf-8")))
            else:
                self.send_json({})
            return
        if parsed.path == "/api/port-owners":
            lang = self._get_lang(parsed)
            result = scan_port_owners()
            if lang == "en" and result.get("ok"):
                result["lang"] = "en"
                for p in result.get("ports", []):
                    if p.get("description"):
                        desc = p["description"]
                        for ja, en in [
                            ("で使われることがある", "may be used by"),
                            ("の代替ポート", "alternative port"),
                            ("見慣れない待ち受け — 何のソフトか確認してみてください", "Unfamiliar listener — check what software this is"),
                        ]:
                            desc = desc.replace(ja, en)
                        p["description"] = desc
                if result.get("summary"):
                    s = result["summary"]
                    for ja, en in [
                        ("基本道具を読み取り専用で確認しました。", "Basic tools checked in read-only mode."),
                        ("個のポートがLISTEN中です", " ports are listening"),
                        ("ポートがLISTEN中", " ports listening"),
                        ("外から見える可能性があります", " may be externally visible"),
                        ("ポートを止めるときは、まずそのソフトを通常方法で終了してください", "To stop a port, first close the software normally"),
                    ]:
                        s = s.replace(ja, en)
                    result["summary"] = s
            self.send_json(result)
            return
        if parsed.path == "/api/tool-basics":
            lang = self._get_lang(parsed)
            result = scan_basic_tools()
            if lang == "en" and result.get("ok"):
                result["lang"] = "en"
                for tool in result.get("tools", []):
                    tool["status_en"] = {'both': 'Available on both Windows and WSL/agent side', 'agent_only': 'Available on agent side', 'windows_only': 'On Windows side but not found on agent side', 'missing': 'Not found'}.get(tool.get("status", ""), "")
                    tool["beginner_explanation_en"] = {'python': 'Python is commonly used for AI tools and small automation scripts.', 'node': 'Node.js is used for JavaScript dev tools and web apps.', 'npm': 'npm installs Node.js packages. Check what goes in before using.', 'git': 'Git records file changes. Used for undo, diff, and GitHub.', 'gh': 'GitHub CLI operates GitHub from the terminal. May need login.', 'powershell': 'PowerShell is Windows command line. Used for port and app checks.', 'wsl': 'WSL runs Linux inside Windows. Tools may differ between sides.', 'docker': 'Docker runs software in isolated containers. May share folders and ports.'}.get(tool.get("id", ""), "")
                    tool["agent_caution_en"] = {'python': 'Agents running in WSL need Python on their side. Check for virtual environments.', 'node': 'If doing npm in WSL, need node on both Windows and WSL.', 'npm': 'npm install adds files and accesses network. Confirm folder and get user approval first.', 'git': 'git operations change state. Explain purpose before executing.', 'gh': 'gh touches GitHub accounts. Login, repo, PR, push need user confirmation.', 'powershell': 'WSL agents use powershell.exe to check Windows. No config changes without confirmation.', 'wsl': 'WSL agents may not access Windows tools. Specify which side.', 'docker': "docker run involves image pull, port, volume, processes. Don't start without confirmation."}.get(tool.get("id", ""), "")
                if result.get("summary"):
                    s = result["summary"]
                    for ja, en in [('基本道具を読み取り専用で確認しました。', 'Basic tools checked in read-only mode.'), ('Windows側だけで見つかった道具があります: ', 'Tools found only on Windows side: '), ('エージェント側で見つからない道具があります: ', 'Tools not found on agent side: '), ('不足があっても、この画面はインストールや設定変更を行いません。', 'Even if tools are missing, this tool does not install or change settings.')]:
                        s = s.replace(ja, en)
                    result["summary"] = s
            self.send_json(result)
            return
        if parsed.path == "/api/auto-diagnostic":
            lang = self._get_lang(parsed)
            self.send_json(scan_auto_diagnostic(lang))
            return
        if parsed.path == "/api/url-cards":
            cards = read_url_cards()
            # Return only pending (not dismissed) cards
            pending = [c for c in cards if c.get("status") == "pending"]
            self.send_json({"ok": True, "cards": pending})
            return
        if parsed.path == "/api/check-commands":
            cards = read_command_cards()
            # Sort: high-risk first, then by recency
            risk_order = {"high": 0, "medium": 1, "low": 2}
            sorted_cards = sorted(cards, key=lambda c: (risk_order.get(c.get("risk", "low"), 99), c.get("created_at", ""),), reverse=False)
            # First sort by risk priority, then within same risk by newest first
            # Simpler: high first, rest by time
            high = [c for c in cards if c.get("risk") == "high"]
            rest = [c for c in cards if c.get("risk") != "high"]
            # Sort each group by newest first
            high.sort(key=lambda c: c.get("created_at", ""), reverse=True)
            rest.sort(key=lambda c: c.get("created_at", ""), reverse=True)
            self.send_json({"ok": True, "cards": high + rest, "high_risk_count": len(high), "total": len(cards)})
            return
        if parsed.path == "/api/check-commands/pending":
            cards = read_command_cards()
            pending_high = [c for c in cards if c.get("risk") == "high" and c.get("status") == "pending"]
            self.send_json({"ok": True, "cards": pending_high, "count": len(pending_high)})
            return
        if parsed.path == "/api/command-card-mode":
            self.send_json({"ok": True, "mode": read_command_mode(), "valid_modes": list(_VALID_MODES)})
            return
        if parsed.path.startswith("/api/check-command-explain/"):
            cid = parsed.path.rsplit("/", 1)[-1]
            cards = read_command_cards()
            lang = self._get_lang(parsed)
            for card in cards:
                if card.get("id") == cid:
                    explanation = explain_command(card.get("command", ""), lang)
                    self.send_json({"ok": True, "id": cid, "explanation": explanation})
                    return
            self.send_json({"error": "card not found"}, status=404)
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        try:
            payload = self.read_body_json()
        except Exception as exc:  # noqa: BLE001
            self.send_json({"error": str(exc)}, status=400)
            return
        if parsed.path == "/api/scan":
            raw_target = str(payload.get("target_path", "")).strip()
            if not raw_target:
                self.send_json({"ok": False, "error": "target_path is required"}, status=400)
                return
            target = Path(raw_target).expanduser()
            if not target.is_absolute():
                target = (ROOT / target).resolve()
            if not target.exists():
                self.send_json({"ok": False, "error": "path does not exist", "target": str(target)}, status=404)
                return
            self.send_json(run_preflight(target))
            return
        if parsed.path == "/api/scan-text":
            filename = str(payload.get("filename", "dropped-text.txt"))
            content = payload.get("content", "")
            if not isinstance(content, str) or not content.strip():
                self.send_json({"ok": False, "error": "text file content is required"}, status=400)
                return
            self.send_json(run_preflight_for_text(filename, content))
            return
        if parsed.path == "/api/comments":
            text = str(payload.get("text", "")).strip()
            if not text:
                self.send_json({"error": "text is required"}, status=400)
                return
            comments = read_comments()
            now = utc_now()
            item = {
                "id": next_comment_id(comments),
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
            write_json(COMMENTS_PATH, comments)
            self.send_json({"ok": True, "comment": item, "comments": comments}, status=201)
            return
        if parsed.path.startswith("/api/comments/"):
            cid = parsed.path.rsplit("/", 1)[-1]
            comments = read_comments()
            for item in comments:
                if item.get("id") == cid:
                    if "status" in payload:
                        item["status"] = str(payload["status"])
                    if "owner_note" in payload:
                        item["owner_note"] = str(payload["owner_note"])
                    item["updated_at"] = utc_now()
                    write_json(COMMENTS_PATH, comments)
                    self.send_json({"ok": True, "comment": item, "comments": comments})
                    return
            self.send_json({"error": "comment not found"}, status=404)
            return
        if parsed.path == "/api/url-card":
            url = str(payload.get("url", "")).strip()
            reason = str(payload.get("reason", "")).strip()
            ok, err = _validate_url(url)
            if not ok:
                self.send_json({"ok": False, "error": err}, status=400)
                return
            cards = read_url_cards()
            now = utc_now()
            card = {
                "id": next_url_card_id(cards),
                "url": url,
                "reason": reason,
                "status": "pending",
                "created_at": now,
            }
            cards.insert(0, card)
            # Trim to max
            if len(cards) > _MAX_URL_CARDS:
                cards = cards[:_MAX_URL_CARDS]
            write_json(URL_CARDS_PATH, cards)
            self.send_json({"ok": True, "card": card}, status=201)
            return
        if parsed.path.startswith("/api/url-card/"):
            cid = parsed.path.rsplit("/", 1)[-1]
            cards = read_url_cards()
            for card in cards:
                if card.get("id") == cid:
                    new_status = str(payload.get("status", "")).strip()
                    if new_status in ("opened", "copied", "dismissed"):
                        card["status"] = new_status
                        card["updated_at"] = utc_now()
                        write_json(URL_CARDS_PATH, cards)
                    self.send_json({"ok": True, "card": card})
                    return
            self.send_json({"error": "card not found"}, status=404)
            return
        if parsed.path == "/api/check-command":
            command = str(payload.get("command", "")).strip()
            reason = str(payload.get("reason", "")).strip()
            if not command:
                self.send_json({"ok": False, "error": "command is required"}, status=400)
                return
            lang = self._get_lang(parsed)
            mode = read_command_mode()
            if mode == "off":
                self.send_json({"ok": True, "card_id": None, "risk": "off", "summary": "", "ok_to_continue": True, "user_attention": "none", "card_url": None})
                return
            assessment = assess_command_risk(command, reason, lang)
            cards = read_command_cards()
            now = utc_now()
            cid = next_command_card_id(cards)
            card = {
                "id": cid,
                "command": command,
                "reason": reason,
                "risk": assessment["risk"],
                "summary": assessment["summary"],
                "user_attention": assessment["user_attention"],
                "status": "pending",
                "created_at": now,
            }
            cards.insert(0, card)
            if len(cards) > _MAX_COMMAND_CARDS:
                cards = cards[:_MAX_COMMAND_CARDS]
            write_json(COMMAND_CARDS_PATH, cards)
            # Build URL for WebUI card
            card_url = f"http://127.0.0.1:8765/#cmd-{cid}" if assessment["user_attention"] == "required" else None
            if mode == "silent":
                card_url = None
                assessment["user_attention"] = "none"
            elif mode == "strict":
                assessment["user_attention"] = "required"
                card_url = f"http://127.0.0.1:8765/#cmd-{cid}"
                assessment["ok_to_continue"] = False
            resp = {
                "ok": True,
                "card_id": cid,
                "risk": assessment["risk"],
                "summary": assessment["summary"],
                "ok_to_continue": assessment["ok_to_continue"],
                "user_attention": assessment["user_attention"],
                "card_url": card_url,
            }
            self.send_json(resp, status=201)
            return
        if parsed.path.startswith("/api/check-command/") and not parsed.path.startswith("/api/check-command-explain/"):
            cid = parsed.path.rsplit("/", 1)[-1]
            cards = read_command_cards()
            for card in cards:
                if card.get("id") == cid:
                    new_status = str(payload.get("status", "")).strip()
                    if new_status in ("approved", "denied"):
                        card["status"] = new_status
                        card["updated_at"] = utc_now()
                        write_json(COMMAND_CARDS_PATH, cards)
                        resp = {"ok": True, "card": card}
                        if new_status == "denied":
                            resp["hint"] = (
                                "このコマンドはユーザーに拒否されました。説明が足りないかもしれません。"
                                "何のために必要か、何が起きるかをもう少し詳しく書いて、もう一度送ってみてください。"
                            )
                            resp["hint_en"] = (
                                "This command was denied by the user. The explanation may need more detail. "
                                "Please add more context about why it is needed and what will happen, then try again."
                            )
                        self.send_json(resp)
                        return
                    self.send_json({"ok": False, "error": f"invalid status: {new_status}"}, status=400)
                    return
            self.send_json({"error": "card not found"}, status=404)
            return
        if parsed.path == "/api/command-card-mode":
            new_mode = str(payload.get("mode", "")).strip()
            if new_mode not in _VALID_MODES:
                self.send_json({"ok": False, "error": f"invalid mode. valid: {_VALID_MODES}"}, status=400)
                return
            write_json(COMMAND_MODE_PATH, {"mode": new_mode})
            self.send_json({"ok": True, "mode": new_mode})
            return
        self.send_json({"error": "not found"}, status=404)

    def serve_static(self, path: str) -> None:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local Agent Assist Preflight management WebUI")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.host not in {"127.0.0.1", "localhost"}:
        raise SystemExit("This local review UI intentionally binds only to 127.0.0.1/localhost.")
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    if not COMMENTS_PATH.exists():
        write_json(COMMENTS_PATH, [])
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print("=" * 60)
    print("  フォルダの中身チェック を起動しました！")
    print()
    print("  👉 下のリンクを Ctrl+クリック で開いてください：")
    print(f"     http://{args.host}:{args.port}/")
    print()
    print("  または、上の URL をコピーしてブラウザに貼り付けてください。")
    print()
    print("  📁 見ているフォルダ：")
    print(f"     {ROOT}")
    print()
    print("  この画面を閉じるとツールも終了します。")
    print("  終了するときは Ctrl+C を押してください。")
    print("=" * 60)
    httpd.serve_forever()


if __name__ == "__main__":
    main()
