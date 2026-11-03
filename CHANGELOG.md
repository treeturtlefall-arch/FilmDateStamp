# CHANGELOG - FilmDateStamp

フィルム写真の日付焼き付け特化型ComfyUIノード `FilmDateStamp` の更新履歴。

---

## [1.7.0] - 2026-11-03

### Changed
- **フォント定義の単一情報源化 (DRY)**:
  - `FONT_MAP` を `film_config.py` に集約し、`SUPPORTED_FONTS` を辞書のキーから自動導出する構成にリファクタリング。
- **ノード実行時のウィジェット値尊重（プリセット強制上書きバグ解消）**:
  - `nodes.py` で無条件に実行されていた `config.apply_style_preset_if_set()` を整理。ComfyUI フロントエンドでプリセット選択後に `date_mode`（例: `random_vintage`）や `seed` などの特定ウィジェットのみを変更した場合でも、ユーザーの入力値が強制上書きされずに正しく尊重されるよう修正。
- **光学レンダリングパイプラインの高速化・省メモリ化**:
  - `ImageFont` のロード、マスク生成、および 3層光学ブラー合成（`generate_light_map_cached`）に `lru_cache` を導入。
  - バッチ処理時において同一サイズ・同一テキストの再計算を完全スキップし、処理速度を大幅に向上。
  - 3層ブラー光量マップの合成を Python ループから NumPy ブロードキャストによるベクトル演算へ移行。
  - 画像全体の重複した `.copy()` を削減し、不要なメモリ確保を抑制。

### Added
- **構成ファイルの整備**:
  - プロジェクトルートに `.gitignore` および `requirements.txt` を追加。
- **フォント検証レポートの拡充**:
  - `scripts/generate_font_report.py` に全7種のうち未掲載だった `DSEG14_Italic (14-Segment)` を追加し、全フォントの比較画像を再生成。

### Removed
- **不要な一時検証スクリプト・旧アセットの削除**:
  - `scripts/test_render_quick.py`、`scripts/test_smart_quote.py`、`assets/test_patched_quote.png`、`assets/font_comparison_report.png`（旧版）をクリーンアップ。

---

## [1.6.0] - 2026-11-03

### Changed
- **日付設定の整理と独立トグル化 (`show_time`)**:
  - 日付フォーマットの選択肢（`SUPPORTED_DATE_FORMATS`）から混在していた `"'YY MM DD HH:MM"` を除外し、純粋な日付表記スタイル（年月日順・区切り記号）に統一。
  - 新たに `show_time`（BOOLEAN, 初期値 False）ウィジェットを追加し、どの日付フォーマットであってもワンクリックで時刻（`HH:MM`）の表示・非表示を切り替え可能に改善。
  - `custom` モード時におけるスマート挙動:
    - `show_time=False`: `date_string` に末尾時刻が含まれている場合は自動で時刻部分を除去。
    - `show_time=True`: `date_string` に時刻が含まれていればそれを維持し、未入力の場合はデフォルト時刻（`18:30`）を自動付加。
- **スタイルプリセットおよびフロントエンド自動同期の更新**:
  - `Japanese Snap (Disposable)`, `Y2K Digicam (Early 2000s)`, `Compact Fine Dot (Minimal)` を `show_time: true` に更新。
  - `web/js/film_date_stamp.js` のプリセット双方向同期キーに `show_time` を追加。
- **公式ワークフローの同期更新**:
  - `workflows/film_date_stamp_workflow.json` のウィジェット順序および Note ノードの解説を更新。

## [1.5.0] - 2026-11-03

### Changed
- **世界観・地域文化ベースのスタイルプリセット全面刷新**:
  - カメラの固有名詞を排し、地域性や時代背景・写真文化を想起させる洗練されたプリセット体系へリニューアル：
    - `Japanese Tokyo 90s`: 90年代日本の日常スナップ・王道アンバー（'YY MM DD）
    - `Japanese Snap (Disposable)`: 写ルンです風・縦長発光ドット（'YY MM DD HH:MM）
    - `American West Coast`: 90年代西海岸・ロードトリップ（MM DD 'YY / ゴールデン）
    - `American 80s (Red Quartz)`: 80年代モーテル・ホームビデオ・赤色LED（MM DD 'YY）
    - `European Classic (Paris/Berlin)`: 欧州の石畳・上品な佇まい（DD.MM.YY / 控えめアンバー）
    - `Hong Kong Neon (90s Cinema)`: 90年代香港ネオン映画調（'YY MM DD / サイバーグリーン）
    - `Y2K Digicam (Early 2000s)`: 2000年代初期コンデジLCD液晶（'YY MM DD HH:MM）
    - `Compact Fine Dot (Minimal)`: 超高精細スクエアドット（'YY MM DD HH:MM）
- **公式ワークフローおよびドキュメントの同期**:
  - `workflows/film_date_stamp_workflow.json` のデフォルトプリセットおよび説明メモを新体系に更新。

### Added
- **欧州伝統ピリオド記法 (`DD.MM.YY`) の追加**:
  - `SUPPORTED_DATE_FORMATS` およびパーサーに `DD.MM.YY`（例: `24.12.98`）を追加。
- **フロントエンド自動同期の強化 (`web/js/film_date_stamp.js`)**:
  - プリセット選択時に、そのスタイルに最適な代表日付文字列（`date_string`）も同時にウィジェットへ反映。
- **プリセット比較ショーケース生成スクリプト**:
  - `scripts/generate_presets_showcase.py` を追加し、`assets/presets_showcase.png` を生成。

## [1.4.0] - 2026-11-03

### Changed
- **UI階層の全面刷新（プリセット最上段化）**:
  - `style_preset` を最上段（`image` の直下）に移動。
  - ウィジェット順序を【1. プリセット】→【2. 光学・フォント設定】→【3. 日付内容】→【4. レイアウト】の直感的な流れに再編。
- **公式ワークフローの更新**:
  - `workflows/film_date_stamp_workflow.json` のウィジェット順序と解説メモを最新仕様に同期。

### Added
- **プリセット自動同期フロントエンド拡張 (`web/js/film_date_stamp.js`)**:
  - 最上段の `style_preset` を切り替えると、直下のフォント、カラー、露出、ハレーション等のパラメータがプリセット値へ一瞬で自動同期される双方向連携。
  - 各パラメータを手動で変更した瞬間に `style_preset` が自動で「Custom」へ切り替わり、ベースからの微調整が極めてスムーズに。
  - `__init__.py` に `WEB_DIRECTORY` を追加し、ComfyUI フロントエンドに自動ロード。

## [1.3.0] - 2026-11-03

### Added
- **視覚サイズ自動正規化エンジン (`get_font_visual_norm_factor`)**:
  - 各フォントのEM仮想ボディや余白比率の違いを自動吸収する加重幾何平均モデル（横幅75%×高さ25%）を実装。
  - どのフォントに切り替えても同一 `font_scale` で均一な視覚サイズを維持し、個別のサイズ再調整が不要に。
- **実点灯ピクセル外接矩形クロップ（Tight Bounding Box Alignment）**:
  - 各フォント内部の不要な上下余白を排除し、四隅配置時のマージン位置をピクセル単位で統一。
- **公式 DSEG14 quotesingle グリフの DSEG7 への完全移植**:
  - 先端が斜めにシェイプされた本物仕様のセグメントグリフを移植し、字幅・配置を最適化。

### Fixed
- **ComfyUI ウィジェット引数順序の後方互換性修正**:
  - `style_preset` をオプショナル引数末尾に配置し、既存ワークフローの引数スロットがズレて「無効な入力」「範囲外エラー」が発生する問題を完全解決。

## [1.2.0] - 2026-11-03

### Added
- **フォントファミリーの大幅拡充（全7フォント）**:
  - `ShareTechMono (LCD Digital)`: 90〜2000年代コンデジ・カシオG-SHOCK風液晶等幅。
  - `DSEG14_Classic / Italic (14-Segment)`: 高級Hi-Fi・特殊機器風14セグメントLED。
  - `Silkscreen (Fine Dot)`: 正方形8px基調の超高精細ドットマトリクス。
  - `DSEG7_Italic (7-Segment)`: 公式のBoldItalicフォントを導入。
- **スマート・アポストロフィ（実機クォーツデート右上セグメント）機能**:
  - `DSEG7` に存在しなかったアポストロフィ（`0x27`）に対し、物理クォーツデート実機と同様の右上セグメントを抽出してパッチ。豆腐（□）を完全根絶。
- **新スタイルプリセットの追加**:
  - `2000s Digicam LCD (ShareTechMono)`
  - `Compact Fine Dot (Silkscreen)`

## [1.1.0] - 2026-11-03

### Added
- **スタイル一括プリセット機能 (`style_preset`) の追加**:
  - `Fuji QuickSnap (写ルンです・日時)`: VT323 ドットマトリクス、Fuji Orange、core_glow=0.50、font_scale=1.20、margin=1.50、現在日時・時分併記 ('YY MM DD HH:MM) の完全プリセット。
  - `Autoboy Quartz (90s 王道アンバー)`: 傾斜7セグ、Amber Classic、王道日付。
  - `Retro Quartz (80s レトロレッド)`: 直立7セグ、昭和・初期型クォーツデート。
  - `2000s Compact (ゴールデンイエロー)`: 2000年代前後のコンパクトカメラ風。
- **インポート安全性の向上**:
  - ComfyUI本体からのロード時に生じるパッケージ内外のインポートパスを自動フォールバック対応。

## [1.0.0] - 2026-11-03

### Added
- **元プロジェクト (`rec-frame-ComfyUI`) からの完全独立フォーク**:
  - フィルムクォーツデート特化パッケージとして初期リリース。
- **光学露光エンジン (`film_stamp.py`)**:
  - 3層光路モデル（高輝度白コア ＋ アンバー主発光 ＋ 乳剤内赤色ハレーション散乱）の実装。
  - `optical_burn`: Reinhard肩特性ロールオフによるハイライト飽和・白飛び埋もれシミュレーション。
  - PIL Image および NumPy 配列（float32 / uint8）の高速演算対応。
  - アフィン変換（シアー変形）による 11.5度傾斜イタリック対応 (`DSEG7_Italic`)。
  - 4方向配置（`bottom_right`, `bottom_left`, `top_right`, `top_left`）および短辺基準のアダプティブマージン計算。
- **設定データクラス・日付パーサー (`film_config.py`)**:
  - 5種のカラープリセット（Amber Classic, Quartz Red, Fuji Orange, Golden Yellow, Cyber Green）。
  - 日付モード（`custom`, `current_date`, `random_vintage`）。
  - 7種以上の日付フォーマット（`'YY MM DD`, `MM DD 'YY`, `DD MM 'YY`, `YY-MM-DD`, `YY.MM.DD`, `'YY MM DD HH:MM`, `YYYY MM DD`）。
  - シード値によるランダム過去日付の完全な再現性担保。
- **ComfyUI ノード (`nodes.py`, `__init__.py`)**:
  - `FilmDateStamp` ノードクラス定義。
  - PyTorch Tensor (`[B, H, W, C]`, float32) とのシームレスなバッチ合成処理。
  - `custom_nodes/FilmDateStamp` ジャンクション連携。
- **ワークフロー & テスト**:
  - 公式ワークフロー JSON (`workflows/film_date_stamp_workflow.json`) の追加。
  - 単体テスト・回帰テストスイート (`tests/test_date_stamp.py`) の全テストパス確認。
