# FilmDateStamp AGENTS.md

フィルム写真の感光乳剤に焼き付けられる「クォーツデート（日付スタンプ）」の光学・物理質感を徹底追及し、ComfyUI の画像生成パイプライン上で本物の露光・ハレーション・埋もれを再現・合成するカスタムノードパッケージ。

元プロジェクト: `C:\Users\coffe\Documents\rec-frame-ComfyUI` からの完全独立フォーク・特化パッケージ。
設置場所: `C:\Users\coffe\Documents\FilmDateStamp`

> [!NOTE]
> **ドキュメント運用ルール**:
> - **仕様・光学モデル・レンダリングパイプライン**: [`SPEC.md`](./SPEC.md) に集約。
> - **設計思想・アーキテクチャ・運用ガイド**: 本ファイル（[`AGENTS.md`](./AGENTS.md)）に集約。
> - **変更履歴**: [`CHANGELOG.md`](./CHANGELOG.md) に記録。

---

## 1. コンセプト・開発方針

1. **「文字貼り付け」の完全脱却 — 光学感光（Optical Burn-in）モデル**
   - フィルムカメラの日付写し込みは、カメラ背面の小型LED（または極小ランプ）がフィルム乳剤を直接露光（感光）させたもの。
   - インクの通常合成（alpha_composite）や単純なスクリーン合成ではなく、**リニア空間での加算露光と乳剤の未感光キャパシティ（Headroom）** に基づいた物理感光合成を常時適用。
   - **ハイライト埋もれ再現**: 背景が真っ白・高輝度な写真では、フィルム乳剤がすでに飽和しているため、デートスタンプの光が白飛びして背景に埋もれ、判別困難になる「実物のあの現象」を忠実にシミュレートする。
2. **H&D分光感光飽和 ＆ 多重スケール散乱（Spectrophotometric Bleaching & Multi-scale PSF）**
   - **分光色飽和**: 単なる色ブラーの重ね合わせではなく、露光エネルギー $E$ に応じて赤→橙→黄→白（クリーム色）へと波長順に感光飽和するフィルム本来のレスポンス。
   - **LED中心尾根（Hotspot Ridge）**: 近似距離変換によるセグメント中心線の高輝度ピークと回折ブルーミング。
   - **多重スケールPSF**: 狭角前方散乱（Mie）からベース裏面・圧板反射による広角ハレーション、超広角ベールグレアまでの有機的合成。
3. **3階層の有機的ゆらぎ（Organic Irregularity）**
   - **Macro**: LED素子ごとの個体差（±10%前後）および投影レンズの周辺光量落ち・傾斜による光量ムラ。
   - **Meso**: フィルム裏蓋圧板の密着ムラ（雲状ノイズ）とドメインワープによるハレーション外縁の非対称な波打ち・歪み。
   - **Micro**: 銀塩粒子（フィルムグレイン）の感光閾値ゆらぎ。ハレーションの淡い裾野でのみ色素雲（Dye Cloud）によって輪郭がちぎれる物理特性を再現。
4. **実機幾何学 ＆ 空想フォント（厳選8種・完全自社製TrueType中心）**
   - **FDSMechanical70s**: 1970s機械式活字彫刻・DIN 1451/JIS工業彫刻文字準拠（Canon Canodate E / Datematic）
   - **FDS7Strict-Compact**: 1980s諏訪精工舎モジュール実機幾何学完全準拠・前傾-7.0°（Autoboy, L35AD等）
   - **FDS7Strict-SLR**: 1980s一眼レフデータバック直立実機準拠・直立0.0°（Nikon MF-12/14/16等）
   - **FDSDotStrict**: 1990s写ルンです・高級コンパクト機 5×7縦長カプセルドット完全準拠
   - **ShareTechMono**: 90〜2000年代コンデジ・カシオG-SHOCK等幅液晶
   - **Michroma**: 80s-90s宇宙探査機・SF映画調テレメトリ（超ワイド幾何学・空想枠）
   - **MochiyPopOne**: 平成レトロお餅丸文字・プリクラ電飾（Kawaii・空想枠）
   - **EagleLake**: 錬金術師の野帳・古文書インク筆記・SCP機密記録（魔導・空想枠）
5. **視覚サイズ自動正規化（Visual Size Normalization）**
   - フォントごとの内部EM枠や余白比率の違いを自動吸収し、`font_scale` をフォントごとに手動調整することなく、切り替えるだけで同じ視覚サイズ・同じ四隅マージン位置にピタリと揃う。
6. **直感的な日付指定インターフェース**
   - `date_string` にそのまま文字を入力すれば直接カスタム描画（例: `'98 12 24`）。
   - `"auto"` または `"today"` と入力すれば実行時の現在日時を自動生成。
   - `"random"` と入力すればヴィンテージ年代（1985〜2005）のランダム日時をシード再現性を持って自動生成。
   - `show_time` の True/False で時刻表示を直感的に切り替え。

---

## 2. ディレクトリ構成

- `__init__.py` — ComfyUI カスタムノードのエントリーポイント。
- `README.md` — グローバル公開用公式ドキュメント（英語・プライマリ）。
- `README_ja.md` — 公式ドキュメント日本語版。
- `nodes.py` — ComfyUI ノード定義層（PyTorch `Tensor` ⇄ `PIL.Image` / `NumPy`、バッチ処理）。
- `film_stamp.py` — コア光学レンダリングエンジン（Pillow / NumPy ベース、視覚サイズ正規化、タイト矩形クロップ、ComfyUI非依存）。
- `film_config.py` — 設定データクラス、カラープリセット、スタイル一括プリセット、日付フォーマットパーサー。
- `fonts/` — 同梱フォント（厳選8種、実機再現4種自社製 ＆ SIL OFL 1.1 ライセンス）：
  - `FDSMechanical70s-Regular.ttf`（★1970s機械式活字・DIN 1451/JIS工業彫刻文字完全準拠・自社製）
  - `FDS7Strict-Compact.ttf`（★1980s実機幾何学完全準拠・前傾-7.0°・自社製）
  - `FDS7Strict-SLR.ttf`（★1980s実機幾何学完全準拠・直立0.0°・自社製）
  - `FDSDotStrict-Regular.ttf`（★写ルンです・90sコンパクト機 5×7縦長カプセルドット完全準拠・自社製）
  - `ShareTechMono-Regular.ttf`（90〜2000sコンデジ液晶等幅・OFL）
  - `Michroma-Regular.ttf`（80s-90s宇宙探査・超ワイド幾何学HUD・OFL）
  - `MochiyPopOne-Regular.ttf`（平成レトロ・お餅丸文字ポップ・OFL）
  - `EagleLake-Regular.ttf`（古文書・錬金術インク手書き筆記・OFL）
- `workflows/` — 公式ワークフロー JSON（`film_date_stamp_workflow.json`）。
- `web/` — ComfyUI フロントエンド拡張スクリプト（`web/js/film_date_stamp.js`、プリセット値の自動同期およびカスタム切替）。
- `scripts/` — フォントビルド、プロトタイプ検証、比較レポート生成用スクリプト。
- `tests/` — 単体テスト、光学合成パイプライン、サイズ正規化の回帰テスト。
- `assets/` — ドキュメント用ビジュアルアセット、比較検証レポート画像。

---

## 3. テスト・検証コマンド

ComfyUI 本体の仮想環境 Python を使って、単体で高速に自動テストおよび各種検証スクリプトを実行する：

```powershell
# 単体テストの実行（全24件、全件PASS確認）
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" -m unittest discover -s "C:\Users\coffe\Documents\FilmDateStamp\tests"

# テストボード画像の生成 (assets/prototype_test.png)
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" "C:\Users\coffe\Documents\FilmDateStamp\scripts\prototype_render.py"

# ショーケース画像の生成 (assets/presets_showcase_en.png / presets_showcase_ja.png)
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" "C:\Users\coffe\Documents\FilmDateStamp\scripts\generate_presets_showcase.py"

# 厳選フォント比較レポート画像の生成 (assets/font_comparison_report_v2.png)
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" "C:\Users\coffe\Documents\FilmDateStamp\scripts\generate_font_report.py"
```
