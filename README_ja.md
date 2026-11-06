<div align="center">

# 🎞️ FilmDateStamp

### フィルム乳剤の光学露光・ハレーション・白飛びを物理再現する ComfyUI カスタムノード

[![Version](https://img.shields.io/badge/version-v1.0.0-ff8c00?style=flat-square)](https://github.com/treeturtlefall-arch/FilmDateStamp/releases)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-2ea44f?style=flat-square)](https://github.com/comfyanonymous/ComfyUI)
[![Python](https://img.shields.io/badge/python-3.9%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Optical Engine](https://img.shields.io/badge/optics-H%26D_Spectrophotometric-e04000?style=flat-square)](#7段階の光学レンダリングパイプライン)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue?style=flat-square)](LICENSE)
[![Fonts: OFL 1.1](https://img.shields.io/badge/fonts-SIL_OFL_1.1-8a2be2?style=flat-square)](fonts/LICENSE-OFL.txt)

**[🇺🇸 English](README.md)** | **[🇯🇵 日本語 (Japanese)](README_ja.md)**

[なぜ「光学感光」なのか？](#-なぜ光学感光optical-burn-inなのか) •
[ハイライト埋もれ再現](#%EF%B8%8F-乳剤感光余力とハイライト埋もれ再現) •
[厳選8フォント](#-厳選8フォントと視覚サイズ自動正規化) •
[12種のスタイルプリセット](#-時代文化世界観を喚起する12種のスタイルプリセット) •
[インストール](#-インストール方法) •
[パラメータ仕様](#%EF%B8%8F-パラメータ仕様)

<br>

![FilmDateStamp Hero Banner](assets/hero_banner.png)

*単なる「文字の貼り付け」からの完全脱却。カメラ背面の微小LEDが感光乳剤層を直接露光・飽和させる物理プロセスをエミュレート。*

</div>

---

## 🔬 なぜ「光学感光（Optical Burn-in）」なのか？

本物のフィルムカメラ（コンパクト機・一眼レフデータバック・写ルンです等）の日付スタンプは、**現像後の写真の上にインクで文字を印刷したものではありません**。カメラ内部のフィルムゲート背面から、極小のLEDや白熱電球がマイクロレンズを介して**未現像の感光乳剤（ハロゲン化銀・色素カプラー）に光子を直接照射（露光）**して焼き付けたものです。

従来のデジタル合成（通常レイヤー合成や単純なガウスぼかし＋スクリーン合成）では「ステッカーを貼ったような違和感」が拭えませんでした。**FilmDateStamp** は、7段階の物理光学モデルによって本物の焼き付き質感を再現します：

| 光学特性 | 従来の文字オーバーレイ | 単純なガウスグロー合成 | **FilmDateStamp（物理光学感光モデル）** |
| :--- | :---: | :---: | :---: |
| **セグメント中心（フィラメント芯）** | ❌ ベタ塗りの単色 | ❌ ぼやけて芯が消失 | ✅ 距離変換尾根による**白飛びホットスポット芯** |
| **色相の空間遷移** | ❌ 単一RGBのまま | ❌ 単色の不透明度フェード | ✅ **H&D分光感光飽和**（`赤` → `橙` → `アンバー` → `クリーム白`） |
| **光散乱（PSF）** | ❌ デジタル特有の鋭利なエッジ | ⚠️ 単一半径の均一ボケ | ✅ **多重スケールPSF**（狭角Mie前方散乱 ＋ 広角ベース裏面反射ハレーション） |
| **高輝度背景での振る舞い** | ❌ 白い空の上でも文字が浮く | ⚠️ 不自然なクリップ | ✅ **リニア乳剤感光余力（Headroom）**（白背景に溶け込んで自然に埋もれる） |
| **アナログの個体差・ゆらぎ** | ❌ 100%均一なデジタル文字 | ❌ 100%均一なボケ | ✅ **3階層の有機的ゆらぎ**（LED素子光量差・圧板密着ムラ・色素雲ちぎれ） |

![Burn-in vs Overlay Comparison](assets/comparison_burnin_vs_overlay.png)

---

## ☀️ 乳剤感光余力とハイライト埋もれ再現

逆光の空や白い壁など、背景がすでに強い光を受けて露出オーバーになっている領域では、フィルム乳剤のハロゲン化銀粒子は **「すでに飽和（感光しきった状態）」** となっており、それ以上デートスタンプの光を受け止める余力（*Emulsion Headroom*）が残っていません。

FilmDateStamp は背景画像をリニア光空間（$sRGB \to \text{Linear}$）へ変換し、画素ごとの未感光キャパシティを算出した上でフィルムの肩特性（Soft Shoulder Roll-off）を適用します：

$$I_{\text{exposed}} = \frac{I_{\text{base}} + L_{\text{stamp}}}{1.0 + \max(0,\, I_{\text{base}} + L_{\text{stamp}} - 1.0) \times k_{\text{shoulder}}}$$

- **暗部・シャドウ上 ($I_{\text{base}} \approx 0$)**: 乳剤の感光余力が100%残っているため、中心の白いフィラメント芯から周囲の赤いハレーションまで鮮烈に焼き付きます。
- **高輝度・白飛び背景上 ($I_{\text{base}} \approx 1$)**: 乳剤がすでに飽和しているため、日付の光が背景の白の中に自然に溶け込み、判別しづらくなる**「実物のフィルム写真ならではのあの現象」**を忠実に再現します。

![Highlight Bleed-Through Demo](assets/highlight_bleedthrough_demo.png)

---

## 🔤 厳選8フォントと視覚サイズ自動正規化

1970〜90年代の名機モジュールを実機採寸レベルでゼロから設計した**自社製TrueTypeフォント4種**、**デジタル液晶等幅1種**、さらに物理感光エンジンを活かした**特殊・空想フォント3種**の計8種を厳選収録（すべて **SIL Open Font License 1.1** 準拠）。

![厳選8フォント 光学感光マクロ標本](assets/font_comparison_report_v2.png)

| フォント選択肢 (`font_type`) | 区分 | 幾何学・光学設計仕様 | 代表年代・モチーフ実機／世界観 |
| :--- | :--- | :--- | :--- |
| **`FDS_Mechanical_70s (70s Mechanical)`** | ★自社製実機準拠 | DIN 1451 / JIS工業彫刻文字準拠、カプセル型`0`、カギ鼻`1`、傾斜ダッシュ`'` | **1970年代機械式ダイヤル活字**: Canon Canodate E (1970), Datematic (1974), Data Back A |
| **`FDS7_Strict_Compact (80s -7°)`** | ★自社製実機準拠 | 諏訪精工舎モジュール準拠（スリム比率 $W/H=0.50$, **前傾 $-7.0^\circ$**）、上部浮遊ドット`'` | **1980〜90年代コンパクト機黄金期**: Canon Autoboy, Nikon L35AD（ピカイチ）, Olympus AF-10 |
| **`FDS7_Strict_SLR (80s 0°)`** | ★自社製実機準拠 | 一眼レフデータバック直立7セグ（比率 $W/H=0.50$, **直立 $0.0^\circ$**）、上部浮遊ドット`'` | **1980年代一眼レフデータバック**: Nikon MF-12 / MF-14 / MF-16, Olympus Recordata |
| **`FDS_Dot_Strict (90s Dot Matrix)`** | ★自社製実機準拠 | $5\times7$グリッド縦長カプセルドット（$65\times80$）、中空`0`、斜め2点アポストロフィ`'` | **1990年代写ルンです・高級コンパクト**: 富士フイルム 写ルンです、Cardia/Tiara、Ricoh GR1 |
| **`ShareTechMono (LCD Digital)`** | デジタル液晶 | 端正な等幅デジタル液晶プロポーション | **90年代末〜2000年代初期コンデジ**: 初期CCDデジタルカメラ、カシオ G-SHOCK |
| **`Michroma (Cyber Telemetry)`** | 空想・SF HUD | 超ワイド幾何学・扁平ユーロスタイル | **80s-90s宇宙探査・SF映画調**: 惑星探査機テレメトリ、『ブレードランナー』等の光学HUD |
| **`MochiyPopOne (Y2K Pop)`** | 空想・Kawaii | お餅のように角が丸く膨らんだ極太ポップ丸文字 | **平成レトロファンシー**: 平成初期の限定トイカメラ、プリクラ電飾ネオン露光 |
| **`EagleLake (Arcane Script)`** | 空想・魔導書 | 生々しい毛筆・羽根ペンの太細と掠れを持つ古文書筆記体 | **魔導・ダークファンタジー**: 錬金術師の野帳、禁断の魔導書、SCP極秘オブジェクト記録 |

> [!TIP]
> **視覚サイズ自動正規化（Visual Size Normalization）**: フォントごとに異なる内部EM枠や上下余白の差を自動吸収し、さらに**実点灯ピクセルの外接矩形でタイトクロップ**して配置します。`font_scale` や `margin` を一切触ることなく、8種類のどのフォントに切り替えても同じ視覚サイズ・同じ四隅マージン位置にピタリと揃います。

---

## 🎨 時代・文化・世界観を喚起する12種のスタイルプリセット

ノード最上段の **`style_preset`** ドロップダウンを選ぶだけで、フォント・発光スペクトル・露光強度・コアの白飛び・ハレーション・地域別の日付フォーマットが一括で自動セットされます。

![プリセット・ショーケース](assets/presets_showcase_ja.png)

### 📸 実機・時代再現プリセット（9種）

| スタイルプリセット名 | 使用フォント | 発光スペクトル | 日付・時刻構成 | 世界観・時代背景 |
| :--- | :--- | :--- | :--- | :--- |
| **`Japanese Tokyo 90s`** | `FDS7_Strict_Compact` (-7°) | `Amber Classic` | `'YY MM DD` | 90年代日本の街角・日常スナップ。最も親しみ深い王道アンバー発光 |
| **`Japanese Snap (Disposable)`** | `FDS_Dot_Strict` (5×7 Dot) | `Fuji Orange` | `'YY MM DD HH:MM` | 「写ルンです」特有の鮮やかなオレンジ5×7カプセルドット＋時分併記 |
| **`American West Coast`** | `FDS7_Strict_Compact` (-7°) | `Golden Yellow` | `MM DD 'YY` | 90年代アメリカ西海岸のロードトリップ。北米式の月・日・年順（`MM DD 'YY`） |
| **`American 80s (Red Quartz)`** | `FDS7_Strict_SLR` (0°) | `Quartz Red` | `MM DD 'YY` | 80年代アメリカのモーテルや一眼レフデータバックの鮮烈な赤色LED |
| **`European Classic (Paris/Berlin)`** | `FDS7_Strict_SLR` (0°) | `Amber Classic` | `DD.MM.YY` | 欧州の石畳に似合う上品で控えめな露光。ピリオド区切り日・月・年順 |
| **`Y2K Digicam (Early 2000s)`** | `ShareTechMono` (LCD) | `Golden Yellow` | `'YY MM DD HH:MM` | 2000年代初頭の初期コンデジLCD液晶タイムスタンプ |
| **`Compact Fine Dot (Minimal)`** | `FDS_Dot_Strict` (5×7 Dot) | `Fuji Orange` | `'YY MM DD HH:MM` | 90年代高級チタンコンパクト機の繊細でシャープな微細カプセルドット |
| **`Monochrome 70s (Canodate E)`** | `FDS_Mechanical_70s` | `Paper White` | `YY MM DD` | 1970年代の白黒銀塩プリント。印画紙の白抜き文字を再現 |
| **`Vintage 70s Color (Datematic)`** | `FDS_Mechanical_70s` | `Bulb Warm Ivory` | `'YY MM DD` | 1970年代の小型白熱電球（タングステン球）による温かいアイボリー露光 |

### ✨ 空想・特殊表現プリセット（3種）

| スタイルプリセット名 | 使用フォント | 発光スペクトル | 日付・時刻構成 | 世界観・時代背景 |
| :--- | :--- | :--- | :--- | :--- |
| **`Cyber Telemetry (80s Sci-Fi)`** | `Michroma` | `Cyber Green` | `'YY MM DD HH:MM:SS` | 80s-90s宇宙探査機・SF映画調の緑色レーザーHUD（自動で秒 `:SS` まで刻印） |
| **`Y2K Pop (Heisei Fancy)`** | `MochiyPopOne` | `Neo Pink` | `'YY MM DD HH:MM` | 平成レトロのお餅丸文字とプリクラ電飾のような甘いネオピンクMie散乱 |
| **`Arcane Occult (Crimson Script)`** | `EagleLake` | `Crimson Red` | `'YY MM DD` | 錬金術師の野帳・古文書に浮かび上がる深紅の呪印ハレーション |

---

## 🧬 7段階の光学レンダリングパイプライン

<details>
<summary><b>クリックして物理レンダリングエンジンの内部構造を表示</b></summary>

<br>

```text
                        [ 露光エネルギー E 分布 ]
                     高輝度ホットスポット尾根 (Core Ridge)
                                 ┌───────────┐
                                 │           │
                      乳剤層内狭角散乱 (Mie Scattering Body)
                         ┌───────┴───────────┴───────┐
                         │                           │
               ベース裏面・圧板反射ハレーション (Wide Halation Wave)
               ┌─────────┴───────────────────────────┴─────────┐
            ───┴───────────────────────────────────────────────┴─── (フィルム乳剤層)
```

1. **Step 1 — LED発光尾根（Distance Transform Ridge & Blooming）**: 文字ストローク内部のユークリッド距離変換によってセグメント中心線（尾根）を抽出し、LEDチップ直上のホットスポットとスリット回折による角の丸まりを生成します。
2. **Step 2 — ① Macroゆらぎ（素子別光量ジッター）**: セグメントやドットごとの製造個体差（±10%前後）および投影レンズの周辺光量落ち・傾斜ムラをシミュレートします。
3. **Step 3 — 多重スケール異方性PSF散乱**: 狭角前方散乱（アンバーボディ）、ベース裏面・圧板反射による広角ハレーション、超広角ベールグレアを重み付け合成します。
4. **Step 4 — ② Mesoゆらぎ（圧板密着ムラ & ドメインワープ）**: フィルム裏蓋圧板のわずかな浮き・たわみを雲状ノイズと変位場（ドメインワープ）でモデル化し、ハレーション外縁に有機的な波打ちを与えます。
5. **Step 5 — ③ Microゆらぎ（銀塩グレイン & 色素雲クラッピング）**: 銀塩粒子の感光閾値ゆらぎを注入。高露光の中心部は滑らかに保ちつつ、ハレーションの淡い裾野でのみ色素雲（Dye Cloud）によって輪郭がちぎれる物理特性を再現します。
6. **Step 6 — H&D分光感光飽和モデル（Spectrophotometric Bleaching）**: 露光エネルギー $E$ に対して $I = 1.0 - \exp(-E^\gamma)$ の非線形分光応答を計算。微光部では長波長（赤）のみが立ち上がり、中露光で緑が加わりアンバーへ、強露光の中心芯では青まで飽和してクリームホワイトへと連続的に色飛び（ブリーチ）します。
7. **Step 7 — リニア空間・乳剤感光余力（Emulsion Headroom）合成**: 背景写真をリニアRGBへ変換し、未感光キャパシティ（$1.0 - L_{\text{base}}^{1.35} \times 0.72$）に応じた加算露光とフィルム肩特性ロールオフを経てsRGBへ復元します。

</details>

---

## 📦 インストール方法

### 方法 1: ComfyUI-Manager（推奨）
**ComfyUI-Manager** を開き、**`Film Date Stamp`**（または `FilmDateStamp`）で検索して **Install** をクリックします。

### 方法 2: Comfy-CLI
```bash
comfy node install comfyui-film-date-stamp
```

### 方法 3: 手動 Git Clone
ComfyUI の `custom_nodes` ディレクトリ内で本リポジトリをクローンします：
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/treeturtlefall-arch/FilmDateStamp.git
```
*(追加のpipパッケージインストールは不要です。ComfyUI標準の `torch`, `numpy`, `Pillow` のみで高速に動作します。)*

---

## 🚀 クイックスタート ＆ ワークフロー連携

1. **ノードの追加**: キャンバス上で右クリック → `image` → `film` → **`Film Date Stamp (Optical Burn-in)`** を選択。
2. **プリセット選択**: 最上段の **`style_preset`** から好みの時代・スタイルを選択。
3. **自由な微調整**: いずれかのスライダーや設定を手動で動かすと、フロントエンド拡張によって自動的に `style_preset` が `Custom` に切り替わり、そのまま微調整できます。
4. **サンプルワークフロー**: [`workflows/film_date_stamp_workflow.json`](workflows/film_date_stamp_workflow.json) を ComfyUI 画面へドラッグ＆ドロップするとすぐに試せます。

### 💡 直感的な日付入力 (`date_string`)
複雑なモード切替スイッチを廃し、`date_string` への入力内容だけで直感的に動作します：
- **任意の文字列を直接入力**: `'98 12 24` や `'95 08 15 14:30` のように入力した文字がそのまま焼き付けられます。
- **現在日時の自動取得**: `"auto"`、`"today"`、または `"now"` と入力すると、実行時のシステム現在日時を `date_format` と `show_time` に従って自動生成します。
- **ヴィンテージ年代ランダム生成**: `"random"` と入力すると、1985〜2005年のランダムな日時を `seed` による再現性付きで自動生成します。

### 🔌 3つの出力スロットの活用法
- **`image` (`IMAGE`)**: 日付スタンプが光学感光・焼き付け合成された完成画像テンソル `[B, H, W, C]`。
- **`mask` (`MASK`)**: スタンプ発光領域の高精度アルファマスク `[B, H, W]`（文字コア部 `1.0`、ハレーション裾野は滑らかな減衰グラデーション）。後段の **Film Grain ノード**に繋いで「発光した色素雲にだけ粒子を乗せる」処理や、**Inpaint ノード**での日付消去テストに最適です。
- **`date_text` (`STRING`)**: 実際に描画された日付・時刻文字列（例: `'98 12 24 18:30`）。`SaveImage` ノードのファイル名プレフィックスやキャプション生成ノードへそのまま接続できます。

---

## ⚙️ パラメータ仕様

| パラメータ名 | 型 | デフォルト | 範囲 / 選択肢 | 説明 |
| :--- | :--- | :--- | :--- | :--- |
| **`style_preset`** | `COMBO` | `Custom` | `Custom` + 全12種 | 最上段のマスタープリセット。選択すると下部パラメータを一括自動設定 |
| **`font_type`** | `COMBO` | `FDS7_Strict_Compact (80s -7°)` | 厳選8フォント | 発光素子のタイポグラフィ（視覚サイズ自動正規化対応） |
| **`preset_color`** | `COMBO` | `Amber Classic` | 全9パレット | 発光スペクトル（実機再現6種 ＋ 特殊・空想3種） |
| **`exposure_intensity`** | `FLOAT` | `1.00` | `0.00` 〜 `2.00` | フィルム乳剤へ照射する露光エネルギー全体の強度 |
| **`core_glow`** | `FLOAT` | `1.00` | `0.00` 〜 `2.00` | セグメント中心の白飛びフィラメント芯（Hotspot Ridge）の強度 |
| **`halation`** | `FLOAT` | `1.00` | `0.00` 〜 `3.00` | 乳剤層・ベース裏面反射による赤色ハレーションの広がりと強さ |
| **`date_string`** | `STRING` | `'98 12 24` | 直接入力 / `"auto"` / `"random"` | 焼き付ける文字列、または動的生成キーワード（`"auto"`, `"today"`, `"random"`） |
| **`date_format`** | `COMBO` | `'YY MM DD` | 全9フォーマット | 自動日時生成時およびプリセット適用時の年月日フォーマット記法 |
| **`show_time`** | `BOOLEAN` | `False` | `True` / `False` | 時刻（`HH:MM`、Cyber Telemetry時は `HH:MM:SS`）の併記トグル |
| **`position`** | `COMBO` | `bottom_right` | `bottom_right`, `bottom_left`, `top_right`, `top_left` | スタンプの配置コーナー（点灯ピクセル外接矩形による精密配置） |
| **`font_scale`** | `FLOAT` | `1.00` | `0.50` 〜 `2.50` | 画像短辺に対する文字サイズ倍率（基準 $4.0\%$） |
| **`margin`** | `FLOAT` | `1.00` | `0.00` 〜 `3.00` | 画面端からの等方マージン倍率（縦横比 約5:4） |
| **`irregularity`** *(任意)* | `FLOAT` | `1.00` | `0.00` 〜 `2.00` | 3階層の有機的ゆらぎ強度（`0.0`=均一、`1.0`=実機相当、`2.0`=強調） |
| **`seed`** *(任意)* | `INT` | `0` | `0` 〜 `2^64-1` | `"random"` 日時生成および有機的ゆらぎパターンの再現用シード |

<details>
<summary><b>🌈 発光スペクトルパレット一覧 ＆ 日付フォーマット記法一覧（クリックで展開）</b></summary>

### 発光スペクトルパレット (`preset_color`)

| パレット名 | コア色 (RGB) | 主発光色 (RGB) | ハレーション色 (RGB) | 特徴・モチーフ |
| :--- | :---: | :---: | :---: | :--- |
| **`Amber Classic`** | `(255, 255, 210)` | `(255, 130, 20)` | `(240, 45, 0)` | 90年代コンパクトカメラの黄金アンバー（王道標準） |
| **`Quartz Red`** | `(255, 230, 220)` | `(255, 40, 20)` | `(200, 10, 0)` | 80年代初期の一眼レフデータバックに見られる深紅の赤色LED |
| **`Fuji Orange`** | `(255, 250, 190)` | `(255, 115, 20)` | `(250, 60, 10)` | 「写ルンです」特有の鮮烈で温かみのあるオレンジ発光 |
| **`Golden Yellow`** | `(255, 255, 240)` | `(255, 185, 30)` | `(240, 110, 0)` | 90年代末〜2000年代前後のコンパクト機に見られる黄みの強い発光 |
| **`Bulb Warm Ivory`** | `(255, 250, 232)` | `(255, 242, 204)` | `(255, 214, 138)` | 1970年代電球式データバック（Datematic等）の白熱球ウォームアイボリー |
| **`Paper White (Monochrome)`** | `(248, 246, 240)` | `(245, 242, 234)` | `(235, 232, 224)` | 1970年代銀塩モノクロ（Canodate E等）の印画紙白抜き文字 |
| **`Cyber Green`** *(特殊・空想)* | `(230, 255, 230)` | `(40, 255, 80)` | `(0, 180, 40)` | 宇宙探査機テレメトリ・90年代香港映画ネオン風の緑色レーザー感光 |
| **`Neo Pink`** *(特殊・空想)* | `(255, 235, 248)` | `(255, 70, 170)` | `(230, 25, 115)` | 平成トイカメラ・プリクラ電飾の甘く広がるネオピンクMie散乱 |
| **`Crimson Red`** *(特殊・空想)* | `(255, 235, 225)` | `(235, 25, 35)` | `(185, 5, 15)` | 禁断の魔導書・血の呪印・SCP極秘記録の禍々しい深紅ハレーション |

### 日付フォーマット記法 (`date_format`)

| フォーマット記法 | 出力例 (`show_time=False`) | 出力例 (`show_time=True`) | 主な用途・地域慣習 |
| :--- | :--- | :--- | :--- |
| **`'YY MM DD`** | `'98 12 24` | `'98 12 24 18:30` | 日本・東アジア標準（最も象徴的なクォーツデート表記） |
| **`YY MM DD`** | `98 12 24` | `98 12 24 18:30` | アポストロフィなし（1970年代 Canodate E 等） |
| **`MM DD 'YY`** | `12 24 '98` | `12 24 '98 18:30` | 北米（US）標準の月・日・年順 |
| **`DD MM 'YY`** | `24 12 '98` | `24 12 '98 18:30` | 英国・欧州標準の日・月・年順 |
| **`DD.MM.YY`** | `24.12.98` | `24.12.98 18:30` | ドイツ・大陸欧州伝統のピリオド区切り |
| **`YY-MM-DD`** | `98-12-24` | `98-12-24 18:30` | ハイフン区切り |
| **`YY.MM.DD`** | `98.12.24` | `98.12.24 18:30` | ドット区切り |
| **`YYYY MM DD`** | `1998 12 24` | `1998 12 24 18:30` | 4桁西暦（2000年問題対応モジュール） |
| **`YYYY-MM-DD`** | `1998-12-24` | `1998-12-24 18:30` | ISO 8601 4桁西暦ハイフン区切り |

</details>

---

## 📄 ライセンス

- **ソースコード**: [MIT License](LICENSE)
- **同梱フォント (`fonts/*.ttf`)**: [SIL Open Font License 1.1](fonts/LICENSE-OFL.txt)（自社製の実機幾何学準拠フォント `FDS*` 4種および同梱OFLフォント4種すべてを含む）
