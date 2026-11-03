# FilmDateStamp SPEC.md — 光学物理仕様・設計書

フィルム写真の日付焼き付け（クォーツデート / デートバック機能）の光学物理特性を再現するための詳細仕様書。

---

## 1. 光学物理モデル (Optical Burn-in Model)

フィルムカメラの日付モジュールは、微小な発光ダイオード（LED）またはランプから発せられた光線束がレンズアレイを介してフィルム裏面/表面に投射されることで感光乳剤を直接露光する。

この現象を以下の 3 層光路モデルで表現する：

```
                    [ 露光光量分布 ]
           高輝度コア (White / Pale Yellow)
               ┌───────────┐
               │           │
          主発光体 (Amber / Orange)
         ┌─────┴───────────┴─────┐
         │                       │
      ハレーション光散乱 (Deep Red / Orange Glow)
   ┌─────┴───────────────────────┴─────┐
───┴───────────────────────────────────┴─── (フィルム乳剤層)
```

### 1.1 3層レイヤーの光学特性

1. **第1層：コア (White / Pale Yellow Core)**
   - 光源の直中心部。露光量がフィルム乳剤の飽和領域（D-max）に達するため、RGB値が白（255, 255, 230）近くまで飛ぶ。
   - 形状: 文字ストロークの極めてタイトな中心線。ブラー半径極小（`radius = 0.5px〜1.5px`）。
2. **第2層：主発光体 (Amber Body)**
   - LED本来の発光スペクトル。温かみのあるアンバー（琥珀色: `RGB(255, 120, 20)` 付近）。
   - 形状: 文字の骨格全体を覆う。適度なエッジの柔らかさ（`radius = 1.5px〜3.0px`）。
3. **第3層：ハレーション・乳剤散乱 (Film Emulsion Halation)**
   - フィルムのゼラチン乳剤層、フィルムベース、および裏面圧板（プレッシャープレート）の間で赤色波長が内部反射・散乱して発生する光の滲み。
   - 色: 深い赤橙色〜ディープレッド（`RGB(255, 50, 0)` 付近、または長波長側の散乱光）。
   - 形状: 広く柔らかく拡散（`radius = 5.0px〜15.0px`、アルファ減衰曲線）。

### 1.2 露光・合成モデル（Film Saturation Blending）

単なる `alpha_composite`（不透明上書き）はCG感を生む最大の原因。
感光露光の基本式は **加算（Add / Linear Dodge）またはスクリーン（Screen）** をベースとし、フィルムのハイライトロールオフ（肩特性）をシミュレートする。

#### 数式モデル (RGB各チャンネル 0.0〜1.0)
ベース画像 $I_{base}$、露光光 $L_{stamp}$ に対し：

$$I_{out} = 1.0 - (1.0 - I_{base}) \times (1.0 - L_{stamp})$$
（スクリーン合成による感光の基本式）

さらに、強い発光（オーバー露光）時は加算発光 $I_{base} + L_{stamp}$ を適用しつつ、1.0 を超える領域をシネマティック/フィルム風に緩やかにソフトクリップ（Reinhard または ACES風ハイライト圧縮）する：

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
