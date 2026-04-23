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
- **練習範囲**: 開始セクション → 終了セクション をドロップダウンで選択
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
- データは `window.storage` API で永続化（キー: `metro-lib4`）

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

> 以下の値は実装コードの実測値。旧 SPEC（accent: 1200Hz/0.7、normal: 800Hz/0.4、ci: 1000Hz/0.5）は実装と乖離していたため修正済み。

| 種類 | オシレーター周波数 | オシレーター音量 | ノイズ音量 | 用途 |
|------|-----------------|----------------|-----------|------|
| accent | 1500Hz | 0.8 | 0.6 | 小節頭（1拍子の場合は全拍） |
| normal | 900Hz | 0.5 | 0.3 | 通常拍 |
| ci | 1200Hz | 0.6 | 0.4 | Tap Off / End Check |
| sub | 未定（三角波 or 低周波サイン波推奨） | メインの 40〜50% | 任意 | Subdivision サブビート |

音声構成: サイン波オシレーター + ノイズトランジェント（4ms バースト）、約 40〜50ms で減衰。

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
- **Subdivision 中のサブビート表示: 小さいドット or 別色（実装時に決定）**

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
  tempo: 120,               // BPM
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
JSON → Base64エンコード。バージョン: `v:4`

---

## 技術スタック

- HTML/CSS/JS（フレームワークなし）
- Web Audio API（音声生成 + lookahead scheduling）
- `window.storage` API（Artifact 永続ストレージ、ライブラリデータ用）
- `localStorage`（テーマ設定）
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
- 再生ボタン（`.pb`）は現在 64×64px — 維持または拡大
- ±1/±5/±10 ボタン（`.fb`）は現在 height: 30px — **44px に拡大が必要**

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
