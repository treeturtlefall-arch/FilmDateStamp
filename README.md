# FilmDateStamp (ComfyUI Custom Node)

フィルム写真の感光乳剤に焼き付けられる「クォーツデート（日付スタンプ）」の光学・物理質感を徹底追及した、ComfyUI専用のカスタムノードパッケージです。

単なる「文字の貼り付け（透過オーバーレイ）」ではなく、**「フィルム乳剤へのLED露光（光の焼き付け）」**を物理的にシミュレートします。

---

## 🌟 主な特徴

1. **光学感光（Optical Burn-in）モデル**
   - フィルム乳剤への光子照射をシミュレート（加算露光 ＋ Reinhardハイライト肩特性ロールオフ）。
   - **ハイライト埋もれ再現**: 背景が明るい／白い写真では、感光乳剤が飽和して日付の光が自然に溶け込んで見えにくくなる「実物の白飛び現象」を忠実に再現。
2. **3層光路モデル（3-Layer Optical Path）**
   - **高輝度コア（Core）**: 中心部の光量が乳剤を完全飽和させる白〜淡黄色の極タイトな芯。
   - **主発光体（Body）**: 琥珀色（アンバー）〜オレンジの鮮やかな発光体。
   - **フィルム内光散乱（Halation）**: 乳剤層・ベース層内で長波長（赤色）が横方向に散乱して滲む赤色の微細グロー。
3. **時代考証と多彩なフォント（全7種）**
   - `DSEG7_Classic / Italic (7-Segment)`: 往年の名機に見られる直立／11.5度傾斜7セグ（公式アポストロフィ移植済みで豆腐になりません）。
   - `DSEG14_Classic / Italic (14-Segment)`: 高級Hi-Fi機器・特殊カメラ調の14セグメントLED。
   - `VT323 (Dot Matrix)`: 「写ルンです」等の温かみのある縦長ドットマトリクス。
   - `Silkscreen (Fine Dot)`: 引き締まった正方形の超高精細ドット（8px調）。
   - `ShareTechMono (LCD Digital)`: 90〜2000年代初期コンデジ・カシオG-SHOCK風液晶等幅。
4. **視覚サイズ自動正規化（Visual Size Normalization）**
   - フォント内部の余白・仮想ボディ比率の差を自動吸収。フォントを切り替えても、同じ `font_scale` で均一な大きさと右下端の正確なマージン位置を維持します。
5. **柔軟な日付生成**
   - `custom`: 自由入力（例: `'98 12 24`）。
   - `current_date`: ComfyUI実行時の現在日時を自動フォーマット。
   - `random_vintage`: 1985〜2005年のランダムな日時を自動生成（エモいオールドフォト生成に最適）。
6. **地域・文化・時代を想起させる新スタイルプリセット**
   - `Japanese Tokyo 90s`: 90年代日本の街角・日常スナップ（'YY MM DD / 7セグ斜体 / アンバー）
   - `Japanese Snap (Disposable)`: 写ルンです風・縦長ドット・時分併記（'YY MM DD HH:MM / オレンジ）
   - `American West Coast`: 90年代西海岸・ロードトリップ（MM DD 'YY / 7セグ斜体 / ゴールデン）
   - `American 80s (Red Quartz)`: 80年代モーテル・ホームビデオ・赤色LED（MM DD 'YY / 7セグ直立 / クォーツレッド）
   - `European Classic (Paris/Berlin)`: 欧州の石畳・上品な佇まい（DD.MM.YY / 7セグ直立 / 控えめアンバー）
   - `Hong Kong Neon (90s Cinema)`: 90年代香港ネオン映画調（'YY MM DD / 14セグ斜体 / サイバーグリーン）
   - `Y2K Digicam (Early 2000s)`: 2000年代初期コンデジLCD液晶（'YY MM DD HH:MM / 液晶等幅 / ゴールデン）
   - `Compact Fine Dot (Minimal)`: 超高精細スクエアドットマトリクス（'YY MM DD HH:MM）

---

## 📦 インストール方法

### ComfyUI の `custom_nodes` に配置
```powershell
cd C:\Users\coffe\Documents\ComfyUI\custom_nodes
git clone https://github.com/.../FilmDateStamp.git
```
またはローカル開発環境からのディレクトリジャンクション：
```powershell
New-Item -ItemType Junction -Path "C:\Users\coffe\Documents\ComfyUI\custom_nodes\FilmDateStamp" -Target "C:\Users\coffe\Documents\FilmDateStamp"
```

---

## 🚀 使い方

1. ComfyUI のノード追加メニューより、`image` > `film` > **`Film Date Stamp (Optical Burn-in)`** を選択。
2. 最上段の **`style_preset`** からお好みの世界観（`Japanese Tokyo 90s` や `American West Coast` など）を選ぶと、フォント・色・発光・日付順が一発で自動セットされます。
3. パラメータを手動で動かすと自動的に `Custom` に切り替わり、自由な微調整が可能です。
4. サンプルワークフローは `workflows/film_date_stamp_workflow.json` を ComfyUI 画面にドラッグ＆ドロップしてください。

---

## ⚙️ パラメータ仕様

| パラメータ名 | 区分 | 型 / 選択肢 | デフォルト | 説明 |
|---|---|---|---|---|
| `style_preset` | 必須 | `Custom`, `Japanese Tokyo 90s`, `American West Coast`, etc. | `Custom` | スタイル一括プリセット（最上段） |
| `font_type` | 必須 | `DSEG7`, `DSEG14`, `VT323`, `Silkscreen`, `ShareTechMono` | `DSEG7_Classic` | 発光素子タイポグラフィ（全7種） |
| `preset_color` | 必須 | `Amber Classic`, `Quartz Red`, `Fuji Orange`, `Golden Yellow`, `Cyber Green` | `Amber Classic` | 発光スペクトルプリセット |
| `exposure_intensity`| 必須 | FLOAT (0.0〜2.0) | `1.0` | 露光光量全体の強度 |
| `core_glow` | 必須 | FLOAT (0.0〜2.0) | `1.0` | 中心白コアの強さ |
| `halation` | 必須 | FLOAT (0.0〜3.0) | `1.0` | 赤色乳剤散乱の広がり・強さ |
| `optical_burn` | 必須 | BOOLEAN | `True` | 物理感光露光（True=白背景で自然に埋もれる） |
| `date_mode` | 必須 | `custom`, `current_date`, `random_vintage` | `custom` | 日付生成モード |
| `date_string` | 必須 | STRING | `'98 12 24` | `custom` 時に使用する文字列 |
| `date_format` | 必須 | `'YY MM DD`, `MM DD 'YY`, `DD MM 'YY`, `DD.MM.YY`, etc. | `'YY MM DD` | 自動日時生成時のフォーマット |
| `show_time` | 必須 | BOOLEAN | `False` | 時刻（HH:MM）の表示・非表示切り替え |
| `position` | 必須 | `bottom_right`, `bottom_left`, `top_right`, `top_left` | `bottom_right` | スタンプの配置位置 |
| `font_scale` | 必須 | FLOAT (0.5〜2.5) | `1.0` | 画像短辺に対するフォントスケール |
| `margin_x` / `margin_y` | 必須 | FLOAT (0.0〜3.0) | `1.0` | 画面端からのマージン倍率 |
| `seed` | 任意 | INT | `0` | `random_vintage` の乱数再現用シード |

---

## 📄 ライセンス

- コード: MIT License
- 同梱フォント: SIL Open Font License 1.1 (`fonts/LICENSE-OFL.txt`)
