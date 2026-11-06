# CHANGELOG - FilmDateStamp

フィルム写真の感光乳剤に焼き付けられる「クォーツデート（日付スタンプ）」の光学・物理質感を徹底再現する ComfyUI カスタムノードパッケージ `FilmDateStamp` の更新履歴。

---

## [1.0.0] - 2026-11-04 (Initial Public Release)

### Added
- **光学物理エミュレーションエンジン (`film_stamp.py`)**:
  - **Optical Burn-in 物理モデル**: 単なる文字オーバーレイや単純なスクリーン合成を排し、リニア輝度空間（`sRGB <-> Linear`）での光子照射加算と、背景写真の輝度に応じた **フィルム乳剤感光余力（Emulsion Headroom）合成 ＋ ソフト肩特性ロールオフ** を常時適用。
  - **ハイライト埋もれ現象の再現**: 白背景や空・逆光などの高輝度部では乳剤がすでに飽和しているため、スタンプ光が自然に白飛びして背景に溶け込む実物の光学特性を忠実にシミュレート。
  - **H&D 非線形分光感光モデル (Spectrophotometric Bleaching)**: 露光エネルギー $E$ に応じて、裾野の長波長（赤）から中間部（アンバー・オレンジ）、中心コアの飽和白（ブリーチ）へと波長順に連続遷移する発色モデルを実装。
  - **LED 発光尾根 (Hotspot Ridge)**: 反復モルフォロジー近似距離変換によりセグメント中心線の高輝度フィラメント尾根と回折ブルーミングを抽出。
  - **多重スケール点拡がり関数 (Multi-Scale PSF) 散乱**: 狭角前方散乱（Mie散乱）からベース裏面・圧板反射による広角ハレーション、超広角ベールグレアまでを周波数領域（FFT空間）の単一伝達関数として高速合成。
  - **3階層の有機的ゆらぎ (`irregularity`)**:
    - **Macro**: LED素子ごとの発光個体差（±10%前後）および投影レンズの周辺減光・傾斜ムラ。
    - **Meso**: 裏蓋圧板の密着ムラ（雲状fBmノイズ）とドメインワープによるハレーション外縁の非対称な波打ち・滲み。
    - **Micro**: 銀塩粒子（フィルムグレイン）の感光閾値ゆらぎと、淡い裾野でのみ色素雲（Dye Cloud）によって輪郭がちぎれる物理特性。
  - **完全スタンドアロン設計**: 空間フィルタ・距離変換・ノイズ生成をすべて純粋な `NumPy` + `Pillow` のみで実装（`scipy` 等の外部依存なし）。

- **実機幾何学完全準拠の自社製TrueTypeフォント ＆ 厳選タイポグラフィ（全8種・SIL OFL 1.1準拠）**:
  - **`FDSMechanical70s-Regular.ttf`**（自社製）: 1970年代最初期の機械式活字ドラム・タングステン電球投影カメラ（Canon Canodate E [1970] / Datematic [1974]）準拠。DIN 1451 / JIS工業彫刻文字ベース、カプセル形状の `0`、45°カギ鼻ビークの `1`、クローズド `4`。
  - **`FDS7Strict-Compact.ttf`**（自社製）: 1980〜90年代コンパクトカメラ黄金期標準（諏訪精工舎モジュール準拠、前傾 $-7.0^\circ$、スリム比率 $W/H=0.500$、セグメント厚10%、35°テーパーカット、上部浮遊ドットアポストロフィ）。
  - **`FDS7Strict-SLR.ttf`**（自社製）: 1980年代一眼レフデータバック標準（Nikon MF-12/14/16、Olympus Recordata準拠、直立 $0.0^\circ$、スリム比率 $W/H=0.500$）。
  - **`FDSDotStrict-Regular.ttf`**（自社製）: 1990年代写ルンです・高級コンパクト機標準（5×7縦長カプセルドット $65\times 80\text{u}$、斜線なし中空 `0`、斜め2ドットアポストロフィ、乳剤内での光学融合を再現）。
  - **`ShareTechMono-Regular.ttf`**: 90〜2000年代初期コンデジ・カシオG-SHOCK風等幅液晶。
  - **`Michroma-Regular.ttf`**: 【空想・サイバー枠】80s-90s宇宙探査機・SF映画調テレメトリ（超ワイド幾何学HUD）。
  - **`MochiyPopOne-Regular.ttf`**: 【空想・Kawaii枠】平成レトロお餅丸文字・プリクラ電飾（ASCIIサブセット最適化済み）。
  - **`EagleLake-Regular.ttf`**: 【空想・魔導枠】錬金術師の野帳・古文書インク筆記スクリプト。

- **視覚サイズ自動正規化 (Visual Size Normalization) ＆ タイト矩形クロップ**:
  - フォントごとの内部EM枠や余白比率の差を自動吸収し、どのフォントに切り替えても同じ `font_scale` で均一な視覚サイズと四隅マージン位置を維持。
  - 現代のディスプレイ・SNS表示での視認性と実機感を両立する基準フォントサイズ（短辺の $4.0\%$）を採用。

- **時代・地域・世界観を網羅する12種のスタイルプリセット (`style_preset`) ＆ 9種の発光スペクトル (`preset_color`)**:
  - 実機再現プリセット9種（`Japanese Tokyo 90s`, `Japanese Snap (Disposable)`, `American West Coast`, `American 80s (Red Quartz)`, `European Classic (Paris/Berlin)`, `Y2K Digicam (Early 2000s)`, `Compact Fine Dot (Minimal)`, `Monochrome 70s (Canodate E)`, `Vintage 70s Color (Datematic)`）。
  - 空想・シミュレーティブプリセット3種（`Cyber Telemetry (80s Sci-Fi)`, `Y2K Pop (Heisei Fancy)`, `Arcane Occult (Crimson Script)`）。
  - ComfyUI フロントエンド拡張（`web/js/film_date_stamp.js`）により、プリセット選択時の各ウィジェット自動反映と、手動微調整時の `"Custom"` 自動切替を実現。

- **直感的な日付入力 (`date_string`) と時刻トグル (`show_time`)**:
  - 任意のカスタム文字列の直接入力に加え、`"auto"` / `"today"` / `"now"`（実行時現在日時、キャッシュ自動無効化）および `"random"`（1985〜2005年のヴィンテージ日時、シード再現性対応）をサポート。
  - 9種の日付フォーマット（`'YY MM DD`, `YY MM DD`, `MM DD 'YY`, `DD MM 'YY`, `DD.MM.YY`, `YY-MM-DD`, `YY.MM.DD`, `YYYY MM DD`, `YYYY-MM-DD`）と、ワンクリックで時分（`HH:MM`）を付加・除去する `show_time` トグルを搭載。

- **ComfyUI ノード多機能入出力 (`nodes.py`)**:
  - バッチテンソル処理（`[B, H, W, C]`）、RGBA（4ch）アルファ保持、1chグレースケール入出力、HDRオーバーシュート保護に対応。
  - 3つの出力スロット:
    1. `IMAGE`: 光学焼き付け合成後の画像テンソル。
    2. `MASK`: 文字コアからハレーション裾野まで滑らかに減衰する高精度アルファマスク `[B, H, W]`。
    3. `STRING` (`date_text`): 実際に描画された日付・時刻文字列。
  - Comfy Registry / ComfyUI-Manager 準拠の `pyproject.toml`、公式サンプルワークフロー（`workflows/film_date_stamp_workflow.json`）、3言語対応公式ドキュメント（`README.md` / `README_ja.md` / `README_zh.md`）、単体テストスイート（全24件）を完備。
