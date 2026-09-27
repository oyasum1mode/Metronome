# STATUS

## 現在地

- 公開中: https://oyasum1mode.github.io/Metronome/ (公開版は Phase 8〜8.2 プレイリスト機能 `b038df2` まで)
- 作業ツリー(未コミット): **Phase 9 ナビゲーション改善 + Codex指摘修正 + 再レビュー指摘(取り消し時の単曲同期・練習範囲の復元、範囲の未操作判定を変更カウンター化)修正済み。Codex 再レビュー待ち**。Chrome で動作確認済み、Safari/iPhone 未確認
- sw.js キャッシュ名: `metronome-pro-v23`

### Phase 9 Codex指摘の修正(2026-09-27、未コミット)

- [P1] 同一プレイリスト再読込時に `editSongId`/`editSecs`/`sTitle`(`#sT`) が食い違う問題を修正(`loadPlaylist()`)。対象曲がまだ含まれるなら復元、含まれなければ三者を揃えて初期化
- [P2] 曲編集タブの既定編集対象を `_pn`(削除済み曲混在時にズレる詰め番号)ではなく `_songId` で特定するよう修正(`buildFlatSecs()` に `_songId` 付与、`switchTab('song')` の該当ロジック変更)
- [P2] 範囲の再マッピングが gap/tapin(疑似セクション)を選んでしまう問題を修正(`remapPlaylistPosition()` で除外)。対象曲に演奏セクションが無くなった場合は全体の最初/最後の演奏セクションへフォールバック(`firstPlayableSecIdx()`/`lastPlayableSecIdx()`、`rebuildFlatSecsPreservingRange()`)。`rF>rT` にならないことを確認
- 使いやすさ: 現在地バー(`#pST`/`#sST`)のタップ可能範囲を拡大(行全体、曲編集は曲セレクト/戻るボタンを除く)
- プレイリスト読込中の曲編集「クリア」を「✕ 曲の内容をクリア」に改名、確認文を詳細化、クリア直後の取り消しトースト(`#toastU`)を追加
- 検証: `node --check`(構文OK)、`remapPlaylistPosition`/`firstPlayableSecIdx`/`lastPlayableSecIdx` 相当ロジックの純粋関数テスト(node、手動抽出)は passed。**ブラウザでの実機能確認は未実施**(前回同様の環境上の制約)
- 詳細は `METRONOME_SPEC.md`「Codex レビュー指摘の修正（Phase 9 追加）」節を参照

### Phase 9(未コミット、ブラウザ確認待ち)

- 現在地バー(パフォーマンス `#pST` / 曲編集 `#sST`)をタップすると選曲シート(`#selSheet`)が開き、プレイリスト・曲を一覧からタップで即読込
- プレイリスト読込中でも曲編集タブで曲を編集可能に(ロック・「単曲モードに戻る」を廃止)。編集は専用バッファ `editSecs`(`lib` 由来、`editSongId` で対象を保持)で行い、パフォーマンスの平坦化 `secs` とは分離。保存時に `buildFlatSecs()` で `secs` を作り直し、範囲(`rF`/`rT`)を曲番号+曲内位置(`_pn`/`_localIdx`)で再マッピング(`rebuildFlatSecsPreservingRange()`/`remapPlaylistPosition()`)
- プレイリスト編集の各曲行に「✎」ボタン→曲編集タブでその曲を選択した状態で開き、「← プレイリスト編集」で戻れる
- 検証: `node --check`(構文OK)、`remapPlaylistPosition` 相当ロジックの純粋関数テスト(node、手動抽出)は passed。**ブラウザでの実機能確認(スマホ幅・3テーマ・実際のプレイリスト編集/曲編集往復)は未実施**(環境上、この作業ツリーではブラウザペインがローカルファイルを静的スナップショットとしてしか開けず、JS実行を伴う確認ができなかった。次セッションでの確認を推奨)

### Phase 8〜8.2 の内容(未コミット)

- **プレイリスト**: `metronome-playlists`(`{id,title,items:[{songId,link:{mode,gapBeats,tapBeats}}]}`)。ライブラリタブに「曲｜プレイリスト」切替、編集画面 `#tab-pledit`。曲はライブラリ参照(削除済み曲は再生時スキップ)
- **再生**: 各曲の sections を連結した平坦化 secs(`buildFlatSecs`)を既存の再生エンジンへ渡す。曲間に疑似セクション `gap`(無音)・`tapin`(タップイン)を挿入
- **つなぎ**: 「そのまま」は前曲 End を除外して直結。「無音→Tap in」は無音の1拍目に End を1打、残り無音(拍数指定、前曲の終了テンポ・拍子)→ 次曲テンポで Tap in
- **Tap in パターン** `TAPIN_PATTERNS`(A=accent音/T=ci音): 4=TTTT、6=ATTATT、8=ATATAAAA、12=ATTATTAAAAAA。パフォーマンスのカウントインとプレイリストのつなぎで共用
- **Tap in/out(カウントイン/エンドチェック)** は再生範囲の最初と最後のみ。範囲終端が End のときは End をエンドチェック1拍目と兼ねて二重打ちしない。範囲終端が通常セクションの場合に途中でエンドチェックへ飛ぶ既存バグも修正
- **範囲選択**: プレイリスト時は「開始 曲▼位置▼ / 終了 曲▼位置▼」の2行グリッド。単曲時は従来どおり
- **共有コード**: `v:6 kind:'playlist'`(曲ごと1コード)。旧 v:5 単曲コード・旧つなぎ形式(`end`/`gapMeasures`)も読込時に変換
- **BPM 表示ちらつき修正**: 原因は区間切替時の表示更新がスケジュール時(音より先)に即時実行され、その後に残っていた前区間の表示イベントが古い BPM で上書きしていたこと。表示更新を `queueVisual({kind:'state'})` で音の時刻に同期
- **バックグラウンド時の拍乱れ修正**(公開版からの既存問題): 非表示・非フォーカス時は先読みを 0.1s→1.5s に延長し、`blur`/`visibilitychange` 時に即予約
- **縦向き専用**: `manifest.json` に `orientation:portrait`。タッチ端末の横向き時は「縦向きにしてください」オーバーレイ
- **UI**: プレイリスト一覧の再生ボタンを 44px・START 色に。曲編集タブはプレイリスト読込中ロック(「単曲モードに戻る」)

### 検証状況

- Chrome(ブラウザペイン): 2曲プレイリストで カウントイン4 → 曲1 → 無音(End+3拍) → Tap in 6(ATTATT) → 曲2 → エンドチェック4(End と合流)の発音順を確認。BPM 表示は1回だけ切替(ちらつきなし)。範囲の曲/位置セレクト、エクスポート→インポート往復、再生ボタン表示を確認
- Safari: Phase 8.2 時点の版で正常に鳴ることをユーザー確認済み。Codex 指摘6件修正以降の版は Safari 未確認
- 未確認: iPhone 実機、3テーマそれぞれの新 UI の見た目、横向きオーバーレイの実機表示

## ドキュメントの役割

- `METRONOME_SPEC.md` — 機能仕様（一次情報。Phase 8/8.1/8.2 節あり）
- `DESIGN.md` — デザイン仕様（テーマ・レイアウト・配色、一次情報）
- `USER_GUIDE.md` — 利用者向け取扱説明書
- `CODEX_PROMPT.md` — Phase 5 当時の Codex 向けハンドオフ（履歴）
- `STATUS.md` — 本ファイル

### Codex レビュー指摘6件の修正(2026-09-27、未コミット)

- ID生成を `genId(prefix)` に共通化(`crypto.randomUUID()` フォールバック・既存ID重複チェック)し、曲・プレイリストの全ID生成箇所を統一
- 停止直後の再開で旧予約音が鳴る問題を修正(`pendingOscillators` で発音予定の OscillatorNode を保持し `stopTransport()` で全停止)
- 表示(curS/curM/isCi/isEc/ciBt/ecBt)と音の再生時刻の同期を徹底(論理状態と表示状態を分離、`queueVisual`/`applyVisual` 経由でのみ表示更新)
- `exitPlaylistMode()`・曲削除(読込中の曲)で再生中なら `pStop()` してから `secs` を差し替えるよう修正
- プレイリスト編集の名前入力を `#plT` の `input` イベントで即時データ反映(曲追加・並べ替え等の再描画で消えなくなった)
- 不正な共有コード(songs/items/各要素の構造不正)を取り込み前に全体検証し、不正時は何も変更せず toast 表示するよう修正
- 詳細は `METRONOME_SPEC.md`「Codex レビュー指摘の修正(Phase 8.2 追加)」節を参照

## 次アクション候補

- **Phase 9 のブラウザ確認**(最優先): スマホ幅(390×844)でのレイアウト崩れ、3テーマでの見た目、選曲シートの開閉、プレイリスト読込中の曲編集→保存→パフォーマンス反映、プレイリスト編集✎→曲編集→戻る、の一連の動作確認
- **Codex レビュー** → 指摘対応 → コミット・push
- iPhone 実機確認(レイアウト・タップ・Bluetooth 遅延・縦向き固定)
- アイコンが旧オレンジ配色のまま。新テーマ配色で更新
- テーマ B で「◀◀ 10」表記が2行に折り返される問題
- 不要になった発光系 CSS 変数(`--lcdglow` 等)の整理
