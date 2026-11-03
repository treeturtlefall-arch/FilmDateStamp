# FilmDateStamp SPEC.md — 光学物理仕様・設計書

フィルム写真の日付焼き付け（クォーツデート / デートバック機能）の光学物理特性を再現するための詳細仕様書。

---

## 1. 光学物理モデル (Optical Burn-in Model v2.0)

フィルムカメラの日付モジュールは、微小な発光ダイオード（LED）またはランプから発せられた光線束がレンズアレイを介してフィルム裏面/表面に投射されることで感光乳剤を直接露光する。

v2.0 では単なる 3 色レイヤーの重ね合わせを排し、**「距離変換によるセグメント内 LED 輝度尾根」＋「多重スケール点拡がり関数（PSF）」＋「H&D 非線形分光感光飽和」＋「3 階層の有機的ゆらぎ（Macro/Meso/Micro）」＋「リニア空間乳剤感光余力（Headroom）合成」** による物理エミュレーションを採用。

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

### 2.1 フォント方式（全7フォント）

| 方式 | 特徴 | 適用年代・カメラ | アポストロフィ |
|---|---|---|---|
| **`DSEG7_Classic (7-Segment)`** | 直立型の7セグLED。 | 一般的なクォーツデートバック、デジタル表示 | 公式グリフ移植済み |
| **`DSEG7_Italic (7-Segment)`** | 往年の名機に見られる11.5度傾斜の公式イタリック7セグ。 | Canon Autoboy, Nikon L35AF, Olympus μ等 | 公式グリフ移植済み |
| **`DSEG14_Classic (14-Segment)`** | 高級オーディオや車載機器調の14セグLED。 | 高級ユニット・プロ機器 | 標準対応 |
| **`DSEG14_Italic (14-Segment)`** | 傾斜14セグLED。 | 90年代ハイテクコンパクト機 | 標準対応 |
| **`VT323 (Dot Matrix)`** | 極小発光ドット群（縦長）。 | 「写ルンです」等の使い捨てカメラ | 標準対応 |
| **`Silkscreen (Fine Dot)`** | 引き締まった正方形極小ドット（8px調）。 | 写ルンです以外のコンパクト機、業務用タイムコード | 標準対応 |
| **`ShareTechMono (LCD Digital)`** | 端正な等幅液晶フォント。 | 90〜2000年代初期コンデジ、カシオG-SHOCK | 標準対応 |

### 2.2 視覚サイズ自動正規化モデル (Visual Size Normalization)

フォントごとのEM枠（仮想ボディ）やグリフ比率の差異を自動吸収し、`font_scale` を固定したままでも同一の視覚占有面積・高さを保つアルゴリズム：

基準文字列 $S_{ref} = \text{"88 88 88"}$ に対する各フォントの描画矩形 $(W_{font}, H_{font})$ と、理想ターゲットサイズ $(W_{target}=360.0, H_{target}=65.0)$ より：

$$k_{norm} = \left(\frac{W_{target}}{W_{font}}\right)^{0.75} \times \left(\frac{H_{target}}{H_{font}}\right)^{0.25}$$

- 有効フォントサイズ: $S_{effective} = \text{round}(S_{base} \times k_{norm})$
- 実点灯ピクセル外接矩形クロップ（Tight Bounding Box Alignment）により、フォント固有のアセンダ／ディセンダ余白を完全排除し、四隅マージン位置をピクセル単位で完全一致させる。

### 2.3 日付フォーマット記法と時刻制御 (`show_time`)

| フォーマット | 出力例 (show_time=False) | 出力例 (show_time=True) | 用途・地域 |
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
  - `show_time`（BOOLEAN）を True/False で切り替えるだけで、どの日付フォーマットであっても時刻（`HH:MM`）の付加・非表示をワンクリックで制御。
  - `custom` モード時は入力文字列に時刻が含まれていれば自動トリム/表示維持し、未入力時は自動補完。
  - `current_date`, `random_vintage` では生成日時に応じた時分が連動。
- **日付入力モード (`date_mode`)**:
  - `custom`: 任意の文字列（例: `'98 12 24'`）
  - `current_date`: ComfyUI実行時の現在日時を自動変換
  - `random_vintage`: 1985〜2005年のランダムな過去日時を自動生成（エモい写真生成に最適！）

### 2.4 配置とマージン

- デフォルト位置: **右下（Bottom-Right）**
- マージン計算: 写真の短辺 $S = \min(W, H)$ を基準とする。
  - 右マージン: $W - \text{margin}_x$ （短辺の約 4%〜6% 内側）
  - 下マージン: $H - \text{margin}_y$ （短辺の約 3%〜5% 内側）
- フォントサイズ: 短辺の約 2.5%〜4.0%（写真サイズに対して過大にならず、本物のサイズ感を維持）。

---

## 3. カラーパレット定義

| プリセット名 | コア色 (RGB) | 主発光色 (RGB) | ハレーション色 (RGB) | 解説 |
|---|---|---|---|---|
| **Amber Classic (王道アンバー)** | `(255, 255, 210)` | `(255, 130, 20)` | `(240, 45, 0)` | 90年代フィルムカメラの黄金色・最も親しみのあるオレンジ |
| **Quartz Red (レトロレッド)** | `(255, 230, 220)` | `(255, 40, 20)` | `(200, 10, 0)` | 80年代初期の初期型クォーツデート。純赤に近い発光 |
| **Fuji Orange (写ルンですオレンジ)** | `(255, 250, 190)` | `(255, 110, 10)` | `(250, 60, 10)` | 使い捨てカメラ特有の少し黄みがかった鮮烈なオレンジ |
| **Golden Yellow (ゴールデン)** | `(255, 255, 240)` | `(255, 185, 30)` | `(240, 110, 0)` | 2000年代前後のコンパクト機に見られる黄みの強い発光 |
| **Cyber Green (グリーンLED)** | `(230, 255, 230)` | `(40, 255, 80)` | `(0, 180, 40)` | 一部の特殊機器・ミリタリー・業務用カメラの日付 |

---

## 4. スタイル一括プリセット定義 (Style Presets)

カメラの固有名詞を排し、地域・文化・時代背景を想起させる洗練されたプリセット体系：

| プリセット名 | フォント | カラー | 日付フォーマット | show_time | core_glow | halation | 特徴・世界観 |
|---|---|---|---|---|---|---|---|
| **`Japanese Tokyo 90s`** | DSEG7_Italic | Amber Classic | `'YY MM DD` | False | 1.00 | 1.00 | 90年代日本の街角・日常スナップ（王道アンバー） |
| **`Japanese Snap (Disposable)`** | VT323 | Fuji Orange | `'YY MM DD` | True | 0.50 | 1.00 | 写ルンです風・縦長ドット・時分併記 |
| **`American West Coast`** | DSEG7_Italic | Golden Yellow | `MM DD 'YY` | False | 0.85 | 1.00 | 90年代西海岸・ロードトリップ（月日年順） |
| **`American 80s (Red Quartz)`** | DSEG7_Classic | Quartz Red | `MM DD 'YY` | False | 1.00 | 1.30 | 80年代モーテル・ホームビデオ・赤色LED |
| **`European Classic (Paris/Berlin)`** | DSEG7_Classic | Amber Classic | `DD.MM.YY` | False | 0.70 | 0.80 | 欧州の石畳・上品で控えめな露光（ピリオド区切り） |
| **`Hong Kong Neon (90s Cinema)`** | DSEG14_Italic | Cyber Green | `'YY MM DD` | False | 1.10 | 1.60 | 90年代香港ネオン映画調・サイバーグリーン |
| **`Y2K Digicam (Early 2000s)`** | ShareTechMono | Golden Yellow | `'YY MM DD` | True | 0.60 | 0.90 | 2000年代初頭の初期コンデジLCD液晶 |
| **`Compact Fine Dot (Minimal)`** | Silkscreen | Fuji Orange | `'YY MM DD` | True | 0.40 | 0.90 | 超高精細スクエアドットマトリクス |
| **`Custom`** | 任意 | 任意 | 任意 | 任意 | 任意 | 任意 | 各ウィジェットの手動設定をそのまま使用 |

---

## 5. パラメータ設計・UI連携（ComfyUI ノード用）

最上段に `style_preset` を配置し、その直下に光学・フォント設定、続いて日付設定、レイアウト設定という直感的な階層構造を採用。
同梱のフロントエンド拡張（`web/js/film_date_stamp.js`）により、**プリセット選択時に各パラメータが自動同期され、スライダーや項目を手動で変更すると自動的に「Custom」へ切り替わる双方向連携**を実現。

```python
{
    "required": {
        "image": ("IMAGE",),
        "style_preset": (list(STYLE_PRESETS.keys()), {"default": "Custom"}),
        # 光学・フォント設定 (プリセット連動項目)
        "font_type": ["DSEG7_Classic (7-Segment)", "DSEG7_Italic (7-Segment)", "DSEG14_Classic (14-Segment)", "DSEG14_Italic (14-Segment)", "VT323 (Dot Matrix)", "Silkscreen (Fine Dot)", "ShareTechMono (LCD Digital)"],
        "preset_color": ["Amber Classic", "Quartz Red", "Fuji Orange", "Golden Yellow", "Cyber Green"],
        "exposure_intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
        "core_glow": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
        "halation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
        "optical_burn": ("BOOLEAN", {"default": True}),
        # 日付設定
        "date_mode": ["custom", "current_date", "random_vintage"],
        "date_string": ("STRING", {"default": "'98 12 24"}),
        "date_format": ["'YY MM DD", "MM DD 'YY", "DD MM 'YY", "DD.MM.YY", "YY-MM-DD", "YY.MM.DD", "YYYY MM DD", "YYYY-MM-DD"],
        "show_time": ("BOOLEAN", {"default": False}),
        # レイアウト設定
        "position": ["bottom_right", "bottom_left", "top_right", "top_left"],
        "font_scale": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.5, "step": 0.05}),
        "margin_x": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
        "margin_y": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
    },
    "optional": {
        "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
    }
}
```

### 5.1 出力スロット仕様 (Output Types)

```python
RETURN_TYPES = ("IMAGE", "MASK", "STRING")
RETURN_NAMES = ("image", "mask", "date_text")
```

1. **`image` (`IMAGE`)**:
   - フィルム乳剤への光学露光が焼き付けられた画像テンソル `[B, H, W, C]`。
2. **`mask` (`MASK`)**:
   - スタンプ発光領域のアルファマスクテンソル `[B, H, W]` (0.0〜1.0)。
   - コア部分は完全な白（1.0）、ハレーション・グロー外縁は滑らかに減衰。後段での Film Grain 付与や Inpaint マスクとして利用可能。
3. **`date_text` (`STRING`)**:
   - 実際に画像へ焼き付けられた日付・時刻文字列（例: `'98 12 24 18:30`）。
   - `SaveImage` のファイル名プレフィックスやキャプションノードへの受け渡しが可能。
