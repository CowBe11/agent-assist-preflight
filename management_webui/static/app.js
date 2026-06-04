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
  const terms = Object.entries(glossaryData);
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
    return a[0].localeCompare(b[0], 'ja');
  });
  $('glossaryCount').textContent = `${filtered.length} / ${terms.length} 件`;
  if (!filtered.length) {
    grid.innerHTML = `<p class="muted" style="padding:2rem;text-align:center">「${escapeHtml(filter)}」に一致する用語は見つかりませんでした。別の言葉で試してください。</p>`;
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
    return `<section class="reader-guide">
      <p class="reader-guide-kicker">最初に読むところ</p>
      <h3>まず「これは何のための道具か」を短く説明し、そのあとに機能と使い方を並べています。</h3>
      <p>初めて見る人には、機能一覧より先に「いつ使うのか」「何をしないのか」が分かる方が読みやすいので、README はその順番で整理しています。</p>
    </section>`;
  }
  if (id === 'beginner-guide') {
    return `<section class="reader-guide">
      <p class="reader-guide-kicker">初心者向けガイド</p>
      <h3>コマンドを実行する前に、何を確認すればいいかを順番に読むための文書です。</h3>
      <p>README で全体像を掴んだあと、実際にフォルダをチェックするときの読み方をここで確認できます。</p>
    </section>`;
  }
  return '';
}

// ── Comments ──
function renderComments() {
  const box = $('comments');
  const comments = state.filter === 'all' ? state.comments : state.comments.filter((c) => c.status === state.filter);
  if (!comments.length) {
    box.innerHTML = '<p class="muted">この状態のリクエストはまだ無い。</p>';
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
      ${c.beginner_reaction ? `<p><strong>反応:</strong> ${escapeHtml(c.beginner_reaction)}</p>` : ''}
      <p>${escapeHtml(c.text)}</p>
      ${c.owner_note ? `<p><strong>作業メモ:</strong> ${escapeHtml(c.owner_note)}</p>` : ''}
      <button class="copy-btn" data-copy="${escapeHtml(c.text)}">このリクエストをコピー</button>
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
  const ja = jaHelp[item.category];
  return { what: ja?.[0] || item.plain_language || '', why: ja?.[1] || item.why_it_matters || '', next: ja?.[2] || item.beginner_next_step || '', title: `項目${index + 1}: ${item.category}` };
}

function renderLegendCard(items) {
  const present = new Set();
  for (const item of items) { if (item.category) present.add(item.category); }
  if (!present.size) return '';
  const chips = Array.from(present).map((cat) => {
    const emoji = jaCategoryEmoji[cat] || '•';
    const label = jaCategoryLabel[cat] || cat;
    return `<span class="legend-chip"><span class="legend-emoji">${emoji}</span><span>${escapeHtml(label)}</span></span>`;
  }).join('');
  return `<div class="legend-card"><div class="legend-head"><span class="legend-title">🔍 このスキャンで検出された話題</span><span class="muted">${present.size} 種類</span></div><p class="muted legend-hint">下に続く各カードに付いている絵文字の意味です。専門用語にカーソルを合わせると解説が出ます。</p><div class="legend-chips">${chips}</div></div>`;
}

function renderIntroCard() {
  return `<div class="intro-card"><div class="intro-head">📋 このツールがやること（毎回確認）</div><ul class="intro-list"><li><strong>読み取り専用で</strong>スキャンします。指定されたフォルダのファイルを<strong>読みます</strong>。</li><li><strong>ファイルは書き換えません</strong>。新規作成も削除もしません。</li><li><strong>外部には送信しません</strong>。スキャン結果はあなたのブラウザにだけ表示されます。</li><li><strong>コマンドは実行しません</strong>。検出された注意点を表示するだけです。</li></ul><p class="muted intro-note">個人情報が含まれるフォルダを最初に入れるのは避け、テスト用フォルダで試してからにしてください。</p></div>`;
}

function renderScanResult(data) {
  if (!data.ok) {
    $('scanSummary').innerHTML = `<p class="bad">確認できませんでした: ${escapeHtml(data.error || 'unknown error')}</p>`;
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
      <p><strong>これは何？</strong> ${annotateTerms(help.what)}</p>
      <p><strong>なぜ確認？</strong> ${annotateTerms(help.why)}</p>
      <p><strong>次にすること:</strong> ${annotateTerms(help.next)}</p>
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
              <p><strong>判定:</strong> ${escapeHtml(report.decision)}</p>
              <p><strong>最大優先度:</strong> ${escapeHtml(report.max_priority)}</p>
              <p><strong>確認項目:</strong> ${items.length}件</p>
              <p>${escapeHtml(beginnerSummaryText(report.beginner_summary))}</p>
            </div>
            <div class="decision-card-actions">
              <button type="button" class="primary" data-action="rerun">🔄 別のフォルダでやり直す</button>
              <button type="button" class="expand-all-btn">全部ひらく</button>
              <button type="button" class="collapse-all-btn">全部たたむ</button>
              <button type="button" class="clear-result-btn">✕ 結果をしまう</button>
            </div>
          </div>
        </div>
        <div class="scan-items-wrap">${renderedItems || '<p class="muted">表示する確認項目はありません。</p>'}</div>
        <div class="next-step-card">
          <div class="next-step-head">👉 このあとどうすればいい？</div>
          <ol class="next-step-list">
            <li>上の確認項目と元の説明書を読み、<strong>分からない点が残る場合は実行前に相談</strong>してください。</li>
            <li>心配な項目があったら、<strong>「診断結果をコピー」ボタンでコピー</strong>して、ChatGPT や詳しい人に「これ大丈夫？」と相談してください。</li>
            <li>このツールは<strong>読み取っただけで、あなたのPCは何も変わっていません</strong>。安心して閉じても大丈夫です。</li>
          </ol>
          <p class="muted next-step-foot">🆓 このツールは完全無料・オープンソースです。お金は一切かかりません。</p>
        </div>
      </div>
    </details>`;
}

function clearScanResult() {
  $('scanSummary').innerHTML = '<p class="muted scan-empty-msg">まだ実行していません。ダウンロードしたフォルダのパスを入れるか、README などのテキストファイルをドラッグ＆ドロップしてください。</p>';
  $('scanResultTools').style.display = 'none';
  delete $('scanSummary').dataset.raw;
}

function rerunScan() {
  const input = $('targetPathInput');
  if (input) { input.focus(); input.select?.(); }
  const shell = $('scanSummary').querySelector('details.scan-shell');
  if (shell) shell.open = false;
  const status = $('pickFolderStatus');
  if (status) status.textContent = 'パスを変えるか、「フォルダ/ファイルを選ぶ...」で選び直して「このフォルダを確認する」を押してください。';
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
  $('scanSummary').textContent = '確認中...';
  const payload = Object.fromEntries(new FormData(form).entries());
  const data = await fetchJson('/api/scan', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
  renderScanResult(data);
  // Scroll to result
  $('scanResultArea')?.scrollIntoView?.({ behavior: 'smooth' });
}

async function pickFolder() {
  const status = $('pickFolderStatus');
  status.textContent = 'Windowsの「開く」ダイアログを開いています...';
  const data = await fetchJson('/api/pick-folder');
  if (!data.ok) {
    status.textContent = data.cancelled ? 'キャンセルしました。' : `選択できませんでした: ${data.error || 'unknown error'}`;
    return;
  }
  $('targetPathInput').value = data.path;
  status.textContent = `選択しました: ${data.path}`;
}

async function scanTextFile(file) {
  if (!file) return;
  const status = $('scanSummary');
  if (file.size > 1_000_000) {
    status.innerHTML = '<p class="bad">1MB を超えるテキストファイルは扱いません。</p>';
    return;
  }
  status.textContent = `${file.name} を読み込み中...`;
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
      <h3>🤖 AI/MCP候補まとめ</h3>
      <p>よく知られたAI・MCP・ローカルLLM系ポートは見つかりませんでした。これは「何も使えない」という意味ではなく、今このPCで待ち受けているものからは候補を拾えなかった、という意味です。</p>
    </div>`;
  }
  const askText = `このPCでAIエージェントやバイブコーディングに使えそうなローカルツール候補を確認したいです。\n\n` + candidates.map((p) => `- port ${p.port} / ${p.process_name || '不明'} / ${p.candidate_label} / address ${p.address}`).join('\n') + `\n\nこれらがMCP、ローカルLLM、音声合成、画像生成、ブラウザ操作などに使えるか、初心者向けに確認手順を教えてください。いきなり設定変更やkillはしない前提でお願いします。`;
  return `<div class="ai-candidate-box">
    <div class="ai-candidate-head">
      <div>
        <h3>🤖 AI/MCP候補まとめ</h3>
        <p>ポート一覧の中から、AIエージェント・MCP・ローカルLLM・VOICEVOX・ComfyUI・ブラウザ操作に関係しそうなものだけを先にまとめました。</p>
      </div>
      <button class="mcp-copy-btn" data-copy="${escapeHtml(askText)}">📋 AIに聞く文をコピー</button>
    </div>
    <div class="ai-candidate-grid">
      ${candidates.map((p) => `<article class="ai-candidate-card">
        <strong>:${escapeHtml(p.port)}</strong>
        <span>${escapeHtml(p.candidate_label)}</span>
        <small>${escapeHtml(p.process_name || '不明')} / ${escapeHtml(p.visibility_ja || p.address || '')}</small>
      </article>`).join('')}
    </div>
    <p class="ai-candidate-note">📖 見つかった候補は「使えるかもしれない入口」です。MCPとして本当に使えるか、安全に接続できるかは、そのツールの設定と説明を確認してください。</p>
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
    <span class="mcp-summary-label">ポートがLISTEN中</span>
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
    html += '<h3 class="mcp-section-title">🟢 用途がわかっているポート</h3>';
    html += _portTable(knownPorts, false);
  }

  // Unknown external — warning, shown by default
  if (unknownExt.length > 0) {
    html += '<h3 class="mcp-section-title">⚠️ 見慣れないポート（外から見える可能性）</h3>';
    html += _portTable(unknownExt, true);
  }

  // Unknown local — collapsed by default
  if (unknownLocal.length > 0) {
    html += `<details class="port-unknown-section">
      <summary class="port-unknown-toggle">🔒 見慣れないポート（自分だけ） — ${unknownLocal.length}個 ▶</summary>
      ${_portTable(unknownLocal, false)}
    </details>`;
  }

  table.innerHTML = html;
}

function _portTable(ports, isExternal) {
  let html = '<div class="port-table-wrap"><table class="port-table">';
  html += '<thead><tr><th>ポート</th><th>プロセス</th><th>PID</th><th>説明</th><th>相談</th></tr></thead><tbody>';
  for (const p of ports) {
    const portClass = p.is_self ? 'port-self' : (isExternal ? 'port-ext' : (p.is_known ? 'port-known' : 'port-local'));
    const desc = p.description ? escapeHtml(p.description) : '<span class="muted">—</span>';
    const selfBadge = p.is_self ? ' <span class="port-self-badge">このツール</span>' : '';
    const unknownBadge = !p.is_known ? ' <span class="port-unknown-badge">見慣れない</span>' : '';
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
  btn.textContent = 'チェック中...';
  status.textContent = 'ポート情報を取得しています...';
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
    btn.textContent = '🔍 今使われているポートを一覧';
  }
}


// ══════════════════════════════════════════════
//  Basic Tool Checker
// ══════════════════════════════════════════════

function yesNo(value) {
  return value ? 'あり' : 'なし';
}

function buildToolBasicsAskText(data) {
  const lines = [
    '初心者のPCでAIエージェント作業を始める前に、基本道具の状態を確認しました。',
    '',
    `実行側: ${data.running_side || '不明'}`,
    '',
    ...(data.tools || []).map((t) => {
      const current = t.current_side || {};
      const win = t.windows_side || {};
      return `- ${t.label}: ${t.status_ja} / エージェント側=${yesNo(t.agent_can_use)} / Windows側=${yesNo(win.present)} / 実行コマンド=${t.run_command || current.command || t.id} / version=${current.version || '不明'}`;
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
    <div><span class="mcp-summary-count">${tools.length}</span><span class="mcp-summary-label">個の基本道具を確認</span></div>
    <button class="mcp-copy-btn" data-copy="${escapeHtml(askText)}">📋 AIに渡す確認メモをコピー</button>
  </div>
  <p class="mcp-summary-text">${escapeHtml(data.summary || '')}</p>
  <div class="tool-agent-route-card">
    <h3>🤖 AIエージェント向け導線</h3>
    <p>エージェントは「自分が動いている側」にある道具しかそのまま使えません。Windows側だけにある道具をWSL側エージェントが使う作業では失敗することがあります。</p>
    <ul>
      <li>エージェント側で見つからない道具: <strong>${agentMissing}</strong> 個</li>
      <li>Windows側だけで見つかった道具: <strong>${windowsOnly}</strong> 個</li>
      <li>不足があっても、勝手にインストールせず、まずユーザーに確認してください。</li>
    </ul>
  </div>`;

  table.innerHTML = `<div class="tool-table-wrap"><table class="tool-table">
    <thead><tr><th>道具</th><th>状態</th><th>バージョン</th><th>実行コマンド</th><th>Windows側</th><th>エージェント側</th><th>説明 / 注意</th></tr></thead>
    <tbody>${tools.map((t) => {
      const current = t.current_side || {};
      const win = t.windows_side || {};
      const cls = t.agent_can_use ? 'tool-ok' : (win.present ? 'tool-windows-only' : 'tool-missing');
      return `<tr class="${cls}">
        <td><strong>${escapeHtml(t.label)}</strong></td>
        <td><span class="tool-status ${cls}">${escapeHtml(t.status_ja)}</span></td>
        <td class="tool-version">${escapeHtml(current.version || '—')}</td>
        <td><code>${escapeHtml(t.run_command || current.command || t.id)}</code></td>
        <td>${escapeHtml(yesNo(win.present))}${win.path ? `<br><small title="${escapeHtml(win.path)}">${escapeHtml(win.command || '')}</small>` : ''}</td>
        <td>${escapeHtml(yesNo(t.agent_can_use))}${current.path ? `<br><small title="${escapeHtml(current.path)}">${escapeHtml(current.command || '')}</small>` : ''}</td>
        <td><p>${escapeHtml(t.beginner_explanation || '')}</p><p class="muted">🤖 ${escapeHtml(t.agent_caution || '')}</p></td>
      </tr>`;
    }).join('')}</tbody>
  </table></div>`;
}

async function runToolBasicsScan() {
  const btn = $('toolBasicsBtn');
  const status = $('toolBasicsStatus');
  btn.disabled = true;
  btn.textContent = 'チェック中...';
  status.textContent = '基本道具を確認しています...';
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
    btn.textContent = '🔍 基本道具をチェック';
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
  try { await pickFolder(); } catch (err) { $('pickFolderStatus').textContent = `選択できませんでした: ${err.message}`; }
});
$('copyScanBtn')?.addEventListener('click', () => navigator.clipboard?.writeText($('scanSummary').dataset.raw || $('scanSummary').innerText));
$('glossarySearch')?.addEventListener('input', (e) => renderGlossary(e.target.value));
$('portOwnersBtn')?.addEventListener('click', runPortOwnersScan);
$('toolBasicsBtn')?.addEventListener('click', runToolBasicsScan);

(async function boot() {
  setupDropZone();
  await loadState();
  await loadDoc('readme-ja');
  loadGlossary();
  // デフォルトは「試す」タブ
  switchTab('try');
})();
