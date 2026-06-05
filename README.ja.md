# Agent Assist Preflight / フォルダの中身チェック

[English README](README.md) | `v0.1.2` | 無料・オープンソース・ローカル専用

**JA:** ダウンロードした開発プロジェクトを実行する前に、README やエラー文の「そのまま進めて大丈夫？」をやさしく確認する read-only ツールです。

**EN:** A beginner-friendly, read-only preflight checker for downloaded developer projects. It explains risky-looking README/setup lines and pasted CLI errors before you run commands.

<table>
<tr>
<td width="42%" valign="top">
<h3>スクロール前に分かること</h3>
<p>知らない README、インストーラー、MCP サーバー、AI エージェント用ツール、ターミナルエラーに出てきたコマンドを、理解しないまま実行しそうな時に使います。</p>
<ul>
<li><strong>テキストだけ読む</strong>: README、<code>.md</code>、<code>.txt</code>、<code>.py</code>、<code>.json</code>、ログ</li>
<li><strong>コマンドは実行しない</strong>: install しない、shell を動かさない、常駐もしない</li>
<li><strong>外部へ送信しない</strong>: 既定は <code>127.0.0.1</code> のローカル画面</li>
<li><strong>初心者向けに説明</strong>: これは何か、なぜ確認するか、次に何をするか</li>
</ul>
<p><strong>Windows で一番早い開き方</strong></p>
<pre><code>起動する.bat</code></pre>
<p>自動で開かない場合は <code>http://127.0.0.1:8765/</code> をブラウザに貼り付けてください。</p>
</td>
<td width="58%" valign="top">
<img src="docs/assets/webui-preview.png" alt="初心者向けの確認項目を表示する Agent Assist Preflight の画面">
</td>
</tr>
</table>

## 何をチェックする？

Agent Assist Preflight は、初心者や AI エージェント利用者が、PC・アカウント・今後のエージェント設定に影響しそうな手順の前で一度止まれるようにします。

| 領域 | 日本語 | English |
| --- | --- | --- |
| フォルダ / README チェック | README や設定ファイルから、グローバルインストール、`curl | sh`、秘密情報、課金、常駐サービス、設定変更、コンテナ、ポート、ブラウザ制御、ファイル書き込みなどを拾います。 | Finds setup lines about global installs, `curl | sh`, secrets, billing, daemons, config edits, containers, ports, browser control, and file writes. |
| CLI エラー貼り付け診断 | ターミナルや PowerShell のエラーを貼ると、認証エラー、コマンド不足、ポート競合、権限エラー、怪しいログ文などを説明します。 | Lets you paste terminal/PowerShell errors and explains common causes such as npm auth errors, missing commands, port conflicts, permission errors, and suspicious log text. |
| 初心者向けの出力 | `secrets_or_auth` のようなラベルだけでなく、「これは何？ / なぜ確認？ / 次にすること」に変換します。 | Turns labels like `secrets_or_auth` into "what this means / why it matters / beginner next step." |

## スクリーンショット

### フォルダ / README の実行前チェック

![ローカルWebUIでフォルダの注意点を表示している画面](docs/assets/webui-preview.png)

### CLI エラー貼り付け診断

![npm認証エラーを説明するCLIエラー診断画面](docs/assets/cli-error-preview.png)

## クイックスタート

### Windows の WebUI

ダブルクリック:

```bat
起動する.bat
```

Python 3 が見つかれば、ローカル専用 WebUI が起動してブラウザが開きます。

```text
http://127.0.0.1:8765/
```

日本語名のランチャーもあります。

```bat
フォルダの中身チェックを起動する.bat
```

### WSL / macOS / Linux の WebUI

```bash
python3 management_webui/server.py
```

起動後、次を開いてください。

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

パッケージとしてインストールした後:

```bash
agent-assist-preflight path/to/candidate --format markdown
```

## やらないこと

このプロジェクトは、意図的に控えめな立ち位置です。これは **セキュリティスキャナではありません**。プロジェクトが安全であることを証明しません。

以下は行いません。

- 候補コマンドの実行
- 依存関係のインストール
- パッケージマネージャーの呼び出し
- MCP / Hermes / Claude / Codex / アプリ設定の変更
- 外部サービスへの接続
- ブラウザ、daemon、コンテナの起動
- 専門家レビュー、secret scanning、依存関係監査、sandboxing の代替

誤検知も見逃しも起こり得ます。目的は「完璧な安全判定」ではなく、初心者が実行前に読める形で一度止まれることです。

## 判定と優先度

レポートは、以下の3種類の decision を返します。

- `no_review_items_found`: 目立つレビュー項目は見つかりませんでした。ただし安全保証ではありません。
- `review_before_trying`: 試す前に、表示された項目を確認してください。
- `confirm_before_running`: このプロジェクトのコマンドを実行する前に、いったん止まって誰かに確認してください。

レビュー優先度:

- `confirm`: 明示的に確認するまで実行しない方がよい項目
- `review`: 内容を読み、可能なら使い捨てフォルダや dry-run から試したい項目
- `note`: 影響は比較的小さいが、知っておくとよい項目

互換性メモ: 古い JSON フィールドである `finding_count`, `max_severity`, `findings`, `human_approval_categories` も当面は出力します。新しい連携では `review_item_count`, `max_priority`, `review_items`, `confirmation_categories` を使ってください。

## 初心者向けの使い方

1. 候補プロジェクトに対して WebUI または CLI を実行する。
2. まず plain-language summary を読む。
3. 各 review item では、以下を読む。
   - `What this means`
   - `Why it matters`
   - `Beginner next step`
4. 本物の token を貼る、支払い情報を入れる、agent 設定を変える、daemon を起動する、グローバルインストールをする、といった操作は、該当項目を理解するまで行わない。
5. 可能なら、最初は使い捨てフォルダや隔離された workspace で試す。

詳しくは [docs/beginner-guide.md](docs/beginner-guide.md) を参照してください。

## エージェント向けローカル API

WebUI には、read-only の agent preflight 用ローカル API があります。WebUI を起動したあと、次を開いてください。

```text
http://127.0.0.1:8765/api
```

基本方針は保守的です。ローカル専用、read-only、外部 URL の自動 fetch なし、コマンド実行なしです。

## 開発

テスト実行:

```bash
python3 -m pytest -q
```

このヘルパーを自分自身に対して実行:

```bash
python3 preflight_checker.py . --format markdown --output self-preflight.md
```

バージョン確認:

```bash
python3 preflight_checker.py --version
python3 standalone.py --version
```

## ロードマップ

- pip, cargo, docker, systemctl などの CLI エラーパターン追加
- AWS, Azure, GCP, Slack, Discord などの秘密情報マスク強化
- 多言語ターミナルエラー説明の品質向上
- モバイル表示の改善
- ローカル AI 連携は、明示ボタン、マスク済みテキスト、確認画面、read-only、ツール権限なしの場合だけ optional で追加

## ライセンス

MIT.
