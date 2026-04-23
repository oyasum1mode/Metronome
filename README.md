# Metronome Pro

マーチングバンド向けの単一 HTML 構成メトロノームです。`metronome.html` を GitHub Pages に置くだけで動作し、PWA としてホーム画面追加にも対応します。

## 使い方

1. `metronome.html` を開く
2. テンポタブでは BPM / 拍子 / Tap Tempo / Subdivision を設定して `Start`
3. パフォーマンスタブでは曲を読み込み、必要なら Tap Off / End Check / 範囲 / Subdivision を設定して `Start`
4. スペースキーでも再生 / 停止できます

## データ保存

- 曲ライブラリは `window.storage` の `metro-lib4` キーに保存されます
- 曲編集タブからエクスポート / インポートできます

## PWA 配布メモ

- `manifest.json` と `sw.js` を同じ階層に置いてください
- GitHub Pages へ配置するとオフラインでもアプリ本体を開けます
- 再生中は対応ブラウザで Wake Lock を要求し、画面スリープを防ぎます

## 必要なアイコン

以下の PNG を用意して `icons/` 配下に置いてください。

- `icons/icon-192.png` - 192x192
- `icons/icon-512.png` - 512x512
- `icons/apple-touch-icon.png` - 180x180
