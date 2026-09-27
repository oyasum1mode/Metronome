# Metronome Pro — 仕様書・引き継ぎドキュメント

## 概要
マーチング / 吹奏楽向けの高機能メトロノームWebアプリ。  
曲ごとにセクション分割し、テンポ・拍子チェンジを管理して練習できる。  
GitHub Pages で配布する PWA 対応 Web アプリ。

> 本書は**機能仕様**の一次情報。デザイン（色・配置・キー表記など）は `DESIGN.md` が一次仕様。利用者向けの説明は `USER_GUIDE.md`、現在地・次アクションは `STATUS.md` を参照。`CODEX_PROMPT.md` は Phase 5 当時のハンドオフ履歴。

---

## ファイル構成

- `metronome.html` — アプリ本体（HTML + CSS + JS）
- `manifest.json` — PWA マニフェスト
- `sw.js` — Service Worker（オフライン対応）
- `icons/icon.svg` — アイコンマスター（ビートドット 4 つ並び、ダーク背景にオレンジドット）
- `icons/icon-192.png` — PWA アイコン（192×192px）
- `icons/icon-512.png` — PWA アイコン（512×512px）
- `icons/apple-touch-icon.png` — iOS Safari ホーム画面アイコン（180×180px）
- `icon-builder.html` — `icon.svg` から PNG 3 サイズを書き出すローカル変換ツール（公開対象外、開発用）
- `fonts/DSEG7Classic-Bold.woff2` / `fonts/DSEG-LICENSE.txt` — 表示窓の7セグフォント（OFLライセンス、オフライン動作のため同梱）
- `DESIGN.md` — テーマ・レイアウトのデザイン仕様（一次情報）
- `METRONOME_SPEC.md` — 本ファイル（機能仕様の一次情報）
- `USER_GUIDE.md` — 利用者向け取扱説明書
- `STATUS.md` — 現在地・次アクションのサマリ
- `CODEX_PROMPT.md` — Phase 5 当時の Codex 向けハンドオフ履歴

> `manifest.json`・`sw.js`・`icons/` は PWA 化（Phase 4）で新規追加するファイル。  
> Service Worker はセキュリティ制約上 HTML に inline できないため別ファイル必須。  
> PNG アイコンは `icon-builder.html` をブラウザで開いてダウンロードボタンから書き出し、`icons/` に手動配置する運用（ImageMagick 等のインストール不要）。

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
- 拍子: **12種から選択**（`1`, `2/4`, `3/4`, `4/4`, `5/4`, `6/4`, `7/4`, `8/4`, `9/4`, `6/8`, `9/8`, `12/8`）。ドロップダウン（`<select>`）で表現し、必要に応じて ±1/±5/±10 等のボタン群と横並びに配置してよい。デフォルト `4/4`
- Tap Tempo対応
- **Subdivision Click**: **OFF / 8th / Tri / 16th の4ボタン横並び**（ラジオ風選択）。再生中も即時切替可能
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
- **テンポオフセット**: BPM 表示の直下に `[ -10 ][ -5 ][ -1 ][ +1 ][ +5 ][ +10 ]` と `[ In tempo ]`（横長・2段目）ボタンで現曲全セクションのテンポを一括でずらせる（遅練習用）。詳細は「テンポオフセット」節
- **Subdivision Click**: **ON/OFF の2ボタン**のみ。ON のときは曲編集で各セクションに設定された subdivision（`none`/`8th`/`triplet`/`16th`）に従って鳴らす。OFF のときは一切鳴らさない（Phase 7.1: このON/OFFトグルは再生画面から設定シート `#pSet` へ移動。テンポタブの4ボタンSubdivisionは再生画面に残す）
- スペースキーで再生/停止

### 3. 曲編集
- 曲名入力
- セクション追加（A〜Z, AA〜ZZ まで自動ラベル）
  - 各セクション: 開始小節、小節数（0=手動）、テンポ、拍子（**12種から選択**、上記テンポタブと同じ選択肢）
  - **詳細（折りたたみ）**: 終了テンポ、カーブ、**Subdivision**（`OFF`/`8th`/`Tri`/`16th`）
  - ▲▼ボタンで順序変更可能
  - **新規追加時のテンポ・拍子引き継ぎ**: 直前セクション `prev` が存在する場合、`tempo`/`tempoEnd` は `prev.type==='main' ? (prev.tempoEnd ?? prev.tempo) : prev.tempo`（＝直前セクションの変化後テンポ）を引き継ぎ、`timeSig`/`beatUnit` も `prev` の値をそのまま引き継ぐ（新規セクションは定速スタートのため `tempoEnd=tempo`、`changeFrom=1`）。`prev` が存在しない（曲の先頭に追加する）場合のみ、従来通りテンポタブの現在値（`mBpm`/`mBeats`/`mBeatUnit`）を初期値にする
- エンドブロック追加（1曲に1つのみ、常に最後に配置）
  - 頭1拍のみ再生される特殊ブロック
  - ▲▼ボタンなし（位置固定）
  - Subdivision は持たない（頭1拍のみのため）
  - テンポ・拍子引き継ぎのルールはセクション追加と同じ（直前セクションの変化後テンポ・拍子を引き継ぎ、曲が空の場合のみテンポタブの現在値）
- 💾 ライブラリに保存ボタン / ↗ エクスポート（Base64コード）/ ↙ インポート / ✕ クリア
  - 4つは `.sa{display:grid;grid-template-columns:1fr 1fr}` の **2×2 グリッド**配置（Phase 7）。各ボタン `.sab` は横幅 50%・**高さ 48px 以上**で押しやすくする

### 4. ライブラリ
- 保存した曲一覧
- クリックで曲を読み込み → パフォーマンスタブへ遷移
- 各曲行に **↑↓ボタン**（Phase 7）を追加し、`lib` 配列内の並び順を入れ替えられる。セクション編集の ▲▼（`.mvb`）と同じ実装パターンで、先頭の↑・末尾の↓は `.disabled` クラスで無効表示にする。並べ替え後は既存の `saveLib()` で `metronome-lib` に保存するためリロード後も順序を保持する
- 各曲からエクスポート / 削除
- 「+ 新しい曲を作成」ボタン
- データはブラウザの `localStorage` で永続化（キー: `metronome-lib`）
- 初回起動時は曲一覧が空。ユーザーが作成・保存した曲のみがそのブラウザに残る（端末・ブラウザをまたぐ共有はエクスポート/インポート経由）
- **保存失敗時の通知**: `saveLib()` は `localStorage.setItem` の例外を握りつぶさず真偽値を返す。保存ボタン（`svL`）は成功時のみ「保存しました」を表示し、失敗時は「保存に失敗しました。エクスポートで退避してください」を表示する。セクション編集などの自動保存（`saveCur()` 経由）が失敗した場合も同じ toast を出すが、短時間の連続失敗ではトーストの再表示を抑制する（`saveLibNotify()` のデバウンス）

---

## 追加機能: Subdivision Click

メインビートに重ねてサブクリックを鳴らすオプション機能。タブごとに UI と振る舞いが異なる。

### 状態の種類（共通）
| キー | ラベル | 分割数 |
|------|-------|--------|
| `none` | OFF | 1（鳴らさない） |
| `8th` | 8th | 2 |
| `triplet` | Tri | 3 |
| `16th` | 16th | 4 |

### UI（タブ別）

**テンポタブ**
- 横並び **4ボタン**（OFF / 8th / Tri / 16th）。ラジオ風で常に1つだけ選択中
- 現在の選択は `.active` クラスで視覚的にハイライト
- 再生中もボタン押下で即時切替可能（次のスケジューリングサイクルから反映）
- グローバル変数: `mSubdivision`（値: `'none'`/`'8th'`/`'triplet'`/`'16th'`）

**パフォーマンスタブ**
- 横並び **2ボタン**（OFF / ON）
- グローバル変数: `pSubdivision`（値: `'on'`/`'off'`）
- ON のとき: 各セクションに保存された `subdivision` フィールドに従って鳴らす（`none` のセクションは鳴らない）
- OFF のとき: subdivision を一切鳴らさない（セクション側の設定は無視）

**曲編集タブ**
- セクションの「⋯ 詳細」折りたたみ内にセレクトボックス（OFF / 8th / Tri / 16th）
- セクションデータの `subdivision` フィールドに保存
- エンドブロック（`type='end'`）には表示しない

### 音声仕様
| 状態 | 分割数 | インターバル@120BPM | 音量 | 音色 |
|------|--------|---------------------|------|------|
| none | — | — | — | — |
| 8th | 2分割 | 250ms | メインの 40〜50% | メインと同じ矩形波、音量小さめ・短め（下記「音色」節参照） |
| triplet | 3分割 | 166.7ms | メインの 40〜50% | 同上 |
| 16th | 4分割 | 125ms | メインの 40〜50% | 同上 |

メインビート自体は Subdivision の有無にかかわらず通常通り鳴らす。サブクリックはその間隔で追加される。

### 動作仕様
- テンポ変更・拍子変更に追従（次スケジューリングサイクルから即反映）
- Start/Stop 時も Subdivision の選択状態を保持
- **メインとサブの位相ズレが発生しないこと**  
  → lookahead スケジューラ内で同一 `beatTime` を基準に `beatTime + subOffset * n` で算出・予約すること
- Count-in（Tap Off）中および End Check 中はサブクリックを鳴らさない
- パフォーマンスタブではセクション境界跨ぎで subdivision の数が動的に変わる（dot 再描画）

### 実装要件
- `AudioContext.currentTime` ベースの lookahead scheduling で実装すること（後述）
- サブビートは、メインビートと同じスケジューラ内で一括予約する
- パフォーマンスタブの `scheduleNext` 内で、`pSubdivision==='on'` ならセクションの `subdivision` を、OFF なら `'none'` を `scheduleSubdivision()` に渡す

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
│     (非表示・非フォーカス時は 1.5s 先まで。後述)             │
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
- **UI 表示**: ライブラリタブ末尾（「+ 新しい曲を作成」の下）に小さく「Bluetooth スピーカー使用時は音が少し遅れる場合があります（接続側の固定遅延）」と注意書きを表示する

---

## 音色（Web Audio API）— Phase 6 で電子音（矩形波）に刷新

> **履歴（Phase 5 まで）**: 以前はノイズ＋バンドパスフィルター＋低音オシレーターの3パス構成で BOSS DB-30 系の「コッカッ」というパーカッシブ音を合成していた（Pa/Ta フォルマント版の試作を経て DB-30 Click 版に戻した経緯あり）。Phase 6 でこの構成は廃止し、下記の矩形波オシレーター1本によるシンプルな電子音に置き換えた。

現行実装（`playClick(type, time, opts)`、`metronome.html`）は、単一の矩形波（`OscillatorType: 'square'`）オシレーター + 1本の Gain ノードのみで音を作る。ノイズバッファ・バンドパスフィルター・低音オシレーターは使用しない。

### ノード構成

```
Oscillator(square, freq) → Gain(env) → masterGain → destination
```

- `osc.type='square'` 固定。周波数は種類ごとに固定値（後述の表）
- Gain は `setValueAtTime(.0001)` → `exponentialRampToValueAtTime(peak, +1.5ms)`（アタック）→ `setValueAtTime(peak, dur*0.8)` → `exponentialRampToValueAtTime(.0001, dur)`（減衰）のエンベロープ
- ノイズ・BPF・低音レイヤーは存在しない（Phase 5 以前の実装からの変更点）

### 音色 高 / 低 の切替（`soundType`）

- ヘッダー左上の **音 高 / 音 低** ボタン（`#sndBtn`）でクリック音全体のピッチを高音セット/低音セットに切替できる（テンポ・パフォーマンス両タブ共通のグローバル設定）
- `localStorage` キー `metronome-sound`（値: `'high'` | `'low'`、既定 `'high'`）に保存し、次回起動時も引き継ぐ
- 各セットの周波数・音量・長さは以下の固定値（`playClick` 内 `defaultsHigh` / `defaultsLow`）

| 種類 | 高（freq） | 高（peak） | 高（dur） | 低（freq） | 低（peak） | 低（dur） | 用途 |
|------|--------:|--------:|-------:|--------:|--------:|-------:|------|
| accent | 2000 Hz | 0.18 | 35 ms | 1000 Hz | 0.20 | 45 ms | 小節頭（1拍子の場合は全拍） |
| normal | 1000 Hz | 0.18 | 35 ms | 500 Hz | 0.20 | 45 ms | 通常拍 |
| ci | 1500 Hz | 0.18 | 35 ms | 750 Hz | 0.20 | 45 ms | Tap Off / End Check |
| sub | 1000 Hz | 0.08 | 20 ms | 500 Hz | 0.08 | 20 ms | Subdivision サブビート |

- Subdivision（サブビート）はメインビートと同じ周波数・同じ矩形波だが、`peak`（音量）と `dur`（長さ）を小さくして「軽い」音にしているだけで、波形や音色そのものは変えていない
- `opts.frequency` を渡せば個別に周波数を上書き可能（現状呼び出し側では未使用）

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

## 外観 / テーマ（Phase 7 で復活）

- Phase 6 までは `themeBtn` を廃止しダークテーマ固定としていたが、Phase 7 で 80 年代機器風の 3 テーマへ切替可能にする方針に変更
- `<html data-theme="rhythm|deck|calc">` でテーマを切替。ヘッダー左上の `#themeBtn`（テキスト表示）をタップすると rhythm→deck→calc→rhythm の順に循環する
  - **rhythm**（A・リズムマシン風）: グレー筐体、赤 7 セグ LED、四角いキー、上部にオレンジのライン
  - **deck**（B・コンポ/デッキ風）: シルバー筐体、蛍光表示管（緑）、細枠のメカボタン
  - **calc**（C・電卓/デジタル時計風）: 黒筐体、反射液晶（緑がかったグレー地に濃色文字）、角丸ゴムボタン、START ボタンのみ常時オレンジ
- 選択は `localStorage`キー `metronome-theme` に保存（既定 `rhythm`）。`<meta name="theme-color">` もテーマに合わせて JS で切り替える
- 各テーマは CSS変数（`--bg`/`--sf`/`--s2`/`--bd`/`--tx`/`--dm`/`--mt`/`--ac`/`--ag`/`--as`/`--ba`/`--bi`/`--bac`/`--ci`/`--cig`/`--ec`/`--ecg`/`--red`/`--endc`/`--endg`、および新設の `--lcdbg`/`--lcdfg`/`--lcdglow`/`--lcdglow2`/`--lcdrad`/`--key1`〜`--key3`/`--keyrad`/`--keytx`/`--chassis-line`）を再定義することで実現し、コンポーネント側の個別 CSS 追加は最小限に抑える
- フッターのアフィリエイト/広告枠（旧 `.aff-footer`）は運用しないため削除（この方針は継続）
- **Phase 7.1（フラットデザイン化）**: 全テーマ共通で box-shadow / text-shadow（発光）/ inset shadow / グラデーション、および押下時の `translateY` を廃止。押下フィードバックは `filter:brightness(.8)` または `.active` クラスの配色変化のみで表現する。LED（`.dot`/`.subdot`）・LCD 数字も発光なしのベタ塗り色
- **Phase 7.2（モック準拠のデザイン固定）**: `DESIGN.md` を一次のデザイン仕様として新設し、以後のテーマ色・配置・キー表記の変更はこのファイルに従う（逸脱する場合は実装前に `DESIGN.md` を更新）
  - `.app`（筐体面）の背景を各テーマの `--bg`（A `#c9c5bb` / B `#b4b2a9` / C `#2c2c2a`）に変更し、機種名ラベル・表示窓・キーが筐体面の上に直接乗る構成にした。`body` 背景は枠色 `--bd` を使用
  - 各テーマの筐体面に直接乗る文字（タイトル、Subdivisionラベル、範囲行ラベル、テンポ増減の目盛りなど）は新設の `--dm-onbg` で筐体色に対する可読性を確保（カード/モーダル内の文字は従来どおり `--dm`/`--tx`）
  - テンポ・パフォーマンス両タブの表示窓上部に機種名ラベル行を追加（A: `RHYTHM METRONOME MR-80` / B: `STEREO TEMPO DECK`（● POWER 併記）/ C: `DIGITAL METRONOME`）
  - 表示窓の数字を DSEG7 Classic（OFL、`fonts/DSEG7Classic-Bold.woff2` に同梱・オフライン対応）による 7 セグ表示に変更。上下中央、背面に消灯セグメント「888」を薄く重ねる（Phase 7.3 で右詰めに修正、下記参照）
  - Subdivision ラベルを OFF ボタン直前に固定幅で配置（ラベル＋4ボタンを1行に収める）
  - テーマ別のキー配色・拍インジケータ・START/STOP表記を追加（A: 拍は四角/START `#e24b4a`、B: テンポキーが `◀◀10`等の矢印表記・START/STOPが `▶ PLAY`/`■ STOP`、C: 拍は `■□` 表記・START のみ `#d85a30`）
- **Phase 7.3（表示窓の右詰め修正・テーマA配色変更・小節アクセントON/OFF）**
  - 表示窓の数字・消灯セグメント「888」を右詰めに変更し、同一フォント・文字幅・位置でぴったり重ねる（電卓のように未使用の上位桁だけが消灯表示に見える）。消灯色は各テーマの数字色を不透明度 12% にしたもの
  - テーマ A（RHYTHM METRONOME MR-80）: テンポ増減キー（−10/−5/−1/+1/+5/+10、パフォーマンスのオフセット含む）を全て `#f1efe8` 地・`#2c2c2a` 字に統一。TAP を `#ef9f27`（旧 −1 の色）、設定ボタン(⚙)を `#d85a30` 地・白字（旧 −10 の色）に変更。START `#e24b4a`・Subdivision `#444441` は現状維持
  - パフォーマンスタブの設定シート（`#pSet`）に「小節アクセント」トグル（既定 ON）を追加。変数 `pAccent`、`localStorage` キー `metronome-perf-accent` に保存（曲データには含めない）。OFF のとき、パフォーマンス再生の通常スケジューラで小節頭アクセントを無効化（`playClick` に `accent` を渡さない）し、1拍目 LED の強調表示（`.dot.acc`）も通常拍と同じにする。カウントイン・End Check の音、テンポタブの動作は変更なし

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
  changeFrom: 1,             // ★セクション内の相対小節（1始まり、既定1）。テンポ変化の開始小節。type='end' では未使用
  timeSig: 4,               // 拍子の分子（1〜12）
  beatUnit: 4,              // ★拍子の分母（4 または 8、既定 4）。BPM はこの音符の毎分数を意味する
  subdivision: 'none'        // ★main のみ: 'none' | '8th' | 'triplet' | '16th'（既定 'none'）。end には付与しない
}
```

**BPM の意味**: BPM は `beatUnit` の音符の毎分数。例えば `beatUnit: 8`（6/8 や 9/8 等）の場合、BPM=120 は「8分音符が1分間に120回」=「8分音符1個 0.5秒」を意味する。`beatDuration = 60 / BPM` の式は不変。

**1小節の長さ**: `measures × timeSig × (60 / BPM)` 秒。例: BPM=120, 6/8 → 1小節 = 1 × 6 × 0.5 = 3 秒。

### ライブラリ（lib配列）
```javascript
{
  id: 's1234567890',        // ユニークID
  title: 'My Song',         // 曲名
  sections: [...]            // セクション配列のコピー
}
```

### エクスポート形式
JSON → Base64エンコード。バージョン: **`v:5`**（`beatUnit` と `subdivision` を追加）。

**v:5 のフィールド対応**:
- `tp`=type, `n`=name, `sm`=startMeasure, `m`=measures
- `t`=tempo, `te`=tempoEnd, `tc`=tempoCurve
- `ts`=timeSig, **`tu`=beatUnit**, **`sd`=subdivision**（`tu`/`sd` が新規追加）
- `cf`=changeFrom（既定値 1 のときはキー自体を省略。フォーマットバージョンは据え置き）

**後方互換性**: 読込側 `dec()` はバージョンを見ず、`normalizeSection()` がデフォルト補完する。
- v:4 以下のデータ（`tu`/`sd` なし）→ `beatUnit: 4`、`subdivision: 'none'` で補完
- `cf` なしのデータ（v:5 の旧データ含む）→ `changeFrom: 1` で補完
- localStorage に保存済みの v:4 ライブラリは初回起動時に自動マイグレートされ、編集・保存時に v:5 形式で書き戻される

**入力検証（インポート・localStorage 読込共通）**: `normalizeSection()` は外部由来（共有コード・localStorage）の値を無条件に信用しない。
- 読込時（インポート・localStorage）の `normalizeSection()` は型の検証のみ行い、上限クランプはしない: `startMeasure` は整数化し 1 未満・非数値は 1、`measures` は整数化し負・非数値は 0（`MAX_MEASURE`/`MAX_MEASURES_COUNT` の上限は適用しない）。`changeFrom` は `1〜measures` の範囲に収める。`type` は `'main'`／`'end'` 以外なら `'main'` として扱う
- `MAX_MEASURE=9999`／`MAX_MEASURES_COUNT=999` の上限は、UI からの手入力（`change` ハンドラ・`<input max>`）と `addS`/`addE` の自動計算にのみ適用する
- `name`・`label`・曲タイトルは常に `String()` 化した上で描画時に `escapeHtml()` を通す（`renderSL`・`renderLL`・`upSB` などの `innerHTML` 生成箇所すべて）
- 1曲あたりのセクション数は最大 **200**（`MAX_SECTIONS`）。ただし `normalizeSections` は既存・インポートデータを切り詰めない（読込データの消失を防ぐため）。上限は UI からのセクション追加（`addS`/`addE`）にのみ適用され、到達時は追加をブロックしトースト通知する。インポート時・起動時読込時に 200 超のデータが見つかった場合は削除・切り詰めせずトーストで警告するのみ

---

## 拍子（Time Signature）

複合拍子・特殊拍子に対応するため、拍子は **分子（`timeSig`）+ 分母（`beatUnit`）** の組で表現する。

### 選択可能な拍子（12種）

UI から選べる拍子は以下に限定する。テンポタブ・曲編集タブの両方で同じ選択肢を使う。

| 表示 | timeSig | beatUnit |
|------|--------:|---------:|
| `1` | 1 | 4 |
| `2/4` | 2 | 4 |
| `3/4` | 3 | 4 |
| `4/4` | 4 | 4 |
| `5/4` | 5 | 4 |
| `6/4` | 6 | 4 |
| `7/4` | 7 | 4 |
| `8/4` | 8 | 4 |
| `9/4` | 9 | 4 |
| `6/8` | 6 | 8 |
| `9/8` | 9 | 8 |
| `12/8` | 12 | 8 |

`1` は「1拍/小節」の特殊表示で、内部的には `timeSig:1, beatUnit:4`。1拍子のときは全拍がアクセント音（既存仕様維持）。

### ヘルパ関数（実装目安）

```javascript
const TIME_SIG_OPTIONS = [
  [1,4,'1'], [2,4,'2/4'], [3,4,'3/4'], [4,4,'4/4'],
  [5,4,'5/4'], [6,4,'6/4'], [7,4,'7/4'], [8,4,'8/4'],
  [9,4,'9/4'], [6,8,'6/8'], [9,8,'9/8'], [12,8,'12/8']
];
function clampBeats(v)    { return Math.max(1, Math.min(12, v||4)) }   // 上限を 12 に拡大
function clampBeatUnit(v) { return v===8 ? 8 : 4 }                     // 4 か 8 のみ
function tsLabel(ts, bu)  { return (ts===1 && bu===4) ? '1' : `${ts}/${bu}` }
function parseTsValue(s) {
  if (s === '1') return [1, 4];
  const [a, b] = s.split('/').map(n => parseInt(n, 10));
  return [clampBeats(a), clampBeatUnit(b)];
}
```

### ロジック上の取り扱い

- BPM の意味は `beatUnit` の音符の毎分数。`beatDuration = 60 / BPM` の式は **変更不要**
- ドット数は `timeSig` 個（メインドット）。subdivision に応じて補助ドットが間に追加される
- アクセントは小節の頭（`beatIndex===0`）のみ。`timeSig===1` の場合のみ全拍アクセント（既存仕様維持）
- 進捗計算 `progress(sec, beatIndex, measureIndex)` の `totalBeats = measures × timeSig` も **変更不要**

### UI 配置

- **テンポタブ**: ドロップダウン（`<select>`）。±1/±5/±10 ボタン群と横並びにレイアウトしてもよい
- **曲編集タブ**: 各セクションの拍子フィールドをドロップダウンに置き換え
- **パフォーマンスタブ**: 表示のみ。`tsLabel(timeSig, beatUnit)` 形式で現在のセクションの拍子を表示

### モバイル制約

- 12/8 + 16th subdivision の組み合わせはメイン12 + サブ36 = 48 ドットになり、iPhone SE では2〜3段に折り返す。`flex-wrap:wrap` で破綻はしないが視認性は許容範囲（リリース後の改善候補）

---

## accel / rit（テンポ変化）

通常セクションの中で開始テンポから終了テンポへ滑らかに変化させる機能。指揮者ごとの揺らし方の違いをカーブスライダーで表現する。

### データ表現

セクションの `tempo`（開始）と `tempoEnd`（終了）、`tempoCurve`（カーブ）、`changeFrom`（変化開始小節）の 4 値で表す。`tempoEnd === tempo` または `tempoEnd` 未定義の場合は定速。

- `changeFrom`: セクション内の相対小節番号（1始まり、既定 1）。`1〜measures` にクランプ。`measures = 0` の場合は常に 1
- エクスポート時のキーは `cf`（既定値 1 のときはキー自体を省略）。旧データ（`cf` なし）は `normalizeSection()` で `changeFrom: 1` として補完される（後方互換、フォーマットバージョン `v:5` は据え置き）

### 進捗とカーブ式

セクション内の小節・拍から求めた絶対位置 `pos` と、変化が始まる位置 `startPos` を使う。`changeFrom` の小節より手前は常に開始テンポ（定速）とし、`changeFrom` の小節頭からカーブが始まる。

```
ts       = timeSig
pos      = measureIndex * ts + beatIndex                            // セクション内の絶対拍位置（0始まり）
startPos = (changeFrom - 1) * ts                                    // 変化が始まる拍位置
total    = measures * ts

t  = pos <= startPos ? 0 : (pos - startPos) / (total - startPos)     // 0〜1（進捗）
v  = tempoCurve                                                      // -1〜+1
t' = t ^ (2 ^ v)                                                     // v=0→線形, v=-1→t^0.5, v=+1→t^2
BPM(t) = tempo + (tempoEnd - tempo) * t'
```

- `changeFrom = 1`（既定）の場合、`startPos = 0` となり従来通りセクション全体でカーブする
- スライダー中央 (v=0): 線形（均等にテンポ変化）
- スライダー左 (v<0): 早めに変化（前半に大きく動く）
- スライダー右 (v>0): 遅めに変化（後半に大きく動く）
- `measures = 0`（手動小節モード）の場合は定速にフォールバック（進捗が定義できないため）。`changeFrom` も編集不可（常に 1 扱い）

### スケジューラへの組み込み

- `progress(sec, beatIndex, measureIndex)` が `changeFrom` を踏まえた進捗 `t` を返す（`sec.changeFrom` を直接参照）
- `createPerformanceTransport.scheduleNext(time)` 内で `currentTempo = clampTempo(tempoAt(sec, progress(sec, beatIndex, measureIndex)) + tempoOffset)` に逐次更新
- `advance()` で `nextNoteTime += 60 / currentTempo`
- `scheduleSubdivision(time, beatDuration, ...)` の `beatDuration = 60 / currentTempo`
- `enterMain()` の `currentTempo = clampTempo(sec.tempo + tempoOffset)` はセクション先頭（`pos=0` で `changeFrom` に関わらず開始テンポと一致）の初期化として残す

### 曲編集 UI

通常セクションのカードに、常時表示の行を追加する（詳細に隠さない）:

- **テンポ変化** セレクト（なし / accel. / rit.）
  - 状態は `tempoEnd` と `tempo` の大小関係から導出（`tempoEnd > tempo` → accel.、`tempoEnd < tempo` → rit.、それ以外 → なし）
  - 「accel.」選択時に `tempoEnd` が `tempo` を上回っていなければ `tempoEnd = tempo + 10` に設定。「rit.」選択時に下回っていなければ `tempoEnd = tempo - 10`
  - 「なし」選択時は `tempoEnd = tempo`、`changeFrom = 1` にリセット
- **目標テンポ** 数値入力（= `tempoEnd`）。「なし」の間は非表示/disabled
- **開始小節** 数値入力。**曲全体の絶対小節番号**で表示・入力する（`startMeasure + changeFrom - 1`）。保存時は相対値（`changeFrom = 入力値 - startMeasure + 1`）に変換してクランプ。「なし」または `measures = 0` の間は非表示/disabled

**テンポ変化のカーブ**（Phase 7.2 でラベル変更。旧「カーブ」）スライダー（`min=-1 max=1 step=0.1 value=0`）と **Subdivision** は既存の「詳細」トグル内に残す。エンドセクションには表示しない。
- スライダーの目盛りは左「早めに変化」／中央「一定」／右「遅めに変化」を表示（`t^(2^v)` の指数 `v` に対応。`v<0` で早めに変化＝立ち上がりが速い、`v>0` で遅めに変化）
- スライダー横に小さなカーブ図（SVG）を表示し、現在値に応じて曲線形状をリアルタイムに再描画する（x=小節の進み、y=テンポ）。テンポ変化が「なし」の間はスライダー・カーブ図とも無効表示（disabled + 薄色）

### ビジュアル

#### 曲編集タブ

- 再生中は BPM 数値を瞬時値で更新（`pUpd()` を `scheduleNext` 内で呼ぶ。`Math.round` で整数化）
- テンポ名の隣に方向アイコン `↗`（accel）/ `↘`（rit）/ なし（定速）

#### パフォーマンスタブ（目立つ表示）

BPM 表示の下（`pTn` 付近）にタグ行 `#pChg` を常設し、`updateTempoTrend()` と同タイミング（拍ごと）で更新する:

- **変化中**（現在のセクションが変化区間に入っている、`curM >= changeFrom - 1`）: 強調表示。例 `rit. → 100` / `accel. → 140`。accel と rit で配色を変える（`--ec` / `--red`）
- **変化開始前**（同一セクション内、まだ変化区間の手前）: 控えめ表示。例 `m.13 から rit.`
- **次セクション予告**（現在のセクション最後の2小節以内で、次セクションが `changeFrom = 1` の変化ありセクション）: 控えめ表示。例 `次: accel. → 140`
- 上記いずれにも該当しない・カウントイン中・End Check 中・停止中: 空
- 表示するテンポ値は `tempoOffset` を加算した値（実際の再生テンポと整合させる）

---

## テンポオフセット（パフォーマンスタブ専用）

遅いテンポで練習するために、現曲のすべてのセクションのテンポを一括でずらすオフセット機構。

### 仕様

- **配置**: パフォーマンスタブの BPM 数値の直下に、1段目 `[ -10 ][ -5 ][ -1 ][ +1 ][ +5 ][ +10 ]` を横並び均等割り、2段目に横長の `[ In tempo ]` ボタン
- **状態**: グローバル変数 `tempoOffset`（初期値 0、範囲 -200〜+200）
- **適用**: `scheduleNext` 内で `currentTempo = clampTempo(tempoAt(sec, progress(...)) + tempoOffset)`
- **BPM 表示**:
  - 再生中: `scheduleNext` で `queueVisual({kind:'tempo'})` 経由でオフセット込みの瞬時値を表示（既存ロジック）
  - 停止中: `pUpd()` で現在選択中セクション（`secs[curS] || secs[rF]`）の `tempo + tempoOffset` を `clampTempo` して表示。曲未読込時は `pBpm` のまま
- **In tempo ボタン**: 現在値を併記。例: オフセット 0 → `In tempo`、+30 → `In tempo (+30)`、-20 → `In tempo (-20)`
- **リセットタイミング**: `loadSong` / `newS`（新規曲作成）/ `clB`（クリア）の冒頭で 0 にリセット
- **保持**: 再生停止 / タブ切替では保持。リロードで 0（localStorage には保存しない）
- **再生中の曲切替**: パフォーマンス再生中にライブラリから別の曲を選ぶ（`loadSong`）、新規作成、インポート、クリア、またはセクションの追加・削除・並べ替え・小節数/拍子などの編集を行った場合は、切替・変更の直前に `pStop()` で再生を停止してから状態を切り替える（旧曲の拍子・小節などの内部状態が新しい再生に混入しないようにするため）
- **適用範囲**: パフォーマンスタブのみ。テンポタブ（`createMetroTransport`）には影響させない

### UI

- ボタンは既存の `.fb` スタイル（`min-width:44px; min-height:48px; pill 形`）を流用
- `In tempo` ボタンのみ最低幅 120px・横幅いっぱい（`.ofwide`）に拡張してオフセット値併記の余裕を持たせる
- `.ofb`（offset buttons コンテナ）内を `.ofrow`（1段目 6 ボタン、flex 均等割り）と `In tempo`（2段目、横長）の2段構成にする
- id: 新設 `pOfM5`(−5) `pOfM1`(−1) `pOfP1`(+1) `pOfP5`(+5)。既存 `pOfM`(−10) `pOfP`(+10) `pOf0`(In tempo) は維持し、いずれも既存 `applyTempoOffset(delta)` / `resetTempoOffset` を再利用

---

## 技術スタック

- HTML/CSS/JS（フレームワークなし）
- Web Audio API（音声生成 + lookahead scheduling）
- `localStorage`（永続化。キー: `metronome-lib`=曲ライブラリ、`metronome-playlists`=プレイリスト、`metronome-volume`=マスター音量、`metronome-sound`=音色高/低、`metronome-theme`=テーマ、`metronome-perf-accent`=小節アクセントON/OFF）
- Service Worker（オフラインキャッシュ）
- Wake Lock API（画面スリープ防止、再生中のみ）
- フォント: DSEG7 Classic（`fonts/DSEG7Classic-Bold.woff2` に同梱、OFLライセンス、外部CDN不使用）。Google Fonts は Phase 7.2 で廃止し使用していない

---

## モバイルUI要件（再生コア1画面 + 設定はスクロール）

### ターゲット環境

- 縦向き（portrait）が主。**iPhone SE 相当（375×667px）で破綻しないこと**
- 横向き（landscape）はタッチ端末では「縦向きにしてください」オーバーレイで利用不可（Phase 8.2）。PC の横長小ウィンドウでは従来どおりスクロールで利用可

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

### レイアウト優先順位（Phase 7 で全面刷新）

- Phase 6 までの `.play-top`（再生コア）/`.play-bottom`（設定・スクロール可）の2ブロック構成をやめ、**テンポ・パフォーマンスタブ全体を `.play-tab.active{flex:1;min-height:0}` としてスクロールなしの1画面**に収める
  - 画面内の並び（上から）: 機種名ラベル行（Phase 7.2 で追加）→ `.lcd-wrap`（BPM LCD＋拍 LED、パフォーマンスは曲名/セクション表示も含む）→ **パフォーマンスタブのみ練習範囲行 `#rR`（`#rF`/`#rT`、Phase 7.2 でモーダルシートからメイン画面へ移動）** → テンポ操作（テンポタブ: スライダー+±1/±5/±10 / パフォーマンスタブ: オフセット±1/±5/±10+In tempo）→ テンポタブのみ Subdivision（4ボタン）→ **最下段 `.pw.bottom-bar`（`margin-top:auto` で下端に固定）: ⚙設定 + TAP + START/STOP**
  - 使用頻度の低い設定はモーダルシート（`.mo`/`.md` を流用、開閉のみの軽量 JS）に退避する。DOM 上の ID は維持し、要素を移動しただけで JS ロジックは変更していない
    - テンポタブ: `#mSet`（拍子セレクト `#mTsSel`）
    - パフォーマンスタブ: `#pSet`（Tap Off `#ciT`/`#ciS`、End Check `#ecT`/`#ecBS`/`#ecTS`、**Phase 7.1でSubdivision ON/OFF `#pSubGrp` もここへ移動**）。練習範囲 `#rF`/`#rT` は Phase 7.2 でメイン画面（`#tab-perf` の `.lcd-wrap` 直後）へ移動し、`#pSet` からは削除済み（ID・JSロジックは変更なし）
  - **Phase 7.1**: 設定ボタン（`#mGear`/`#pGear`）は `.lcd-wrap` 内の右上absolute配置から**最下段バー `.pw.bottom-bar` の左端**へ移動。並びは `[⚙設定][TAP][START/STOP]`（テンポタブ）/ `[⚙設定][START/STOP]`（パフォーマンスタブ）。高さは他ボタンと揃え、幅比は 設定:TAP:START = 1:1:2
- タップターゲットは最低 **44×44px** を確保
- ±1/±5/±10 ボタン（`.fb`）は **min-width 44px / min-height 48px 以上**

### LCD内表示（Phase 7.1）

- BPM数値（`#mBv`/`#pBv`）は LCD パネル（`.lcd-panel`）内の左側に大きく表示し、右側に `.bv-side` として BPM ラベルと速度記号（`#mTn`/`#pTn`）を上下2段で並べる
- パフォーマンスタブでは accel/rit タグ（`#pChg`）と↗↘（`.trend`/`#pTrend`）も `.bv-side` 内、速度記号の下に配置する
- DOM移動のみで、要素の ID・JSロジックは維持

### スタートボタンと Tap Tempo のレイアウト

- スタートボタン（`.pb`）は `.pw.bottom-bar` 内に配置し、**高さ 56px 以上**の角丸四角（pill）形状
- **テンポページ**: 設定ボタン・Tap Tempo・スタートボタンを横並び。`flex:1`（設定）/`flex:1`（Tap）/`flex:2`（START）の比率で **START が横幅の半分程度**を占める
- **パフォーマンスページ**: タップテンポなし。設定ボタン（`flex:1`）＋スタートボタン（`flex:2`）
- iPhone SE（375×667）で破綻しないこと。BPM LCD のフォントサイズは `clamp(40px,10svh,76px)` で画面高に応じて自動縮小する

### タッチ・スクロール挙動

- **テンポ・パフォーマンスタブ**: 上記の1画面レイアウトによりスクロール自体が発生しない（`document.documentElement.scrollHeight <= clientHeight` を維持）
  - `body` は `overflow-y:auto`（固定 `height:100vh`/`overflow:hidden` はやめ、`min-height:100svh` のみ指定）。曲編集・ライブラリタブはこの挙動でスクロールする
  - iOS のバウンス（rubber-band）・プルトゥリフレッシュ抑止は維持: `html,body{overscroll-behavior:none}` に加え `body{overscroll-behavior-y:contain}`
  - スライダー（`input[type=range]`）には `touch-action: pan-x` を残し、横操作を確保する
  - 設定シート（`#mSet`/`#pSet`）表示中はその上に重なるのみで、背後のタブレイアウトは変化しない
- **曲編集・ライブラリタブ**: コンテンツが長くなるためスクロール可（既存の `overflow:auto` を維持）
- ランドスケープ用メディアクエリ（`@media (orientation:landscape) and (max-height:500px)` で `body{overflow:auto}`）は維持

### 曲編集 UI のコンパクト化

accel/rit「⋯ 詳細」トグル追加でセクションカードが縦に伸びがち。モバイルでスクロール量を減らすため、機能を損なわない範囲で軽くチューニング:

- セクションカード内の余白（padding / gap）を必要に応じて縮小
- 4 列フィールド（開始小節 / 小節数 / テンポ / 拍子）の gap を詰める、ラベル文字サイズを小さく
- `.sdet summary` の高さを 24〜28px 程度に抑える
- 過度に詰めて操作性を損なわないこと（タップターゲットは引き続き確保）
- 曲編集・ライブラリはスクロール前提のため、入力欄（`.sni`、`.fg input`/`.fg select`）は **min-height 40px 前後・font-size 16px 以上**にして iOS Safari のフォーカス時自動ズームを防ぐ。移動/削除ボタン（`.mvb`/`.sdel`）もあわせて一回り拡大する

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

### manifest.json（現行値）

```json
{
  "name": "Metronome Pro",
  "short_name": "Metronome",
  "start_url": "./metronome.html",
  "display": "standalone",
  "background_color": "#1c1d1f",
  "theme_color": "#1c1d1f",
  "icons": [
    { "src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

> `theme_color`/`background_color` は Phase 7 のテーマ導入前の値（旧オレンジ系 `#f05e23`）から `#1c1d1f` に変更済み。テーマ切替（rhythm/deck/calc）に応じて `<meta name="theme-color">` は JS で動的に上書きされるが、`manifest.json` 自体の値は固定（アイコンは旧オレンジ配色のまま — 次アクション候補として `STATUS.md` に記載）。

### 必要なアイコンファイル

| ファイル | サイズ | 用途 |
|---------|--------|------|
| `icons/icon-192.png` | 192×192px | Android Chrome ホーム画面・W3C manifest |
| `icons/icon-512.png` | 512×512px | スプラッシュ画面・Google Play PWA |
| `icons/apple-touch-icon.png` | 180×180px | iOS Safari「ホーム画面に追加」アイコン |

- フォーマット: PNG（背景色あり、透過なし）
- デザイン: ビートドット 4 つ並び（ダーク背景、オレンジドット）。`icons/icon.svg` をマスターとして保持
- 書き出し: `icon-builder.html` をブラウザで開き、「ダウンロード」ボタンで 192/512/180 PNG を取得 → `icons/` に配置（ImageMagick 等のインストール不要）

### Service Worker（sw.js）

- キャッシュ戦略: **Cache First**（静的アセット向け）
- キャッシュ対象: `metronome.html`、`manifest.json`、アイコン類、Google Fonts
- オフライン時はキャッシュ版を返す
- `activate` イベントで古いキャッシュを削除する際は、削除対象を `key.startsWith('metronome-pro-') && key !== CACHE_NAME` に限定する（同一オリジン上の他アプリ・他リポジトリのキャッシュを誤って削除しないため）。`CACHE_NAME` はバージョンアップ時にインクリメントする（現行 `metronome-pro-v15`）

### Wake Lock API

- 再生開始時（`pStart()` / `mStart()`）に `navigator.wakeLock.request('screen')` を呼ぶ
- 停止時（`pStop()` / `mStop()`）に `wakeLock.release()` を呼ぶ
- API 非対応端末（iOS 16.3 以下等）は `try/catch` で無害に握り潰す
- ページ非表示時（`visibilitychange` イベント）は OS が自動解除するため、再表示時に再取得する処理を追加すること

### HTML `<head>` に追加するタグ

```html
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#c9c5bb" id="metaTheme">
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
| **Phase 5** | 配布フィードバック反映（音色強化・Subdivision UI 再編・拍子拡張・セクション別 subdivision・v:5マイグレーション） | Phase 1〜4 完了後 |
| **Phase 6** | 音色を矩形波の電子音に刷新（ノイズ/BPF/低音レイヤーは廃止）・音色 高/低 切替・accel/rit の小節途中開始（`changeFrom`）・曲編集への常時テンポ変化行・パフォーマンスの rit./accel. 予告表示・テンポオフセット±1/±5 追加 | Phase 5 完了後 |
| **Phase 7〜7.3** | 80年代機器風テーマ3種（rhythm/deck/calc）、`DESIGN.md` を一次デザイン仕様として新設、フラットデザイン化、DSEG7 7セグ表示、Google Fonts 廃止、テンポ/パフォーマンスタブの iPhone 1画面レイアウト、設定シート、練習範囲のメイン画面常時表示、パフォーマンスの小節アクセントON/OFF、ライブラリ並べ替え | Phase 6 完了後 |
| **Phase 8** | プレイリスト機能（複数曲の通し練習、曲間のつなぎ方（そのまま/無音→タップイン）、`metronome-playlists` の新設、v:6 共有コード） | Phase 7.3 完了後 |
| **Phase 8.1** | プレイリスト改善（End 整理・拍子に合うタップインパターン・範囲選択の曲/位置分割・細かな不具合修正） | Phase 8 完了後 |
| **Phase 8.2** | 表示と音の同期、背景時の先読み延長、停止時の予約音取り消し、Tap in/out と End の整理、縦向き専用、Codex 指摘修正（`b038df2`） | Phase 8.1 完了後 |
| **Phase 9** | ナビゲーション改善（現在地バー・選曲シート・プレイリストのまま曲編集・✎で曲編集へ・クリアの元に戻す）（`b1e36d5`） | Phase 8.2 完了後 |
| **セキュリティ修正**（`c1992dd`） | インポート・保存データの数値検証とHTMLエスケープ漏れ修正、保存失敗時の通知、再生中の曲切替・セクション編集時の自動停止、Service Workerキャッシュ削除を `metronome-pro-` プレフィックスに限定 | Phase 7.3 完了後 |

> **注**: Phase 6 以降は本仕様書の各節（音色・テーマ・アクセル/リタルダンド・データ構造など）に直接反映済み。以下の「Phase 5 の内訳」表は Phase 5 時点の履歴として残す（音色強化の記述は Phase 6 で置き換えられているため、現行仕様は上の「音色（Web Audio API）」節を参照）。

### Phase 5 の内訳（履歴 — Phase 5 時点の記録。現行仕様と異なる箇所あり）

| 項目 | 概要 |
|------|------|
| 音色強化 | `playClick()` に低音 Oscillator を1本追加して中低域を厚くする |
| テンポタブ Subdivision | 循環式トグル → OFF/8th/Tri/16th の4ボタン横並び |
| パフォーマンスタブ Subdivision | ON/OFF の2ボタン。各セクションの subdivision に従って鳴らす |
| 曲編集 Subdivision | セクションの「⋯ 詳細」内に subdivision セレクトを追加 |
| 拍子拡張 | 6/8, 9/8, 12/8, 9/4 を追加。`beatUnit` フィールド新設、UI を select 化 |
| エクスポート | `v:4 → v:5` に進める。新フィールド `tu`/`sd`、`normalizeSection` で互換補完 |

---

## Phase 8: プレイリスト

1ショー分（複数曲）を通しで練習するための機能。曲同士のつなぎ方（そのまま続ける / 無音区間を挟んでタップインで再開）を保存し、パフォーマンスタブで通しの選曲・再生範囲を扱えるようにする。

### データ

- `localStorage` 新キー `metronome-playlists`:
  ```javascript
  {
    id: 'pl1234567890',
    title: 'セットリスト',
    items: [
      { songId: 's...', link: { mode: 'direct'|'gap', gapBeats: 4, tapBeats: 4 } },
      ...
    ]
  }
  ```
  - `items[i].link` は「`items[i]` の曲 → 次の曲」のつなぎ方。最後の曲の `link` は使用しない
  - `mode:'direct'` はそのまま次の曲へ進む。曲の Endセクションは常に除外する（End あり/なしの選択は廃止）
  - `mode:'gap'` は無音区間を挟んだ後タップインで次の曲へ進む。Endセクションは鳴らさず、無音区間の1拍目に Endの音（accent 音）を1打鳴らし、残り（`gapBeats-1`拍）は無音にする
  - `gapBeats`（0〜64、既定4）: 無音区間の拍数。1拍目の End 音を含めて数える（テンポ・拍子は前曲末尾の値を引き継ぐ）。1 = End のみで即タップイン。**0 = 無音区間も End も挟まず、前曲の最後の拍の次の拍からすぐタップイン**（「そのまま」ではなく Tap in だけを挟みたい場合。Phase 9.1）
  - `tapBeats`（4/6/8/12、既定4）: タップインの拍数。「なし(0)」は選択肢から廃止（無音→タップインを選ぶ以上、タップインは必須のため）。旧データで `0` または不正値が保存されていた場合は読込時に `4` へ変換する
  - 曲は `metronome-lib` の `id` を参照するのみ（実体はコピーしない）。曲を編集すればプレイリスト側の再生にも反映される。参照先が消えた曲は編集画面で「(削除済み)」と表示し、再生用の平坦化ではスキップする
- 読込時（`normalizePlaylist`/`normalizePlaylistItem`）は既存の `normalizeSection` と同じ方針で型の検証のみ行い、上限クランプはしない。上限クランプ（プレイリスト内曲数 50・`gapBeats` 0〜64）は編集画面での手入力時のみ適用する（`tapBeats` は選択肢固定のセレクトのため常に有効値）
- **旧データ変換（Phase 8.1）**: 旧形式 `link:{mode, end, gapMeasures, tapBeats}` を読み込んだ場合、`gapBeats = gapMeasures × 前曲末尾セクションの拍子`（0 なら 1）に変換する。`end` フィールドは廃止（常に除外扱い）。旧 v:6 共有コードも同じ変換ロジックで読める

### タップインパターン（Phase 8.1）

- 共通定義 `TAPIN_PATTERNS`（`A`=accent 音・`T`=ci 音、両方とも既存の音色・見た目を流用）:
  - 4拍: `T T T T`
  - 6拍: `A T T A T T`
  - 8拍: `A T A T A A A A`
  - 12拍: `A T T A T T A A A A A A`
- パフォーマンス設定のカウントイン（`#ciS`）は 4/6/8/12 拍から選択（旧: 4/8）。テンポは練習範囲の開始セクション（次に演奏する曲）準拠
- プレイリストの「無音→タップイン」もこのパターンを共用し、テンポは次の曲の冒頭に合わせる
- ドット表示は Accent 拍（`A`）を常時ハイライトする（`renderTapinDots()`）。無音区間の1拍目（End 音）も同様に常時ハイライトする（`renderGapDots()`）

### 再生（既存エンジンの再利用）

- プレイリストを読み込むと、各曲の `sections` を連結した「平坦化 secs」を生成して既存の `secs`/`rF`/`rT`/`createPerformanceTransport` にそのまま渡す（`buildFlatSecs()`、`loadPlaylist()`）
- 曲と曲の間には疑似セクションを挿入する:
  - `type:'gap'`: 前の曲の最後のテンポ・拍子を引き継いだ1個の疑似セクション（`measures:1`、内部の拍数は `gapBeats`）。1拍目に accent 音（End 相当）を鳴らし、残りは無音でドット表示のみ進める
  - `type:'tapin'`: 次の曲の冒頭テンポ・拍子で `tapBeats` 拍分のカウントイン（`TAPIN_PATTERNS` に従い `ci`/`accent` 音を打ち分ける）。拍数は `tapBeats` を直接 `currentBeats` として扱う（`clampBeats` の 12 拍上限を回避するため）
  - 曲末尾の Endセクションは、直前の曲（最後の曲を除く）では常に平坦化時に除外する（`mode` に関わらず）
- `createPerformanceTransport.scheduleNext()`/`enterMain()` に `sec.type==='gap'`（1拍目のみ accent 音、他は無音）/`'tapin'`（`TAPIN_PATTERNS` に基づく accent/ci 音）の分岐がある。単曲再生（`sec.type` が常に `'main'`/`'end'`）の挙動は変更していない
- 練習範囲は疑似セクション（gap/tapin）を選択肢から除外し、プレイリスト読込中は「曲▼ 位置▼」×開始/終了の4セレクト（`#rFSong`/`#rFPos`/`#rTSong`/`#rTPos`）に切り替える。単曲時は従来の `#rF`/`#rT` 1行セレクトのまま。開始 > 終了になった場合は自動補正する。停止後の範囲表示ラベルにも曲番号を付ける

### UI

- ライブラリタブ上部に「曲｜プレイリスト」切替（`#libToggle`）。プレイリスト一覧は新規作成・エクスポート・削除・▲▼並べ替えに対応
- プレイリスト編集画面（`#tab-pledit`）: 曲を選択して追加（上限50）、▲▼並べ替え、削除、曲間ごとの「つなぎ」設定（そのまま/無音→タップイン・無音拍数・タップイン拍数）。表示中はライブラリタブをハイライトする
- パフォーマンスタブの `#pST` に「プレイリスト名 / 現在の曲名」を表示し、再生中に曲が切り替わるたびに更新する
- ~~曲編集タブはプレイリスト読込中は編集不可（ロック＋「単曲モードに戻る」）~~ → Phase 9 で廃止。プレイリスト読込中も曲編集可能（Phase 9 節参照）

### インポート/エクスポート

- 新フォーマット `{v:6, kind:'playlist', title, songs:[曲（既存v5相当の形式）], items:[{i:曲index, link:{mode,gapBeats,tapBeats}}]}` を Base64 エンコードして共有する（`encPl()`）
- インポート時は `songs` をライブラリへ新規追加し、`items` の曲参照をその新規IDへ張り替えてプレイリストを作成する（`importPlaylistPayload()`）
- 既存の v5 単曲コード・曲タブのインポートも同じ入力欄・同じ判定ロジック（`doImport()`）でそのまま読める（`d.kind==='playlist'` でなければ単曲として扱う）。旧 `link` フィールド（`end`/`gapMeasures`）を含む v:6 コードも読込時に変換する

### Phase 8.1 追加修正（BPM表示ちらつき・Tap in/out・再生ボタン）

- **BPM表示ちらつきの修正**: `setPerformanceMainState`/`enterCountInState`/`enterEndCheckState` は `curS`/`curM`/`isCi`/`isEc`/`ciBt`/`ecBt` など論理状態のみを即時更新するようにした（スケジューラの lookahead 内で先行実行されるため）。表示側（`pBpm`/`pBeats`・ドット再描画・`upSB()`/`upSTB()`/`renderSL()`）は `applyPerformanceMainVisual()`/`applyCountInVisual()`/`applyEndCheckVisual()` に分離し、`queueVisual({kind:'state', time:this.nextNoteTime, ...})` で該当セクション先頭拍の音の時刻に積んでから `applyVisual()` で適用する。これにより、キューに残っていた前セクションの `kind:'tempo'` 表示更新に新しい値が上書きされて戻る、という順序逆転（ちらつき）を解消した
  - `startTransport()` は transport 生成関数を受け取り、`stopTransport(false)`→`clearNoteQueue()` の後に生成するよう変更（`createMetroTransport`/`createPerformanceTransport` を関数参照で渡す）。これは、transport 生成時点（`enterMain`/`enterCountIn`/`enterEndCheck` の初回呼び出し）で `queueVisual` される初期表示イベントが、直後の `clearNoteQueue()` で消えてしまわないようにするため
  - 停止時（`pStop`/`stopTransport`）はキューを破棄するため影響しない
- **Tap in/out は再生範囲に対して適用**: カウントイン（`ciOn`）・エンドチェック（`ecOn`）は練習範囲（`rF`〜`rT`）の最初の前・最後の後にのみ発生し、プレイリストの曲境界（`gap`/`tapin` 疑似セクション）では発生しない（従来通り。曲境界のタップインは `link.mode:'gap'` の疑似セクションが担う、既存仕様）
  - **End とエンドチェックの二重打ち防止**: End は次の小節の1拍目を表すため、再生範囲の終わり（`rT`）が End セクションそのもの、または End セクション直前の場合、End 単独の打鍵とエンドチェック1拍目が重複しないよう、End の打鍵を省いてエンドチェックの1拍目をその代わりとする。この「省略して合流」は `secs[rT].type==='end'` のときのみ発生し、`rT` が通常の演奏セクションの場合は最後まで通常どおり再生してからエンドチェックへ移行する（`createPerformanceTransport().advance()`/初期分岐で `secs[rF]`/`secs[rT]` の型を判定するよう修正。単曲・プレイリスト両方に適用される共通ロジック）
- **プレイリスト一覧の再生ボタン**: 「読込▶」ボタン（`.lib.plPlay`）を 44×44px に拡大し、START ボタンと同じテーマ変数（`--start-bg`/`--start-tx`）で着色した（詳細は `DESIGN.md` の「ライブラリ: プレイリスト再生ボタン」節）
- **縦向き専用化**: `manifest.json` に `"orientation":"portrait"` を追加。orientation lock が効かない環境向けに、横向き検出時（`@media (orientation:landscape) and (max-height:500px) and (pointer:coarse)`＝タッチ端末のみ）は画面全体を覆う「縦向きにしてください」オーバーレイ（`.rotateOverlay`）を表示する（詳細は `DESIGN.md` の「画面向き」節）
- `sw.js` キャッシュ名を `metronome-pro-v20` に更新

---

## 過去に議論・実装して削除した機能

- **サブセクション**: 親セクション内の途中開始位置を指定する機能。移動時に正しく動作しなかったため削除済み。将来再実装する場合は、親セクションの紐付けと位置移動のロジックを慎重に設計する必要がある
- **⏮⏭（早送り/巻き戻し）ボタン**: 不要として削除
- **ライトテーマ**: 文字の可読性が低かったため Phase 6 まで削除し、`themeBtn` も廃止していた。ただし Phase 7 で方針転換し、80年代機器風の3テーマ（rhythm/deck/calc、いずれもダーク〜中間色の筐体）と `themeBtn` を復活させた（詳細は「外観 / テーマ」節）。単純な「白背景ライトテーマ」は復活していない
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

### バックグラウンド時の先読み延長（Phase 8.2）

- Safari 等はタブ非表示・ウィンドウ非フォーカス時に `setInterval` を間引くため、先読み 100ms では予約が途切れて拍が乱れる
- `scheduleAhead()`: `document.hidden || !document.hasFocus()` のときは `SCHEDULE_AHEAD_BG`(1.5s)、それ以外は `SCHEDULE_AHEAD_TIME`(0.1s)
- `window` の `blur` と `visibilitychange`(hidden) で即座に `runScheduler()` を呼び、背景へ移る直前に先読み分を予約する
- 副作用: 背景中のテンポ変更は最大 1.5s 遅れて反映。停止時は `muteMasterGain` で予約済み音も消音される

### Codex レビュー指摘の修正（Phase 8.2 追加）

- **ID生成の共通化・重複防止**: 曲・プレイリストの ID は `genId(prefix)` に統一。`crypto.randomUUID()` があれば使用し、無ければ `Date.now().toString(36)` ＋乱数2個を連結したものにフォールバックする。生成のたびに既存 `lib`/`playlists` の `id` と重複していないか確認し、重複する場合は再生成する（`normalizePlaylist`・`importSongPayload`・`importPlaylistPayload`・新規曲/新規プレイリスト作成・無題曲の保存、すべてこの関数を使用）
- **停止直後の再開で旧予約音が鳴る問題の修正**: `playClick()` で生成した `OscillatorNode` を `pendingOscillators`（Set）に保持し、`onended` で自動的に除去する。`stopTransport()` は `muteMasterGain()` に加えて `stopAllPendingOscillators()` を呼び、Set 内の全 osc を `stop(0)`/`disconnect()` する。これによりテンポタブ・パフォーマンスタブ双方、subdivision の音も含めて、停止直後に旧予約分が鳴ることがなくなる
- **表示と音の同期の徹底**: 論理状態（transport 内部の `this.sectionIndex`/`this.measureIndex`/`this.ciIndex`/`this.ecIndex` 等）と表示状態（`curS`/`curM`/`isCi`/`isEc`/`ciBt`/`ecBt`）を完全に分離した。表示状態は音の再生時刻に同期して `queueVisual`→`applyVisual` 経由でのみ更新し、スケジュール時点（先読み中）には一切書き換えない
  - `applyPerformanceMainVisual(sectionIndex, measureIndex)` / `applyCountInVisual(tempo)` / `applyEndCheckVisual(tempo)` が表示状態の設定を担う（旧 `setPerformanceMainState`/`enterCountInState`/`enterEndCheckState` は廃止・統合）
  - 小節進行・カウントイン/エンドチェックの拍数進行も、`scheduleNext()` が発行する per-beat の `queueVisual` イベントに `sectionIndex`/`measureIndex`/`ciBt`/`ecBt` を積み、`applyBeatProgressVisual(evt)` が音の時刻でこれらを反映してから `upSB()` を呼ぶ。`advance()` 側の即時 `curM=...`/`upSB()` 呼び出しは削除した
- **プレイリスト・単曲切替時の停止漏れ修正**: `exitPlaylistMode()` と、ライブラリからの曲削除（読込中の曲を削除するケース）で、`secs` を差し替える前に再生中なら `pStop()` を呼ぶよう修正。`loadSong`/`loadPlaylist`/クリアボタンは元々対応済みだったことを確認した
- **プレイリスト編集の名前消失修正**: `#plT` の `input` イベントで編集中データ（`playlists` 内の該当エントリ）の `title` に即時反映するようにした。保存は従来どおり保存ボタン（`#plSave`）。曲追加・並べ替え・つなぎ変更で `renderPlEdit()` が再描画されても、入力中のタイトルが失われない
- **不正な共有コードの取り込み耐性強化**: `isValidPlaylistImportPayload(d)` を新設し、`songs` が配列で各要素がオブジェクト（`sections` が配列）であること、`items` が配列で各要素がオブジェクト（`i` が `songs` の範囲内の整数、`link` がオブジェクト）であることを、`lib`/`playlists` に反映する前にすべて検証する。一つでも不正なら何も変更せず `toast('無効なコード')` を表示する。単曲 v5 の取り込みも `d.sections` が配列であることを明示的に確認するよう修正した
- `sw.js` キャッシュ名を `metronome-pro-v21` に更新

### Phase 9: ナビゲーション改善

プレイリスト導入後、「ライブラリで選ぶ → 曲編集 → 単曲モードに戻る → ライブラリで選び直す」の往復を減らし、現在地を常に見えるようにした。

#### 1. 現在地バー（パフォーマンス・曲編集タブ共通）

- パフォーマンスタブ: 既存の `#pST`（高さ・位置は据え置き。1画面レイアウトを崩さない）
  - プレイリスト読込中: `▶ プレイリスト名  現在の曲番号/曲数 › 曲名 ▾`（`upSTB()`）
  - 単曲: `♪ 曲名 ▾`、未選択: `曲を選ぶ ▾`
- 曲編集タブ: 新設の `#sST`（`renderSongBar()`）
  - プレイリスト読込中: `✎ プレイリスト名 ▾` に加え、編集対象曲を選ぶ `<select id="editSongSel">`（プレイリスト内の曲一覧、曲順表示）
  - 単曲: `♪ 曲名 ▾`、未選択: `曲を選ぶ ▾`
- どちらのバーも行全体（曲編集は曲セレクトと「← プレイリスト編集」を除く）をタップすると **選曲シート**（`#selSheet`、既存の設定シート `.mo`/`.md` の様式を流用）を開く（`openSelSheet()`/`renderSelSheet()`）
  - シート上部に「プレイリスト｜曲」切替（`#selToggle`）、一覧をタップで即読込（`loadPlaylist()`/`loadSong()`）。現在読込中のものは `.cur` でハイライト
  - 曲編集タブから開いた場合は曲を選ぶと曲編集タブへ戻り（`selSheetOrigin`）、プレイリストを選ぶとパフォーマンスタブへ（`loadPlaylist()` の既存挙動）
  - 再生中に切替えたら既存どおり `pStop()` してから読込む（`loadSong`/`loadPlaylist` に既存実装）

#### 2. 曲編集をプレイリスト読込中のまま可能に

- 「プレイリスト再生中は曲編集できません」のロックメッセージ（`#songLockMsg`）と「単曲モードに戻る」ボタン（`#songUnlockBtn`）を廃止。`#songEditWrap` は常時表示
- **編集バッファと平坦化 secs の分離**: プレイリスト読込中の曲編集は、パフォーマンス用の平坦化配列 `secs`（`buildFlatSecs()` の出力。曲間の `gap`/`tapin` 疑似セクションを含む）を直接編集しない。代わりに専用の編集バッファ `editSecs`（対象曲の `lib` セクションを複製したもの）と、対象曲IDを保持する `editSongId` を新設した
  - `esecs()`: 曲編集UI（`renderSL()`・セクション追加/削除/並べ替え/各フィールド編集・`assignLabels()`）が参照する配列を返す。プレイリスト読込中は `editSecs`、単曲モードでは従来どおり `secs`（単曲モードは元々 編集とパフォーマンスが同じ配列を共有しているため変更なし）
  - `selectEditSong(songId)`: `lib` から該当曲を複製して `editSecs`/`editSongId`/`sTitle` にセットし、曲編集タブを再描画する。再生中なら先に `pStop()`
  - `saveCur()`: プレイリスト読込中は `editSongId` の曲を `lib` に保存してから `rebuildFlatSecsPreservingRange()` を呼ぶ。単曲モードは従来どおり `curSId` の曲を保存
  - `rebuildFlatSecsPreservingRange()`: `buildFlatSecs()` で `secs` を作り直し、範囲 `rF`/`rT` を **曲番号(`_pn`)＋曲内位置(`_localIdx`)** で再マッピングする（`remapPlaylistPosition()`）。同じ曲・同じ位置が無くなっていれば同じ曲内で最も近い位置へ、その曲自体が無ければ（削除等）そのままインデックスの妥当性を保証できないため全体（`0`〜`length-1`）にフォールバックする。再生中は先に `pStop()`
  - `buildFlatSecs()` は各曲のセクションに `_localIdx`（曲内での並び順。`gap`/`tapin` 疑似セクションには付与しない）を付与するよう拡張した
- 曲編集タブを開いたとき、プレイリスト読込中かつ編集対象未選択（または対象曲が削除済み）なら、パフォーマンスで表示中の曲（`secs[curS]`/`secs[rF]` の `_pn`）に対応する曲を既定の編集対象にする（`switchTab('song')`）
- 保存ボタン（`#svL`）・エクスポート（`#exB`）・クリア（`#clB`）もプレイリスト読込中は `editSongId`/`editSecs` を対象に動作するよう分岐した。クリアはパフォーマンスの `secs` には触れない
- ライブラリタブでの曲削除時、削除対象が `editSongId` なら編集バッファを解除し、プレイリスト読込中なら `buildFlatSecs()` で `secs` を作り直す

#### 3. プレイリスト編集から曲編集へ

- プレイリスト編集（`renderPlEdit()`）の各曲行に「✎」ボタンを追加（`data-editsong`）。押すと `openSongEditFromPlaylist(songId)` が実行され、
  1. 対象プレイリストが読込中でなければ `loadPlaylist()` で読み込む
  2. `plEditReturnId` にプレイリストIDを保持
  3. `selectEditSong(songId)` で該当曲を編集対象にする
  4. `switchTab('song')` で曲編集タブを開く
- `plEditReturnId` が現在のプレイリストと一致する間、曲編集タブの現在地バーに「← プレイリスト編集」ボタンが表示され、押すと `openPlEdit()` でプレイリスト編集へ戻る
- 曲編集タブ以外へ切り替える、または `loadSong`/`loadPlaylist`（別プレイリスト）を呼ぶと `plEditReturnId` はクリアされる

#### 4. パフォーマンスの表示・変更点

- `renderSL()` は表示中のタブが曲編集タブでないときは描画をスキップする（`if(!$('tab-song').classList.contains('active'))return;`）。プレイリスト再生中に毎セクション `applyPerformanceMainVisual()` から呼ばれても、曲編集タブを開いていなければ無駄な再描画をしない。曲編集タブを開いたとき（`switchTab('song')`）に改めて描画される
- `renderSL()` の再生中ハイライト（`.playing`）は単曲モードのみ付与する（プレイリスト読込中は `esecs()`＝`editSecs` のインデックスとパフォーマンスの `curS` は無関係のため）

### Codex レビュー指摘の修正（Phase 9 追加）

- **[P1] プレイリスト再読込時の編集対象消失を修正**: `loadPlaylist()` で、別プレイリストへの切替や単曲モードからの読込では従来どおり `editSongId`/`editSecs`/`plEditReturnId`/`sTitle`（`#sT`）を揃えて初期化する。**同一プレイリストの再読込**（選曲シート等から同じプレイリストを選び直した場合）では、`editSongId` がそのプレイリストにまだ含まれているかを確認し、含まれていれば `sTitle`/`#sT` を該当曲のタイトルで復元、含まれていなければ三者を揃えて初期化する。これにより、曲編集中に同じプレイリストを読み直しても曲名が空のまま `saveCur()` されることがなくなった
- **[P2] 曲編集タブの既定編集対象を songId で特定するよう修正**: `buildFlatSecs()` が生成する各セクションに `_songId`（曲のライブラリID）を付与するよう拡張。`switchTab('song')` の既定編集対象決定ロジックを、`secs[curS]._pn`/`secs[rF]._pn` で `pl.items[pn-1]` を直接引く実装（削除済み曲混在時に `_pn` が詰め番号のためズレる）から、`secs[curS]._songId`/`secs[rF]._songId` を直接使う実装に変更した
- **[P2] 範囲の再マッピングが gap/tapin を選んでしまう問題を修正**: `remapPlaylistPosition()` の候補列挙で `type==='gap'`/`'tapin'` のセクションを除外するようにした。加えて、対象曲を再マッピングした結果 `null`（＝その曲に演奏セクションが無い。曲クリア直後など）の場合は、`rebuildFlatSecsPreservingRange()` が新設の `firstPlayableSecIdx()`/`lastPlayableSecIdx()`（gap/tapin を飛ばして最初/最後の演奏セクションを返す）へフォールバックする。`if(rT<rF)rT=rF` の安全策は維持し、`rF>rT` にならないことを確認した
- **使いやすさ改善**: パフォーマンスの現在地バー（`#pST`）は行全体をタップ可能にした（`bar.onclick=openSelSheet`、再描画のたびにリスナーが積み重ならないよう `addEventListener` ではなく `onclick` 代入に統一）。曲編集の現在地バー（`#sST`）も同様に行全体へ `onclick` を設定しつつ、曲セレクト（`#editSongSel`）と「← プレイリスト編集」ボタン（`#sBackToPl`）のクリックは `stopPropagation()` して選曲シートが誤って開かないようにした
- **[プレイリスト読込中の曲クリア] ボタン名・確認文・取り消しトースト**: プレイリスト読込中に曲編集タブを開いているときのみ、クリアボタンの表示名を「✕ 曲の内容をクリア」に変更（`updateClearBtnLabel()`、`renderSongBar()`/`updateAll()` から呼び出し）。確認ダイアログを「「{曲名}」の内容を空にします。ライブラリの元の曲が変更され、この曲を使うすべてのプレイリストに反映されます。続けますか？」に変更（曲名は `confirm()`/`textContent` にのみ使用しHTMLへは挿入しないため escapeHtml 不要）。タイトル（`sTitle`/`#sT`）はクリア対象に含めず、セクションのみを空にする。クリア直後に専用の取り消しトースト（`#toastU`、`showUndoToast()`）を5秒間表示し、「元に戻す」を押すとクリア前の `sections` をライブラリへ書き戻し、`editSecs`/平坦化 `secs`/範囲/編集表示を復元する。既存の `toast()`（`#toast`）とは別要素・別タイマーで管理し干渉しない
- `sw.js` キャッシュ名を `metronome-pro-v23` に更新

#### 変更ファイル

`metronome.html`、`sw.js`（`metronome-pro-v23`）、`DESIGN.md`、`USER_GUIDE.md`、`STATUS.md`

### 取り消し(元に戻す)の追加修正(Phase 9 再レビュー)

- クリア後に同じ曲を単曲で読み込んでいた場合、「元に戻す」はライブラリに加えて単曲の編集・再生データ(`secs`)も復元する(復元後の保存で再び空になる不具合の修正)
- プレイリスト読込中の「元に戻す」は、クリア後に練習範囲・プレイリストが変更されていなければクリア前の練習範囲も復元する。変更されていればユーザーの選択を優先する。判定は値の一致ではなく、範囲・曲・プレイリストの選択操作ごとに増える変更カウンター `rangeSelSeq` で行う(同じ範囲を選び直した場合もユーザーの選択として扱う)
