# Agent Assist Preflight 正式計画

発行日: 2026-06-02
状態: 正式計画 v0.1 / 共同レビュー開始
作業場所: `/mnt/e/hermes_kingdom/workspaces/agent-preflight-checker-publish`

## 1. 目的

Agent Assist Preflight は、初心者や AI コーディングエージェント利用者が、新しい CLI / MCP サーバー / installer / developer tool を試す前に、README や設定手順を落ち着いて読めるようにする read-only の実行前アシストである。

この計画の目的は、ツール本体だけでなく、初心者目線での「何が怖いのか」「次に何を確認すればいいのか」を共同で磨ける管理用 WebUI を用意し、ユーザーの物言いをそのまま開発タスクへ変換できる状態にすること。

## 2. 明確に名乗らないもの

このプロジェクトは以下を名乗らない。

- セキュリティスキャナ
- 脆弱性検出器
- sandbox
- safety guarantee
- exploit detector
- protection layer
- 監査完了ツール

理由: 実装も専門性も、そこまでの保証をまだ持っていないため。初心者を守るために強い言葉を使うのではなく、強い言葉を避けて、分かる言葉と確認手順を出す。

## 3. 製品の立ち位置

推奨する看板:

- read-only preflight assistant
- setup review notes
- beginner checklist
- confirm-before-running helper
- plain-language explanation layer

v1 の基本方針:

1. ローカルのテキストを読むだけ
2. 候補コマンドを実行しない
3. install しない
4. network fetch しない
5. 「危険/安全」ではなく「確認すべき項目」を出す
6. すべての review item に初心者向け説明を付ける

## 4. 利用形態の整理

現在の主役は CLI である。理由は、AIエージェント連携、CI連携、ローカル読み取り専用の検証がしやすく、依存も少ないため。

ただし、初心者個人ユーザーに CLI だけを強制するのは弱い。初心者は黒い画面や文字コマンドを見ただけで理解を拒みやすい。したがって、将来のユーザー向け形態として以下を正式に候補化する。

- 箱/ウィンドウ型の小さなローカル画面
- 日本語/英語などの言語切り替え
- レビュー項目や警告文のコピー機能
- ChatGPTなどに相談するためのコピー用テンプレート
- 「この内容をエージェントや詳しい人に聞いてください」と明示する初心者導線

現在の管理 WebUI はこの完成版ではない。あくまで共同レビュー用の作業机である。

## 5. 重要な出力契約

各 review item は必ず以下を持つ。

```text
Location: file and line
Matched text: short redacted excerpt
What this means: plain-language translation
Why it matters: practical beginner-level reason to pause
Beginner next step: concrete action before running commands
```

初心者レビューで特に見る観点:

- category 名だけで意味が分かるか
- 説明が怖がらせるだけになっていないか
- 次の行動が具体的か
- 「自分なら何を押せばいいか」が分かるか
- 誤検知のときにも納得できるか

## 6. 現在の成果物

CLI:

- `preflight_checker.py`
- entrypoint: `agent-assist-preflight`
- 互換 entrypoint: `agent-preflight-checker`

Docs:

- `README.ja.md`（日本語版。日本語ユーザーが外部チャット翻訳に頼らず読める入口）
- `README.md`
- `docs/beginner-guide.md`
- `docs/limitations.md`
- `docs/review-check-design.md`
- `docs/rule-design.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

Tests:

- `tests/test_preflight_checker.py`
- `tests/fixtures/danger/README.md`
- `tests/fixtures/safe/README.md`

管理用 WebUI:

- `management_webui/server.py`
- `management_webui/static/index.html`
- `management_webui/static/app.js`
- `management_webui/static/styles.css`
- `management_webui/data/review_comments.json`

## 7. 管理用 WebUI の役割

WebUI は公開向けの豪華ダッシュボードではない。共同制作のための作業机である。

v0.1 でできること:

- 正式計画をブラウザで読む
- README / beginner guide / limitations / review design を切り替えて読む
- 初心者目線のコメントを記録する
- コメントに対象セクション・優先度・状態を付ける
- open / accepted / fixed / parked として管理する
- 現在の CLI サンプル出力を確認する

v0.1 でやらないこと:

- GitHub Issue 同期
- ログイン
- 外部公開
- 任意コマンド実行
- AI 自動修正
- 本番 DB

## 8. 開発フェーズ

### Phase 0: 共同レビュー台の作成

状態: 今回実施。

- 正式計画を発行する
- 管理用 WebUI を作る
- コメント保存先を作る
- ローカル起動を確認する

完了条件:

- `python3 management_webui/server.py` で起動する
- `http://127.0.0.1:8765/` で表示できる
- コメントを追加できる
- コメントが `management_webui/data/review_comments.json` に保存される

### Phase 1: 初心者レビュー反映ループ

ユーザーが WebUI を見ながら物言いを付ける。私はそれを受けて以下に分類する。

- 文言修正
- review check の追加/削除
- beginner next step の改善
- README構成変更
- テスト追加
- CLI仕様変更

完了条件:

- 主要コメントが open ではなく accepted / fixed / parked に分類される
- 反映済みコメントには変更ファイルが紐づく

### Phase 1.5: 初心者向けウィンドウ版の設計検討

CLIを怖がる初心者のために、CLI本体を薄く包むローカル画面を検討する。

候補:

- フォルダ/ファイルのパスを入力してブラウザから試す（v0.1で最低限実装）
- 言語を切り替える
- Markdown/JSONを見なくてもレビュー項目が読める（v0.1で最低限実装）
- レビュー項目を1クリックでコピーする
- ChatGPTなどに聞くための相談文をコピーする

反論/保留点:

- 完成GUIまで作ると範囲が広がりすぎる
- ただし、作者本人がCLIで試せない状態は初心者向けとして破綻している
- よって v0.1 では「ブラウザから対象パスを入力してread-only診断する」最低限の試用欄を実装し、完成GUIは後続に回す

### Phase 2: explain / checklist 機能

候補:

- `agent-assist-preflight explain "curl ... | bash"`
- `agent-assist-preflight checklist path/to/project`
- WebUI からサンプル文章を貼って説明を確認

完了条件:

- 初心者が「このコマンドを貼ったら何が起きるか」を読み取れる
- 実行はしない

### Phase 3: fixture と評価セット拡張

追加したい fixture:

- billing / subscription
- daemon / cron / service
- config mutation
- browser automation
- destructive command
- token required
- negation: “No API key required”

完了条件:

- 誤検知・過検知がコメントとして管理される
- 主要ケースが unittest で固定される

### Phase 4: 公開準備

公開する場合でも、看板は beginner assist とする。

公開前チェック:

- README が過大主張していない
- `SECURITY.md` が「security scannerではない」と明示している
- secretっぽい値が混入していない
- `python3 -m unittest discover -s tests -v` が通る
- `git add -n .` で公開対象を確認する

## 9. 運用ルール

1. ユーザーコメントはまず否定しない。
2. 初心者が引っかかった箇所は、実装者にとって自然でも改善候補にする。
3. 「安全」という言葉で雑に締めない。
4. 「怖い」より「確認すれば進める」を優先する。
5. ルール追加より、説明と次の行動を優先する。
6. Hard Guard は opt-in にする。
7. WebUI はローカル専用。外部公開しない。

## 10. 次にやること

- WebUIを見ながら、まず README 冒頭と decision 名に物言いを付ける
- コメントを open で貯める
- 1まとまりごとに私がコード・docs・testsへ反映する
- 反映後、コメント状態を fixed にする
