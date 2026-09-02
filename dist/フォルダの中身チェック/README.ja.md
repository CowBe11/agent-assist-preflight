# Agent Assist Preflight / AIエージェント初心者支援ツール

[![CI](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml/badge.svg)](https://github.com/CowBe11/agent-assist-preflight/actions/workflows/ci.yml)

## AIエージェントに任せる前の初心者支援ツール

[English README](README.md) | `v0.2.3 "Revival"` / リバイバル | 無料・オープンソース・ローカル専用

---

> **AIエージェントに任せる前の、人間の目。**
>
> Claude Code・Cursor・Codex・OpenCode・ChatGPT・Hermes などのAIエージェントとつなげて使える、ローカル専用の実行前レビュー・初心者支援ツールです。

Agent Assist Preflight は、AIエージェント、README、ターミナルエラーに押されて「よく分からないまま実行する」前に、いったん読める画面へ変えるツールです。旧来の「フォルダの中身チェック」だけではなく、AIエージェントからのURL確認、エラー相談前の秘密情報マスク、READMEの実行前確認までまとめて扱います。

はじめての人が置いていかれないように、画面も説明も「怖い言葉を減らす」「最後は自分で選べる」と分かることを大事にしています。

たとえば、こんな時に使います。

- エージェントが「このURLを開いて」と言ってきた
- README に `curl | sh`、`npm install -g`、`pip install`、daemon 起動が出てきた
- 赤いエラー文を ChatGPT や Claude に貼りたいけれど、秘密情報が混ざっていないか不安
- WSL / CUI / コンテナ環境で、ブラウザ連携がうまくいかない
- `PATH`、`pip`、`npm`、`daemon` などの言葉が怖い

```text
AIエージェント / README / ターミナルエラー
        ↓
ローカルで動く Agent Assist Preflight
        ↓
読みやすい確認カード
        ↓
あなたが判断: 開く / コピー / 無視 / 貼る / 止まる
```

## 60秒で試す

インストーラーもアカウントも不要です。まずクローンします。

```bash
git clone https://github.com/CowBe11/agent-assist-preflight.git
cd agent-assist-preflight
```

**Windows:** `起動する.bat` をダブルクリック。

**WSL / macOS / Linux:**

```bash
python3 management_webui/server.py
```

その後 `http://127.0.0.1:8765/` を開きます。最初は「これからセットアップしようとしていたリポジトリ」をフォルダ / README プリフライトにかけるのが一番分かりやすい試し方です。

## まず見るところ

| やりたいこと | 使う機能 |
|---|---|
| エージェントにブラウザを直接触らせず、URLだけ確認したい | **URLカード** |
| エラー文を外部AIへ貼る前に、秘密情報を隠したい | **エラー整形 + 秘密情報マスク** |
| ダウンロードしたリポジトリを実行前に軽く確認したい | **フォルダ / README プリフライト** |
| `daemon`、`PATH`、`pip`、`npm`、`secrets_or_auth` をやさしく知りたい | **用語辞典** |
| Python、pip、PATH、ポート、AIツール側のズレを見たい | **ローカルWebUIチェック** |

## いちばん大事な機能: URLカード

このツールの中心機能です。

AIエージェントがブラウザを直接操作できないことはよくあります。逆に、できたとしても、勝手にブラウザを開かせるのは不安です。

そこで Agent Assist Preflight では、エージェントがローカルAPIへ送る内容を2つだけにします。

1. URL
2. なぜ開きたいのか

WebUIにURLカードが表示されます。あなたは理由を読んでから選びます。

- **ブラウザで開く**
- **URLをコピー**
- **無視する**

![URLカード — エージェントの依頼、あなたが判断](docs/assets/url-card-preview.png)

```text
エージェント → ローカルAPI → URLカード → あなたが判断 → 承認した時だけブラウザで開く
```

エージェントが勝手にブラウザを開くことはありません。エージェントへ直接ブラウザ操作権限も渡しません。最後に決めるのはユーザーです。

## ほかに確認できること

### エラー整形 + 秘密情報マスク

赤いエラー文を貼ると、APIキー、トークン、パスワードなどの秘密情報らしき文字列をローカルでマスクし、外部AIに相談しやすいプロンプト形式へ整えます。

### フォルダ / README プリフライト

ダウンロードしたプロジェクトを実行する前に、README や設定系のテキストから次のような確認項目を拾います。

- グローバルインストール / `curl | sh`
- 秘密情報、トークン、認証、課金、支払いへの言及
- daemon / service / cron などの常駐化
- AIエージェント系設定ファイルの変更
- コンテナ、ポート、ブラウザ制御、外部ネットワーク、ファイル書き込み

判定は3段階です。

- `no_review_items_found` — 目立つ問題なし（安全の保証ではありません）
- `review_before_trying` — 試す前に確認を
- `confirm_before_running` — いったん止まって誰かに確認を

### 怖いCLI用語の辞典

初心者が怖がりやすい「黒い画面の言葉」を、次の3点で説明します。

- **これは何？**
- **なぜ確認するの？**
- **次にすること**

## 安全姿勢

このツールは**意図的に控えめな立ち位置**です。セキュリティスキャナではなく、プロジェクトが安全であることを証明しません。

基本方針は次の通りです。

- **確認対象のプロジェクトには read-only** — README等で見つけたコマンドを勝手に実行しません
- **local-only / ローカル専用** — WebUIはlocalhostだけで待ち受けます
- **固定の読み取り診断のみ** — WebUI自身の環境確認では、あらかじめ決めた読み取り系コマンドだけを使います
- **依存関係のインストールなし**
- **外部への自動送信なし**
- **勝手なブラウザ操作なし**

誤検知も見逃しも起こり得ます。目的は「完璧な安全判定」ではなく、**実行前に読める形で一度止まれること**です。

## スクリーンショット

現在あるスクリーンショット:

### フォルダ / README プリフライト

![ローカルWebUIでフォルダの確認結果を表示している画面](docs/assets/webui-preview.png)

### CLIエラー診断

![npm認証エラーを説明しているCLIエラー診断画面](docs/assets/cli-error-preview.png)

URLカード、用語辞典、`--format markdown` のスクリーンショットは今後追加予定です。まだ画像ファイルがないものは、リンク切れを避けるためREADMEには掲載していません。

---

## クイックスタート

### Windows（一番早い）

ダウンロードして、ダブルクリック:

```bat
起動する.bat
```

`起動する.bat` は、ローカルの Python WebUI を起動するための最小限のバッチです。依存関係のインストール、設定変更、外部送信は行いません。中身は、Python の存在確認、UTF-8設定、`standalone.py` の起動、メッセージ確認用の pause だけです。

もうひとつ、日本語名の起動補助ファイルもあります。

```bat
フォルダの中身チェックを起動する.bat
```

こちらは `起動する.bat` を呼び出すだけの短いファイルです。

Python 3 が入っていれば、ブラウザが自動で開きます。開かない場合:

```text
http://127.0.0.1:8765/
```

> Python 3 が入っているか確認したい場合: コマンドプロンプトで `python --version` または `python3 --version` を実行してください。

### WSL / macOS / Linux

```bash
python3 management_webui/server.py
```

起動後、ブラウザで開く:

```text
http://127.0.0.1:8765/
```

### CLI

```bash
# フォルダをチェック
python3 preflight_checker.py ./調べたいフォルダ --format markdown

# JSON形式で出力
python3 preflight_checker.py ./調べたいフォルダ --format json

# confirm項目があれば終了コードを返す
python3 preflight_checker.py ./調べたいフォルダ --fail-on confirm

# バージョン確認
python3 preflight_checker.py --version
```

パッケージとしてインストールした後:

```bash
agent-assist-preflight ./調べたいフォルダ --format markdown
```

---

## 初心者向けの使い方

1. WebUI または CLI を候補プロジェクトに対して実行する
2. まず plain-language summary（やさしい説明）を読む
3. 各確認項目で「これは何？ / なぜ確認するの？ / 次にすること」を読む
4. 本物のトークン、支払い情報、agent設定変更、グローバルインストールは、該当項目を理解するまで進めない
5. 可能なら、最初は使い捨てフォルダや隔離された環境で試す

詳しくは [docs/beginner-guide.md](docs/beginner-guide.md) を参照してください。

---

## エージェント向けローカルAPI

WebUI 起動後、ローカルAPIが使えます。

```text
http://127.0.0.1:8765/api
```

基本方針: **ローカル専用・確認対象プロジェクトにはread-only・固定の読み取り診断のみ・外部への自動fetchなし**。

URLカード機能はこのAPIから呼び出せます。想定する流れは次の通りです。

```text
POST /api/url-card { url, reason }
```

エージェントが頼む。あなたが理由を読む。あなたが判断する。

---

## ロードマップ

**最優先:**

- ダッシュボードGUIと、URLカード中心の導線改善

**安全レイヤーとして追加予定:**

- Agent config scan
  - `CLAUDE.md`、`agents.md`、`.cursorrules`、`.cursor/rules`、`.github/copilot-instructions.md`
  - 不審な指示、過剰権限、外部送信、秘密情報要求などを検出
- Token explosion / infinite loop warning
  - ディレクトリ全読み込み、巨大ログ、`node_modules`、`.venv`、`dist`、`build`、無限に読みそうな設定を警告
- Dangerous dependency / trap command detection
  - `curl | sh`、`sudo`、global install、外部ポート公開、`~/.ssh` / `.env` / token files へのアクセス示唆を警告
- Secret sending prevention
  - `.env`、API keys、SSH keys、OAuth tokens、billing / payment references の検出強化

**将来的な検討:**

- コマンド確認カード ✅ 実装済み（`POST /api/check-command`）
  - エージェントがコマンド実行前にリスク評価を依頼。low/medium/high の3段階で判定し、低リスク（`git status`など）はスルー、中リスク（`pip install`など）は任意確認、高リスク（`rm -rf`など）のみWebUI確認必須。
  - レスポンスには `risk`, `summary`, `ok_to_continue`, `user_attention`, `card_url` を含む。エージェントは `ok_to_continue` を見て続行可否を判断できる。
  - 拒否時は「説明が足りないかも」とヒントが返り、エージェントが説明を改善して再送できる（学習ループ）。
  - WebUI側はコマンド確認履歴パネルとして蓄積。高リスクカードだけ目立つ警告表示。
  - 設定 `command_card_mode`: silent（履歴のみ）/ smart（デフォルト・危険度に応じて）/ strict（毎回確認）/ off（無効）。
  - 今後の拡張: コピペ用質問文生成（段階2）、エージェントコールバック（段階3・エコシステム対応待ち）。

**その他の予定:**

- pip・cargo・docker・systemctl のCLIエラーパターン追加
- AWS・Azure・GCP・Slack・Discord の秘密情報マスク強化
- 多言語ターミナルエラー説明の品質向上
- モバイル表示の改善
- ローカルAI連携（明示ボタン・マスク済みテキスト・確認画面・read-only・ツール権限なし、の条件を満たす場合のみ）

---

## ライセンス

MIT — 無料で使えます。

---

*このツールは、AIエージェントに慣れていない人が「ちょっと待って」と言えるための道具です。完璧な安全を保証するものではありません。AIエージェントの提案を、人間が安全に受け取り、理由を読んで、開くか・無視するか・止まるかを決めるための補助輪です。*
