# Agent Assist Preflight / フォルダの中身チェック

[日本語README](README.ja.md) | `v0.1.2` | Free, open-source, local-only

**EN:** A beginner-friendly, read-only preflight checker for downloaded developer projects. It explains risky-looking README/setup lines and pasted CLI errors before you run commands.

**JA:** ダウンロードした開発プロジェクトを実行する前に、README やエラー文の「そのまま進めて大丈夫？」をやさしく確認する read-only ツールです。

<table>
<tr>
<td width="42%" valign="top">
<h3>Understand it before scrolling</h3>
<p>Use this when a README, installer, MCP server, AI-agent tool, or terminal error tells you to run something you do not fully understand yet.</p>
<ul>
<li><strong>Reads text only</strong>: README, <code>.md</code>, <code>.txt</code>, <code>.py</code>, <code>.json</code>, logs</li>
<li><strong>Does not run commands</strong>: no install, no shell, no daemon start</li>
<li><strong>Does not send data out</strong>: local browser UI, <code>127.0.0.1</code> by default</li>
<li><strong>Explains in plain language</strong>: what it means, why it matters, next step</li>
</ul>
<p><strong>Fastest start on Windows</strong></p>
<pre><code>起動する.bat</code></pre>
<p>Then open <code>http://127.0.0.1:8765/</code> if the browser does not open automatically.</p>
</td>
<td width="58%" valign="top">
<img src="docs/assets/webui-preview.png" alt="Agent Assist Preflight WebUI showing beginner-friendly review notes">
</td>
</tr>
</table>

## What It Checks

Agent Assist Preflight helps beginners and AI-agent users pause before setup steps that can affect the machine, account, or future agent sessions.

| Area | English | 日本語 |
| --- | --- | --- |
| Project folder scan | Finds setup lines about global installs, `curl | sh`, secrets, billing, daemons, config edits, containers, ports, browser control, and file writes. | README や設定ファイルから、グローバルインストール、秘密情報、課金、常駐サービス、設定変更などを拾います。 |
| CLI error paste checker | Lets you paste terminal/PowerShell errors and explains common causes such as npm auth errors, missing commands, port conflicts, permission errors, and suspicious log text. | ターミナルや PowerShell のエラーを貼ると、認証エラー、コマンド不足、ポート競合、権限エラー、怪しいログ文などを説明します。 |
| Beginner output | Turns labels like `secrets_or_auth` into "what this means / why it matters / beginner next step." | `secrets_or_auth` のようなラベルだけでなく、「これは何？ / なぜ確認？ / 次にすること」に変換します。 |

## Screenshots

### Folder / README Preflight

![Folder preflight result in the local WebUI](docs/assets/webui-preview.png)

### CLI Error Paste Checker

![CLI error checker explaining an npm authentication error](docs/assets/cli-error-preview.png)

## Quick Start

### Windows WebUI

Double-click:

```bat
起動する.bat
```

This starts the standalone local WebUI with Python 3 and opens:

```text
http://127.0.0.1:8765/
```

There is also a Japanese-named launcher:

```bat
フォルダの中身チェックを起動する.bat
```

### WSL / macOS / Linux WebUI

```bash
python3 management_webui/server.py
```

Then open:

```text
http://127.0.0.1:8765/
```

### CLI

```bash
python3 preflight_checker.py path/to/candidate --format markdown
python3 preflight_checker.py path/to/candidate --format json
python3 preflight_checker.py path/to/candidate --fail-on confirm
python3 preflight_checker.py --version
```

After package installation:

```bash
agent-assist-preflight path/to/candidate --format markdown
```

## What It Does Not Do

This project is intentionally modest. It is **not a security scanner** and does **not** prove a project is safe.

It does not:

- execute candidate commands
- install dependencies
- call package managers
- mutate MCP, Hermes, Claude, Codex, or app config
- contact external services
- start browsers, daemons, or containers
- replace expert review, secret scanning, dependency auditing, or sandboxing

False positives and false negatives are expected. The goal is not perfect safety judgment; the goal is to give beginners a readable pause before action.

## Decisions And Priorities

Reports return one of three decisions:

- `no_review_items_found`: no obvious review items were found; this is not a safety guarantee
- `review_before_trying`: review these items before trying the project
- `confirm_before_running`: stop and ask before running commands from this project

Review priorities:

- `confirm`: do not run yet without explicit confirmation
- `review`: inspect the instruction and prefer a disposable workspace or dry-run first
- `note`: lower-impact context that may still be useful

Compatibility note: older JSON fields such as `finding_count`, `max_severity`, `findings`, and `human_approval_categories` are still emitted for now. New integrations should prefer `review_item_count`, `max_priority`, `review_items`, and `confirmation_categories`.

## Beginner Workflow

1. Run the WebUI or CLI against the candidate project.
2. Read the plain-language summary first.
3. For each review item, read:
   - `What this means`
   - `Why it matters`
   - `Beginner next step`
4. Do not paste real tokens, enter payment details, change agent config, start daemons, or run global installs until you understand the relevant item.
5. Try first in a disposable folder or isolated workspace when possible.

See [docs/beginner-guide.md](docs/beginner-guide.md) for a longer walkthrough.

## Local API For Agents

The WebUI exposes a local API for read-only agent preflight workflows. Start the WebUI, then open:

```text
http://127.0.0.1:8765/api
```

The default design remains conservative: local-only, read-only, no automatic external fetch, no command execution.

## Development

Run tests:

```bash
python3 -m pytest -q
```

Run the helper against itself:

```bash
python3 preflight_checker.py . --format markdown --output self-preflight.md
```

Check versions:

```bash
python3 preflight_checker.py --version
python3 standalone.py --version
```

## Roadmap

- more CLI error patterns: pip, cargo, docker, systemctl
- stronger secret redaction patterns: AWS, Azure, GCP, Slack, Discord
- better multilingual terminal-error explanations
- mobile layout improvements
- optional local AI handoff only with explicit user action, masked text, confirmation screen, read-only mode, and no tool privileges

## License

MIT.
