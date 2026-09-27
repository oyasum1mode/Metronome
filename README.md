# Metronome Pro

マーチング・吹奏楽向けの高機能メトロノーム Web アプリ。曲ごとにセクション分割してテンポ・拍子を管理し、accel/rit やテンポオフセットで本番に近い練習を支援します。単一 HTML（`metronome.html`）+ PWA で配布、ホーム画面追加にも対応。

**公開 URL**: https://oyasum1mode.github.io/Metronome/

## 主な機能

- **テンポタブ** — 独立メトロノーム。BPM 20〜400、Tap Tempo、Subdivision（8th/Triplet/16th）、テンポオフセット±1/±5/±10
- **パフォーマンスタブ** — 曲を読み込んで再生。Tap Off（カウントイン 4/6/8/12拍）、End Check（終了確認ビート）、練習範囲指定（メイン画面常時表示）、Subdivision ON/OFF、小節アクセント ON/OFF、テンポオフセット（±1/±5/±10・In tempo で全体ずらし）、rit./accel. の予告表示
- **曲編集** — セクション単位で BPM・拍子・小節数を設定。accel/rit のテンポ変化を小節途中（`changeFrom`）から開始可能、変化カーブも指定可。次セクション/エンドブロック追加時は変化後テンポ・拍子を自動引き継ぎ
- **ライブラリ** — 曲を `localStorage` に保存、エクスポート/インポート（Base64）で端末間共有、並べ替え対応
- **プレイリスト** — 複数曲をショー順に並べ、曲間のつなぎ（そのまま / 無音→Tap in 4・6・8・12拍）を保存。パフォーマンスタブで「曲＋位置」単位の範囲指定で通し練習。プレイリストごと1コードで共有可
- **音色 高/低 切替** — クリック音（矩形波の電子音）のピッチをヘッダーの音色ボタンで切替
- **テーマ切替** — 80年代機器風の3テーマ（rhythm/deck/calc）をヘッダーの THEME ボタンで循環切替。デザイン仕様は `DESIGN.md` を参照
- PWA（オフライン動作、ホーム画面追加対応、縦向き専用）、Wake Lock
- 別タブ・別アプリに切り替えても拍が乱れにくいよう、背景時は先読みを延長
- iOS Safari/Chrome ではバウンス・プルトゥリフレッシュを抑止して 1 画面（iPhone SE 相当）に収まるレイアウト。設定シートに Tap Off / End Check / Subdivision / 小節アクセントをまとめ、再生コアは常時1画面表示

## 使い方

1. ローカルで `metronome.html` を開く（または公開 URL）
2. テンポタブで BPM/Tap Tempo/Subdivision を設定して `Start`
3. パフォーマンスタブでは曲を読み込み、必要なら Tap Off / End Check / 範囲 / Subdivision / テンポオフセットを設定して `Start`
4. スペースキーでも再生 / 停止できます
5. ↑↓ キー（テンポタブ）で BPM ±1

## データ保存

- `localStorage` キー:
  - `metronome-lib` — 曲ライブラリ（曲名 + セクション配列）
  - `metronome-playlists` — プレイリスト（曲参照 + つなぎ設定）
  - `metronome-volume` — マスター音量
  - `metronome-sound` — 音色設定（`high` / `low`）
  - `metronome-theme` — テーマ設定（`rhythm` / `deck` / `calc`）
  - `metronome-perf-accent` — パフォーマンスタブの小節アクセント ON/OFF
- 端末・ブラウザをまたぐ共有は曲編集タブのエクスポート（Base64）/ インポートで

## モバイル / Bluetooth について

- iOS Safari / Android Chrome でホーム画面追加に対応（PWA）
- iOS のホーム画面追加は **Safari のみ**（iOS Chrome は非対応）
- Bluetooth スピーカー利用時は接続側の固定遅延が乗ります。アプリ側でレイテンシを削減する手段はありませんが、メインビートとサブビートの **相対タイミング** は lookahead scheduling で正確に保たれます

## ファイル構成

- `metronome.html` — アプリ本体（HTML + CSS + JS）
- `manifest.json` — PWA マニフェスト
- `sw.js` — Service Worker（オフラインキャッシュ）
- `icons/icon.svg` — アイコンマスター
- `icons/icon-192.png` / `icon-512.png` / `apple-touch-icon.png` — PWA アイコン
- `icon-builder.html` — アイコン PNG 書き出し用ツール（開発用）
- `fonts/` — 表示窓の7セグフォント（DSEG7 Classic、OFLライセンス同梱）
- `METRONOME_SPEC.md` — 機能仕様（一次情報）
- `DESIGN.md` — テーマ・レイアウトのデザイン仕様（一次情報）
- `USER_GUIDE.md` — 利用者向け取扱説明書
- `STATUS.md` — 現在地・次アクションのサマリ

## 開発

- フレームワークなしの単一 HTML
- Web Audio API + Chris Wilson 方式の lookahead scheduling
- 詳細仕様: [METRONOME_SPEC.md](METRONOME_SPEC.md)
