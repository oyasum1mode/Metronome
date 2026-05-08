# Metronome Pro

マーチング・吹奏楽向けの高機能メトロノーム Web アプリ。曲ごとにセクション分割してテンポ・拍子を管理し、accel/rit やテンポオフセットで本番に近い練習を支援します。単一 HTML（`metronome.html`）+ PWA で配布、ホーム画面追加にも対応。

**公開 URL**: https://oyasum1mode.github.io/Metronome/

## 主な機能

- **テンポタブ** — 独立メトロノーム。BPM 20〜400、Tap Tempo、Subdivision（8th/Triplet/16th）
- **パフォーマンスタブ** — 曲を読み込んで再生。Tap Off（カウントイン）、End Check（終了確認ビート）、練習範囲指定、Subdivision、テンポオフセット（±10/In tempo で全体ずらし）
- **曲編集** — セクション単位で BPM・拍子・小節数を設定。accel/rit のテンポ変化と変化カーブも指定可
- **ライブラリ** — 曲を `localStorage` に保存、エクスポート/インポート（Base64）で端末間共有
- PWA（オフライン動作、ホーム画面追加対応）、Wake Lock、ダークテーマ固定
- iOS Safari/Chrome ではバウンス・プルトゥリフレッシュを抑止して 1 画面に収まるレイアウト

## 使い方

1. ローカルで `metronome.html` を開く（または公開 URL）
2. テンポタブで BPM/Tap Tempo/Subdivision を設定して `Start`
3. パフォーマンスタブでは曲を読み込み、必要なら Tap Off / End Check / 範囲 / Subdivision / テンポオフセットを設定して `Start`
4. スペースキーでも再生 / 停止できます
5. ↑↓ キー（テンポタブ）で BPM ±1

## データ保存

- `localStorage` キー:
  - `metronome-lib` — 曲ライブラリ（曲名 + セクション配列）
  - `metronome-volume` — マスター音量
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
- `METRONOME_SPEC.md` — 詳細仕様

## 開発

- フレームワークなしの単一 HTML
- Web Audio API + Chris Wilson 方式の lookahead scheduling
- 詳細仕様: [METRONOME_SPEC.md](METRONOME_SPEC.md)
