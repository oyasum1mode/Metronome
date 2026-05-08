# Metronome Pro — 仕様書・引き継ぎドキュメント

## 概要
マーチング / 吹奏楽向けの高機能メトロノームWebアプリ。  
曲ごとにセクション分割し、テンポ・拍子チェンジを管理して練習できる。  
GitHub Pages で配布する PWA 対応 Web アプリ。

---

## ファイル構成

- `metronome.html` — アプリ本体（HTML + CSS + JS）
- `manifest.json` — PWA マニフェスト
- `sw.js` — Service Worker（オフライン対応）
- `icons/icon-192.png` — PWA アイコン（192×192px）
- `icons/icon-512.png` — PWA アイコン（512×512px）
- `icons/apple-touch-icon.png` — iOS Safari ホーム画面アイコン（180×180px）

> `manifest.json`・`sw.js`・`icons/` は PWA 化（Phase 4）で新規追加するファイル。  
> Service Worker はセキュリティ制約上 HTML に inline できないため別ファイル必須。

---

## 想定ユースケース

- **主な利用デバイス**: スマートフォン（iPhone / Android、縦向き中心）
- **音声出力**: Bluetooth スピーカー経由で練習場に流す
- **利用シーン**: 練習中、片手操作でテンポや Subdivision を切り替える
- **UI 設計方針**: 操作ターゲットは最低 44×44px。重要なコントロールは親指の届く画面下半分に優先配置する

---

## 4タブ構成

### 1. テンポ（独立メトロノーム）
- 曲・セクションとは**完全に無関係**
- BPM: 20〜400（スライダー + ±1/±5/±10ボタン）
- 拍子: 1〜8（スライダー、デフォルト4/4）
- Tap Tempo対応
- **Subdivision Click**: 後述の仕様に従いトグルボタンで切替可能
- Tap Off / End Check / セクション機能なし
- スペースキーで再生/停止

### 2. パフォーマンス（曲連動メトロノーム）
- 曲編集で作成したセクションデータと連動
- 曲名表示、現在セクション・小節番号表示
- **Tap Off**: 再生開始前のカウントイン（4拍 or 8拍選択、ON/OFF）
- **End Check**: 練習範囲終了後に鳴る確認ビート（4拍 or 8拍選択、ON/OFF）
  - 「前テンポ」: rangeFromのテンポ（EC直前まで鳴っていたテンポ）で鳴る
  - 「後テンポ」: rangeToのテンポ（ECはrangeToの代わりに鳴るため）で鳴る
  - rangeToの1拍目からEnd Check音に切り替わる（rangeToのセクション自体は通常再生しない）
  - ただし rF === rT の場合は、そのセクション自体をEC音で置き換え
- **練習範囲**: 開始セクション → 終了セクション をドロップダウンで選択。表示は `name (label)` 形式（例: `Intro (A)`）。name が空のセクションは label のみ表示
- **テンポオフセット**: BPM 表示の直下に `[ -10 ] [ In tempo ] [ +10 ]` ボタンで現曲全セクションのテンポを一括でずらせる（遅練習用）。詳細は「テンポオフセット」節
- **Subdivision Click**: 後述の仕様に従いトグルボタンで切替可能
- スペースキーで再生/停止

### 3. 曲編集
- 曲名入力
- セクション追加（A〜Z, AA〜ZZ まで自動ラベル）
  - 各セクション: 開始小節、小節数（0=手動）、テンポ、拍子
  - ▲▼ボタンで順序変更可能
- エンドブロック追加（1曲に1つのみ、常に最後に配置）
  - 頭1拍のみ再生される特殊ブロック
  - ▲▼ボタンなし（位置固定）
- 💾 ライブラリに保存ボタン
- エクスポート（Base64コード）/ インポート
- クリア

### 4. ライブラリ
- 保存した曲一覧
- クリックで曲を読み込み → パフォーマンスタブへ遷移
- 各曲からエクスポート / 削除
- 「+ 新しい曲を作成」ボタン
- データはブラウザの `localStorage` で永続化（キー: `metronome-lib`）
- 初回起動時は曲一覧が空。ユーザーが作成・保存した曲のみがそのブラウザに残る（端末・ブラウザをまたぐ共有はエクスポート/インポート経由）

---

## 追加機能: Subdivision Click

メインビートに重ねてサブクリックを鳴らすオプション機能。テンポタブ・パフォーマンスタブ両方で利用可能。

### UI
- トグルボタン 1つ（循環式）
- 状態遷移: **None → 8th → Triplet → 16th → None**
- ボタン上に現在の状態を表示（例: `—` / `8th` / `Tri` / `16th`）

### 音声仕様
| 状態 | 分割数 | インターバル@120BPM | 音量 | 音色 |
|------|--------|---------------------|------|------|
| None | — | — | — | — |
| 8th | 2分割 | 250ms | メインの 40〜50% | メインと異なる音色（三角波 or 低周波サイン波） |
| Triplet | 3分割 | 166.7ms | メインの 40〜50% | 同上 |
| 16th | 4分割 | 125ms | メインの 40〜50% | 同上 |

メインビート自体は Subdivision の有無にかかわらず通常通り鳴らす。サブクリックはその間隔で追加される。

### 動作仕様
- テンポ変更・拍子変更に追従（次スケジューリングサイクルから即反映）
- Start/Stop 時も Subdivision の選択状態を保持
- **メインとサブの位相ズレが発生しないこと**  
  → lookahead スケジューラ内で同一 `beatTime` を基準に `beatTime + subOffset * n` で算出・予約すること
- Count-in（Tap Off）中および End Check 中はサブクリックを鳴らさない

### 実装要件
- `AudioContext.currentTime` ベースの lookahead scheduling で実装すること（後述）
- サブビートは、メインビートと同じスケジューラ内で一括予約する

---

## タイミング精度・スケジューリング方式

### 現状の実装（v1 — 要書き換え）

> ⚠️ **現在のコードは lookahead scheduling 未使用。Subdivision 実装前（Phase 1）に書き換えが必要。**

| タブ | 現状の方式 | 問題点 |
|------|-----------|--------|
| テンポ | `setInterval(mTick, 60000/mBpm)` | JS イベントループの遅延がそのまま音のジッタになる |
| パフォーマンス | `setTimeout` チェーン | 同上。セクション境界の精度は改善されているが根本は同じ |

現在の `ck()` 関数は `o.start(actx.currentTime)` を呼んでいる（= コールバック発火の瞬間に鳴らす）。  
コールバックが 10ms 遅れれば音も 10ms 遅れる。16th note（125ms@120BPM）に対して ±10ms は約 8% の誤差になり聴感上問題になる。

### 目標実装：Chris Wilson 方式

```
┌──────────────────────────────────────────────────────────┐
│ scheduler（setInterval 25ms ごとに実行）                   │
│  └─ 現在時刻から 100ms 先までのビートを先読み              │
│  └─ oscillator.start(beatTime) で音を予約                 │
│  └─ サブビートも beatTime + subOffset × n で同時予約      │
├──────────────────────────────────────────────────────────┤
│ visual updater（requestAnimationFrame）                    │
│  └─ noteQueue[] を参照して dot 点灯・BPM フラッシュ       │
└──────────────────────────────────────────────────────────┘
```

- 音声スケジューリングとビジュアルフィードバックを**完全に分離**する
- `noteQueue[]` に予約済みビートを積み、visual updater が消化する方式
- セクション遷移・Count-in・End Check もこの方式に統合する

### Bluetooth レイテンシに関する制約

- A2DP Bluetooth の遅延は 100〜400ms（デバイス依存の固定オフセット）
- **アプリ側でレイテンシを削減する手段はない**
- `AudioContext.setSinkId()` による出力先プログラム選択は iOS Safari / Chrome 両方で**未サポート**（Apple の制限）
- lookahead scheduling により、main ビートと sub ビートの**相対タイミングは正確**に保たれる
- 全音声に均一なオフセットが乗るため、練習用途では実用上問題なし
- UI に「Bluetooth スピーカー使用時は音が少し遅れる場合があります」旨を添えることを推奨

---

## 音色（Web Audio API）

BOSS DB-30 系の Click 音（木魚っぽい「コッカッ」）を Web Audio で合成する。サンプル音源は将来導入予定だが、現時点では合成のみ。

> Pa/Ta フォルマント版（DB-90 Voice 風の試作）は DB-90 実機との差が大きかったため、サンプル音源導入までは DB-30 Click 版に戻して運用する。

### ノード構成

```
NoiseBuffer(50ms) → BiquadFilter(BPF) → Gain(env) ─┐
                                                    ├→ masterGain → destination
Oscillator(sine)                      → Gain(env) ─┘
```

- **ノイズ + バンドパスフィルター**でピッチを作るパーカッシブ成分（Click の主成分）
- **サイン波（少量）**で芯を加える
- 各 Gain は超高速アタック（≦1ms）→ exp 減衰でクリック感を出す
- ノイズバッファは 50ms、`getNoiseBuffer` でキャッシュ再利用

### 音色パラメータ（実装目安）

| 種類 | BPF中心周波数 | Q | ノイズピーク | サインピーク | 減衰 | 用途 |
|------|------------|---|------------|------------|------|------|
| accent | 2200 Hz | 12 | 0.9 | 0.25 | 50 ms | 小節頭（1拍子の場合は全拍） |
| normal | 1100 Hz | 12 | 0.6 | 0.18 | 40 ms | 通常拍 |
| ci | 1500 Hz | 14 | 0.7 | 0.22 | 45 ms | Tap Off / End Check |
| sub | 800 Hz | 10 | 0.35 | 0.08 | 25 ms | Subdivision サブビート |

数値は試聴で調整可。`playClick(type, time, opts)` の `opts` キーは旧形式（`frequency` / `Q` / `noiseGain` / `toneGain` / `toneDecay` / `waveform`）でオーバーライド可能。

---

## ビジュアルフィードバック

- ビートドット: 拍数分の丸が並び、現在拍がハイライト
  - 通常: オレンジ (`--ba`)
  - アクセント: 明るいオレンジ (`--bac`)
  - Count-in: 紫 (`--ci`)
  - End Check: 緑 (`--ec`)
  - End: 黄色 (`--endc`)
- BPM数値が拍に合わせて色フラッシュ
- 再生ボタンにパルスリングアニメーション
- **accel / rit 中の表示**: BPM 数値は瞬時値で逐次更新（`Math.round` で整数化）。テンポ名の隣に方向アイコン `↗`（accel: tempoEnd > tempo）/ `↘`（rit: tempoEnd < tempo）を表示。定速時は非表示
- **テンポオフセット適用時の表示**: BPM 数値はオフセット込みの値を表示。オフセット 0 でなければ `In tempo (+30)` のようにオフセット値も `In tempo` ボタンに併記
- **Subdivision 中のサブビート表示**: メインドットの間に補助ドット（subdot）を挿入する
  - 8th → メインドット間に 1 個 / Triplet → 2 個 / 16th → 3 個 / None → なし
  - 補助ドットはメインドットより小さく（直径 4〜6px）、色は控えめ（`var(--dm)` など）
  - サブビート発音時に短くフラッシュ
  - Count-in / End Check 中はサブビートを鳴らさないため非表示

---

## 外観 / テーマ

- ダークテーマ固定。ライトテーマは可読性が低いため廃止
- テーマ切替ボタン（旧 `themeBtn`）も廃止し、CSS 変数は `:root` に集約
- フッターのアフィリエイト/広告枠（旧 `.aff-footer`）は運用しないため削除

---

## データ構造

### セクション（secs配列）
```javascript
{
  type: 'main' | 'end',     // mainは通常セクション、endはエンドブロック
  label: 'A',               // 自動生成（A〜ZZ）
  name: 'Intro',            // ユーザー入力の名前
  startMeasure: 1,          // 曲中の開始小節番号（表示用）
  measures: 4,              // 小節数（0=手動モード）。endの場合は1固定
  tempo: 120,               // セクション開始時の BPM
  tempoEnd: 100,             // セクション終了時の BPM（省略時 = tempo、定速）
  tempoCurve: 0,             // -1.0〜+1.0、変化カーブ（既定 0=線形）。type='end' では未使用
  timeSig: 4                // 拍子（1〜8）
}
```

### ライブラリ（lib配列）
```javascript
{
  id: 's1234567890',        // ユニークID
  title: 'Doddy',           // 曲名
  sections: [...]            // セクション配列のコピー
}
```

### エクスポート形式
JSON → Base64エンコード。バージョン: `v:4`（`tempoEnd` / `tempoCurve` を含む。読込側で未定義なら定速扱いとしてデフォルト補完）。

---

## accel / rit（テンポ変化）

通常セクションの中で開始テンポから終了テンポへ滑らかに変化させる機能。指揮者ごとの揺らし方の違いをカーブスライダーで表現する。

### データ表現

セクションの `tempo`（開始）と `tempoEnd`（終了）、`tempoCurve`（カーブ）の 3 値で表す。`tempoEnd === tempo` または `tempoEnd` 未定義の場合は定速。

### 進捗とカーブ式

```
t  = (measureIndex * timeSig + beatIndex) / (measures * timeSig)   // 0〜1
v  = tempoCurve                                                     // -1〜+1
t' = t ^ (2 ^ v)                                                    // v=0→線形, v=-1→t^0.5, v=+1→t^2
BPM(t) = tempo + (tempoEnd - tempo) * t'
```

- スライダー中央 (v=0): 線形（均等にテンポ変化）
- スライダー左 (v<0): 早めに変化（前半に大きく動く）
- スライダー右 (v>0): 遅めに変化（後半に大きく動く）
- `measures = 0`（手動小節モード）の場合は定速にフォールバック（進捗が定義できないため）

### スケジューラへの組み込み

- `createPerformanceTransport.scheduleNext(time)` 内で `currentTempo = tempoAt(sec, progress(...))` に逐次更新
- `advance()` で `nextNoteTime += 60 / currentTempo`
- `scheduleSubdivision(time, beatDuration, ...)` の `beatDuration = 60 / currentTempo`
- `enterMain()` の `currentTempo = clampTempo(sec.tempo)` はセクション先頭の初期化として残す

### 曲編集 UI

通常セクションの編集行に以下を追加:

- **終了テンポ** 数値入力（既定値は `tempo` と同じ。空欄なら定速扱い）
- **カーブ** スライダー（`min=-1 max=1 step=0.1 value=0`）

縦長になりすぎないよう、accel/rit 入力は **「詳細を開く」トグル / 折りたたみ行** に隠す方針。エンドセクションには表示しない。

### ビジュアル

- 再生中は BPM 数値を瞬時値で更新（`pUpd()` を `scheduleNext` 内で呼ぶ。`Math.round` で整数化）
- テンポ名の隣に方向アイコン `↗`（accel）/ `↘`（rit）/ なし（定速）

---

## テンポオフセット（パフォーマンスタブ専用）

遅いテンポで練習するために、現曲のすべてのセクションのテンポを一括でずらすオフセット機構。

### 仕様

- **配置**: パフォーマンスタブの BPM 数値の直下に `[ -10 ] [ In tempo ] [ +10 ]` を横並び
- **状態**: グローバル変数 `tempoOffset`（初期値 0、範囲 -200〜+200）
- **適用**: `scheduleNext` 内で `currentTempo = clampTempo(tempoAt(sec, progress(...)) + tempoOffset)`
- **表示**: `In tempo` ボタンに現在値を併記。例: オフセット 0 → `In tempo`、+30 → `In tempo (+30)`、-20 → `In tempo (-20)`
- **リセットタイミング**: `loadSong` / `newS`（新規曲作成）/ `clB`（クリア）の冒頭で 0 にリセット
- **保持**: 再生停止 / タブ切替では保持。リロードで 0（localStorage には保存しない）
- **適用範囲**: パフォーマンスタブのみ。テンポタブ（`createMetroTransport`）には影響させない

### UI

- ボタンは既存の `.fb` スタイル（`min-width:44px; min-height:44px; pill 形`）を流用
- `In tempo` ボタンのみ最低幅 120px に拡張してオフセット値併記の余裕を持たせる
- `.ofb`（offset buttons）クラスで flex 横並び中央寄せ

---

## 技術スタック

- HTML/CSS/JS（フレームワークなし）
- Web Audio API（音声生成 + lookahead scheduling）
- `localStorage`（永続化。キー: `metronome-lib`=曲ライブラリ、`metronome-volume`=マスター音量）
- Service Worker（オフラインキャッシュ）
- Wake Lock API（画面スリープ防止、再生中のみ）
- Google Fonts: DM Mono, Instrument Serif

---

## モバイルUI要件（1画面完結）

### ターゲット環境

- 縦向き（portrait）が主。**iPhone SE 相当（375×667px）で破綻しないこと**
- 横向き（landscape）は最低限レイアウトが崩れないこと

### ビューポート・セーフエリア対応

- iOS Safari の `100vh` 問題に対応するため **`svh`** を使用する
  - `dvh`（Dynamic Viewport Height）はアドレスバーアニメーション中に毎フレーム再計算が走りレイアウトジッタが発生する。固定 1 画面レイアウトには `svh` が適切
  - フォールバック: `svh` 非対応ブラウザ向けに `100vh` を先に記述する
  ```css
  height: 100vh;        /* fallback */
  height: 100svh;
  ```
- セーフエリア対応: `env(safe-area-inset-*)` を使用
  - iOS Chrome（WKWebView ベース）ではページロード直後に値が未設定になる WebKit バグ（#191872）があるため、**CSS フォールバック値を必ず併記すること**
  ```css
  padding-bottom: 16px;                              /* fallback */
  padding-bottom: max(16px, env(safe-area-inset-bottom));
  ```
- `<meta name="viewport">` に `viewport-fit=cover` を追加すること

### レイアウト優先順位

- **主要コントロール**（Start/Stop ボタン、BPM 調整、Subdivision トグル）は**画面下半分**に優先配置
- タップターゲットは最低 **44×44px** を確保
- ±1/±5/±10 ボタン（`.fb`）は **min-width / min-height ともに 44px**

### スタートボタンと Tap Tempo のレイアウト

- スタートボタン（`.pb`）は **角丸四角（pill）** 形状で 220×64px、`border-radius: 32px`
- **テンポページ**: スタートボタンの左に Tap Tempo を横並び。Tap Tempo は同じ pill 形状で **110×64px（高さ同じ、幅狭）**。`.pw` を flex コンテナにして `[Tap] [Start]` を中央揃え
- **パフォーマンスページ**: タップテンポなし。スタートボタン単独を中央配置（同じ 220×64 サイズ）
- iPhone SE（375×667）で破綻しないこと。狭幅では gap や周辺マージンを縮めて対応

### タッチ・スクロール挙動

- **テンポ・パフォーマンスタブ**: 1 画面に収めることが前提のため、iOS Safari/Chrome のバウンス（rubber-band）とプルトゥリフレッシュを抑止する
  - `html, body { overscroll-behavior: none }`
  - 当該タブに `touch-action: pan-x pinch-zoom` を付与し、縦スワイプによるスクロールを止める
  - スライダー（`input[type=range]`）には `touch-action: pan-x` を残し、横操作を確保する
- **曲編集・ライブラリタブ**: コンテンツが長くなるためスクロール可（既存の `overflow:auto` を維持）
- ランドスケープ用メディアクエリ（`@media (orientation:landscape) and (max-height:500px)` で `body{overflow:auto}`）は維持

---

## マスター音量

- ヘッダー右側など、画面下半分の主要コントロールを邪魔しない位置にスライダーを設置
- 範囲: 0.0 〜 1.5 / ステップ: 0.05 / デフォルト: 1.0
- 永続化: `localStorage` キー `metronome-volume`
- 既存の `masterGain.gain.value` に書き込む形で実装する（音生成側は全ノードを `masterGain` に集約済み）
- `input` イベントで即時反映

---

## PWA 要件

### 対応ブラウザ・プラットフォーム

| ブラウザ | ホーム画面追加 | Service Worker | Wake Lock |
|---------|-------------|---------------|-----------|
| iOS Safari | ✅ | ✅（制限あり） | ✅（iOS 16.4+）|
| iOS Chrome | ❌ | ✅（制限あり） | ✅（iOS 16.4+）|
| Android Chrome | ✅ | ✅ | ✅ |

> **iOS ではホーム画面への追加は Safari のみ対応。**  
> iOS Chrome ユーザーへは「Safari で開いて追加してください」と案内する文言を UI に添えること。

### manifest.json（雛形）

```json
{
  "name": "Metronome Pro",
  "short_name": "Metronome",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#0a0a0c",
  "theme_color": "#f05e23",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

### 必要なアイコンファイル

| ファイル | サイズ | 用途 |
|---------|--------|------|
| `icons/icon-192.png` | 192×192px | Android Chrome ホーム画面・W3C manifest |
| `icons/icon-512.png` | 512×512px | スプラッシュ画面・Google Play PWA |
| `icons/apple-touch-icon.png` | 180×180px | iOS Safari「ホーム画面に追加」アイコン |

- フォーマット: PNG（背景色あり推奨、透過なし）
- デザイン: シンプルなメトロノームまたはビートドットのモチーフ。SVG でマスターを作成し PNG に書き出すこと

### Service Worker（sw.js）

- キャッシュ戦略: **Cache First**（静的アセット向け）
- キャッシュ対象: `metronome.html`、`manifest.json`、アイコン類、Google Fonts
- オフライン時はキャッシュ版を返す

### Wake Lock API

- 再生開始時（`pStart()` / `mStart()`）に `navigator.wakeLock.request('screen')` を呼ぶ
- 停止時（`pStop()` / `mStop()`）に `wakeLock.release()` を呼ぶ
- API 非対応端末（iOS 16.3 以下等）は `try/catch` で無害に握り潰す
- ページ非表示時（`visibilitychange` イベント）は OS が自動解除するため、再表示時に再取得する処理を追加すること

### HTML `<head>` に追加するタグ

```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#f05e23">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Metronome">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
```

---

## 実装ロードマップ

リリース前に完了させる 4 フェーズ。Phase 1 が後続の基盤となるため必ず先行させること。

| Phase | 内容 | 依存関係 |
|-------|------|---------|
| **Phase 1** | lookahead scheduling への書き換え（テンポタブ・パフォーマンスタブ両方） | なし（最初に実施） |
| **Phase 2** | Subdivision Click 機能の追加 | **Phase 1 完了後** |
| **Phase 3** | モバイルUI最適化（1画面レイアウト、svh、safe-area-inset、タップターゲット） | Phase 1・2 と独立 |
| **Phase 4** | PWA 化（manifest.json、sw.js、Wake Lock、アイコン） | Phase 3 完了後が望ましい |

---

## 過去に議論・実装して削除した機能

- **サブセクション**: 親セクション内の途中開始位置を指定する機能。移動時に正しく動作しなかったため削除済み。将来再実装する場合は、親セクションの紐付けと位置移動のロジックを慎重に設計する必要がある
- **⏮⏭（早送り/巻き戻し）ボタン**: 不要として削除
- **ライトテーマ**: 文字の可読性が低かったため削除。テーマ切替ボタン（`themeBtn`）も廃止
- **PR/広告枠（`.aff-footer`）**: アフィリエイトや広告を運用する予定がなくなったため削除

---

## 既知の改善候補・未実装の要望（リリース後検討）

1. **サブセクション機能の再実装** — セクション間に挿入できる中間地点。開始位置は親セクションの小節数内で指定。所属先の親変更も可能にする
2. **ドリル対応** — マーチングのドリル（動きの指示）と連動する仕組み

---

## Coworkでの作業の始め方

このドキュメントと `metronome.html` を渡して、以下のように指示してください：

```
添付の metronome.html がメトロノームアプリです。
METRONOME_SPEC.md に仕様が書いてあります。
このファイルを編集して以下の改善をしてください：
（具体的な修正・追加内容を記載）
```
