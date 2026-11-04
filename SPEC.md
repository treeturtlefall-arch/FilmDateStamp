# FilmDateStamp SPEC.md — 光学物理仕様・設計書

フィルム写真の日付焼き付け（クォーツデート / デートバック機能）の光学物理特性を再現するための詳細仕様書。

---

## 1. 光学物理モデル (Optical Burn-in Model)

フィルムカメラの日付モジュールは、微小な発光ダイオード（LED）またはランプから発せられた光線束がレンズアレイを介してフィルム裏面/表面に投射されることで感光乳剤を直接露光する。

単なる 3 色レイヤーの重ね合わせや安価なスクリーン合成を排し、**「距離変換によるセグメント内 LED 輝度尾根」＋「多重スケール点拡がり関数（PSF）」＋「H&D 非線形分光感光飽和」＋「3 階層の有機的ゆらぎ（Macro/Meso/Micro）」＋「リニア空間乳剤感光余力（Headroom）合成」** による物理エミュレーションを常時適用する。

```
                       [ 露光エネルギー E 分布 ]
                    高輝度ホットスポット尾根 (Core Ridge)
                        ┌───────────┐
                        │           │
                 乳剤層内狭角散乱 (Mie Scattering Body)
               ┌────────┴───────────┴────────┐
               │                             │
          ベース裏面・圧板反射ハレーション (Wide Halation Wave)
      ┌────────┴─────────────────────────────┴────────┐
   ───┴───────────────────────────────────────────────┴─── (フィルム乳剤層)
```

### 1.1 光学レンダリングパイプライン

1. **Step 1: LED 発光尾根 (Distance Transform Ridge & Hotspot)**
   - 文字ストローク内部の近似ユークリッド距離変換により、各セグメントの中心線（尾根）を抽出。
   - LED チップ直上のホットスポットと光学スリット回折による微細な角の丸まり（Blooming）を再現。
2. **Step 2: ① Macro ゆらぎ (Character & Segment Power Jitter)**
   - LED 素子ごとの個体差（±10% 前後）およびデート投影レンズの周辺光量落ち・傾斜による光量ムラを乗算。
3. **Step 3: 多重スケール PSF 散乱 (Point Spread Function)**
   - 狭角前方散乱（アンバーボディの主骨格）から、ベース裏面・圧板反射による広角ハレーション、超広角ベールグレアまで、複数スケールの PSF を重み付け合成。
   - フィルム圧板の浮き・たわみに応じた楕円（異方性）散乱とサブピクセルオフセットを適用。
4. **Step 4: ② Meso ゆらぎ (Pressure Plate Anisotropy & Dye Cloud Warping)**
   - 低周波の雲状変調ノイズ（圧板密着ムラ）を乗算。
   - ドメインワープ（変位場）によるハレーション外縁の非対称な波打ち・歪みを生成。
5. **Step 5: ③ Micro ゆらぎ (Silver Halide Grain & Dye Cloud Edge Clumping)**
   - 銀塩粒子（フィルムグレイン）の感光閾値ゆらぎ。
   - 高露光部（飽和領域）では滑らかになり、ハレーションの淡い裾野でのみ色素雲の塊によって輪郭がちぎれる物理特性を再現。
6. **Step 6: H&D 分光感光モデル (Spectrophotometric Bleaching)**
   - 露光エネルギー $E$ に応じた非線形感光レスポンス $I = 1.0 - \exp(-E^\gamma)$。
   - 裾野の微光では長波長（赤）のみが立ち上がり、中エネルギーで緑が加わりアンバーへ、強露光のコアでは青まで飽和して「白〜クリームイエロー」へと連続的・有機的に色飛び（ブリーチ）する。
7. **Step 7: リニア空間・乳剤感光余力（Emulsion Headroom）合成**
   - リニア空間（$sRGB \to Linear$）にて背景写真の輝度からフィルム乳剤の未感光キャパシティ（$Headroom = 1.0 - L_{base}^{1.35} \times 0.72$）を算出。
   - 背景が明るいハイライト部ではデート光が自然に溶け込んで埋もれる本物の白飛び現象をシミュレートし、フィルム肩特性（Soft Shoulder Roll-off）を経て sRGB へ復元。

$$I_{exposed} = \frac{I_{base} + L_{stamp}}{1.0 + \max(0, I_{base} + L_{stamp} - 1.0) \times k_{shoulder}}$$

- **背景が暗い場合**: $I_{base} \approx 0$ のため、露光光 $L_{stamp}$ が鮮明に発光。
- **背景が明るい場合**: $I_{base} \approx 1.0$ のため、加算しても変化が微小となり、日付が白背景の中に自然に埋もれて消えかかる（リアルな白飛び現象）。

---

## 2. タイポグラフィと配置仕様

### 2.1 厳選フォント構成（全8種）

自社製の実機幾何学ゼロスクラッチ生成TrueType（4種）、液晶等幅（1種）に加え、物理感光シミュレーションを活かした空想・飛び道具フォント（3種、すべてOFL準拠）を収録。

| 方式 | 特徴 | 適用年代・代表カメラ／世界観 | アポストロフィ |
|---|---|---|---|
| **`FDS7_Strict_Compact (80s -7°)`** | **【黄金期標準】** 諏訪精工舎モジュール実機幾何学完全準拠（$W/H=0.50$, 前傾 $-7.0^\circ$, 厚さ $10\%$）。 | Canon Autoboy, Nikon L35AD（ピカイチ）, Olympus AF-10等 | 上部浮遊ドット（実機完全一致） |
| **`FDS7_Strict_SLR (80s 0°)`** | **【一眼レフ標準】** 実機幾何学完全準拠の直立型（$W/H=0.50$, 直立 $0.0^\circ$, 厚さ $10\%$）。 | Nikon MF-12/14/16, Olympus Recordata, Minolta Data Back G等 | 上部浮遊ドット（実機完全一致） |
| **`FDS_Dot_Strict (90s Dot Matrix)`** | **【写ルンです・90s実機標準】** 5×7グリッド・縦長カプセルドット（$65\times 80$, $W/H\approx 0.537$, 斜線なし中空0）。 | 写ルンですデート、富士フイルム Cardia/Tiara、京セラ T-Proof、リコー GR1 | 斜め2ドット（実機完全一致） |
| **`FDS_Mechanical_70s (70s Mechanical)`** | **【1970s機械式活字標準】** DIN 1451/JIS工業彫刻文字準拠（等幅620u, ステム96u, 角丸R=20u, カプセル0, カギ鼻1）。 | 世界初Canon Canodate E（1970）、Canon Datematic（1974）、Canon Data Back A | 傾斜ダッシュ（実機完全一致） |
| **`ShareTechMono (LCD Digital)`** | 端正な等幅液晶フォント。 | 90〜2000年代初期コンデジ、カシオG-SHOCK | 等幅液晶標準 |
| **`Michroma (Cyber Telemetry)`** | **【空想・サイバー】** 超ワイド幾何学・平べったい横長プロポーション。 | 80s-90s宇宙探査機・SF映画（ブレードランナー等）のテレメトリ記録 | スラッシュ・アポストロフィ |
| **`MochiyPopOne (Y2K Pop)`** | **【空想・Kawaii】** 平成レトロ・お餅のように角が丸く膨らんだ極太ポップ丸文字。 | 平成初期限定発売ファンシーカメラ、プリクラ電飾露光 | 丸型クォート |
| **`EagleLake (Arcane Script)`** | **【空想・魔導】** ケルト・古文書風のインク筆記体。手書きの生々しい太細と掠れ。 | 錬金術師の野帳、禁断の魔導書、SCP極秘記録・血塗られた呪符 | 筆記アポストロフィ |

### 2.2 視覚サイズ自動正規化モデル (Visual Size Normalization)

フォントごとのEM枠（仮想ボディ）やグリフ比率の差異を自動吸収し、`font_scale` を固定したままでも同一の視覚占有面積・高さを保つアルゴリズム：

- 基準フォントサイズ: $S_{base} = \max(10, \text{int}(S \times 0.040 \times \text{font\_scale}))$ （現代のディスプレイ・SNS表示における視認性と写真全体のバランスを両立する黄金比率 $4.0\%$）
- 有効フォントサイズ: $S_{effective} = \text{round}(S_{base} \times k_{norm})$
- 実点灯ピクセル外接矩形クロップ（Tight Bounding Box Alignment）により、フォント固有のアセンダ／ディセンダ余白を完全排除し、四隅マージン位置をピクセル単位で完全一致させる。

### 2.3 直感的な日付入力・生成仕様

`date_mode` による複雑な分岐を廃止し、`date_string` の内容に応じた直感的なパーサーに一本化：

1. **直接入力**: そのまま文字列を入力（例: `'98 12 24`）
2. **`auto` / `today` / `now`**: 実行時の現在日時を `date_format` と `show_time` に従って自動フォーマット（キャッシュ無効化対象）。
3. **`random`**: 1985〜2005年のヴィンテージランダム日時を生成（`seed` による再現性あり）。

| フォーマット記法 (`date_format`) | 出力例 (show_time=False) | 出力例 (show_time=True) | 用途・地域 |
|---|---|---|---|
| `'YY MM DD` | `'98 12 24` | `'98 12 24 18:30` | 日本・アジア標準（最もポピュラー） |
| `MM DD 'YY` | `12 24 '98` | `12 24 '98 18:30` | 北米（US）標準 |
| `DD MM 'YY` | `24 12 '98` | `24 12 '98 18:30` | ヨーロッパ（EU）標準 |
| `DD.MM.YY` | `24.12.98` | `24.12.98 18:30` | ドイツ・欧州伝統ピリオド区切り |
| `YY-MM-DD` | `98-12-24` | `98-12-24 18:30` | ハイフン区切り |
| `YY.MM.DD` | `98.12.24` | `98.12.24 18:30` | ドット区切り |
| `YYYY MM DD` | `1998 12 24` | `1998 12 24 18:30` | 4桁西暦（2000年問題対応型） |
| `YYYY-MM-DD` | `1998-12-24` | `1998-12-24 18:30` | 4桁西暦ハイフン区切り |

- **時刻表示スイッチ (`show_time`)**:
  - `show_time`（BOOLEAN）の True/False で時刻（`HH:MM`）の付加・非表示をワンクリックで制御。
  - 直接入力時、時刻が含まれていれば自動トリム/維持し、未入力時は `"18:30"` を自動補完。

### 2.4 配置とマージン

- デフォルト位置: **右下（Bottom-Right）**
- マージン計算: 写真の短辺 $S = \min(W, H)$ を基準とし、単一の `margin` スケールで縦横比（約 5:4）を維持しながら等方的に余白を制御。

---

## 3. カラーパレット定義

特殊・飛び道具カラー（Cyber Green, Neo Pink, Crimson Red）は選択肢の最後尾に配置。

| プリセット名 | コア色 (RGB) | 主発光色 (RGB) | ハレーション色 (RGB) | 解説 |
|---|---|---|---|---|
| **Amber Classic** | `(255, 255, 210)` | `(255, 130, 20)` | `(240, 45, 0)` | 90年代フィルムカメラの黄金色・最も親しみのある王道アンバー |
| **Quartz Red** | `(255, 230, 220)` | `(255, 40, 20)` | `(200, 10, 0)` | 80年代初期の赤色LEDクォーツデート。鮮烈なレトロレッド |
| **Fuji Orange** | `(255, 250, 190)` | `(255, 115, 20)` | `(250, 60, 10)` | 写ルンです特有の少し黄みがかった鮮烈なオレンジ |
| **Golden Yellow** | `(255, 255, 240)` | `(255, 185, 30)` | `(240, 110, 0)` | 2000年代前後のコンパクト機に見られる黄みの強い発光 |
| **Bulb Warm Ivory** | `(255, 250, 232)` | `(255, 242, 204)` | `(255, 214, 138)` | 1970年代電球式データバック（Datematic）の温かい白熱球色 |
| **Paper White (Monochrome)** | `(248, 246, 240)` | `(245, 242, 234)` | `(235, 232, 224)` | 1970年代銀塩モノクロ（Canodate E）の印画紙白抜き文字 |
| **Cyber Green** | `(230, 255, 230)` | `(40, 255, 80)` | `(0, 180, 40)` | 【特殊・空想】香港映画ネオン・宇宙探査テレメトリ・サイバー感のある緑色発光 |
| **Neo Pink** | `(255, 235, 248)` | `(255, 70, 170)` | `(230, 25, 115)` | 【特殊・空想】平成トイカメラ・プリクラ電飾・甘く広がるマゼンタMie散乱光 |
| **Crimson Red** | `(255, 235, 225)` | `(235, 25, 35)` | `(185, 5, 15)` | 【特殊・空想】禁忌の魔導書・血の呪印・SCP極秘記録の禍々しい深紅 |

---

## 4. スタイル一括プリセット定義 (Style Presets)

実機エミュレート9種に加え、物理感光を活かした空想（Fiction）3種（計12種）を収録。

| プリセット名 | フォント | カラー | 日付フォーマット | show_time | 特徴・世界観 |
|---|---|---|---|---|---|
| **`Japanese Tokyo 90s`** | FDS7_Strict_Compact | Amber Classic | `'YY MM DD` | False | 90年代日本の街角・日常スナップ（王道アンバー） |
| **`Japanese Snap (Disposable)`** | FDS_Dot_Strict | Fuji Orange | `'YY MM DD` | True | 写ルンです風・5×7カプセルドット・時分併記 |
| **`American West Coast`** | FDS7_Strict_Compact | Golden Yellow | `MM DD 'YY` | False | 90年代西海岸・ロードトリップ（月日年順） |
| **`American 80s (Red Quartz)`** | FDS7_Strict_SLR | Quartz Red | `MM DD 'YY` | False | 80年代モーテル・一眼レフ・赤色LED |
| **`European Classic (Paris/Berlin)`** | FDS7_Strict_SLR | Amber Classic | `DD.MM.YY` | False | 欧州の石畳・上品で控えめな露光（ピリオド区切り） |
| **`Y2K Digicam (Early 2000s)`** | ShareTechMono | Golden Yellow | `'YY MM DD` | True | 2000年代初頭の初期コンデジLCD液晶 |
| **`Compact Fine Dot (Minimal)`** | FDS_Dot_Strict | Fuji Orange | `'YY MM DD` | True | 90年代コンパクト機微細カプセルドット |
| **`Monochrome 70s (Canodate E)`** | FDS_Mechanical_70s | Paper White | `YY MM DD` | False | 70年代銀塩モノクロ（機械式彫刻活字） |
| **`Vintage 70s Color (Datematic)`** | FDS_Mechanical_70s | Bulb Warm Ivory | `'YY MM DD` | False | 70年代カラー（電球色ウォームアイボリー） |
| **`Cyber Telemetry (80s Sci-Fi)`** | Michroma | Cyber Green | `'YY MM DD` | True | 80s-90s宇宙探査・SF映画調（超ワイド幾何学HUD） |
| **`Y2K Pop (Heisei Fancy)`** | MochiyPopOne | Neo Pink | `'YY MM DD` | True | 平成トイカメラ・プリクラ電飾（お餅ぷっくり丸文字） |
| **`Arcane Occult (Crimson Script)`** | EagleLake | Crimson Red | `'YY MM DD` | False | 禁断の魔導書・錬金術師の野帳（古文書インク筆記・深紅） |
| **`Custom`** | 任意 | 任意 | 任意 | 任意 | 各ウィジェットの手動設定をそのまま使用 |

---

## 5. ノード定義仕様 (ComfyUI INPUT_TYPES)

```python
{
    "required": {
        "image": ("IMAGE",),
        "style_preset": (list(STYLE_PRESETS.keys()), {"default": "Custom"}),
        # 光学・フォント設定 (プリセット連動項目)
        "font_type": (SUPPORTED_FONTS, {"default": "FDS7_Strict_Compact (80s -7°)"}),
        "preset_color": (list(COLOR_PRESETS.keys()), {"default": "Amber Classic"}),
        "exposure_intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
        "core_glow": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
        "halation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
        # 日付設定 (直接文字列 または "auto" / "today" / "random")
        "date_string": ("STRING", {"default": "'98 12 24"}),
        "date_format": (SUPPORTED_DATE_FORMATS, {"default": "'YY MM DD"}),
        "show_time": ("BOOLEAN", {"default": False}),
        # レイアウト設定
        "position": (SUPPORTED_POSITIONS, {"default": "bottom_right"}),
        "font_scale": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.5, "step": 0.05}),
        "margin": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
    },
    "optional": {
        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
        "irregularity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
    }
}
```

### 5.1 出力スロット仕様

```python
RETURN_TYPES = ("IMAGE", "MASK", "STRING")
RETURN_NAMES = ("image", "mask", "date_text")
```
