# STATUS

## 現在地

- 公開中: https://oyasum1mode.github.io/Metronome/
- 最新: Codex 再検証指摘2件の修正 + ドキュメント最新化(2026-09-27)
- Phase 7.3 + セキュリティ修正 + 入力制限の修正まで完了
  - 入力制限の修正: セクション数上限(200)は UI 追加時のみ適用し既存/インポートデータは切り詰めない、`MAX_MEASURE`/`MAX_MEASURES_COUNT` の上限クランプは手入力と `addS`/`addE` のみに適用し、読込(localStorage・インポート)は型検証のみで既存の有効データを書き換えない、保存失敗と上限超過が同時発生した場合は1つの toast にまとめる
  - Phase 6: 音色を矩形波の電子音に刷新、音色 高/低 切替、accel/rit の小節途中開始（`changeFrom`）、曲編集の常時テンポ変化行、パフォーマンスの rit./accel. 予告表示、テンポオフセット±1/±5 追加
  - Phase 7〜7.3: 80年代機器風テーマ3種（rhythm/deck/calc）、`DESIGN.md` を一次デザイン仕様として新設、フラットデザイン化、DSEG7 7セグ表示（`fonts/` 同梱・オフライン対応）、Google Fonts 廃止、テンポ/パフォーマンスタブの iPhone 1画面レイアウト、設定シート、練習範囲のメイン画面常時表示、小節アクセント ON/OFF、ライブラリ並べ替え
  - セキュリティ修正（`c1992dd`）: インポート・保存データの数値検証とHTMLエスケープ漏れ修正、保存失敗時の通知、再生中の曲切替・セクション編集時の自動停止、Service Worker のキャッシュ削除を `metronome-pro-` プレフィックスに限定

## ドキュメントの役割

- `METRONOME_SPEC.md` — 機能仕様（一次情報）
- `DESIGN.md` — デザイン仕様（テーマ・レイアウト・配色、一次情報）
- `USER_GUIDE.md` — 利用者向け取扱説明書
- `CODEX_PROMPT.md` — Phase 5 当時の Codex 向けハンドオフ（履歴、現行仕様は上記2ファイルを参照）
- `STATUS.md` — 本ファイル。現在地・次アクションの短いサマリ

## 次アクション候補

- iPhone 実機での動作確認（レイアウト・タップ操作・Bluetooth 遅延）
- アイコン（`icons/icon-192.png` 等）が旧オレンジ配色のまま残っている。Phase 7 の新テーマ配色に合わせた更新を検討
- `DESIGN.md` のテーマ B（STEREO TEMPO DECK）で「◀◀ 10」表記が2行に折り返される問題の確認・修正
- Phase 7.1 のフラットデザイン化で不要になった発光系 CSS 変数（`--lcdglow`/`--lcdglow2` 等）の整理
