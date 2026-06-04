// ══════════════════════════════════════════════
//  i18n — English / Japanese language switching
// ══════════════════════════════════════════════

const LANG_KEY = 'preflight-lang';
let currentLang = localStorage.getItem(LANG_KEY) || (navigator.language.startsWith('ja') ? 'ja' : 'en');

const i18n = {
  ja: {
    // Static HTML text keys (for restoring from English)
    'site.title': 'フォルダの中身チェック — 無料の安全確認ツール',
    'site.eyebrow': 'ダウンロードしたプロジェクトを、実行する前にチェック　🆓 完全無料・オープンソース',
    'site.h1': 'フォルダの中身チェック',
    'tab.try': '🔍 試す', 'tab.docs': '📖 読む', 'tab.glossary': '📚 用語辞典',
    'tab.beginner': '🌱 初心者支援', 'tab.customize': '🔧 カスタマイズ',
    'try.h2': 'ダウンロードしたフォルダの README やテキストファイルをチェック',
    'try.desc': 'README、.md、.txt、.py などの<strong>テキストファイル</strong>を読み取って、「インストールするとPC全体に影響しそう」「秘密情報が書いてあるかも」といった<strong>心配な部分を日本語で説明</strong>します。<br>画像や動画、zip などは対象外です。フォルダを入れると中のテキストファイルだけを見ます。',
    'try.placeholder': '例: /mnt/c/Users/.../Downloads/tool （フォルダかテキストファイルのパス）',
    'try.submit': 'このフォルダを確認する',
    'try.pickBtn': 'フォルダ/ファイルを選ぶ...',
    'try.pickStatus': 'Windowsの見慣れた「開く」ダイアログが開きます',
    'try.dropTitle': 'ここにテキストファイルをドラッグ＆ドロップ',
    'try.dropDesc': 'README、.txt、.md を 1 つだけ投げると中身をチェックします (1MB まで)',
    'try.emptyMsg': 'まだ実行していません。ダウンロードしたフォルダのパスを入れるか、README などのテキストファイルをドラッグ＆ドロップしてください。',
    'try.copyBtn': '診断結果をコピー',
    'try.copyHint': 'ChatGPT などに貼って相談できます',
    'try.copyWarn': '⚠️ 貼る前に、実際のパスワードやトークンが含まれていないか自分の目で確認してください。見つかった場合は <strong>その部分を消してから</strong>貼ってください。<br>（<strong>[REDACTED]</strong> と表示されている部分はツールが自動でマスク済みです）',
    'docs.eyebrow': 'ドキュメント', 'docs.loading': '読み込み中...',
    'docs.copyBtn': 'この文書をコピー',
    'glossary.eyebrow': '分からない言葉をやさしく解説',
    'glossary.h2': '用語辞典',
    'glossary.desc': 'ソフトやプログラミングの用語を、<strong>やさしい言葉で</strong>検索・一覧できます。<br>下の検索欄に入れたり、スクロールして気になる言葉を探してください。',
    'glossary.placeholder': '🔍 調べたい言葉を入力（例: sudo, CLI, コミット...）',
    'glossary.loading': '読み込み中...',
    'beginner.eyebrow': 'バイブコーディングを楽しむための補助輪',
    'beginner.h2': '🌱 バイブコーディング初心者支援機能',
    'beginner.desc': 'AIエージェントやバイブコーディングを始める人が、つまずきにくくなるための機能をまとめています。<br>下から使いたい機能を選んでください。',
    'port.title': '🔢 今どのポート使ってる？ — ポート取り合いチェッカー',
    'port.introBold': '今このPCで、どのポートがどのプロセスに使われているかを一覧します。',
    'port.introDesc': '開発サーバーやMCP、VOICEVOX、ローカルLLMなどがポートを占有していて、<br>新しいツールが起動できないことがあります。「今誰が使ってんの？」を確認できます。<br>よく使われるポートには「VOICEVOX」「ComfyUI」など用途候補も表示します。',
    'port.safeNote': '📖 <strong>見るだけ</strong>です。ポートを塞いだり、プロセスを停止したり、設定を書き換えたりはしません。',
    'port.scanBtn': '🔍 今使われているポートを一覧',
    'port.nextTitle': 'このあとどうすればいい？',
    'tools.title': '🧰 基本道具チェック — AIエージェントの作業前確認',
    'tools.introBold': 'Python、Node.js、npm、Git、GitHub CLI、PowerShell、WSL、Docker が使えるかを確認します。',
    'tools.introDesc': 'Windows側にあるか、WSL/エージェント側にあるかがズレると、AIエージェントが「入っているはずなのに使えない」で止まることがあります。',
    'tools.safeNote': '📖 <strong>見るだけ</strong>です。インストール、更新、ログイン、Docker起動、設定変更はしません。',
    'tools.checkBtn': '🔍 基本道具をチェック',
    'tools.nextTitle': 'エージェントが見た時の導線チェック',
    'review.eyebrow': 'UIや機能の調整をリクエスト',
    'review.h2': 'カスタマイズリクエスト',
    'review.refreshBtn': '更新',
    'review.desc': '表示や機能について「ここをこうしてほしい」というリクエストをためられます。<br>ここで出したリクエストはチケットとして記録され、<strong>AIエージェントやバイブコーディングツールに「これ直して」とお願いするための材料</strong>になります。<br>画面は自動では変わりません。直し方は：<br>① 下の「リクエストをコピー」で内容をコピー<br>② このプロジェクトのフォルダを <strong>Cursor や Claude Code などのバイブコーディングツールで開く</strong><br>③ コピーしたリクエストを貼り付けて「これ直して」と依頼する',
    'review.sectionLabel': '対象セクション',
    'review.sectionPlaceholder': '例: README冒頭 / decision名 / WebUI',
    'review.priorityLabel': '優先度',
    'review.reactionLabel': 'どんなふうに変えてほしい？',
    'review.reactionPlaceholder': '例: もっと簡単な言葉で / ボタンを大きく / 順番を変えて',
    'review.textLabel': 'リクエスト内容',
    'review.textPlaceholder': '例: confirm_before_running は『実行前に確認』と表示してほしい',
    'review.submitBtn': 'リクエストを追加',
    'urlcard.title': 'エージェントがURLを開きたがっています',
    'urlcard.reason': '理由:',
    'urlcard.url': 'URL:',
    'urlcard.open': '開く',
    'urlcard.copy': 'コピー',
    'urlcard.dismiss': '無視',
    'urlcard.opened': '開きました',
    'urlcard.copied': 'コピーしました',
    'urlcard.none': '現在保留中のURLカードはありません。',
    // Dynamic-rendering keys only
    'yes': 'あり', 'no': 'なし',
    'checking': 'チェック中...', 'error.prefix': 'エラー: ',
    'fetching.ports': 'ポート情報を取得しています...',
    'fetching.tools': '基本道具を確認しています...',
    'scan.checking': '確認中...', 'scan.error': '確認できませんでした',
    'scan.items': '件の確認項目', 'scan.decision': '判定',
    'scan.maxPriority': '最大優先度', 'scan.confirmItems': '確認項目',
    'scan.rerun': '🔄 別のフォルダでやり直す', 'scan.expandAll': '全部ひらく',
    'scan.collapseAll': '全部たたむ', 'scan.clear': '✕ 結果をしまう',
    'port.listenLabel': 'ポートがLISTEN中', 'port.knownTitle': '🟢 用途がわかっているポート',
    'port.unknownTitle': '⚠️ 見慣れないポート（外から見える可能性）',
    'port.collapsedTitle': '🔒 見慣れないポート（自分だけ）',
    'port.headers': ['ポート','プロセス','PID','説明','相談'],
    'port.selfBadge': 'このツール', 'port.unknownBadge': '見慣れない',
    'port.aiTitle': '🤖 AI/MCP候補まとめ',
    'port.aiDesc': 'ポート一覧の中から、AIエージェント・MCP・ローカルLLM・VOICEVOX・ComfyUI・ブラウザ操作に関係しそうなものだけを先にまとめました。',
    'port.aiEmptyTitle': '🤖 AI/MCP候補まとめ',
    'port.aiEmptyDesc': 'よく知られたAI・MCP・ローカルLLM系ポートは見つかりませんでした。これは「何も使えない」という意味ではなく、今このPCで待ち受けているものからは候補を拾えなかった、という意味です。',
    'port.aiCopy': '📋 AIに聞く文をコピー',
    'port.aiNote': '📖 見つかった候補は「使えるかもしれない入口」です。MCPとして本当に使えるか、安全に接続できるかは、そのツールの設定と説明を確認してください。',
    'port.consultUnknown': '見慣れない待ち受け — 何のソフトか確認してみてください',
    'tools.confirmed': '個の基本道具を確認', 'tools.copyMemo': '📋 AIに渡す確認メモをコピー',
    'tools.agentRoute': '🤖 AIエージェント向け導線',
    'tools.agentDesc': 'エージェントは「自分が動いている側」にある道具しかそのまま使えません。Windows側だけにある道具をWSL側エージェントが使う作業では失敗することがあります。',
    'tools.agentMissing': 'エージェント側で見つからない道具',
    'tools.windowsOnly': 'Windows側だけで見つかった道具',
    'tools.noAutoInstall': '不足があっても、勝手にインストールせず、まずユーザーに確認してください。',
    'tools.headers': ['道具','状態','バージョン','実行コマンド','Windows側','エージェント側','説明 / 注意'],
    'tools.statusBoth': 'Windows側にもWSL/エージェント側にもあります',
    'tools.statusAgentOnly': 'エージェントが使う側にはあります',
    'tools.statusWindowsOnly': 'Windows側にはありますが、エージェント側では見つかりません',
    'tools.statusMissing': '見つかりません',
    'comments.empty': 'この状態のリクエストはまだ無い。',
    'comments.copy': 'このリクエストをコピー', 'comments.reaction': '反応:',
    'comments.workNote': '作業メモ:',
    'scan.introTitle': '📋 このツールがやること（毎回確認）',
    'scan.legendTitle': '🔍 このスキャンで検出された話題',
    'scan.legendHint': '下に続く各カードに付いている絵文字の意味です。専門用語にカーソルを合わせると解説が出ます。',
    'scan.nextTitle': '👉 このあとどうすればいい？',
    'scan.freeNote': '🆓 このツールは完全無料・オープンソースです。お金は一切かかりません。',
    'glossary.noMatch': 'に一致する用語は見つかりませんでした。別の言葉で試してください。',
    'help.destructive_delete': ['削除・リセット系のコマンドが書かれています。', '違うフォルダで実行すると、作業ファイルや設定を消す可能性があります。', 'まだ実行しないでください。何を消すのか、バックアップやdry-runがあるか確認してください。'],
    'help.global_install': ['グローバルインストール、またはダウンロードしたスクリプトをそのまま実行する手順が書かれています。', 'プロジェクトフォルダの外までPC環境を変える可能性があります。', 'まずローカルインストール、仮想環境、使い捨てフォルダで試せるか確認してください。sudo、-g、curl | sh は人に確認してから。'],
    'help.secrets_or_auth': ['トークン、パスワード、APIキー、OAuth、.env などの秘密情報について書かれています。', '秘密情報はログ、履歴、スクリーンショット、コミット、AIエージェントの文脈に漏れることがあります。', '最初はダミー値を使ってください。本物の秘密情報を貼る前に、どこへ保存されるか確認してください。'],
    'help.paid_or_billing': ['課金、有料プラン、クレジットカード、quota、credits について書かれています。', '設定後にお金がかかったり、有料API枠を消費する可能性があります。', '支払い情報はエージェント経由で入れず、料金の発生条件を自分で確認してください。'],
    'help.daemon_or_cron': ['daemon、service、cron、バックグラウンド常駐について書かれています。', 'ターミナルを閉じても動き続け、初心者には止め方が分かりにくいことがあります。', '起動する前に、停止・無効化・アンインストール方法を確認してください。'],
    'help.config_mutation': ['Agent、MCP、Claude、Hermes、アプリ設定ファイルを変更する手順かもしれません。', '今後のエージェント実行や別プロジェクトにも影響する可能性があります。', '変更前に設定ファイルをバックアップし、どのファイルが変わるか確認してください。'],
    'help.remote_code_execution': ['eval、exec、subprocess、shell実行など、コードやコマンドを実行する仕組みが見えます。', '内容次第でPC上のコマンドを実行できます。', '周辺コードを読み、何を実行するのか分かるまで動かさないでください。'],
    'help.external_network': ['外部Web/API/ネットワークアクセスについて書かれています。', 'データが外へ送られたり、外部サービスに依存する可能性があります。', '何を送るのか、オフライン/ローカルモードがあるか確認してください。'],
    'help.filesystem_write': ['ファイルの作成、コピー、移動、書き込みについて書かれています。', '意図しない場所のファイルを上書きする可能性があります。', '書き込み先パスを確認し、最初は使い捨てフォルダで試してください。'],
    'help.container_or_vm': ['Docker、Kubernetes、Vagrantなどのコンテナ/VMについて書かれています。', '隔離っぽく見えても、ローカルフォルダのマウント、ポート、ディスク使用、常駐が起こります。', 'volume、port、cleanup手順を確認してから起動してください。'],
    'help.ports': ['ローカルポートを使うWebアプリやエージェントについて書かれています。', '他のローカルツールと競合したり、意図せずサービスが見える場合があります。', 'そのポートが使用中か、localhostだけにbindするか確認してください。'],
    'help.browser_control': ['ブラウザ自動操作やリモートブラウザ制御について書かれています。', 'ログイン済みブラウザや個人データに触れる可能性があります。', '専用ブラウザプロファイルを使い、最初は個人アカウントのページを避けてください。'],
    'help.local_read': ['ローカルファイルやDBを読む処理について書かれています。', '読み取り自体は低影響でも、内容がログやレポートに出ることがあります。', '最初は個人情報のないフォルダで試してください。'],
    'help.dry_run_hint': ['dry-run、preview、read-only など、変更しない試用モードのヒントがあります。', '学習中の最初の一歩として使いやすいモードです。', '変更するコマンドの前に、まずdry-run/previewを試してください。'],
    'cat.destructive_delete': '削除・リセット系', 'cat.global_install': 'インストール操作',
    'cat.secrets_or_auth': '秘密情報', 'cat.paid_or_billing': '課金・クレジット',
    'cat.daemon_or_cron': '常駐サービス', 'cat.config_mutation': '設定ファイル書き換え',
    'cat.remote_code_execution': 'コード/コマンド実行', 'cat.external_network': '外部ネットワーク通信',
    'cat.filesystem_write': 'ファイル書き込み', 'cat.container_or_vm': 'コンテナ/VM',
    'cat.ports': 'ローカルポート使用', 'cat.browser_control': 'ブラウザ自動操作',
    'cat.local_read': 'ローカル読み取り', 'cat.dry_run_hint': '試用モードのヒント',
  },
  en: {
    // Static HTML text (applied via data-i18n)
    'site.title': 'Folder Contents Check — Free Safety Review Tool',
    'site.eyebrow': 'Check downloaded projects before running them 🆓 Free & Open Source',
    'site.h1': 'Folder Contents Check',
    'tab.try': '🔍 Try', 'tab.docs': '📖 Read', 'tab.glossary': '📚 Glossary',
    'tab.beginner': '🌱 Beginner Help', 'tab.customize': '🔧 Customize',
    'try.h2': 'Check README and text files in downloaded folders',
    'try.desc': 'Reads <strong>text files</strong> like README, .md, .txt, .py and explains <strong>risky parts in plain language</strong> — such as "this may affect your whole PC" or "this may contain secrets".<br>Images, videos, zip files are not scanned. Dropping a folder only reads text files inside.',
    'try.placeholder': 'e.g. /mnt/c/Users/.../Downloads/tool (folder or text file path)',
    'try.submit': 'Check this folder',
    'try.pickBtn': 'Choose folder/file...',
    'try.pickStatus': 'Opens a familiar Windows "Open" dialog',
    'try.dropTitle': 'Drag & drop a text file here',
    'try.dropDesc': 'Drop one README, .txt, or .md file to check its contents (up to 1MB)',
    'try.emptyMsg': 'Not yet run. Enter a path to a downloaded folder, or drag & drop a README or text file.',
    'try.copyBtn': 'Copy scan results',
    'try.copyHint': 'Paste into ChatGPT or ask someone for help',
    'try.copyWarn': '⚠️ Before pasting, check that no real passwords or tokens are included. If found, <strong>remove them first</strong>.<br>(Parts shown as <strong>[REDACTED]</strong> are automatically masked by the tool.)',
    'docs.eyebrow': 'Documentation', 'docs.loading': 'Loading...',
    'docs.copyBtn': 'Copy this document',
    'glossary.eyebrow': 'Simple explanations for unfamiliar terms',
    'glossary.h2': 'Glossary',
    'glossary.desc': 'Search and browse <strong>software and programming terms</strong> in simple language.<br>Type in the search box below or scroll to explore.',
    'glossary.placeholder': '🔍 Search terms (e.g. sudo, CLI, commit...)',
    'glossary.loading': 'Loading...',
    'beginner.eyebrow': 'Training wheels for vibe coding',
    'beginner.h2': '🌱 Vibe Coding Beginner Support',
    'beginner.desc': 'Features to help beginners and AI agent users get started with fewer obstacles.<br>Choose a feature below.',
    'port.title': '🔢 Who\'s using my ports? — Port conflict checker',
    'port.introBold': 'Lists which ports are in use by which processes on this PC.',
    'port.introDesc': 'Dev servers, MCP tools, VOICEVOX, local LLMs and others may hold ports,<br>preventing new tools from starting. Find out "who\'s using it?"<br>Common ports show usage hints like "VOICEVOX" or "ComfyUI".',
    'port.safeNote': '📖 <strong>Read-only.</strong> It won\'t block ports, stop processes, or change settings.',
    'port.scanBtn': '🔍 List listening ports',
    'port.nextTitle': 'What to do next',
    'tools.title': '🧰 Tool Check — Pre-work check for AI agents',
    'tools.introBold': 'Checks whether Python, Node.js, npm, Git, GitHub CLI, PowerShell, WSL, and Docker are available.',
    'tools.introDesc': 'If tools are missing on the agent side (WSL) but present on Windows, AI agents may stop with "command not found".',
    'tools.safeNote': '📖 <strong>Read-only.</strong> No install, update, login, Docker start, or settings change.',
    'tools.checkBtn': '🔍 Check basic tools',
    'tools.nextTitle': 'Agent workflow check',
    'review.eyebrow': 'Request UI or feature changes',
    'review.h2': 'Customization Requests',
    'review.refreshBtn': 'Refresh',
    'review.desc': 'You can collect requests like "change this part of the UI".<br>Requests are recorded as tickets — <strong>use them as input when asking AI agents or vibe coding tools to fix the app</strong>.<br>The screen won\'t change automatically.<br>How to apply:<br>① Copy the request with "Copy request" below<br>② Open this project folder in <strong>Cursor, Claude Code or another vibe coding tool</strong><br>③ Paste the request and ask "fix this"',
    'review.sectionLabel': 'Target section',
    'review.sectionPlaceholder': 'e.g. README header / decision name / WebUI',
    'review.priorityLabel': 'Priority',
    'review.reactionLabel': 'How should it change?',
    'review.reactionPlaceholder': 'e.g. Use simpler words / Make button bigger / Change order',
    'review.textLabel': 'Request details',
    'review.textPlaceholder': 'e.g. I want confirm_before_running to show as "Confirm before running"',
    'review.submitBtn': 'Add request',
    'urlcard.title': 'Agent wants to open a URL',
    'urlcard.reason': 'Reason:',
    'urlcard.url': 'URL:',
    'urlcard.open': 'Open',
    'urlcard.copy': 'Copy',
    'urlcard.dismiss': 'Dismiss',
    'urlcard.opened': 'Opened',
    'urlcard.copied': 'Copied',
    'urlcard.none': 'No pending URL cards.',
    // Dynamic-rendering keys
    'yes': 'Yes', 'no': 'No',
    'checking': 'Checking...', 'error.prefix': 'Error: ',
    'fetching.ports': 'Fetching port info...',
    'fetching.tools': 'Checking basic tools...',
    'scan.checking': 'Checking...', 'scan.error': 'Could not check',
    'scan.items': 'review items', 'scan.decision': 'Decision',
    'scan.maxPriority': 'Max priority', 'scan.confirmItems': 'Review items',
    'scan.rerun': '🔄 Try another folder', 'scan.expandAll': 'Expand all',
    'scan.collapseAll': 'Collapse all', 'scan.clear': '✕ Hide results',
    'port.listenLabel': 'ports listening', 'port.knownTitle': '🟢 Known ports',
    'port.unknownTitle': '⚠️ Unfamiliar ports (may be externally visible)',
    'port.collapsedTitle': '🔒 Unfamiliar ports (local only)',
    'port.headers': ['Port','Process','PID','Description','Ask AI'],
    'port.selfBadge': 'This tool', 'port.unknownBadge': 'Unfamiliar',
    'port.aiTitle': '🤖 AI/MCP Tool Candidates',
    'port.aiDesc': 'From the port list, we highlighted ports related to AI agents, MCP, local LLM, VOICEVOX, ComfyUI, and browser automation.',
    'port.aiEmptyTitle': '🤖 AI/MCP Tool Candidates',
    'port.aiEmptyDesc': 'No well-known AI/MCP/local LLM ports were found. This doesn\'t mean nothing works — it just means nothing was detected among currently listening ports.',
    'port.aiCopy': '📋 Copy text to ask AI',
    'port.aiNote': '📖 Found candidates are "possible entry points." Whether they\'re actually usable as MCP, and whether you can connect safely, depends on each tool\'s configuration.',
    'port.consultUnknown': 'Unfamiliar listener — try checking what software this is',
    'tools.confirmed': 'basic tools checked', 'tools.copyMemo': '📋 Copy check memo for AI',
    'tools.agentRoute': '🤖 AI Agent Workflow',
    'tools.agentDesc': 'Agents can only use tools available on the side they\'re running on. If a tool exists only on Windows, a WSL agent may fail when trying to use it.',
    'tools.agentMissing': 'Tools not found on agent side',
    'tools.windowsOnly': 'Tools found only on Windows side',
    'tools.noAutoInstall': 'Even if tools are missing, don\'t install automatically — ask the user first.',
    'tools.headers': ['Tool','Status','Version','Command','Windows','Agent','Notes'],
    'tools.statusBoth': 'Available on both Windows and WSL/agent side',
    'tools.statusAgentOnly': 'Available on agent side',
    'tools.statusWindowsOnly': 'On Windows side but not found on agent side',
    'tools.statusMissing': 'Not found',
    'comments.empty': 'No requests with this status yet.',
    'comments.copy': 'Copy this request', 'comments.reaction': 'Reaction:',
    'comments.workNote': 'Work note:',
    'scan.introTitle': '📋 What this tool does (check each time)',
    'scan.legendTitle': '🔍 Topics detected in this scan',
    'scan.legendHint': 'These are the emoji labels on the cards below. Hover over technical terms for explanations.',
    'scan.nextTitle': '👉 What to do next',
    'scan.freeNote': '🆓 This tool is completely free and open source. No cost at all.',
    'glossary.noMatch': '"$1" — no matching terms found. Try a different word.',
    'help.destructive_delete': ['The text includes a delete or reset command.', 'Running it in the wrong folder could remove your work files or settings.', 'Do not run yet. Check what gets deleted, and whether a backup or dry-run option exists.'],
    'help.global_install': ['The setup may install software globally or run a downloaded script.', 'It may affect your PC environment beyond the project folder.', 'Try local install, virtual environment, or a disposable folder first. Confirm with someone before using sudo, -g, or curl | sh.'],
    'help.secrets_or_auth': ['The text mentions tokens, passwords, API keys, OAuth, or .env files.', 'Secrets can leak into logs, shell history, screenshots, commits, or agent context.', 'Use placeholder values while reading. Do not paste real secrets until you know where they are stored.'],
    'help.paid_or_billing': ['The text mentions billing, paid plans, credit cards, quotas, or credits.', 'You may be charged or consume paid API credits after setup.', 'Do not enter payment info through an agent. Check pricing conditions yourself.'],
    'help.daemon_or_cron': ['The text mentions daemons, services, cron, or background processes.', 'They keep running after you close the terminal, which can be hard for beginners to stop.', 'Before starting, check how to stop, disable, or uninstall the service.'],
    'help.config_mutation': ['The text may change agent, MCP, Claude, Hermes, or application config files.', 'This can affect future agent runs or other projects.', 'Back up config files first and check which files will change.'],
    'help.remote_code_execution': ['The text uses code execution patterns like eval, exec, subprocess, or shell execution.', 'Depending on the content, it could run arbitrary commands on your PC.', 'Read the surrounding code. Do not run until you understand what it executes.'],
    'help.external_network': ['The text mentions network calls or external web/API access.', 'Data may be sent externally or depend on external services.', 'Check what data is sent and whether an offline/local mode exists.'],
    'help.filesystem_write': ['The text mentions writing, copying, moving, or creating files.', 'It could overwrite files in unintended locations.', 'Check the write path. Try with a disposable folder first.'],
    'help.container_or_vm': ['The text mentions Docker, Kubernetes, Vagrant, or similar isolated runtimes.', 'Even if it looks isolated, folder mounts, ports, disk usage, and background processes may occur.', 'Check volume, port, and cleanup instructions before starting.'],
    'help.ports': ['The text mentions local ports used by web apps, agents, or browser-control tools.', 'It may conflict with other local tools or expose services unintentionally.', 'Check whether the port is in use and whether it binds to localhost only.'],
    'help.browser_control': ['The text mentions browser automation or remote browser control.', 'It may interact with logged-in browsers or personal data.', 'Use a dedicated browser profile and avoid personal account pages at first.'],
    'help.local_read': ['The text mentions reading local files or databases.', 'Even though reading is low-impact, contents may appear in logs or reports.', 'Try with folders that contain no personal information first.'],
    'help.dry_run_hint': ['The text mentions dry-run, preview, read-only, or no-write modes.', 'This is a good first step when learning.', 'Try the dry-run/preview mode before running any command that makes changes.'],
    'cat.destructive_delete': 'Delete / Reset', 'cat.global_install': 'Install',
    'cat.secrets_or_auth': 'Secrets', 'cat.paid_or_billing': 'Billing / Credits',
    'cat.daemon_or_cron': 'Background Service', 'cat.config_mutation': 'Config Mutation',
    'cat.remote_code_execution': 'Code Execution', 'cat.external_network': 'External Network',
    'cat.filesystem_write': 'File Write', 'cat.container_or_vm': 'Container / VM',
    'cat.ports': 'Local Port', 'cat.browser_control': 'Browser Automation',
    'cat.local_read': 'Local Read', 'cat.dry_run_hint': 'Dry-Run Hint',
  }
};

function t(key, ...args) {
  let text = i18n[currentLang]?.[key] ?? i18n.ja[key] ?? key;
  if (typeof text === 'string') {
    args.forEach((v, i) => { text = text.replace('$' + (i + 1), v); });
  }
  return text;
}

function tArr(key) {
  const val = i18n[currentLang]?.[key] ?? i18n.ja[key];
  return Array.isArray(val) ? val : [val || key];
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem(LANG_KEY, lang);
  document.documentElement.lang = lang;
  applyI18n();
  const btn = document.getElementById('langToggle');
  if (btn) btn.textContent = lang === 'ja' ? '🇺🇸 EN' : '🇯🇵 JA';
  // Re-render dynamic content that depends on language
  if (Object.keys(glossaryData).length) renderGlossary(document.getElementById('glossarySearch')?.value || '');
}

function applyI18n() {
  const lang = currentLang === 'ja' ? i18n.ja : i18n.en;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = lang[key];
    if (text == null) return;
    // For labels with child elements, only update the first text node
    if (el.tagName === 'LABEL' && el.children.length > 0) {
      for (const node of el.childNodes) {
        if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
          node.textContent = text;
          break;
        }
      }
    } else {
      el.textContent = text;
    }
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const key = el.getAttribute('data-i18n-html');
    const text = lang[key];
    if (text != null) el.innerHTML = text;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.getAttribute('data-i18n-placeholder');
    const text = lang[key];
    if (text != null) el.placeholder = text;
  });
  const titleEl = document.querySelector('title[data-i18n]');
  if (titleEl) {
    const key = titleEl.getAttribute('data-i18n');
    const text = lang[key];
    if (text != null) document.title = text;
  }
}

// ── Original state ──
const state = { comments: [], docs: [], filter: 'open', currentDoc: 'readme-ja', activeTab: 'try' };

const $ = (id) => document.getElementById(id);

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, (c) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

function inlineMarkdown(text) {
  let html = escapeHtml(text);
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  return html;
}

function simpleMarkdown(md) {
  const lines = md.split(/\r?\n/);
  let html = '';
  let inCode = false;
  let para = [];
  const flushPara = () => {
    if (para.length) {
      html += `<p>${inlineMarkdown(para.join(' '))}</p>`;
      para = [];
    }
  };
  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      flushPara();
      html += inCode ? '</pre>' : '<pre>';
      inCode = !inCode;
      continue;
    }
    if (inCode) { html += escapeHtml(line) + '\n'; continue; }
    if (!line.trim()) { flushPara(); continue; }
    const h = line.match(/^(#{1,3})\s+(.*)$/);
    if (h) { flushPara(); html += `<h${h[1].length}>${inlineMarkdown(h[2])}</h${h[1].length}>`; continue; }
    const li = line.match(/^[-*]\s+(.*)$/);
    if (li) { flushPara(); html += `<p class="li">• ${inlineMarkdown(li[1])}</p>`; continue; }
    const ordered = line.match(/^\d+\.\s+(.*)$/);
    if (ordered) { flushPara(); html += `<p class="li">${inlineMarkdown(line.trim())}</p>`; continue; }
    para.push(line.trim());
  }
  flushPara();
  return html;
}

async function fetchJson(url, options) {
  const res = await fetch(url, options);
  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new Error(data?.error || res.statusText);
  return data;
}

// ── Tab switching ──
function switchTab(name) {
  state.activeTab = name;
  document.querySelectorAll('.tabs .tab').forEach((b) => b.classList.toggle('active', b.dataset.tab === name));
  document.querySelectorAll('.tab-panel').forEach((p) => p.classList.toggle('active', p.id === 'panel' + name[0].toUpperCase() + name.slice(1)));
}
$('tabNav')?.addEventListener('click', (event) => {
  const btn = event.target.closest('.tab');
  if (!btn) return;
  switchTab(btn.dataset.tab);
});

// ── State / Doc loading ──
async function loadState() {
  const data = await fetchJson('/api/state');
  state.docs = data.docs;
  state.comments = data.comments;
  const select = $('docSelect');
  select.innerHTML = data.docs.map((d) => `<option value="${d.id}">${d.id} — ${d.path} / ${d.label}</option>`).join('');
  select.value = state.currentDoc;
  renderComments();
}

// ── Glossary ──
let glossaryData = {};
let enGlossaryData = {
  "sudo": "Running a command with administrator privileges. Normally restricted operations can be executed with sudo, so be careful.",
  "apt": "A tool that searches for and automatically installs software from the internet. Like a text-only version of a phone's App Store.",
  "brew": "An automatic software installer mainly used on Mac. Also called Homebrew.",
  "pip": "A tool that fetches and adds components for Python from the internet. Convenient, but unknown packages may contain dangerous code.",
  "npm": "A tool that fetches and adds components for Node.js from the internet. Convenient, but unknown packages may contain dangerous code.",
  "curl": "A command that accesses URLs on the internet. Can download files or send data to web services. Running commands without checking their contents is dangerous.",
  "wget": "A command that downloads files from the internet. Similar to curl, but wget is specialized for downloading only.",
  "eval": "A command that executes a string as a program. Useful in some cases, but malicious strings can execute dangerous commands. Beginners should generally avoid it.",
  "exec": "A mechanism that calls and executes another program or command. Convenient, but executing untrusted input can run dangerous commands.",
  "subprocess": "A mechanism for starting new programs inside your computer. Whether it's dangerous depends on what it runs.",
  "shell": "A program that receives commands typed in the terminal and passes them to the computer. Examples: bash, zsh, PowerShell.",
  "chmod": "A command that changes the 'lock' settings on files. It can assign read, write, and execute permissions to yourself, your group, or others.",
  "chown": "A command that changes the 'owner' of a file. It can transfer ownership from one user to another.",
  "rm": "Deletes files. They don't go to the trash and are difficult to recover.",
  "mv": "Moves or renames files.",
  "cp": "Copies files.",
  "crontab": "A timer that automatically runs commands at set times, like 'back up every morning at 7am'.",
  "systemd": "A manager in Linux that starts and stops programs that run continuously in the background.",
  "daemon": "A program that waits in the background, ready to respond when needed.",
  "OAuth": "A mechanism for logging in using another service's account, like 'Sign in with Google.' Convenient, but granting access to untrusted apps can expose your data.",
  "API Key": "A secret passphrase for using an online service. If discovered, others could use your account or credits.",
  "Auth Token": "A digital key proving you are logged in. Like API keys, showing them to others or pasting them in chats can lead to misuse.",
  "AI Token": "The smallest unit AI uses to read text. AI pricing and processing volume are often determined by token count.",
  ".env": "A settings file often used to store passwords, API keys, and configuration values. Convenient, but may contain secrets — don't share or publish it.",
  "quota": "The maximum number of times or amount you can use an online service. Exceeding it may temporarily block access or require extra payment.",
  "credits": "Tickets or coins for using an online service. They decrease with use. When zero, access may stop or require purchasing more.",
  "docker": "A technology that creates a small 'sandbox' inside your computer to run software. Keeps things isolated, but configuration can still affect your main files.",
  "kubernetes": "A system that manages many Docker containers automatically. It can do things like 'replace broken containers with new ones automatically.'",
  "localhost": "Your own computer. It doesn't connect to the internet and stays within your machine.",
  "CDP": "A channel for remotely controlling the Chrome browser from programs. Can click buttons automatically or read page contents.",
  "Playwright": "A tool for automating web browsers (like Chrome) from programs. Can click buttons, check if text appears, and more.",
  "MCP": "A common protocol for AI apps and agents to interact with external tools. For example, it lets AI read files, check calendars, or control other software. Capabilities and safety depend on each MCP server.",
  "MCP Server": "A program that lends its capabilities to AI. For example, it exposes features like 'read files,' 'control browser,' or 'use VOICEVOX' so AI can call them.",
  "MCP Client": "An app that connects to MCP servers and uses their features. AI agents and development tools are examples.",
  "MCP Compatible": "Means the software or tool may be usable via MCP. However, being compatible doesn't automatically mean it's safely connected.",
  "dry-run": "A trial mode that shows what would happen without actually making changes.",
  "venv": "A 'sandbox room' for Python. Creates a separate room for each project so their components don't conflict.",
  "volume": "A 'window' connecting a Docker container to a folder on your computer. Through it, the container can read or write your files.",
  "port": "A 'communication door' in your computer. Each door has a number and handles different tasks (browsing the web, sending email, etc.).",
  "Resident": "Normally, closing a terminal window ends the programs running in it. But 'resident' programs keep running in the background even after closing.",
  "Background": "Running behind the scenes without being displayed on screen.",
  "CLI": "Operating software or your computer by typing text. Instead of clicking buttons, you type commands to run things.",
  "GUI": "The familiar way of operating with buttons and windows. Using a mouse to click.",
  "OSS": "Software whose design is publicly available. Anyone can view, modify, and often use it for free.",
  "README": "The explanation file at the top of a project folder. The first file you should read.",
  "MIT License": "A software license with very high freedom. You can use, modify, distribute, and even sell it if you follow the conditions.",
  "Repository": "A place that manages source code and change history. Often on GitHub, but can also exist on your own computer.",
  "commit": "In Git, recording a file change as 'saved at this state.'",
  "push": "In Git, uploading your local commits to GitHub.",
  "clone": "In Git, copying a project from a server to your local machine.",
  "PR": "Pull Request. On GitHub, proposing 'please include this change.'",
  "issue": "On GitHub etc., a discussion ticket for bugs, requests, or work notes.",
  "CI": "A system that automatically checks 'does it still work?' every time you change code. Gives peace of mind by catching breakage immediately.",
  "Vibe Coding": "A development style where you ask AI to 'build something like this' and it generates code.",
  "WSL": "A mechanism for running Linux inside a Windows computer. You can create a Linux environment inside Windows without needing a separate machine.",
  "Path": "The address of a file or folder. A string like C:\\Users\\... or /home/...",
  "Terminal": "The screen used for CLI. A text-based app where you type into a dark window.",
  "Agent": "An AI program that thinks and acts on its own. For example, if you ask 'check my calendar and tell me when I'm free,' it opens the calendar and finds the answer.",
  "Git": "A tool that records file change history. Lets you track 'when and what changed,' revert to previous states, and collaborate with others.",
  "GitHub": "A service for hosting Git-managed projects online. Commonly used as a code repository, work notebook, and public page.",
  "branch": "A branch in Git for separating work. Useful for safely trying different approaches or keeping changes separate from the main code.",
  "merge": "Combining changes made in separate branches back into the main flow.",
  "fork": "Copying someone else's repository to your own account so you can modify it.",
  "dependency": "Another component required for software to work. If dependencies are missing, installation or startup may fail.",
  "package": "A bundle of software or components. Packages installed via npm or pip are examples.",
  "PATH": "A list of places your computer searches for commands. If not registered in PATH, even installed software may show 'not found.'",
  "Environment Variables": "Configuration values passed to your computer or programs. Often used for API keys or execution modes. Sometimes stored in .env files.",
  "JSON": "A format for writing data like { name: Taro }. Commonly used in APIs and config files.",
  "YAML": "A format often used for config files. Easy to read, but breaks easily if the number of spaces is off.",
  "log": "A record of what a program did. Very useful for finding the cause of errors.",
  "error": "A notification that a program didn't work properly. Not something to fear — it's a clue showing 'where the problem is.'",
  "warning": "A notification that something deserves attention, though it's not serious enough to stop."
};

async function loadGlossary() {
  try {
    glossaryData = await fetchJson('/api/glossary');
  } catch (_) {
    glossaryData = {};
  }
  renderGlossary();
}

function renderGlossary(filter = '') {
  const grid = $('glossaryGrid');
  const source = currentLang === 'en' ? enGlossaryData : glossaryData;
  const terms = Object.entries(source);
  const q = filter.trim().toLowerCase();
  const filtered = q ? terms.filter(([k, v]) =>
    k.toLowerCase().includes(q) || v.toLowerCase().includes(q)
  ) : terms;
  // Sort: exact match first, then prefix match, then alphabetically
  filtered.sort((a, b) => {
    const aExact = a[0].toLowerCase() === q;
    const bExact = b[0].toLowerCase() === q;
    if (aExact !== bExact) return bExact - aExact;
    const aPrefix = a[0].toLowerCase().startsWith(q);
    const bPrefix = b[0].toLowerCase().startsWith(q);
    if (aPrefix !== bPrefix) return bPrefix - aPrefix;
    return a[0].localeCompare(b[0], currentLang === 'ja' ? 'ja' : 'en');
  });
  $('glossaryCount').textContent = `${filtered.length} / ${terms.length} ${currentLang === 'ja' ? '件' : 'terms'}`;
  if (!filtered.length) {
    grid.innerHTML = `<p class="muted" style="padding:2rem;text-align:center">${currentLang === 'ja' ? `「${escapeHtml(filter)}」${t('glossary.noMatch')}` : t('glossary.noMatch', escapeHtml(filter))}</p>`;
    return;
  }
  grid.innerHTML = filtered.map(([term, desc]) => `
    <article class="glossary-card">
      <h3>${escapeHtml(term)}</h3>
      <p>${escapeHtml(desc)}</p>
    </article>`).join('');
}

async function loadDoc(id = state.currentDoc) {
  state.currentDoc = id;
  const data = await fetchJson(`/api/doc?id=${encodeURIComponent(id)}`);
  const meta = state.docs.find((d) => d.id === id) || {};
  $('docTitle').textContent = data.path;
  const internal = meta.kind && meta.kind !== 'public';
  const note = internal ? `<div class="doc-note internal">${escapeHtml(meta.label || meta.kind)}: これは公開ユーザー向け本文ではなく、共同レビュー/保守用の文書です。将来の公開前に整理または削除候補として扱います。</div>` : `<div class="doc-note public">${escapeHtml(meta.label || '公開向け')}: ユーザーに直接見せる前提の文書です。</div>`;
  const guide = docGuide(id);
  $('docContent').innerHTML = guide + note + simpleMarkdown(data.content || '(empty)');
}

function docGuide(id) {
  if (id === 'readme-ja' || id === 'readme') {
    if (currentLang === 'ja') {
      return `<section class="reader-guide">
        <p class="reader-guide-kicker">最初に読むところ</p>
        <h3>まず「これは何のための道具か」を短く説明し、そのあとに機能と使い方を並べています。</h3>
        <p>初めて見る人には、機能一覧より先に「いつ使うのか」「何をしないのか」が分かる方が読みやすいので、README はその順番で整理しています。</p>
      </section>`;
    }
    return `<section class="reader-guide">
      <p class="reader-guide-kicker">Start here</p>
      <h3>Briefly explains what this tool is for, then lists features and usage.</h3>
      <p>For first-time readers, understanding "when to use" and "what it doesn't do" before the feature list makes the README easier to follow.</p>
    </section>`;
  }
  if (id === 'beginner-guide') {
    if (currentLang === 'ja') {
      return `<section class="reader-guide">
        <p class="reader-guide-kicker">初心者向けガイド</p>
        <h3>コマンドを実行する前に、何を確認すればいいかを順番に読むための文書です。</h3>
        <p>README で全体像を掴んだあと、実際にフォルダをチェックするときの読み方をここで確認できます。</p>
      </section>`;
    }
    return `<section class="reader-guide">
      <p class="reader-guide-kicker">Beginner guide</p>
      <h3>A step-by-step guide on what to check before running commands.</h3>
      <p>After understanding the overview from the README, use this to learn how to read the scan results.</p>
    </section>`;
  }
  return '';
}

// ── Comments ──
function renderComments() {
  const box = $('comments');
  const comments = state.filter === 'all' ? state.comments : state.comments.filter((c) => c.status === state.filter);
  if (!comments.length) {
    box.innerHTML = `<p class="muted">${t('comments.empty')}</p>`;
    return;
  }
  box.innerHTML = comments.map((c) => `
    <article class="comment">
      <div class="comment-meta">
        <span class="badge">${escapeHtml(c.id)}</span>
        <span class="badge ${escapeHtml(c.priority)}">${escapeHtml(c.priority)}</span>
        <span class="badge ${escapeHtml(c.status)}">${escapeHtml(c.status)}</span>
        <span>${escapeHtml(c.section)}</span>
      </div>
      ${c.beginner_reaction ? `<p><strong>${t('comments.reaction')}</strong> ${escapeHtml(c.beginner_reaction)}</p>` : ''}
      <p>${escapeHtml(c.text)}</p>
      ${c.owner_note ? `<p><strong>${t('comments.workNote')}</strong> ${escapeHtml(c.owner_note)}</p>` : ''}
      <button class="copy-btn" data-copy="${escapeHtml(c.text)}">${t('comments.copy')}</button>
      <div class="comment-actions">
        ${['open','accepted','fixed','parked'].map((s) => `<button data-id="${c.id}" data-status="${s}">${s}</button>`).join('')}
      </div>
    </article>`).join('');
}

async function updateComment(id, status) {
  const data = await fetchJson(`/api/comments/${encodeURIComponent(id)}`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({status})
  });
  state.comments = data.comments;
  renderComments();
}

async function addComment(form) {
  const payload = Object.fromEntries(new FormData(form).entries());
  const data = await fetchJson('/api/comments', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  });
  state.comments = data.comments;
  form.reset();
  renderComments();
}

// ══════════════════════════════════════════════
//  Scan / diagnosis engine (unchanged from prior)
// ══════════════════════════════════════════════

const jaHelp = {
  destructive_delete: ['削除・リセット系のコマンドが書かれています。', '違うフォルダで実行すると、作業ファイルや設定を消す可能性があります。', 'まだ実行しないでください。何を消すのか、バックアップやdry-runがあるか確認してください。'],
  global_install: ['グローバルインストール、またはダウンロードしたスクリプトをそのまま実行する手順が書かれています。', 'プロジェクトフォルダの外までPC環境を変える可能性があります。', 'まずローカルインストール、仮想環境、使い捨てフォルダで試せるか確認してください。sudo、-g、curl | sh は人に確認してから。'],
  secrets_or_auth: ['トークン、パスワード、APIキー、OAuth、.env などの秘密情報について書かれています。', '秘密情報はログ、履歴、スクリーンショット、コミット、AIエージェントの文脈に漏れることがあります。', '最初はダミー値を使ってください。本物の秘密情報を貼る前に、どこへ保存されるか確認してください。'],
  paid_or_billing: ['課金、有料プラン、クレジットカード、quota、credits について書かれています。', '設定後にお金がかかったり、有料API枠を消費する可能性があります。', '支払い情報はエージェント経由で入れず、料金の発生条件を自分で確認してください。'],
  daemon_or_cron: ['daemon、service、cron、バックグラウンド常駐について書かれています。', 'ターミナルを閉じても動き続け、初心者には止め方が分かりにくいことがあります。', '起動する前に、停止・無効化・アンインストール方法を確認してください。'],
  config_mutation: ['Agent、MCP、Claude、Hermes、アプリ設定ファイルを変更する手順かもしれません。', '今後のエージェント実行や別プロジェクトにも影響する可能性があります。', '変更前に設定ファイルをバックアップし、どのファイルが変わるか確認してください。'],
  remote_code_execution: ['eval、exec、subprocess、shell実行など、コードやコマンドを実行する仕組みが見えます。', '内容次第でPC上のコマンドを実行できます。', '周辺コードを読み、何を実行するのか分かるまで動かさないでください。'],
  external_network: ['外部Web/API/ネットワークアクセスについて書かれています。', 'データが外へ送られたり、外部サービスに依存する可能性があります。', '何を送るのか、オフライン/ローカルモードがあるか確認してください。'],
  filesystem_write: ['ファイルの作成、コピー、移動、書き込みについて書かれています。', '意図しない場所のファイルを上書きする可能性があります。', '書き込み先パスを確認し、最初は使い捨てフォルダで試してください。'],
  container_or_vm: ['Docker、Kubernetes、Vagrantなどのコンテナ/VMについて書かれています。', '隔離っぽく見えても、ローカルフォルダのマウント、ポート、ディスク使用、常駐が起こります。', 'volume、port、cleanup手順を確認してから起動してください。'],
  ports: ['ローカルポートを使うWebアプリやエージェントについて書かれています。', '他のローカルツールと競合したり、意図せずサービスが見える場合があります。', 'そのポートが使用中か、localhostだけにbindするか確認してください。'],
  browser_control: ['ブラウザ自動操作やリモートブラウザ制御について書かれています。', 'ログイン済みブラウザや個人データに触れる可能性があります。', '専用ブラウザプロファイルを使い、最初は個人アカウントのページを避けてください。'],
  local_read: ['ローカルファイルやDBを読む処理について書かれています。', '読み取り自体は低影響でも、内容がログやレポートに出ることがあります。', '最初は個人情報のないフォルダで試してください。'],
  dry_run_hint: ['dry-run、preview、read-only など、変更しない試用モードのヒントがあります。', '学習中の最初の一歩として使いやすいモードです。', '変更するコマンドの前に、まずdry-run/previewを試してください。'],
};

const jaCategoryEmoji = {
  destructive_delete: '🗑️', global_install: '🧰', secrets_or_auth: '🔑', paid_or_billing: '💳',
  daemon_or_cron: '🕰️', config_mutation: '⚙️', remote_code_execution: '⚙️', external_network: '🌐',
  filesystem_write: '📁', container_or_vm: '🧰', ports: '🚪', browser_control: '🧰', local_read: '📁', dry_run_hint: '🧰',
};
const jaCategoryLabel = {
  destructive_delete: '削除・リセット系', global_install: 'インストール操作', secrets_or_auth: '秘密情報',
  paid_or_billing: '課金・クレジット', daemon_or_cron: '常駐サービス', config_mutation: '設定ファイル書き換え',
  remote_code_execution: 'コード/コマンド実行', external_network: '外部ネットワーク通信', filesystem_write: 'ファイル書き込み',
  container_or_vm: 'コンテナ/VM', ports: 'ローカルポート使用', browser_control: 'ブラウザ自動操作',
  local_read: 'ローカル読み取り', dry_run_hint: '試用モードのヒント',
};

const jaTerms = {
  'sudo': 'パソコンの管理者権限で命令を実行すること。ふだんは安全のため制限されている操作も、sudoをつけると実行できてしまうので注意。',
  'apt': 'インターネットからソフトを探してきて、自動でインストールしてくれる道具。',
  'brew': '主にMacで使われる、ソフトの自動インストール道具。Homebrewとも呼ばれる。',
  'pip': 'Pythonで使う部品を、ネットから取ってきて追加する道具。知らない部品を入れると危険なコードが混ざることもある。',
  'npm': 'Node.jsで使う部品を、ネットから取ってきて追加する道具。知らない部品を入れると危険なコードが混ざることもある。',
  'curl': 'インターネット上のURLにアクセスする命令。ファイルをダウンロードしたり、Webサービスにデータを送ったりできる。',
  'wget': 'インターネットからファイルをダウンロードする命令。curlと似ているが、ダウンロードだけに特化している。',
  'eval': '文字列をプログラムとして実行する命令。悪意のある文字列を渡されると危険。初心者は基本的に避けた方がいい。',
  'exec': '別のプログラムや命令を呼び出して実行する仕組み。外から受け取った文字をそのまま実行すると危険な命令まで動くことがある。',
  'subprocess': 'パソコンの中で、別のプログラムを新しく動かす仕組み。何を動かすか次第で危険にもなる。',
  'shell': 'ターミナルに入力された命令を受け取って、実際にパソコンへ伝えるプログラム。bash、zsh、PowerShellなどがある。',
  'chmod': 'ファイルにつける「鍵」の設定を変える命令。「見るだけ」「編集できる」「実行できる」の3つの鍵を配れる。',
  'chown': 'ファイルの「持ち主」を変える命令。',
  'rm': 'ファイルを削除する。ゴミ箱には入らず、復元が難しい。',
  'mv': 'ファイルを移動・リネームする。',
  'cp': 'ファイルを複製する。',
  'crontab': '決まった時間に決まった命令を自動実行するタイマー機能。',
  'systemd': 'Linuxの中で、裏方でずっと動いているプログラムの電源を入れたり切ったりする管理人。',
  'daemon': 'パソコンの裏側で、必要なときに備えて待ち続けるプログラム。',
  'OAuth': '「Googleでログイン」のように、別のサービスのアカウントを使ってログインしたり、必要な権限だけを許可したりする仕組み。',
  'APIキー': 'ネット上のサービスを使うための「秘密の合言葉」。知られるとあなたの利用枠や料金で勝手に使われることがある。',
  'API キー': 'ネット上のサービスを使うための「秘密の合言葉」。知られるとあなたの利用枠や料金で勝手に使われることがある。',
  '認証トークン': 'ログイン済みであることを証明するデジタルな鍵。他人に見せたりチャットに貼ったりすると悪用されることがある。',
  'AIのトークン': 'AIが文章を読むときの細かい単位。AIの料金や処理量は、このトークン数で決まることが多い。',
  '.env': 'パスワード、APIキー、設定値などを入れておくことが多い設定ファイル。秘密情報が入ることがあるので、他人に送ったりネットに公開したりしない。',
  'quota': 'ネットのサービスを使える回数や量の上限。超えると一時的に使えなくなったり、追加料金が必要になったりする。',
  'credits': 'ネットのサービスを使うための「チケット」や「コイン」。使うたびに減っていく。',
  'docker': 'パソコンの中に「小さな実験用の箱」を作って、その中でソフトを動かす仕組み。ただし設定によっては本体のファイルにも触れるので注意。',
  'kubernetes': 'たくさんのDockerの箱を、まとめて自動で管理する仕組み。',
  'localhost': '自分自身のパソコンのこと。インターネットには出ていかない。',
  '127.0.0.1': '自分自身のPCを示すIPアドレス。localhost と同じ。',
  'CDP': 'Chromeブラウザを、プログラムから遠隔操作するための通り道。',
  'Playwright': 'Webブラウザをプログラムで自動操作する道具。',
  'MCP': 'AIアプリやAIエージェントが、外部ツールとやり取りするための共通ルール。ただし使える機能や安全性はMCPサーバーごとの設定による。',
  'MCPサーバー': 'AIに機能を貸し出す側のプログラム。「ファイルを読む」「ブラウザを操作する」などの機能をAIから呼び出せるようにする。',
  'MCPクライアント': 'MCPサーバーに接続して機能を使う側のアプリ。AIエージェントや開発ツールがこれにあたる。',
  'MCP対応': 'そのソフトやツールが、MCP経由でAIから使える可能性があるという意味。ただし対応しているだけで自動的に安全ではない。',
  'dry-run': '実際には変更せず、何が起きるかを表示だけする試運転モード。',
  'read-only': '読み取り専用。書き込みや削除はしない。',
  'read only': '読み取り専用。書き込みや削除はしない。',
  '仮想環境': 'プロジェクト専用に隔離されたPython環境。本体には影響しない。',
  'venv': 'Pythonの「実験用の部屋」。プロジェクトごとに別の部屋を作って部品を入れられる。',
  'volume': 'Dockerの箱と、自分のパソコンのフォルダをつなぐ「窓」。',
  'port': 'パソコンの中にある「通信用のドア」。番号ごとに違う仕事を担当する。',
  '常駐': '画面を閉じても裏で動き続けること。',
  'バックグラウンド': '画面には表示されず、裏で動き続けること。',
  'CLI': '文字を打ってソフトやパソコンを操作する方式。ボタンをクリックする代わりに命令文を入力して動かす。',
  'GUI': 'ボタンやウィンドウで操作する、いつもの見た目の方式。',
  'OSS': '設計図が公開されているソフト。誰でも中身を見たり、改造したりできる。',
  'MITライセンス': 'ソフトの使い方を決めるライセンスのひとつ。かなり自由度が高い。',
  'リポジトリ': 'ソースコードや変更履歴をまとめて管理する場所。GitHub上にも自分のPCの中にも作れる。',
  'commit': 'Gitでファイルの変更を「この状態で保存」と記録すること。',
  'push': 'Gitで、手元のcommitをGitHubにアップロードすること。',
  'clone': 'Gitで、サーバー上のプロジェクトを手元にコピーすること。',
  'PR': 'Pull Request。GitHubで「この修正を取り込んでほしい」と提案すること。',
  'issue': 'GitHubなどで、不具合・要望・作業メモを記録するための相談チケット。',
  'CI': 'プログラムを変更するたびに、自動で「ちゃんと動くかな？」と確認してくれる仕組み。',
  'WSL': 'Windowsパソコンの中でLinuxを動かせるようにする仕組み。',
  'パス': 'ファイルやフォルダの住所。C:\\Users\\... や /home/... のような文字列。',
  'ターミナル': 'CLIを使うための画面。黒い画面に文字を打つタイプのアプリ。',
  'エージェント': '自分で考えて、自分で動くAIプログラム。',
  'Git': 'ファイルの変更履歴を記録する道具。「いつ、何を変えたか」を残せる。',
  'GitHub': 'Gitで管理しているプロジェクトをネット上に置けるサービス。',
  'branch': 'Gitで作業を分けるための枝。安全に別案を試せる。',
  'merge': '分けて作業していた変更を、元の流れに合体させること。',
  'fork': '他人のリポジトリを、自分用にコピーして改造できるようにすること。',
  'dependency': 'そのソフトが動くために必要な別の部品。',
  'package': 'ソフトや部品をひとまとめにしたもの。',
  'PATH': 'パソコンが命令を探しに行く場所のリスト。登録されていないと「見つからない」と言われることがある。',
  '環境変数': 'パソコンやプログラムに渡す設定値。APIキーや実行モードなどを入れることが多い。',
  'JSON': 'データを { "name": "Taro" } のような形で書く形式。APIや設定ファイルでよく使われる。',
  'YAML': '設定ファイルでよく使われる書き方。空白の数がズレると壊れやすい。',
  'log': 'プログラムが何をしたかを記録したメモ。エラーの原因を探すときにとても役立つ。',
  'error': 'プログラムがうまく動かなかったという知らせ。「どこで困っているか」を教えてくれるヒント。',
  'warning': 'すぐ止まるほどではないが、注意した方がいいという知らせ。',
};

function annotateTerms(text) {
  if (!text) return '';
  const terms = Object.keys(jaTerms).sort((a, b) => b.length - a.length);
  const pattern = terms.map((term) => term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const re = new RegExp(`(?<![\\w一-鿿])(${pattern})(?![\\w一-鿿])`, 'g');
  return escapeHtml(text).replace(
    re,
    (matched) => `<span class="term" tabindex="0" data-tip="${escapeHtml(jaTerms[matched])}">${matched}</span>`,
  );
}

function beginnerSummaryText(summary) {
  if (!summary) return '';
  if (typeof summary === 'string') return summary;
  return [summary.decision, summary.message, summary.next_step].filter(Boolean).join(' / ');
}

function helpFor(item, index) {
  const h = tArr('help.' + item.category);
  const ja = jaHelp[item.category];
  const catLabel = t('cat.' + item.category, item.category);
  return { what: h[0] || ja?.[0] || item.plain_language || '', why: h[1] || ja?.[1] || item.why_it_matters || '', next: h[2] || ja?.[2] || item.beginner_next_step || '', title: `${currentLang === 'ja' ? '項目' : 'Item'}${index + 1}: ${catLabel}` };
}

function renderLegendCard(items) {
  const present = new Set();
  for (const item of items) { if (item.category) present.add(item.category); }
  if (!present.size) return '';
  const chips = Array.from(present).map((cat) => {
    const emoji = jaCategoryEmoji[cat] || '•';
    const label = t('cat.' + cat, jaCategoryLabel[cat] || cat);
    return `<span class="legend-chip"><span class="legend-emoji">${emoji}</span><span>${escapeHtml(label)}</span></span>`;
  }).join('');
  const kinds = currentLang === 'ja' ? '種類' : 'types';
  return `<div class="legend-card"><div class="legend-head"><span class="legend-title">${t('scan.legendTitle')}</span><span class="muted">${present.size} ${kinds}</span></div><p class="muted legend-hint">${t('scan.legendHint')}</p><div class="legend-chips">${chips}</div></div>`;
}

function renderIntroCard() {
  if (currentLang === 'ja') {
    return `<div class="intro-card"><div class="intro-head">📋 このツールがやること（毎回確認）</div><ul class="intro-list"><li><strong>読み取り専用で</strong>スキャンします。指定されたフォルダのファイルを<strong>読みます</strong>。</li><li><strong>ファイルは書き換えません</strong>。新規作成も削除もしません。</li><li><strong>外部には送信しません</strong>。スキャン結果はあなたのブラウザにだけ表示されます。</li><li><strong>コマンドは実行しません</strong>。検出された注意点を表示するだけです。</li></ul><p class="muted intro-note">個人情報が含まれるフォルダを最初に入れるのは避け、テスト用フォルダで試してからにしてください。</p></div>`;
  }
  return `<div class="intro-card"><div class="intro-head">📋 ${t('scan.introTitle')}</div><ul class="intro-list"><li>Scans in <strong>read-only</strong> mode. It <strong>reads</strong> files in the specified folder.</li><li><strong>Does not modify files</strong>. No creation, deletion, or changes.</li><li><strong>Does not send data externally</strong>. Results are shown only in your browser.</li><li><strong>Does not execute commands</strong>. It only displays review notes.</li></ul><p class="muted intro-note">Avoid folders with personal information at first. Try a test folder first.</p></div>`;
}

function renderScanResult(data) {
  if (!data.ok) {
    $('scanSummary').innerHTML = `<p class="bad">${t('scan.error')}: ${escapeHtml(data.error || 'unknown error')}</p>`;
    $('scanResultTools').style.display = 'none';
    return;
  }
  $('scanResultTools').style.display = 'flex';
  const report = data.report;
  const items = report.review_items || [];
  const renderedItems = items.map((item, index) => {
    const help = helpFor(item, index);
    return `<details class="scan-item" open>
      <summary><span class="badge ${escapeHtml(item.priority)}">${escapeHtml(item.priority)}</span> ${escapeHtml(help.title)} / ${escapeHtml(item.file)}:${escapeHtml(item.line)} <span class="muted hint">クリックで開閉</span></summary>
      <p><strong>${currentLang === 'ja' ? 'これは何？' : 'What this means:'}</strong> ${annotateTerms(help.what)}</p>
      <p><strong>${currentLang === 'ja' ? 'なぜ確認？' : 'Why it matters:'}</strong> ${annotateTerms(help.why)}</p>
      <p><strong>${currentLang === 'ja' ? '次にすること:' : 'Next step:'}</strong> ${annotateTerms(help.next)}</p>
    </details>`;
  }).join('');
  $('scanSummary').dataset.raw = JSON.stringify(data, null, 2);

  $('scanSummary').innerHTML = `
    <details class="scan-shell" open>
      <summary class="scan-shell-summary"><span class="scan-shell-title">📊 診断結果</span><span class="muted">(${items.length}件の確認項目)</span></summary>
      <div class="scan-shell-body">
        ${renderIntroCard()}
        ${renderLegendCard(items)}
        <div class="decision-card ${escapeHtml(report.max_priority)}">
          <div class="decision-card-head">
            <div>
              <p><strong>${t('scan.decision')}:</strong> ${escapeHtml(report.decision)}</p>
              <p><strong>${t('scan.maxPriority')}:</strong> ${escapeHtml(report.max_priority)}</p>
              <p><strong>${t('scan.confirmItems')}:</strong> ${items.length} ${t('scan.items')}</p>
              <p>${escapeHtml(beginnerSummaryText(report.beginner_summary))}</p>
            </div>
            <div class="decision-card-actions">
              <button type="button" class="primary" data-action="rerun">${t('scan.rerun')}</button>
              <button type="button" class="expand-all-btn">${t('scan.expandAll')}</button>
              <button type="button" class="collapse-all-btn">${t('scan.collapseAll')}</button>
              <button type="button" class="clear-result-btn">${t('scan.clear')}</button>
            </div>
          </div>
        </div>
        <div class="scan-items-wrap">${renderedItems || '<p class="muted">表示する確認項目はありません。</p>'}</div>
        <div class="next-step-card">
          <div class="next-step-head">${t('scan.nextTitle')}</div>
          <ol class="next-step-list">
            ${currentLang === 'ja' ? `
            <li>上の確認項目を読んで、<strong>心配なものがなければそのまま進んでOK</strong>です。</li>
            <li>心配な項目があったら、<strong>「診断結果をコピー」ボタンでコピー</strong>して、ChatGPT や詳しい人に「これ大丈夫？」と相談してください。</li>
            <li>このツールは<strong>読み取っただけで、あなたのPCは何も変わっていません</strong>。安心して閉じても大丈夫です。</li>
            ` : `
            <li>Read the review items above. <strong>If nothing worries you, you're good to go.</strong></li>
            <li>If something concerns you, <strong>copy the scan results</strong> and ask ChatGPT or someone knowledgeable: "Is this safe?"</li>
            <li>This tool only <strong>read files — nothing on your PC has changed</strong>. You can safely close this.</li>
            `}
          </ol>
          <p class="muted next-step-foot">${t('scan.freeNote')}</p>
        </div>
      </div>
    </details>`;
}

function clearScanResult() {
  $('scanSummary').innerHTML = `<p class="muted scan-empty-msg">${t('try.emptyMsg')}</p>`;
  $('scanResultTools').style.display = 'none';
  delete $('scanSummary').dataset.raw;
}

function rerunScan() {
  const input = $('targetPathInput');
  if (input) { input.focus(); input.select?.(); }
  const shell = $('scanSummary').querySelector('details.scan-shell');
  if (shell) shell.open = false;
  const status = $('pickFolderStatus');
  if (status) status.textContent = currentLang === 'ja' ? 'パスを変えるか、「フォルダ/ファイルを選ぶ...」で選び直して「このフォルダを確認する」を押してください。' : 'Change the path or use "Choose folder/file..." to select again, then press "Check this folder".';
}

function setAllScanItems(open) {
  $('scanSummary').querySelectorAll('details.scan-item').forEach((d) => { d.open = open; });
}

$('scanSummary')?.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  if (target.classList.contains('collapse-all-btn')) setAllScanItems(false);
  if (target.classList.contains('expand-all-btn')) setAllScanItems(true);
  if (target.classList.contains('clear-result-btn')) clearScanResult();
  if (target.dataset?.action === 'rerun' || target.classList.contains('rerun-btn')) rerunScan();
});

async function runScan(form) {
  $('scanSummary').textContent = t('scan.checking');
  const payload = Object.fromEntries(new FormData(form).entries());
  const data = await fetchJson('/api/scan', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
  renderScanResult(data);
  // Scroll to result
  $('scanResultArea')?.scrollIntoView?.({ behavior: 'smooth' });
}

async function pickFolder() {
  const status = $('pickFolderStatus');
  status.textContent = currentLang === 'ja' ? 'Windowsの「開く」ダイアログを開いています...' : 'Opening Windows Open dialog...';
  const data = await fetchJson('/api/pick-folder');
  if (!data.ok) {
    status.textContent = data.cancelled ? (currentLang === 'ja' ? 'キャンセルしました。' : 'Cancelled.') : `${t('error.prefix')}${data.error || 'unknown error'}`;
    return;
  }
  $('targetPathInput').value = data.path;
  status.textContent = `${currentLang === 'ja' ? '選択しました: ' : 'Selected: '}${data.path}`;
}

async function scanTextFile(file) {
  if (!file) return;
  const status = $('scanSummary');
  if (file.size > 1_000_000) {
    status.innerHTML = `<p class="bad">${currentLang === 'ja' ? '1MB を超えるテキストファイルは扱いません。' : 'Text files over 1MB are not supported.'}</p>`;
    return;
  }
  status.textContent = currentLang === 'ja' ? `${file.name} を読み込み中...` : `Reading ${file.name}...`;
  const content = await file.text();
  const data = await fetchJson('/api/scan-text', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({filename: file.name, content})
  });
  renderScanResult(data);
}

function setupDropZone() {
  const zone = $('textDropZone');
  const input = $('textFileInput');
  zone.addEventListener('click', () => input.click());
  zone.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); input.click(); } });
  input.addEventListener('change', async () => { await scanTextFile(input.files?.[0]); input.value = ''; });
  for (const name of ['dragenter', 'dragover']) { zone.addEventListener(name, (event) => { event.preventDefault(); zone.classList.add('dragover'); }); }
  for (const name of ['dragleave', 'drop']) { zone.addEventListener(name, (event) => { event.preventDefault(); zone.classList.remove('dragover'); }); }
  zone.addEventListener('drop', async (event) => { const file = event.dataTransfer?.files?.[0]; await scanTextFile(file); });
}

// ══════════════════════════════════════════════
//  Port Conflict Checker
// ══════════════════════════════════════════════

const aiPortHints = {
  1234: ['local-llm', 'LM StudioなどのローカルLLM API候補'],
  50021: ['voice', 'VOICEVOXなどの音声合成ツール候補'],
  50022: ['voice', 'VOICEVOX代替ポート候補'],
  7860: ['image', 'Stable Diffusion WebUI / Gradio系候補'],
  8000: ['dev-mcp', '開発サーバーまたはMCP系ツール候補'],
  8060: ['godot', 'Godot Editor候補'],
  8088: ['local-llm', 'llama.cpp / LM Studio候補'],
  8089: ['local-llm', 'llama.cpp代替ポート候補'],
  8188: ['image', 'ComfyUI候補'],
  8189: ['image', 'ComfyUI代替ポート候補'],
  8642: ['hermes', 'Hermes Desktop候補'],
  9222: ['browser', 'Chrome DevTools Protocol候補'],
  9224: ['browser', 'Chrome DevTools Protocol代替ポート候補'],
  9500: ['godot-mcp', 'Godot AI MCP候補'],
  11434: ['local-llm', 'Ollama候補'],
};

function buildAiToolCandidates(ports) {
  const candidates = [];
  for (const p of ports || []) {
    const hint = aiPortHints[Number(p.port)];
    const proc = String(p.process_name || '').toLowerCase();
    const path = String(p.exe_path || '').toLowerCase();
    const processLooksAi = /(mcp|hermes|claude|cursor|codex|ollama|lm studio|lmstudio|comfy|voicevox|godot|chrome|msedge|python|node)/.test(`${proc} ${path}`);
    if (!hint && !processLooksAi) continue;
    const label = hint ? hint[1] : 'AI/開発ツールっぽいプロセス候補';
    candidates.push({ ...p, candidate_label: label, candidate_kind: hint?.[0] || 'process' });
  }
  return candidates;
}

function renderAiCandidates(ports) {
  const candidates = buildAiToolCandidates(ports);
  if (!candidates.length) {
    return `<div class="ai-candidate-box ai-candidate-empty">
      <h3>${t('port.aiEmptyTitle')}</h3>
      <p>${t('port.aiEmptyDesc')}</p>
    </div>`;
  }
  const askText = `このPCでAIエージェントやバイブコーディングに使えそうなローカルツール候補を確認したいです。\n\n` + candidates.map((p) => `- port ${p.port} / ${p.process_name || '不明'} / ${p.candidate_label} / address ${p.address}`).join('\n') + `\n\nこれらがMCP、ローカルLLM、音声合成、画像生成、ブラウザ操作などに使えるか、初心者向けに確認手順を教えてください。いきなり設定変更やkillはしない前提でお願いします。`;
  return `<div class="ai-candidate-box">
    <div class="ai-candidate-head">
      <div>
        <h3>${t('port.aiTitle')}</h3>
        <p>${t('port.aiDesc')}</p>
      </div>
      <button class="mcp-copy-btn" data-copy="${escapeHtml(askText)}">${t('port.aiCopy')}</button>
    </div>
    <div class="ai-candidate-grid">
      ${candidates.map((p) => `<article class="ai-candidate-card">
        <strong>:${escapeHtml(p.port)}</strong>
        <span>${escapeHtml(p.candidate_label)}</span>
        <small>${escapeHtml(p.process_name || '不明')} / ${escapeHtml(p.visibility_ja || p.address || '')}</small>
      </article>`).join('')}
    </div>
    <p class="ai-candidate-note">${t('port.aiNote')}</p>
  </div>`;
}

function renderPortOwners(data) {
  const area = $('portOwnersArea');
  const summary = $('portOwnersSummary');
  const table = $('portOwnersTable');
  area.style.display = '';
  $('portOwnersStatus').textContent = '';

  // Summary
  summary.innerHTML = `<div class="mcp-summary-box">
    <span class="mcp-summary-count">${data.total || 0}</span>
    <span class="mcp-summary-label">${t('port.listenLabel')}</span>
  </div>
  <p class="mcp-summary-text">${escapeHtml(data.summary || '')}</p>
  ${renderAiCandidates(data.ports || [])}`;

  // Separate by visibility and known/unknown
  const knownPorts = data.ports.filter(p => p.is_known || p.is_self);
  const unknownLocal = data.ports.filter(p => !p.is_known && !p.is_self && p.visibility === 'local');
  const unknownExt = data.ports.filter(p => !p.is_known && !p.is_self && p.visibility === 'all');

  let html = '';

  // Known ports — always visible
  if (knownPorts.length > 0) {
    html += `<h3 class="mcp-section-title">${t('port.knownTitle')}</h3>`;
    html += _portTable(knownPorts, false);
  }

  // Unknown external — warning, shown by default
  if (unknownExt.length > 0) {
    html += `<h3 class="mcp-section-title">${t('port.unknownTitle')}</h3>`;
    html += _portTable(unknownExt, true);
  }

  // Unknown local — collapsed by default
  if (unknownLocal.length > 0) {
    html += `<details class="port-unknown-section">
      <summary class="port-unknown-toggle">${t('port.collapsedTitle')} — ${unknownLocal.length} ▶</summary>
      ${_portTable(unknownLocal, false)}
    </details>`;
  }

  table.innerHTML = html;
}

function _portTable(ports, isExternal) {
  let html = '<div class="port-table-wrap"><table class="port-table">';
  { const h = tArr('port.headers'); html += `<thead><tr><th>${h[0]}</th><th>${h[1]}</th><th>${h[2]}</th><th>${h[3]}</th><th>${h[4]}</th></tr></thead><tbody>`; }
  for (const p of ports) {
    const portClass = p.is_self ? 'port-self' : (isExternal ? 'port-ext' : (p.is_known ? 'port-known' : 'port-local'));
    const desc = p.description ? escapeHtml(p.description) : '<span class="muted">—</span>';
    const selfBadge = p.is_self ? ` <span class="port-self-badge">${t('port.selfBadge')}</span>` : '';
    const unknownBadge = !p.is_known ? ` <span class="port-unknown-badge">${t('port.unknownBadge')}</span>` : '';
    const pathHint = p.exe_path ? `<span class="port-exe" title="${escapeHtml(p.exe_path)}">${escapeHtml(p.process_name)}</span>` : escapeHtml(p.process_name);
    const consultText = `ポート ${p.port} を使っているプロセスを確認したいです。\n\nプロセス名: ${p.process_name}\nPID: ${p.pid}\nアドレス: ${p.address}\n状態: LISTEN中\n\nいきなり kill せず、まず通常の終了方法を教えてください。`;

    html += `<tr class="${portClass}">
      <td class="port-num">:${p.port}</td>
      <td>${pathHint}${selfBadge}${unknownBadge}</td>
      <td class="port-pid">${escapeHtml(p.pid)}</td>
      <td class="port-desc">${desc}</td>
      <td><button class="port-consult-btn" data-consult="${escapeHtml(consultText)}">📋</button></td>
    </tr>`;
  }
  html += '</tbody></table></div>';
  return html;
}

async function runPortOwnersScan() {
  const btn = $('portOwnersBtn');
  const status = $('portOwnersStatus');
  btn.disabled = true;
  btn.textContent = t('checking');
  status.textContent = t('fetching.ports');
  $('portOwnersArea').style.display = 'none';

  try {
    const res = await fetch('/api/port-owners');
    const data = await res.json();
    if (!data.ok) {
      status.textContent = `エラー: ${data.error || '取得失敗'}`;
      return;
    }
    renderPortOwners(data);
  } catch (err) {
    status.textContent = `エラー: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = t('port.scanBtn');
  }
}


// ══════════════════════════════════════════════
//  Basic Tool Checker
// ══════════════════════════════════════════════

function yesNo(value) {
  return value ? t('yes') : t('no');
}

function buildToolBasicsAskText(data) {
  const lines = [
    '初心者のPCでAIエージェント作業を始める前に、基本道具の状態を確認しました。',
    '',
    `実行側: ${data.running_side || '不明'}`,
    '',
    ...(data.tools || []).map((tool) => {
      const current = tool.current_side || {};
      const win = tool.windows_side || {};
      return `- ${tool.label}: ${tool.status_ja} / エージェント側=${yesNo(tool.agent_can_use)} / Windows側=${yesNo(win.present)} / 実行コマンド=${tool.run_command || current.command || tool.id} / version=${current.version || '不明'}`;
    }),
    '',
    'お願い: 不足している道具があっても、勝手にインストール・ログイン・Docker起動・設定変更をしないでください。まず初心者に、何が必要で、どちら側（Windows/WSL）に入れるべきかを短く説明してください。'
  ];
  return lines.join('\n');
}

function renderToolBasics(data) {
  const area = $('toolBasicsArea');
  const summary = $('toolBasicsSummary');
  const table = $('toolBasicsTable');
  area.style.display = '';
  $('toolBasicsStatus').textContent = '';
  const tools = data.tools || [];
  const agentMissing = tools.filter((t) => !t.agent_can_use).length;
  const windowsOnly = tools.filter((t) => t.status === 'windows_only').length;
  const askText = buildToolBasicsAskText(data);
  summary.innerHTML = `<div class="tool-summary-box">
    <div><span class="mcp-summary-count">${tools.length}</span><span class="mcp-summary-label">${t('tools.confirmed')}</span></div>
    <button class="mcp-copy-btn" data-copy="${escapeHtml(askText)}">${t('tools.copyMemo')}</button>
  </div>
  <p class="mcp-summary-text">${escapeHtml(data.summary || '')}</p>
  <div class="tool-agent-route-card">
    <h3>${t('tools.agentRoute')}</h3>
    <p>${t('tools.agentDesc')}</p>
    <ul>
      <li>${t('tools.agentMissing')}: <strong>${agentMissing}</strong></li>
      <li>${t('tools.windowsOnly')}: <strong>${windowsOnly}</strong></li>
      <li>${t('tools.noAutoInstall')}</li>
    </ul>
  </div>`;

  table.innerHTML = `<div class="tool-table-wrap"><table class="tool-table">
    ${(() => { const h = tArr('tools.headers'); return `<thead><tr><th>${h[0]}</th><th>${h[1]}</th><th>${h[2]}</th><th>${h[3]}</th><th>${h[4]}</th><th>${h[5]}</th><th>${h[6]}</th></tr></thead>`; })()}
    <tbody>${tools.map((tool) => {
      const current = tool.current_side || {};
      const win = tool.windows_side || {};
      const cls = tool.agent_can_use ? 'tool-ok' : (win.present ? 'tool-windows-only' : 'tool-missing');
      const statusKey = 'tools.status' + (tool.status === 'both' ? 'Both' : tool.status === 'agent_only' ? 'AgentOnly' : tool.status === 'windows_only' ? 'WindowsOnly' : 'Missing');
      return `<tr class="${cls}">
        <td><strong>${escapeHtml(tool.label)}</strong></td>
        <td><span class="tool-status ${cls}">${escapeHtml(t(statusKey))}</span></td>
        <td class="tool-version">${escapeHtml(current.version || '—')}</td>
        <td><code>${escapeHtml(tool.run_command || current.command || tool.id)}</code></td>
        <td>${escapeHtml(yesNo(win.present))}${win.path ? `<br><small title="${escapeHtml(win.path)}">${escapeHtml(win.command || '')}</small>` : ''}</td>
        <td>${escapeHtml(yesNo(tool.agent_can_use))}${current.path ? `<br><small title="${escapeHtml(current.path)}">${escapeHtml(current.command || '')}</small>` : ''}</td>
        <td><p>${escapeHtml(tool.beginner_explanation || '')}</p><p class="muted">🤖 ${escapeHtml(tool.agent_caution || '')}</p></td>
      </tr>`;
    }).join('')}</tbody>
  </table></div>`;
}

async function runToolBasicsScan() {
  const btn = $('toolBasicsBtn');
  const status = $('toolBasicsStatus');
  btn.disabled = true;
  btn.textContent = t('checking');
  status.textContent = t('fetching.tools');
  $('toolBasicsArea').style.display = 'none';
  try {
    const data = await fetchJson('/api/tool-basics');
    if (!data.ok) {
      status.textContent = `エラー: ${data.error || '取得失敗'}`;
      return;
    }
    renderToolBasics(data);
  } catch (err) {
    status.textContent = `エラー: ${err.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = t('tools.checkBtn');
  }
}

// ══════════════════════════════════════════════
//  Event wiring
// ══════════════════════════════════════════════

document.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  if (target.dataset.filter) {
    state.filter = target.dataset.filter;
    document.querySelectorAll('.filter').forEach((b) => b.classList.toggle('active', b === target));
    renderComments();
  }
  if (target.dataset.id && target.dataset.status) updateComment(target.dataset.id, target.dataset.status);
  if (target.dataset.copy) navigator.clipboard?.writeText(target.dataset.copy);
  // Port consult button
  if (target.classList.contains('port-consult-btn') && target.dataset.consult) {
    const text = target.dataset.consult;
    navigator.clipboard.writeText(text).then(() => {
      target.textContent = '✅ コピーしました';
      setTimeout(() => { target.textContent = '📋'; }, 2000);
    }).catch(() => {
      // Fallback: select text in a temporary textarea
      const ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      target.textContent = '✅ コピーしました';
      setTimeout(() => { target.textContent = '📋'; }, 2000);
    });
  }
});

$('docSelect').addEventListener('change', (e) => loadDoc(e.target.value));
$('refreshBtn').addEventListener('click', async () => { await loadState(); await loadDoc(); });
$('copyDocBtn')?.addEventListener('click', () => navigator.clipboard?.writeText($('docContent').innerText));
$('commentForm').addEventListener('submit', async (e) => { e.preventDefault(); await addComment(e.target); });
$('scanForm')?.addEventListener('submit', async (e) => { e.preventDefault(); await runScan(e.target); });
$('pickFolderBtn')?.addEventListener('click', async () => {
  try { await pickFolder(); } catch (err) { $('pickFolderStatus').textContent = `${t('error.prefix')}${err.message}`;}
});
$('copyScanBtn')?.addEventListener('click', () => navigator.clipboard?.writeText($('scanSummary').dataset.raw || $('scanSummary').innerText));
$('glossarySearch')?.addEventListener('input', (e) => renderGlossary(e.target.value));
$('portOwnersBtn')?.addEventListener('click', runPortOwnersScan);
$('toolBasicsBtn')?.addEventListener('click', runToolBasicsScan);
// ══════════════════════════════════════════════
//  URL Card — browser handoff from agent to user
// ══════════════════════════════════════════════

function renderUrlCards(cards) {
  const area = document.getElementById('urlCardArea');
  const list = document.getElementById('urlCardList');
  if (!cards || !cards.length) {
    area.style.display = 'none';
    return;
  }
  area.style.display = '';
  list.innerHTML = cards.map(c => {
    const safeUrl = escapeHtml(c.url);
    const safeReason = escapeHtml(c.reason || '');
    const isDangerous = /^(javascript|data|file|vbscript):/i.test(c.url);
    const warnClass = isDangerous ? 'url-card-danger' : '';
    return `<div class="url-card ${warnClass}">
      <div class="url-card-head">🔗 ${t('urlcard.title')}</div>
      ${safeReason ? `<p class="url-card-reason"><strong>${t('urlcard.reason')}</strong> ${safeReason}</p>` : ''}
      <p class="url-card-url"><strong>${t('urlcard.url')}</strong> <code>${safeUrl}</code></p>
      ${isDangerous ? '<p class="url-card-warn">⚠️ このURLは安全ではありません。</p>' : ''}
      <div class="url-card-actions">
        <button class="url-card-btn url-card-open" data-card-id="${c.id}" data-url="${safeUrl}" ${isDangerous ? 'disabled title="blocked scheme"' : ''}>${t('urlcard.open')}</button>
        <button class="url-card-btn url-card-copy" data-card-id="${c.id}" data-url="${safeUrl}">${t('urlcard.copy')}</button>
        <button class="url-card-btn url-card-dismiss" data-card-id="${c.id}">${t('urlcard.dismiss')}</button>
      </div>
    </div>`;
  }).join('');
}

async function fetchUrlCards() {
  try {
    const res = await fetch('/api/url-cards');
    const data = await res.json();
    if (data.ok) renderUrlCards(data.cards);
  } catch (_) {}
}

async function updateUrlCardStatus(cardId, status) {
  try {
    await fetch(`/api/url-card/${cardId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status})
    });
    fetchUrlCards();
  } catch (_) {}
}

document.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) return;
  if (target.classList.contains('url-card-open')) {
    const url = target.dataset.url;
    const cardId = target.dataset.cardId;
    window.open(url, '_blank', 'noopener');
    updateUrlCardStatus(cardId, 'opened');
    target.textContent = t('urlcard.opened');
    target.disabled = true;
  }
  if (target.classList.contains('url-card-copy')) {
    const url = target.dataset.url;
    const cardId = target.dataset.cardId;
    navigator.clipboard?.writeText(url).then(() => {
      target.textContent = t('urlcard.copied');
      setTimeout(() => { target.textContent = t('urlcard.copy'); }, 2000);
    });
    updateUrlCardStatus(cardId, 'copied');
  }
  if (target.classList.contains('url-card-dismiss')) {
    updateUrlCardStatus(target.dataset.cardId, 'dismissed');
  }
});

// Poll for URL cards every 10 seconds
setInterval(fetchUrlCards, 10000);

$('langToggle')?.addEventListener('click', () => setLang(currentLang === 'ja' ? 'en' : 'ja'));

(async function boot() {
  setupDropZone();
  await loadState();
  await loadDoc('readme-ja');
  loadGlossary();
  switchTab('try');
  // Apply saved language preference
  setLang(currentLang);
})();
