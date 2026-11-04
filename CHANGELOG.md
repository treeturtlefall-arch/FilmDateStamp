# CHANGELOG - FilmDateStamp

フィルム写真の日付焼き付け特化型ComfyUIノード `FilmDateStamp` の更新履歴。

---

## [2.4.2] - 2026-11-04 (Preset Margin Optimization from Real-world Photo Verification)

### Changed & Improved
- **主要6プリセットの初期マージンを `1.15` に最適化改定**:
  - 実写写真（昭和の街角スナップ写真、2560×1774 / 1774×2560）による実機検証に基づき、端に近すぎず適度なゆとりを持たせたバランス（短辺の約 5.75% / 4.6% 余白）へ初期配置を改定。
  - 改定対象プリセット:
    - `Japanese Tokyo 90s` (`margin`: 1.00 → **1.15**)
    - `American West Coast` (`margin`: 1.00 → **1.15**)
    - `American 80s (Red Quartz)` (`margin`: 1.00 → **1.15**)
    - `European Classic (Paris/Berlin)` (`margin`: 1.10 → **1.15**)
    - `Monochrome 70s (Canodate E)` (`margin`: 1.00 → **1.15**)
    - `Vintage 70s Color (Datematic)` (`margin`: 1.00 → **1.15**)
  - Python設定層（`film_config.py`）およびフロントエンドUI連動層（`web/js/film_date_stamp.js`）の両方を完全同期更新。
- **検証環境・レポートツールの追加**:
  - 実写画像に対する感度比較スクリプト `scripts/test_showa_oji_stamps.py` を整備。
  - 全12プリセット・マージン感度（0.70〜1.50）・フォントサイズ感度（0.80〜1.30）をブラウザでインタラクティブに比較可能な HTML ビューアを生成。

---

## [2.4.1] - 2026-11-04 (Font Scale Modernization & Visual Normalization Finalization)

### Changed & Improved
- **基準フォントサイズの現代的スケールへの底上げ（+25% アップグレード）**:
  - 現代のディスプレイ、SNSタイムライン（X/Instagram）、スマートフォン表示における視認性と写真全体のバランスを追求し、`film_stamp.py` の基本フォントサイズ算出係数を `0.032`（短辺の3.2%）から **`0.040`（短辺の4.0%）** へ +25% 改定。
  - 1024×1024 画像における文字の Cap Height（数字の高さ）が約 20px → **約 25〜26px** へ拡大され、写真の引き（Full View）でも日付が明瞭に判読可能に。
  - 光学コアグローや H&D 分光感光飽和（赤→橙→黄→白のブリーチグラデーション）の階調感がよりリッチに目視可能に。
  - コア係数の底上げにより、各プリセット間の相対スケール（写ルンですの `font_scale=1.20`、欧州クラシックの `font_scale=0.95` 等）の世界観バランスを完全保持。
- **全厳選フォント8種に対する視覚サイズ自動正規化（Visual Size Normalization）の完全検証**:
  - 実機スリム7セグから超ワイド幾何学（Michroma）、カリグラフィ（EagleLake）に至る全8フォントにおいて、最大/最小の描画文字幅比率が **わずか 1.23倍（24%以内）** に収まることを単体テストで厳密に検証・保証。

---

## [2.4.0] - 2026-11-04 (Workspace Optimization, Refactoring & Global Localization)

### Documentation & Internationalization
- **英語プライマリ化と多言語ドキュメント整備**:
  - グローバル公開・Comfy Registry / ComfyUI-Manager 登録基準に準拠し、ルートの `README.md` を洗練された英語ドキュメントに刷新。
  - 日本語ドキュメントを `README_ja.md` として分離・保持し、両ドキュメント冒頭に双方向リンク（`[English](README.md) | [日本語](README_ja.md)`）を設置。
  - `workflows/film_date_stamp_workflow.json` の Note ノード（解説テキスト）を英語化し、海外ユーザーが即座に理解・試用できる環境を整備。
  - `nodes.py` のモジュールおよびクラス Docstring を英語化。

### Optimized & Performance
- **リポジトリ・配布サイズの大幅軽量化 (約 28 MB → 約 1.5 MB 以下, 94% 削減)**:
  - `MochiyPopOne-Regular.ttf` を日付スタンプ用文字（ASCII印字可能文字＋基本約物）にサブセット化（5.16 MB → 19.5 KB、99.6% 削減）。
  - 開発中の一時試用フォント（`tests/temp_fonts/` 計 7.51 MB）およびワンオフ比較スクリプト・試作画像（計 16.5 MB）を安全にクリーンアップ。
- **光学露光エンジンの FFT 周波数領域統合**:
  - `film_stamp.py` の多重ハレーション散乱（`psf_mid`, `psf_wide`, `psf_veil`）を周波数領域（FFT空間）で1つの伝達関数に合成してから逆変換するよう最適化。
  - 2D RFFT / IRFFT の呼び出し回数を削減し、未キャッシュ時のレンダリング時間を約 15% 高速化（57ms → 48ms、キャッシュ時は約 8ms）。
- **入力 NumPy 配列の非破壊性（In-place 変更防止）の完全保証**:
  - `render_film_date_stamp` において入力画像配列（`np.float32`）のビュー直接書き込みを防止するため、描画矩形を明示的にコピーして保護。

### Refactored & Fixed
- **デッドコード・旧互換残骸のクリーンアップ**:
  - `get_font_file_and_shear` から削除済み旧フォント（`FDS7Classic`, `DSEG7`, `DSEG14`）への不要な探索コードを削除し、実在する `FDS7Strict-Compact.ttf` に統一。
  - `film_config.py` に `SUPPORTED_COLORS` を定義し、カラーパレットと分光特性の整合性を担保。
- **ライセンスおよびメタデータの完全整合**:
  - `fonts/LICENSE-OFL.txt` を現在収録されている全8フォント（自社製4種 ＋ OFL 4種: `Share Tech Mono`, `Michroma`, `Mochiy Pop One`, `Eagle Lake`）の正確な著作権・クレジット表記に全面改訂。
  - `__init__.py`, `pyproject.toml`, `CHANGELOG.md` のバージョン番号を `2.4.0` に統一。
  - `.gitignore` にビルド・一時ディレクトリ定義を追加。

---

## [2.3.1] - 2026-11-04 (Preset Refinement & Hong Kong Neon Deprecation)

### Removed
- **`Hong Kong Neon (90s Cinema)` プリセットの廃止**:
  - 1990年代の香港映画的心象風景（『恋する惑星』オマージュ）として設けていたプリセットを整理・削除。
  - 実際の中国・香港のカメラ事情（海鴎 DF-300AD、鳳凰 DC303KD等の石英日期后背は全て赤色・アンバーLED）を精査した結果、実機系プリセットとしての歴史的整合性、および「Custom」で自由に再現可能な点（`Cyber Green` パレットは存続）を踏まえてプリセット一覧から除外。
  - スタイルプリセット総数を全12種（実機9種 ＋ 空想3種 ＋ Custom）に整理。

---

## [2.3.0] - 2026-11-04 (Speculative & Fiction Stamp Expansion)

### Added
- **空想・シミュレーティブ（Fiction / Speculative）3大スタイルの新設**:
  - 実機エミュレートの枠を超え、コア光学感光エンジン（`optical_burn`）を活かした「あり得たかもしれない異世界の光学的日付焼き付け」を3系統新設。
  - **1. サイバー枠 (`Cyber Telemetry (80s Sci-Fi)`)**:
    - フォント: `Michroma (Cyber Telemetry)`（80s-90s宇宙探査機・SF映画調テレメトリ・超ワイド幾何学・OFL準拠）。
    - カラー: `Cyber Green`。
    - 特徴: 高輝度レーザー露光・鋭い回折光。秒付き高密度HUD（`'98 12 24 23:59:59`）に対応。
  - **2. Kawaii / Y2K枠 (`Y2K Pop (Heisei Fancy)`)**:
    - フォント: `MochiyPopOne (Y2K Pop)`（平成レトロ・お餅のように角が丸く膨らんだ極太丸文字・OFL準拠）。
    - カラー: `Neo Pink`（マゼンタ露光 / 広角Mie散乱）。
    - 特徴: 平成初期に限定発売されたファンシーカメラやプリクラ機の電飾露光をシミュレート。
  - **3. ファンタジー / 魔導枠 (`Arcane Occult (Crimson Script)`)**:
    - フォント: `EagleLake (Arcane Script)`（ケルト・古文書風のインク筆記体・OFL準拠）。
    - カラー: `Crimson Red`（血やインクがフィルムに直接染み込んだかのような深紅）。
    - 特徴: 錬金術師の野帳、禁断の魔導書、SCP極秘記録の禍々しい手書き呪印刻印。
- **新カラープリセット ＆ 物理分光特性**:
  - `Neo Pink`: マゼンタ主発光（`#FF50B4`）と甘く広がるMie散乱光。
  - `Crimson Red`: 血の深紅主発光（`#EB1923`）とタイトなハレーション。
- **日付パーサーの秒単位認識対応**:
  - `resolve_date_text` の正規表現を拡張（`\d{1,2}:\d{2}(?::\d{2})?`）し、サイバーHUD等で一般的な秒付きタイムスタンプ（`23:59:59`）の直接入力をサポート。

### Changed
- **フォント総数拡張**: 厳選5種（実機再現） → 全8種（実機再現5種 ＋ 空想3種）。
- **スタイル一括プリセット総数拡張**: 10種 → 全13種（実機10種 ＋ 空想3種 ＋ Custom）。
- **Web UI同期**: `web/js/film_date_stamp.js` に3種の新スタイルプリセットを追加。

---

## [2.2.0] - 2026-11-04 (Pre-release Refactoring & Clean-up)

### Removed / Deprecated (未公開前クリーンアップ＆後方互換性の完全切断)
- **旧世代フォントの完全切断 (11種 → 厳選5種へ集約)**:
  - 自社製 Strict フォント完成により下位互換となった `FDS7Classic-Bold.ttf`, `FDS7Classic-BoldItalic.ttf`, `FDS14Classic-Bold.ttf`, `FDS14Classic-BoldItalic.ttf`, `VT323-Regular.ttf`, `Silkscreen-Regular.ttf` の計6フォントファイルを完全削除。
  - 残存フォントを自社製実機仕様4種（`FDSMechanical70s`, `FDS7Strict-Compact`, `FDS7Strict-SLR`, `FDSDotStrict`）＋ 液晶等幅（`ShareTechMono`）の5種に厳選。
  - 旧フォントパッチ用スクリプト（`scripts/patch_dseg7.py`）を削除。
- **不要パラメータの廃止・統合**:
  - `optical_burn`（True/False）を廃止: 常に物理感光露光モデル（リニア乳剤余力＋フィルム肩特性）を実行。
  - `margin_x` / `margin_y` を単一の `margin` に一本化: フィルムマージンの等方スケーリングに対応。
  - `DateStampConfig` の未使用フィールド（`custom_color_hex`, `italic_angle` 等）を完全削除。
  - `format_datetime` の過去互換用 `'YY MM DD HH:MM` 分岐を削除。
  - Web UI（`web/js/film_date_stamp.js`）内の旧ワークフロー用ズレ修復ハック（`repairShiftedWidgets`）を削除。

### Changed
- **日付入力インターフェースの一本化 (`date_string`)**:
  - `date_mode`（custom / current_date / random_vintage）ウィジェットを完全廃止。
  - `date_string` にそのまま文字を入力すれば直接スタンプ（例: `'98 12 24'`）。
  - `"auto"` または `"today"` と入力すれば現在日時の自動生成（`IS_CHANGED` で NaN を返し動的更新）。
  - `"random"` と入力すれば1985〜2005年のヴィンテージランダム日時の自動生成（`seed` による再現性対応）。
- **カラープリセットの整理**:
  - `Bulb Amber` を削除（`Amber Classic` と統合）。
  - `Cyber Green` をドロップダウン選択肢の最後尾に配置（特殊用途・飛び道具カラーの明確化）。
- **公式ワークフローおよびドキュメントの刷新**:
  - 公式ワークフロー JSON（`workflows/film_date_stamp_workflow.json`）の `widgets_values` を新仕様（14ウィジェット）に同期。
  - `SPEC.md`, `AGENTS.md`, `README.md` から後方互換防衛ルールを撤廃し、v1.0.0 正式公開仕様に刷新。
  - 全単体テスト（22件）を新シグネチャに完全対応させ、全件PASSを確認。

---

## [2.1.0] - 2026-11-04

### Added
- **1970年代最初期 機械式活字・タングステン豆電球光学投影フォント『FDS-Mechanical70s』の同梱**:
  - 世界初のデートカメラ「キヤノデートE（1970年）」および「キヤノン デートマチック（1974年）」の文字盤ドラムに準拠した、DIN 1451 / JIS工業彫刻文字ベースの完全オリジナル自社生成TrueTypeフォント（`FDSMechanical70s-Regular.ttf`）。
  - **1000 UPM 厳密幾何仕様**: 等幅アドバンス幅 620 units、Cap Height 720 units、均一線幅 96 units、単玉縮小レンズの解像ボケを再現する角丸フィレット（外角 R=20u / 内角 R=12u）。
  - **歴史的字形の完全再現**: 縮小投影時の黒潰れを防ぐ角丸カプセル形状（Stadium）の `0`、頂点から左下45°へ力強く突き出す明確なカギ鼻ビークを持つ `1`（台座セリフなし）、頂点が閉じたクローズド・トライアングル `4`、-18°傾斜ダッシュのアポストロフィ `'`。
  - **タングステン白熱電球（2600K）発光物理＆カラープリセット**:
    - `Paper White (Monochrome)`: モノクロ銀塩印画紙の紙白（`#F8F6F0`）。ネガ上の Dmax 遮光により、写真上に純白の白抜き文字として浮かび上がる物理現象を再現。
    - `Bulb Warm Ivory`: 70年代カラー写真標準。タングステン豆電球の温かみのある象牙色（`#FFF2CC`）と外縁アンバーフレア。
    - `Bulb Amber`: 強露光・夜間撮影用の温かい琥珀電球色（`#FFD280`）。
  - **新スタイルプリセット**:
    - `Monochrome 70s (Canodate E)`: モノクロ写真 × 白抜き活字スタンプ（`74 12 25`）。
    - `Vintage 70s Color (Datematic)`: 70年代カラー写真 × タングステン電球色スタンプ（`'74 12 25`）。
  - フォント自動ビルドスクリプト: [`scripts/build_strict_mechanical_font.py`](./scripts/build_strict_mechanical_font.py)
  - 比較検証スクリプト & レポート: [`scripts/compare_strict_mechanical.py`](./scripts/compare_strict_mechanical.py)（[`assets/fds_mechanical_strict_comparison_report.png`](./assets/fds_mechanical_strict_comparison_report.png)）
- **1980s実機幾何学完全準拠のオリジナル自社生成TrueTypeフォント『FDS7Strict』シリーズの同梱**:
  - 1980年代に世界市場シェア95%以上を独占した諏訪精工舎（現・セイコーエプソン）製オートデーティングモジュールの物理・特許調査に基づき、Python `fontTools` で数学的座標からゼロスクラッチ自動生成された完全オリジナルフォント。
  - **`FDS7Strict-Compact.ttf`**: 80年代大ヒットコンパクト機（Canon Autoboy、Nikon L35AD ピカイチ、Olympus AF-10等）に準拠した控えめな前傾 $-7.0^\circ$ × スリム縦長比率 $W/H=0.500$。
  - **`FDS7Strict-SLR.ttf`**: 一眼レフ用データバック（Nikon MF-12/14/16、Olympus Recordata等）に準拠した端正な直立 $0.0^\circ$ × スリム比率 $W/H=0.500$。
  - **セグメント厚10.0% & ギャップ3.5%**: 従来のデジタル時計フォント（DSEG7: 厚さ12.4%, ギャップ1.5%）の過密感を解消し、強ハレーション下でも「8」や「0」の内腔（窓）が潰れずクリアに抜ける光学対応設計。
  - **$35^\circ$ テーパーカット ＋ 先端フラット面（幅18 units）**: 鋭利なピン角を排し、レンズ回折と収差による実機特有の柔らかい輪郭を再現。
  - **独立上部浮遊ドット型アポストロフィ（`'`）**: 文字高上部70%〜95%に浮遊する専用ドット素子を実装し、`'88` や `'98` のアクセントを完璧に再現。
- **写ルンです・90sコンパクト機実機仕様完全準拠の5×7ドットマトリクスフォント『FDS-DotStrict』の同梱**:
  - **`FDSDotStrict-Regular.ttf`**: 5列×7行スリムグリッド（$W=365, H=680, W/H\approx 0.537$）、縦長カプセル型ドット（$65\times 80\text{ units}, R=32.5$）、等幅480 units、直立 $0.0^\circ$。
  - 従来フォント（`VT323` の斜線入りゼロや `Silkscreen` の正方形カクカク感）を完全克服し、斜線なしの中空リング `0`、左上ヒゲ＋下部台座の `1`、クローズド三角型 `4`、斜め2ドットのアポストロフィ `'` を実装。
  - 水平10u・垂直20uの微小ギャップ設計により、`Fuji Orange (255, 115, 20)` 露光時に隣接ドットが乳剤内で滑らかに繋がる「光学融合（Optical Coalescence）」を実現。
- **フォント自動ビルドスクリプト**: [`scripts/build_strict_7seg_font.py`](./scripts/build_strict_7seg_font.py)、[`scripts/build_strict_dot_font.py`](./scripts/build_strict_dot_font.py)
- **新旧フォント光学比較スクリプト & レポート**: [`scripts/compare_strict_7seg.py`](./scripts/compare_strict_7seg.py)（[`assets/fds7_strict_comparison_report.png`](./assets/fds7_strict_comparison_report.png)）および [`scripts/compare_strict_dot.py`](./scripts/compare_strict_dot.py)（[`assets/fds_dot_strict_comparison_report.png`](./assets/fds_dot_strict_comparison_report.png)）
- **自動テストの拡充 (全22件)**: UPM 1000、イタリック角、全収録グリフ（数字・記号）、`FDS7Strict`（$W/H=0.500$）、`FDSDotStrict`（$W/H\approx 0.537$・斜線なし中空0）、および `FDSMechanical70s`（等幅620u・Cap Height 720u・カギ鼻1）の厳密テストを追加。

### Changed
- **主要スタイルプリセットのデフォルトフォントを実機厳密フォントへ正式昇格**:
  - `Japanese Tokyo 90s` および `American West Coast` を `FDS7_Strict_Compact (80s -7°)` に更新。
  - `American 80s (Red Quartz)` および `European Classic (Paris/Berlin)` を `FDS7_Strict_SLR (80s 0°)` に更新。
  - `Japanese Snap (Disposable)` を `FDS_Dot_Strict (90s Dot Matrix)` に更新し、`Fuji Orange` の主発光色を実機準拠の `(255, 115, 20)` に調整。
  - ComfyUI フロントエンド JS（`web/js/film_date_stamp.js`）および公式ワークフロー JSON（`workflows/film_date_stamp_workflow.json`）を完全同期。
- **FDS7Strict / FDSDotStrict の高さ基準視覚サイズ正規化**:
  - 実機のスリム比率（W/H=0.50〜0.537）を活かすため、横幅引き伸ばしを行わず高さ基準で正規化。

---

## [2.0.0] - 2026-11-03

### Added
- **新世代・光学物理エミュレーションエンジン (v2.0)**:
  - 従来の「3色レイヤーの単純重ね合わせ」から、フィルム乳剤・カメラ構造に根差した物理モデルへ全面刷新。
  - **H&D 非線形分光感光モデル**: 露光エネルギー $E$ に応じて赤→橙→黄→白へと波長ごとに順次飽和（ブリーチ）するカラーネガ特有の発色遷移を再現。
  - **LED 発光尾根（Hotspot Ridge）**: 近似距離変換により、セグメント中心線のピーク光量と光学スリット回折による微小な角の丸まり（Blooming）を再現。
  - **多重スケール点拡がり関数（PSF）散乱**: 狭角前方散乱（アンバーボディ）から広角ハレーション、超広角ベールグレアまでを網羅。
  - **3階層の有機的ゆらぎ（Organic Irregularity）**:
    - **Macro**: LED素子ごとの個体差（±10%前後）および投影レンズの周辺光量落ち・傾斜による光量ムラ。
    - **Meso**: フィルム裏蓋圧板の密着ムラ（雲状ノイズ）とドメインワープによるハレーション外縁の非対称な波打ち・歪み。
    - **Micro**: 銀塩粒子（フィルムグレイン）の感光閾値ゆらぎ。ハレーションの淡い裾野でのみ色素雲（Dye Cloud）によって輪郭がちぎれる物理特性を再現。
  - **リニア空間・乳剤感光余力（Headroom）合成**: リニア輝度空間にて背景写真の輝度から未感光キャパシティを計算し、白背景やハイライト領域に文字が自然に埋没・白飛びする現象を再現。
- **新規パラメータ `irregularity`（有機的ゆらぎ強度）の追加**:
  - `optional` の末尾（`seed` の下）に `irregularity`（FLOAT, 初期値 `1.0`, 範囲 `0.0`〜`2.0`, step `0.1`）を追加。
  - `0.0` で完全均一、`1.0` で実機相当のリアルな不均一ムラ、`2.0` で誇張されたヴィンテージ感を表現可能。
  - バッチ画像生成時（`batch_size > 1`）は `batch_seed = seed + b` により、1枚ごとに微妙に異なる焼き付けムラが自動生成。
- **完全スタンドアロン化（scipy 依存ゼロ）**:
  - 高度な空間フィルタやノイズ合成をすべて純粋な `NumPy` + `Pillow` で自前実装。将来の CLI 化や単体アプリ化へのフォークが容易に。

### Changed
- **ハレーション基準量の最適化**:
  - `halation=1.0` を従来の約 0.6 倍タイトな自然な滲みに再基準化。
- **公式ワークフローおよびアセットの同期更新**:
  - 公式ワークフロー JSON のウィジェットマッピングを更新（`widgets_values` 順序不変原則を厳守）。
  - プロトタイプボード（`assets/prototype_test.png`）およびフォント比較レポート（`assets/font_comparison_report_v2.png`）を v2.0 エンジンで再生成。

---

## [1.7.0] - 2026-11-03

### Fixed
- **HDR・1.01超浮動小数点の画像暗転バグの根絶**:
  - `image.max() > 1.01` による不適切な `/ 255.0` 除算を廃止。アップスケーラやシャープネス処理後の微小オーバーシュートを含む画像でも、画像全体が暗転する問題を解消。
- **RGBA (4ch) および 1ch (グレースケール) 画像入力クラッシュの修正**:
  - RGBA 入力時にアルファチャンネルを分離・保持し、RGB 露光合成後に透過度を損なわず復元して出力するよう対応。
  - 1ch 入力時に 3ch 露光処理後に元の 1ch (Luma) に復元して出力するよう対応。
- **改行・タブ・特殊制御文字入力時の例外クラッシュ防止**:
  - `date_string` 内の改行文字（`\n`）やタブ文字を空白に正規化し、Pillow の `textbbox` 例外を防止。極端な文字列長も最大64文字に制限。
- **`current_date` モードの ComfyUI キャッシュ固定化問題の解消**:
  - `nodes.py` に `IS_CHANGED` クラスメソッドを追加。`date_mode == "current_date"` の場合は `float("NaN")` を返し、実行ごとに最新日時が確実に反映されるよう修正。
- **プリセットによる個別ウィジェット値強制上書きの解消**:
  - `render_film_date_stamp` 内での無条件なプリセット適用を撤廃し、ノードから渡された個別のウィジェット引数（位置や日付）が確実に尊重されるよう改善。

### Added
- **多機能な出力スロット拡張 (`MASK`, `STRING`)**:
  - `RETURN_TYPES = ("IMAGE", "MASK", "STRING")` へ拡張。既存ワークフローとの完全な後方互換性を維持。
  - **`mask` (MASK 出力)**: スタンプ発光領域の高精度アルファマスク `[B, H, W]`（0.0〜1.0）を出力。文字コアは1.0、ハレーション外縁は滑らかに減衰。後段ノードでスタンプ領域へのフィルム粒子（Film Grain）付与や Inpaint による日付除去マスクとして活用可能。
  - **`date_text` (STRING 出力)**: 実際に描画された日付・時刻文字列を出力。`random_vintage` や `current_date` で動的生成された日時を、`SaveImage` のファイル名プレフィックスやキャプション生成ノードへそのまま渡すことが可能。
- **Comfy Registry / ComfyUI-Manager 正式対応**:
  - プロジェクトルートに `pyproject.toml`（`PublisherId`, `DisplayName`, パッケージメタデータ）を新規作成。
  - ルートに公式 MIT `LICENSE` ファイルを配置。
  - `__init__.py` に `__version__ = "1.7.0"` を定義。
- **SIL OFL 1.1 法務完全準拠（Reserved Font Name 対策）**:
  - DSEG フォントの Reserved Font Name "DSEG" 制限に準拠するため、派生フォント名を `FDS7Classic` / `FDS14Classic` に正式リネーム。フォント内部の `name` テーブルも更新し、完全な OFL 準拠を達成。
  - `fonts/LICENSE-OFL.txt` を同梱全4ファミリー（DSEG派生、VT323、Silkscreen、Share Tech Mono）の正式クレジット・著作権表示に修正。
- **自動回帰テスト・整合性テストの拡充 (全18件)**:
  - RGBA/1ch 入力、HDR 暗転防止、改行正規化、`IS_CHANGED` 動作検証、ウィジェット値尊重の厳密検証を追加。
  - フロントエンド JS（`film_date_stamp.js`）と Python（`film_config.py`）のプリセット定義一致検証テストを追加。
  - 公式ワークフロー JSON の `widgets_values` と Python `INPUT_TYPES` のウィジェット順序完全一致テストを追加。

### Changed
- **フォント定義の単一情報源化 (DRY)**:
  - `FONT_MAP` を `film_config.py` に集約し、`SUPPORTED_FONTS` を辞書のキーから自動導出する構成にリファクタリング。
- **光学レンダリングパイプラインの高速化・省メモリ化**:
  - `ImageFont` のロード、マスク生成、および 3層光学ブラー合成（`generate_light_map_cached`）に `lru_cache` を導入。
  - 3層ブラー光量マップの合成を Python ループから NumPy ブロードキャストによるベクトル演算へ移行。
- **フロントエンド JS のログ出力クリーンアップ**:
  - `console.log` の常時出力を抑制し、デバッグフラグ化。
- **ドキュメントの一般公開用クリーンアップ**:
  - `README.md` からローカル開発環境の個人パスや仮 URL を削除し、ComfyUI-Manager / Comfy CLI / Git Clone による分かりやすいインストール手順へ刷新。ビジュアルプレビューを追加。

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
