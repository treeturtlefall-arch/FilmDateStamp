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
   - インクの通常合成（alpha_composite）ではなく、**加算露光（Screen / Add / Linear Dodge）と乳剤の飽和特性**に基づいた合成を行う。
   - **ハイライト埋もれ再現**: 背景が真っ白・高輝度な写真では、フィルム乳剤がすでに飽和しているため、デートスタンプの光が白飛びして背景に埋もれ、判別困難になる「実物のあの現象」を忠実にシミュレートする。
2. **多層ハレーション・グロー（Halation & Glow）**
   - **高輝度コア（Core）**: 中心部は光量が強いため白〜極淡黄色に飽和。
   - **主発光（Body）**: 鮮やかなアンバーオレンジ（琥珀色）〜赤橙色。
   - **フィルム内光散乱（Halation）**: フィルムの乳剤層・ベース層で赤色波長が横方向に散乱する赤みのある微細グロー。
3. **時代考証とタイポグラフィ**
   - 7セグメントLED（クォーツデート標準、丸み、斜体/Italic、セグメントギャップ）
   - 14セグメントLED（高級Hi-Fi・特殊機器調）
   - ドットマトリクス（写ルンです等の縦長発光ドット群、超高精細スクエアドット）
   - LCD液晶（90〜2000年代コンデジ・カシオG-SHOCK等幅）
   - **スマート・アポストロフィ**: 7セグフォントで豆腐（□）になりがちな `'`（ASCII `0x27`）に対し、物理クォーツデート実機と同様の公式アポストロフィグリフ（DSEG14 `quotesingle`）を抽出しパッチ適用。
4. **視覚サイズ自動正規化（Visual Size Normalization）**
   - フォントごとの内部EM枠や余白比率の違いを自動吸収し、`font_scale` をフォントごとに手動調整することなく、切り替えるだけで同じ視覚サイズ・同じ右下マージン位置にピタリと揃う。
5. **アナロググレイン・フォトンゆらぎとの調和**
   - デジタルベクター特有の不自然なカドを排し、微細な熱雑音・光量ゆらぎ・フィルムグレインとの馴染みを考慮。

---

## 2. ディレクトリ構成

- `__init__.py` — ComfyUI カスタムノードのエントリーポイント。
- `nodes.py` — ComfyUI ノード定義層（PyTorch `Tensor` ⇄ `PIL.Image` / `NumPy`、バッチ処理）。
- `film_stamp.py` — コア光学レンダリングエンジン（Pillow / NumPy ベース、視覚サイズ正規化、タイト矩形クロップ、ComfyUI非依存）。
- `film_config.py` — 設定データクラス、カラープリセット、スタイル一括プリセット、日付フォーマットパーサー。
- `fonts/` — 同梱フォント（全7種、SIL OFL 1.1 ライセンス）：
  - `DSEG7Classic-Bold.ttf`（7セグ直立・公式アポストロフィ移植済み）
  - `DSEG7Classic-BoldItalic.ttf`（7セグ公式イタリック・公式アポストロフィ移植済み）
  - `DSEG14Classic-Bold.ttf`（14セグ直立）
  - `DSEG14Classic-BoldItalic.ttf`（14セグ公式イタリック）
  - `VT323-Regular.ttf`（写ルンですドットマトリクス）
  - `Silkscreen-Regular.ttf`（正方形超高精細ドット）
  - `ShareTechMono-Regular.ttf`（90〜2000sコンデジ液晶等幅）
- `workflows/` — 公式ワークフロー JSON（`film_date_stamp_workflow.json`）。
- `web/` — ComfyUI フロントエンド拡張スクリプト（`web/js/film_date_stamp.js`、プリセット値の自動同期およびカスタム切替）。
- `scripts/` — プロトタイプ検証、フォントパッチ、比較レポート生成用スクリプト。
- `tests/` — 単体テスト、光学合成パイプライン、サイズ正規化の回帰テスト。
- `assets/` — ドキュメント用ビジュアルアセット、比較検証レポート画像。

---

## 3. ComfyUI 開発における後方互換性ルール

> [!IMPORTANT]
> **ウィジェット順序の不変原則 (Widget Ordering Invariance)**
> ComfyUI はワークフロー JSON 内の `widgets_values` 配列のインデックスと、ノードの `INPUT_TYPES` で定義されたウィジェットの順番を1対1でマッピングする。
> - v1.4.0 にて設定順序を洗練（最上段プリセット → 光学/フォント → 日付 → レイアウト）し、v1.6.0 にて日付ブロックに `show_time` を統合。公式ワークフローも同期更新済み。
> - **以降のバージョンアップにおいて、既存ノードの `required` の先頭や中間に新しい引数を挿入すると、ユーザーの既存ワークフロー設定値がズレて「無効な入力」「範囲外エラー」を引き起こすため、新引数の追加時は公式ワークフローの同期およびオプショナル設計に留意すること。**

---

## 4. テスト・検証コマンド

ComfyUI 本体の仮想環境 Python を使って、単体で高速に自動テストおよび各種検証スクリプトを実行する：

```powershell
# 単体テストの実行（全11件、サイズ正規化テスト含む）
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" -m unittest discover -s "C:\Users\coffe\Documents\FilmDateStamp\tests"

# テストボード画像の生成 (assets/prototype_test.png)
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" "C:\Users\coffe\Documents\FilmDateStamp\scripts\prototype_render.py"

# フォント別比較レポート画像の生成 (assets/font_comparison_report_v2.png)
& "C:\Users\coffe\Documents\ComfyUI\.venv\Scripts\python.exe" "C:\Users\coffe\Documents\FilmDateStamp\scripts\generate_font_report.py"
```
