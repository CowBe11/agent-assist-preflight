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
        raw = self.rfile.read(length).decode("utf-8")
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
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
            self.send_json(GLOSSARY)
            return
        if parsed.path == "/api/port-owners":
            self.send_json(scan_port_owners())
            return
        if parsed.path == "/api/tool-basics":
            self.send_json(scan_basic_tools())
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
