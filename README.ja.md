# Agent Assist Preflight

[English README](README.md)

Agent Assist Preflight は、知らない開発ツールを試す前に「この手順、本当にそのまま実行していいのかな？」を確認するための、小さな read-only ヘルパーです。

たとえば、新しい CLI、MCP サーバー、インストーラー、AI エージェント用ツールを clone したあと、README に書かれた `npm install`、`curl | sh`、`.env`、daemon 設定などをいきなり貼り付ける前に使います。

このツールはプロジェクトを安全判定するものではありません。README や設定ファイル風のテキストを読むだけで、実行前に確認した方がよい行を、初心者にも読める説明に変換します。

- その行がたぶん何を意味しているか
- なぜ一度止まって確認した方がよいか
- 次に何を聞く・確認するべきか

![初心者向けの確認項目を表示する Agent Assist Preflight の画面](docs/assets/webui-preview.png)

## これは何をするツール？

Agent Assist Preflight は、指定したフォルダやテキストファイルの中から、セットアップ時に見落としやすい注意点を探します。

見つかった行には、次のような説明を付けます。

```text
これは何？: トークン、パスワード、APIキー、OAuth、.env ファイルについて書かれています。
なぜ確認？: 秘密情報は、ログ、履歴、スクリーンショット、コミット、AIエージェントの文脈に漏れることがあります。
次にすること: 最初はダミー値を使ってください。本物の秘密情報を貼る前に、どこへ保存されるか確認してください。
```

主な対象は、次の人たちです。

- CLI や MCP や開発ツールを試し始めた初心者
- AI コーディングエージェントに作業を頼む人
- 新しいリポジトリを clone した後、README のコマンドをそのまま貼るのが不安な人
- エージェントが `npm install`、`curl | sh`、`.env`、daemon 設定へ進む前に、人間確認の合図を挟みたい人

## できること

- README、`.md`、`.txt`、`.py`、`.json` などのテキストファイルを読む
- グローバルインストール、秘密情報、課金、常駐サービス、設定変更などの説明を拾う
- Markdown または JSON で結果を出す
- ブラウザ画面からフォルダやテキストファイルを試す
- 結果をコピーして ChatGPT などに相談しやすくする

## やらないこと

このプロジェクトは、意図的に控えめな立ち位置です。

これは **セキュリティスキャナではありません**。プロジェクトが安全かどうかを判定しません。sandbox でもありません。インストール、実行、取得、変更も行いません。知らないコマンドを走らせる前に、一度ゆっくり読めるようにする read-only の実行前アシスタントです。

## まず最初に: 開き方（一番簡単な方法）

**Windows の人:**

フォルダの中にある `起動する.bat` を**ダブルクリック**してください。`フォルダの中身チェックを起動する.bat` でも同じ画面を開けます。

Python が見つかれば、黒い画面が出たあとブラウザが自動で開きます。自動で開かない場合は、表示された次のURLをブラウザに貼り付けてください。

```
  👉 ブラウザが自動で開きます。開かない場合は下のURLをコピー：
     http://127.0.0.1:8765/
```

**WSL / Mac / Linux の人:**

```bash
python3 management_webui/server.py
```

起動後、表示された `http://127.0.0.1:8765/` を Ctrl+クリック、またはブラウザに貼り付けてください。

画面を閉じるときは、黒い画面で `Ctrl+C` を押してから閉じてください。

---

## CLI版もあります

上記のブラウザ版のほかに、ターミナルで直接使う CLI 版もあります：

```bash
python3 preflight_checker.py path/to/candidate --format markdown
```

パッケージとしてインストールした後は：

```bash
agent-assist-preflight path/to/candidate --format markdown
```

ブラウザ版では、診断結果やChatGPTなどへ相談するための文面をコピーできます。

## なぜ作るのか

初心者や AI エージェント利用者は、よく同じ問題にぶつかります。

> 「警告は出たけど、結局それが何を意味しているのか分からない」

Agent Assist Preflight は、`high risk: secrets_or_auth` のようなラベルだけの警告を避けます。代わりに、初心者向けの説明と次の行動を出します。

```text
What this means: トークン、パスワード、APIキー、OAuth、.env ファイルについて書かれています。
Why it matters: 秘密情報は、ログ、シェル履歴、スクリーンショット、コミット、AIエージェントの文脈に漏れることがあります。
Beginner next step: 読んでいる段階ではダミー値を使ってください。どこに保存されるか分かるまで、本物の秘密情報を貼らないでください。
```

## 設計方針

- デフォルトで read-only
- ネットワークアクセスなし
- 依存関係のインストールなし
- 候補コマンドの実行なし
- sandbox だと名乗らない
- 安全保証をしない
- Python 標準ライブラリのみ
- 怖がらせる前に説明する
- デフォルトはブロックではなくソフトな補助

将来 SecWall 風の強いガード機能を追加する場合も、明示的な opt-in にします。デフォルトモードは、ユーザーが理解して判断するための補助であり、ワークフローを勝手に乗っ取るものではありません。

## クイックスタート

```bash
python3 preflight_checker.py path/to/candidate --format markdown
python3 preflight_checker.py path/to/candidate --format json
python3 preflight_checker.py path/to/candidate --exclude 'tests/fixtures/**'
python3 preflight_checker.py path/to/candidate --fail-on confirm
```

例:

```bash
python3 preflight_checker.py tests/fixtures/danger --format markdown
```

## 判定

レポートは、以下の3種類の decision を返します。

- `no_review_items_found`: 目立つレビュー項目は見つかりませんでした。ただし安全保証ではありません。
- `review_before_trying`: 試す前に、表示された項目を確認してください。
- `confirm_before_running`: このプロジェクトのコマンドを実行する前に、いったん止まって誰かに確認してください。

レビュー優先度:

- `confirm`: 明示的に確認するまで実行しない方がよい項目
- `review`: 内容を読み、可能なら使い捨てフォルダや dry-run から試したい項目
- `note`: 影響は比較的小さいが、知っておくとよい項目

互換性メモ: 古い JSON フィールドである `finding_count`, `max_severity`, `findings`, `human_approval_categories` も当面は出力します。新しい連携では `review_item_count`, `max_priority`, `review_items`, `confirmation_categories` を使ってください。

## 現在チェックする内容

実行前に確認したい項目:

- 破壊的な削除・リセットコマンド
- グローバルインストールや `curl | sh` 形式のセットアップ
- token / password / API key / .env に関する説明
- 課金・有料・サブスクリプションに関する説明
- daemon / cron / service のセットアップ
- Agent / MCP / Hermes / Claude の設定変更
- 明らかなコマンド実行パターン

試す前にレビューしたい項目:

- 外部ネットワークアクセス
- ファイルシステムへの書き込み
- コンテナやVM
- よく使われるローカルポート
- ブラウザ自動操作やブラウザ制御

メモ程度の項目:

- ローカルファイル読み取り
- dry-run / read-only / preview のヒント

## WebUI について

ブラウザから使える確認画面があります。

**Windows:** `起動する.bat` をダブルクリック。
**それ以外:** `python3 management_webui/server.py`

起動後、表示された `http://127.0.0.1:8765/` を開いてください。
詳しくは上の「開き方」セクションを見てください。

WebUI では次のことができます：

- フォルダのパスを入れて中身をチェック（🔍 試すタブ）
- README などのドキュメントを読む（📖 読むタブ）
- 表示や機能のカスタマイズリクエストをためる（🔧 カスタマイズタブ）

リクエストは `management_webui/data/review_comments.json` に保存されます。
デフォルトでは `127.0.0.1` にだけ bind します。公開サーバーとしては動かしません。

## 出力形式

Markdown:

```bash
python3 preflight_checker.py tests/fixtures/danger --format markdown
```

JSON:

```bash
python3 preflight_checker.py tests/fixtures/danger --format json
```

CI風のゲート:

```bash
python3 preflight_checker.py tests/fixtures/danger --format json --fail-on confirm
```

終了コード:

- `0`: 完了。指定した失敗しきい値には到達していません。
- `2`: 完了。指定した `--fail-on` しきい値に到達しました。

`--fail-on medium` と `--fail-on high` は互換用エイリアスとして残しています。内部的には `review` と `confirm` に対応します。

## 初心者向けの使い方

1. 候補プロジェクトに対して preflight を実行する。
2. まず plain-language summary を読む。
3. 各 review item では、以下を読む。
   - `What this means`
   - `Why it matters`
   - `Beginner next step`
4. 本物の token を貼る、支払い情報を入れる、agent 設定を変える、daemon を起動する、グローバルインストールをする、といった操作は、該当項目を理解するまで行わない。
5. 可能なら、最初は使い捨てフォルダや隔離された workspace で試す。

より詳しい手順は `docs/beginner-guide.md` を参照してください。

## 範囲と限界

このヘルパーは、指定したパス以下のテキストファイルだけを読みます。以下は行いません。

- 候補コマンドの実行
- 依存関係のインストール
- パッケージマネージャーの呼び出し
- MCP / Hermes / Claude / Codex 設定の変更
- 外部サービスへの接続
- ブラウザ、daemon、コンテナの起動
- プロジェクトが安全であることの証明
- 専門家レビュー、secret scanning、依存関係監査、sandboxing の代替

誤検知も見逃しも起こり得ます。

詳しくは `docs/limitations.md` を参照してください。

## 開発

テスト実行:

```bash
python3 -m unittest discover -s tests -v
```

このヘルパーを自分自身に対して実行:

```bash
python3 preflight_checker.py . --format markdown --output self-preflight.md
```

## ロードマップ

このリポジトリは、初心者向け agent assist kit の小さくきれいな中核として育てます。

- より分かりやすい review check と例
- 初心者プロファイルとセットアップチェックリスト
- command explainer mode
- エージェント作業用 scope planner: 読み書き許可範囲、禁止パス、停止条件
- 明示的に有効化した場合だけの SecWall 風 hard guard wrapper
- SARIF / GitHub code scanning 出力
- MCP / Hermes / Claude / Codex 用 review check pack

## ライセンス

MIT.
