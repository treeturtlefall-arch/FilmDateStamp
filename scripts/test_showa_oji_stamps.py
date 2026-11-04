"""
FilmDateStamp - 昭和王子 実写プリセット・初期配置・フォントサイズ最終確認用生成スクリプト
"""
import os
import sys
import time
from typing import List, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import STYLE_PRESETS, DateStampConfig, COLOR_PRESETS
from film_stamp import render_film_date_stamp

INPUT_DIR = r"C:\Users\coffe\Downloads\昭和王子"
OUTPUT_DIR = r"C:\Users\coffe\Downloads\昭和王子_stamp_test"

# 代表的な検証用画像
IMG_STANDARD = "14354540540_0c951f7dda_o.jpg"      # 横構図・標準（暗め背景）
IMG_BRIGHT = "14539690754_b6cdc8803f_o.jpg"        # 横構図・右下明るい（ハイライト埋もれ検証）
IMG_VERTICAL = "14354738217_98ed951512_o.jpg"      # 縦構図（1774x2560）
IMG_DAYLIGHT = "14541189635_c81b0f7707_o.jpg"      # 横構図・日中スナップ

# フォント（ラベル用）
JP_FONTS = [
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/YuGothB.ttc",
    "C:/Windows/Fonts/msgothic.ttc",
]
LABEL_FONT_PATH = next((f for f in JP_FONTS if os.path.exists(f)), None)


def get_label_font(size: int = 16):
    if LABEL_FONT_PATH:
        return ImageFont.truetype(LABEL_FONT_PATH, size)
    return ImageFont.load_default()


def crop_stamp_area(img: Image.Image, crop_w: int = 700, crop_h: int = 420) -> Image.Image:
    """画像の右下部分をクロップして等倍スタンプ周辺を切り出す"""
    w, h = img.size
    left = max(0, w - crop_w)
    top = max(0, h - crop_h)
    return img.crop((left, top, w, h))


def add_label_banner(crop_img: Image.Image, title: str, subtitle: str) -> Image.Image:
    """クロップ画像の上部に情報バーを付加"""
    w, h = crop_img.size
    banner_h = 44
    res = Image.new("RGB", (w, h + banner_h), (22, 24, 30))
    res.paste(crop_img, (0, banner_h))

    draw = ImageDraw.Draw(res)
    font_t = get_label_font(15)
    font_s = get_label_font(12)

    draw.text((12, 4), title, fill=(255, 255, 255), font=font_t)
    draw.text((12, 24), subtitle, fill=(180, 190, 205), font=font_s)
    draw.line([(0, banner_h - 1), (w, banner_h - 1)], fill=(60, 68, 85), width=1)
    return res


def main():
    print(f"=== FilmDateStamp 昭和王子 実写テストスクリプト ===")
    print(f"入力フォルダ: {INPUT_DIR}")
    print(f"出力フォルダ: {OUTPUT_DIR}")

    if not os.path.exists(INPUT_DIR):
        print(f"エラー: 入力フォルダ {INPUT_DIR} が存在しません。")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    dirs = {
        "presets_full": os.path.join(OUTPUT_DIR, "presets_full"),
        "presets_crops": os.path.join(OUTPUT_DIR, "presets_crops"),
        "margin_full": os.path.join(OUTPUT_DIR, "sensitivity_margin_full"),
        "margin_crops": os.path.join(OUTPUT_DIR, "sensitivity_margin_crops"),
        "scale_full": os.path.join(OUTPUT_DIR, "sensitivity_scale_full"),
        "scale_crops": os.path.join(OUTPUT_DIR, "sensitivity_scale_crops"),
        "snap_crops": os.path.join(OUTPUT_DIR, "sensitivity_snap_crops"),
        "vertical_full": os.path.join(OUTPUT_DIR, "vertical_full"),
        "vertical_crops": os.path.join(OUTPUT_DIR, "vertical_crops"),
        "bright_full": os.path.join(OUTPUT_DIR, "bright_full"),
        "bright_crops": os.path.join(OUTPUT_DIR, "bright_crops"),
        "sheets": os.path.join(OUTPUT_DIR, "contact_sheets"),
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)

    base_std = Image.open(os.path.join(INPUT_DIR, IMG_STANDARD)).convert("RGB")
    base_bright = Image.open(os.path.join(INPUT_DIR, IMG_BRIGHT)).convert("RGB")
    base_vert = Image.open(os.path.join(INPUT_DIR, IMG_VERTICAL)).convert("RGB")

    t_start = time.time()

    # =========================================================================
    # 1. 全スタイルプリセットの適用（標準写真）
    # =========================================================================
    print("\n--- 1. 全プリセットのレンダリング（標準写真） ---")
    preset_names = [k for k in STYLE_PRESETS.keys() if k != "Custom"]
    preset_meta = []

    crop_cards_presets = []

    for idx, name in enumerate(preset_names):
        cfg = DateStampConfig(style_preset=name)
        cfg.apply_style_preset_if_set()

        t0 = time.time()
        res_img = render_film_date_stamp(base_std, cfg, seed=idx + 1)
        render_time = time.time() - t0

        safe_slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")
        filename_full = f"{idx+1:02d}_{safe_slug}.jpg"
        path_full = os.path.join(dirs["presets_full"], filename_full)
        res_img.save(path_full, quality=93)

        # クロップ切り出し
        crop = crop_stamp_area(res_img, 720, 380)
        p_vals = STYLE_PRESETS[name]
        sub = f"scale={p_vals.get('font_scale', 1.0)} | margin={p_vals.get('margin', 1.0)} | {p_vals.get('preset_color', '')}"
        crop_labeled = add_label_banner(crop, f"{idx+1}. {name}", sub)
        path_crop = os.path.join(dirs["presets_crops"], f"crop_{idx+1:02d}_{safe_slug}.jpg")
        crop_labeled.save(path_crop, quality=93)

        crop_cards_presets.append(crop_labeled)
        preset_meta.append({
            "index": idx + 1,
            "name": name,
            "slug": safe_slug,
            "filename_full": filename_full,
            "filename_crop": f"crop_{idx+1:02d}_{safe_slug}.jpg",
            "scale": p_vals.get("font_scale", 1.0),
            "margin": p_vals.get("margin", 1.0),
            "color": p_vals.get("preset_color", ""),
            "font": p_vals.get("font_type", ""),
            "date": p_vals.get("date_string", ""),
            "time": render_time,
        })
        print(f"  [{idx+1:02d}/{len(preset_names):02d}] {name} ({render_time:.2f}s)")

    # =========================================================================
    # 2. 初期配置（margin）感度テスト（基準: Japanese Tokyo 90s）
    # =========================================================================
    print("\n--- 2. 初期配置（margin）感度テスト ---")
    margin_values = [0.70, 0.85, 1.00, 1.15, 1.30, 1.50]
    margin_cards = []
    margin_meta = []

    for m in margin_values:
        cfg = DateStampConfig(style_preset="Japanese Tokyo 90s")
        cfg.apply_style_preset_if_set()
        cfg.margin = m

        res_img = render_film_date_stamp(base_std, cfg, seed=42)
        slug = f"margin_{m:.2f}".replace(".", "_")
        filename_full = f"{slug}.jpg"
        res_img.save(os.path.join(dirs["margin_full"], filename_full), quality=93)

        crop = crop_stamp_area(res_img, 720, 380)
        is_default = " (★現在の初期値)" if abs(m - 1.00) < 1e-4 else ""
        labeled = add_label_banner(
            crop,
            f"margin = {m:.2f}{is_default}",
            f"Xマージン: {int(1774 * 0.05 * m)}px, Yマージン: {int(1774 * 0.04 * m)}px (基準短辺1774px)"
        )
        labeled.save(os.path.join(dirs["margin_crops"], f"crop_{slug}.jpg"), quality=93)
        margin_cards.append(labeled)
        margin_meta.append({"margin": m, "is_default": abs(m - 1.0) < 1e-4, "slug": slug})
        print(f"  margin={m:.2f} 完了")

    # =========================================================================
    # 3. 初期フォントサイズ（font_scale）感度テスト（基準: Japanese Tokyo 90s）
    # =========================================================================
    print("\n--- 3. 初期フォントサイズ（font_scale）感度テスト ---")
    scale_values = [0.80, 0.90, 1.00, 1.10, 1.20, 1.30]
    scale_cards = []
    scale_meta = []

    for s in scale_values:
        cfg = DateStampConfig(style_preset="Japanese Tokyo 90s")
        cfg.apply_style_preset_if_set()
        cfg.font_scale = s

        res_img = render_film_date_stamp(base_std, cfg, seed=42)
        slug = f"scale_{s:.2f}".replace(".", "_")
        filename_full = f"{slug}.jpg"
        res_img.save(os.path.join(dirs["scale_full"], filename_full), quality=93)

        crop = crop_stamp_area(res_img, 720, 380)
        is_default = " (★現在の初期値)" if abs(s - 1.00) < 1e-4 else ""
        labeled = add_label_banner(
            crop,
            f"font_scale = {s:.2f}{is_default}",
            f"基準フォントサイズ: {int(1774 * 0.04 * s)}px (短辺1774pxに対する比率: {4.0 * s:.1f}%)"
        )
        labeled.save(os.path.join(dirs["scale_crops"], f"crop_{slug}.jpg"), quality=93)
        scale_cards.append(labeled)
        scale_meta.append({"scale": s, "is_default": abs(s - 1.0) < 1e-4, "slug": slug})
        print(f"  scale={s:.2f} 完了")

    # =========================================================================
    # 4. 写ルンです（Japanese Snap）のサイズ＆マージン感度テスト
    # =========================================================================
    print("\n--- 4. 写ルンです（Japanese Snap）の感度テスト ---")
    snap_patterns = [
        (1.00, 1.00, "標準サイズ・標準マージン (scale 1.0, margin 1.0)"),
        (1.10, 1.25, "中間バランス (scale 1.1, margin 1.25)"),
        (1.20, 1.50, "★現行プリセット値 (scale 1.2, margin 1.5)"),
        (1.10, 1.50, "控えめサイズ・ゆったりマージン (scale 1.1, margin 1.5)"),
    ]
    snap_cards = []
    snap_meta = []

    for sc, mg, desc in snap_patterns:
        cfg = DateStampConfig(style_preset="Japanese Snap (Disposable)")
        cfg.apply_style_preset_if_set()
        cfg.font_scale = sc
        cfg.margin = mg

        res_img = render_film_date_stamp(base_std, cfg, seed=42)
        slug = f"snap_s{sc:.2f}_m{mg:.2f}".replace(".", "_")
        crop = crop_stamp_area(res_img, 820, 380)
        labeled = add_label_banner(crop, f"Japanese Snap: scale={sc:.2f}, margin={mg:.2f}", desc)
        labeled.save(os.path.join(dirs["snap_crops"], f"crop_{slug}.jpg"), quality=93)
        snap_cards.append(labeled)
        snap_meta.append({"scale": sc, "margin": mg, "desc": desc, "slug": slug})
        print(f"  Snap scale={sc:.2f}, margin={mg:.2f} 完了")

    # =========================================================================
    # 5. 縦構図写真（1774x2560）での検証
    # =========================================================================
    print("\n--- 5. 縦構図写真での検証 ---")
    vert_presets = [
        "Japanese Tokyo 90s",
        "Japanese Snap (Disposable)",
        "Vintage 70s Color (Datematic)",
        "American 80s (Red Quartz)",
        "Cyber Telemetry (80s Sci-Fi)",
    ]
    vert_meta = []
    vert_cards = []

    for name in vert_presets:
        cfg = DateStampConfig(style_preset=name)
        cfg.apply_style_preset_if_set()
        res_img = render_film_date_stamp(base_vert, cfg, seed=42)
        slug = f"vert_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        res_img.save(os.path.join(dirs["vertical_full"], f"{slug}.jpg"), quality=93)

        crop = crop_stamp_area(res_img, 720, 380)
        p_vals = STYLE_PRESETS[name]
        labeled = add_label_banner(
            crop,
            f"[縦写真] {name}",
            f"scale={p_vals.get('font_scale', 1.0)} | margin={p_vals.get('margin', 1.0)}"
        )
        labeled.save(os.path.join(dirs["vertical_crops"], f"crop_{slug}.jpg"), quality=93)
        vert_cards.append(labeled)
        vert_meta.append({"name": name, "slug": slug})
        print(f"  縦写真 {name} 完了")

    # =========================================================================
    # 6. 明部写真（14539690754_b6cdc8803f_o.jpg）でのハイライト埋もれ感検証
    # =========================================================================
    print("\n--- 6. 明部写真でのハイライト埋もれ検証 ---")
    bright_presets = [
        "Japanese Tokyo 90s",
        "Japanese Snap (Disposable)",
        "Vintage 70s Color (Datematic)",
        "Cyber Telemetry (80s Sci-Fi)",
    ]
    bright_meta = []
    bright_cards = []

    for name in bright_presets:
        cfg = DateStampConfig(style_preset=name)
        cfg.apply_style_preset_if_set()
        res_img = render_film_date_stamp(base_bright, cfg, seed=42)
        slug = f"bright_{name.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        res_img.save(os.path.join(dirs["bright_full"], f"{slug}.jpg"), quality=93)

        crop = crop_stamp_area(res_img, 720, 380)
        labeled = add_label_banner(crop, f"[明部背景] {name}", "高輝度下での乳剤飽和・白飛び埋もれ再現")
        labeled.save(os.path.join(dirs["bright_crops"], f"crop_{slug}.jpg"), quality=93)
        bright_cards.append(labeled)
        bright_meta.append({"name": name, "slug": slug})
        print(f"  明部写真 {name} 完了")

    # =========================================================================
    # 7. コンタクトシート（まとめ比較画像）の生成
    # =========================================================================
    print("\n--- 7. コンタクトシートの生成 ---")
    create_grid_sheet(
        crop_cards_presets,
        cols=2,
        title="FilmDateStamp - 全12スタイルプリセット 右下等倍クロップ比較",
        subtitle="実際の昭和写真（2560x1774）に各プリセット初期値を適用した詳細プレビュー",
        out_path=os.path.join(dirs["sheets"], "sheet_01_presets_crops.jpg")
    )

    create_grid_sheet(
        margin_cards,
        cols=2,
        title="FilmDateStamp - 初期配置（margin）感度比較",
        subtitle="基準: Japanese Tokyo 90s / margin = 0.70 〜 1.50（四隅余白の最適バランス検討）",
        out_path=os.path.join(dirs["sheets"], "sheet_02_margin_comparison.jpg")
    )

    create_grid_sheet(
        scale_cards,
        cols=2,
        title="FilmDateStamp - 初期フォントサイズ（font_scale）感度比較",
        subtitle="基準: Japanese Tokyo 90s / font_scale = 0.80 〜 1.30（文字サイズ比率の最適バランス検討）",
        out_path=os.path.join(dirs["sheets"], "sheet_03_scale_comparison.jpg")
    )

    create_grid_sheet(
        snap_cards,
        cols=2,
        title="FilmDateStamp - 写ルンです（Japanese Snap）サイズ＆マージン検討",
        subtitle="日付＋時刻で横長になるカプセルドットスタンプの配置バランス検討",
        out_path=os.path.join(dirs["sheets"], "sheet_04_snap_balance.jpg")
    )

    create_grid_sheet(
        vert_cards,
        cols=2,
        title="FilmDateStamp - 縦構図写真（1774x2560）での適用比較",
        subtitle="縦写真における短辺基準マージン・フォントサイズの収まり確認",
        out_path=os.path.join(dirs["sheets"], "sheet_05_vertical_comparison.jpg")
    )

    create_grid_sheet(
        bright_cards,
        cols=2,
        title="FilmDateStamp - 明部背景でのハイライト埋もれ比較",
        subtitle="路面や白壁などの高輝度背景におけるフィルム光学感光余力（Headroom）の減衰挙動",
        out_path=os.path.join(dirs["sheets"], "sheet_06_bright_headroom.jpg")
    )

    # =========================================================================
    # 8. インタラクティブ HTML ビューアの生成
    # =========================================================================
    print("\n--- 8. インタラクティブ HTML ビューア (index.html) の生成 ---")
    html_path = os.path.join(OUTPUT_DIR, "index.html")
    generate_html_viewer(
        html_path=html_path,
        preset_meta=preset_meta,
        margin_meta=margin_meta,
        scale_meta=scale_meta,
        snap_meta=snap_meta,
        vert_meta=vert_meta,
        bright_meta=bright_meta,
    )

    total_time = time.time() - t_start
    print(f"\n=======================================================")
    print(f"全テストレンダリング完了！ 総所要時間: {total_time:.2f} 秒")
    print(f"HTMLビューア: file:///{html_path.replace(os.sep, '/')}")
    print(f"=======================================================")


def create_grid_sheet(cards: List[Image.Image], cols: int, title: str, subtitle: str, out_path: str):
    """カード画像をグリッド状に配置したコンタクトシートを作成"""
    if not cards:
        return

    cw, ch = cards[0].size
    rows = (len(cards) + cols - 1) // cols

    pad = 20
    header_h = 90
    tw = pad * (cols + 1) + cw * cols
    th = header_h + pad * (rows + 1) + ch * rows

    sheet = Image.new("RGB", (tw, th), (16, 18, 22))
    draw = ImageDraw.Draw(sheet)

    font_t = get_label_font(24)
    font_s = get_label_font(14)

    draw.text((pad, 20), title, fill=(255, 255, 255), font=font_t)
    draw.text((pad, 54), subtitle, fill=(170, 180, 200), font=font_s)
    draw.line([(pad, header_h - 10), (tw - pad, header_h - 10)], fill=(45, 52, 65), width=2)

    for i, c in enumerate(cards):
        col = i % cols
        row = i // cols
        x = pad + col * (cw + pad)
        y = header_h + pad + row * (ch + pad)

        sheet.paste(c, (x, y))
        draw.rectangle([(x, y), (x + cw, y + ch)], outline=(50, 58, 75), width=1)

    sheet.save(out_path, quality=92)
    print(f"  シート保存: {os.path.basename(out_path)}")


def generate_html_viewer(html_path: str, preset_meta, margin_meta, scale_meta, snap_meta, vert_meta, bright_meta):
    """ブラウザで快適に比較・判断できる HTML ビューアを生成"""

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FilmDateStamp - 昭和王子 実写検証レポート</title>
<style>
  :root {{
    --bg-dark: #0f1115;
    --bg-card: #181b22;
    --bg-card-hover: #1f232c;
    --border: #2a313e;
    --border-accent: #3b82f6;
    --text-main: #f3f4f6;
    --text-muted: #9ca3af;
    --accent-orange: #f97316;
    --accent-amber: #f59e0b;
    --accent-blue: #3b82f6;
    --accent-green: #10b981;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", "Hiragino Kaku Gothic ProN", Meiryo, sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-main);
    line-height: 1.6;
    padding: 24px;
  }}
  header {{
    max-width: 1400px;
    margin: 0 auto 24px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 20px;
  }}
  h1 {{
    font-size: 26px;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  h1 span.badge {{
    font-size: 13px;
    padding: 3px 10px;
    background: var(--accent-orange);
    color: #fff;
    border-radius: 999px;
    font-weight: 600;
  }}
  p.lead {{
    color: var(--text-muted);
    font-size: 14px;
    margin-top: 8px;
  }}
  .tabs {{
    display: flex;
    gap: 8px;
    margin-top: 18px;
    flex-wrap: wrap;
  }}
  .tab-btn {{
    background: #1e2430;
    color: var(--text-muted);
    border: 1px solid var(--border);
    padding: 9px 18px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
  }}
  .tab-btn:hover {{
    background: #2a3244;
    color: #fff;
  }}
  .tab-btn.active {{
    background: var(--accent-blue);
    color: #fff;
    border-color: var(--accent-blue);
  }}
  .container {{
    max-width: 1400px;
    margin: 0 auto;
  }}
  .tab-pane {{
    display: none;
  }}
  .tab-pane.active {{
    display: block;
  }}
  .info-box {{
    background: #141822;
    border-left: 4px solid var(--accent-amber);
    padding: 14px 18px;
    border-radius: 4px;
    margin-bottom: 20px;
    font-size: 14px;
    color: #e5e7eb;
  }}
  .grid-2 {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(580px, 1fr));
    gap: 20px;
  }}
  .card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    transition: transform 0.15s, border-color 0.15s;
  }}
  .card:hover {{
    border-color: #4b5563;
  }}
  .card.highlight {{
    border: 2px solid var(--accent-amber);
  }}
  .card-header {{
    padding: 12px 16px;
    background: #13161c;
    border-bottom: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .card-title {{
    font-size: 15px;
    font-weight: 600;
    color: #fff;
  }}
  .card-badge {{
    font-size: 11px;
    padding: 2px 8px;
    background: #242c3d;
    color: #93c5fd;
    border-radius: 4px;
    font-weight: 600;
  }}
  .card-img-wrap {{
    position: relative;
    background: #000;
  }}
  .card-img-wrap img {{
    width: 100%;
    display: block;
    height: auto;
  }}
  .card-desc {{
    padding: 10px 16px;
    font-size: 13px;
    color: var(--text-muted);
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .links-row {{
    display: flex;
    gap: 12px;
  }}
  .links-row a {{
    color: var(--accent-blue);
    text-decoration: none;
    font-size: 12px;
  }}
  .links-row a:hover {{
    text-decoration: underline;
  }}
  .sheet-preview {{
    margin-bottom: 24px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
  }}
  .sheet-preview img {{
    width: 100%;
    border-radius: 6px;
    display: block;
  }}
  table.meta-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 16px;
    background: var(--bg-card);
    border-radius: 8px;
    overflow: hidden;
  }}
  table.meta-table th, table.meta-table td {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    text-align: left;
  }}
  table.meta-table th {{
    background: #141720;
    color: #9ca3af;
    font-weight: 600;
  }}
  table.meta-table tr:hover td {{
    background: var(--bg-card-hover);
  }}
</style>
</head>
<body>

<header>
  <h1>FilmDateStamp <span>実写最終検証レポート</span> <span class="badge">昭和王子 2560x1774</span></h1>
  <p class="lead">
    テスト画像: 昭和の王子スナップ写真（暗部・明部・横構図・縦構図） / 各プリセット初期値・初期配置マージン・初期フォントサイズの適合性確認
  </p>
  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('tab-presets')">① スタイルプリセット一覧 (12種)</button>
    <button class="tab-btn" onclick="switchTab('tab-margin')">② 初期配置 (margin) 感度比較</button>
    <button class="tab-btn" onclick="switchTab('tab-scale')">③ 初期フォントサイズ (font_scale) 感度比較</button>
    <button class="tab-btn" onclick="switchTab('tab-snap')">④ 写ルンです (Disposable) バランス</button>
    <button class="tab-btn" onclick="switchTab('tab-vertical')">⑤ 縦構図写真での収まり</button>
    <button class="tab-btn" onclick="switchTab('tab-bright')">⑥ 明部背景・ハイライト埋もれ</button>
  </div>
</header>

<div class="container">

  <!-- TAB 1: プリセット一覧 -->
  <div id="tab-presets" class="tab-pane active">
    <div class="info-box">
      <strong>【プリセット確認のポイント】</strong><br>
      各時代・地域ごとの日付フォーマット、専用フォント（7セグ・ドット・機械彫刻活字）、固有の発光色、およびそれぞれのプリセットで設定されている <code>font_scale</code> と <code>margin</code> が、実際の昭和写真上でどのように映えるかを確認できます。各カードの「全体フル解像度」リンクから2560x1774の原寸全体像を確認できます。
    </div>

    <div class="sheet-preview">
      <h3 style="margin-bottom: 10px; font-size: 16px;">コンタクトシート一覧</h3>
      <img src="contact_sheets/sheet_01_presets_crops.jpg" alt="プリセットクロップ一覧">
    </div>

    <div class="grid-2">
"""

    for p in preset_meta:
        html += f"""
      <div class="card">
        <div class="card-header">
          <span class="card-title">[{p['index']:02d}] {p['name']}</span>
          <span class="card-badge">scale={p['scale']} | margin={p['margin']}</span>
        </div>
        <div class="card-img-wrap">
          <img src="presets_crops/{p['filename_crop']}" alt="{p['name']}" loading="lazy">
        </div>
        <div class="card-desc">
          <span>{p['color']} / {p['font'].split(' ')[0]}</span>
          <div class="links-row">
            <a href="presets_full/{p['filename_full']}" target="_blank">🔍 全体フル解像度 (2560x1774)</a>
          </div>
        </div>
      </div>
"""

    html += f"""
    </div>

    <h3 style="margin: 28px 0 12px; font-size: 16px;">プリセットパラメータ対比表</h3>
    <table class="meta-table">
      <thead>
        <tr>
          <th>#</th>
          <th>プリセット名</th>
          <th>日付表記</th>
          <th>フォント</th>
          <th>発光色</th>
          <th>font_scale</th>
          <th>margin</th>
        </tr>
      </thead>
      <tbody>
"""
    for p in preset_meta:
        html += f"""
        <tr>
          <td>{p['index']}</td>
          <td><strong>{p['name']}</strong></td>
          <td><code>{p['date']}</code></td>
          <td>{p['font']}</td>
          <td>{p['color']}</td>
          <td><code>{p['scale']}</code></td>
          <td><code>{p['margin']}</code></td>
        </tr>
"""
    html += f"""
      </tbody>
    </table>
  </div>

  <!-- TAB 2: マージン感度 -->
  <div id="tab-margin" class="tab-pane">
    <div class="info-box">
      <strong>【初期配置 (margin) の判断基準】</strong><br>
      基準プリセット（Japanese Tokyo 90s）で <code>margin</code> を 0.70 から 1.50 まで変化させています。<br>
      - <strong>0.70〜0.85</strong>: 画面端ギリギリ（フィルム枠ギリギリに写し込む実機感、ただしプリント時のトリミングで切れるリスク）<br>
      - <strong>1.00 (現在の初期値)</strong>: 標準的な一眼レフデータバック／コンパクト機位置（X余白=約88px, Y余白=約70px）<br>
      - <strong>1.15〜1.30</strong>: やや内側寄り（ゆとりがあり、四隅のケラレや暗部落ちを避ける位置）<br>
      - <strong>1.50</strong>: 写ルンです等の使い捨てカメラで一般的な、かなり内側に押し出された配置
    </div>

    <div class="sheet-preview">
      <img src="contact_sheets/sheet_02_margin_comparison.jpg" alt="マージン比較シート">
    </div>

    <div class="grid-2">
"""
    for m in margin_meta:
        hl = " highlight" if m['is_default'] else ""
        def_tag = " <span style='color:var(--accent-amber); font-weight:bold;'>★現在の初期値</span>" if m['is_default'] else ""
        html += f"""
      <div class="card{hl}">
        <div class="card-header">
          <span class="card-title">margin = {m['margin']:.2f}{def_tag}</span>
        </div>
        <div class="card-img-wrap">
          <img src="sensitivity_margin_crops/crop_{m['slug']}.jpg" alt="margin {m['margin']}" loading="lazy">
        </div>
        <div class="card-desc">
          <span>X: {int(1774 * 0.05 * m['margin'])}px, Y: {int(1774 * 0.04 * m['margin'])}px</span>
          <a href="sensitivity_margin_full/{m['slug']}.jpg" target="_blank">🔍 全体フル解像度</a>
        </div>
      </div>
"""
    html += f"""
    </div>
  </div>

  <!-- TAB 3: フォントサイズ感度 -->
  <div id="tab-scale" class="tab-pane">
    <div class="info-box">
      <strong>【初期フォントサイズ (font_scale) の判断基準】</strong><br>
      基準プリセット（Japanese Tokyo 90s）で <code>font_scale</code> を 0.80 から 1.30 まで変化させています。<br>
      - <strong>0.80〜0.90</strong>: 控えめで上品なリアル実機感。フィルム写真の主役（被写体）を邪魔しないサイズ感。<br>
      - <strong>1.00 (現在の初期値)</strong>: 実機感と視認性のバランスを取った標準設定（文字高さ約70px = 短辺の4.0%）。<br>
      - <strong>1.10〜1.20</strong>: SNSやスマホ画面で縮小表示された際にも日付がパッと読める強調サイズ。<br>
      - <strong>1.30</strong>: かなり主張の強いビッグサイズ。
    </div>

    <div class="sheet-preview">
      <img src="contact_sheets/sheet_03_scale_comparison.jpg" alt="フォントサイズ比較シート">
    </div>

    <div class="grid-2">
"""
    for s in scale_meta:
        hl = " highlight" if s['is_default'] else ""
        def_tag = " <span style='color:var(--accent-amber); font-weight:bold;'>★現在の初期値</span>" if s['is_default'] else ""
        html += f"""
      <div class="card{hl}">
        <div class="card-header">
          <span class="card-title">font_scale = {s['scale']:.2f}{def_tag}</span>
        </div>
        <div class="card-img-wrap">
          <img src="sensitivity_scale_crops/crop_{s['slug']}.jpg" alt="scale {s['scale']}" loading="lazy">
        </div>
        <div class="card-desc">
          <span>短辺比率: {4.0 * s['scale']:.1f}%</span>
          <a href="sensitivity_scale_full/{s['slug']}.jpg" target="_blank">🔍 全体フル解像度</a>
        </div>
      </div>
"""
    html += f"""
    </div>
  </div>

  <!-- TAB 4: 写ルンですバランス -->
  <div id="tab-snap" class="tab-pane">
    <div class="info-box">
      <strong>【写ルンです（Japanese Snap）のバランス検討】</strong><br>
      写ルンですは「日付＋時刻（'98 12 24 18:30）」を表示するため文字数が長く、また実機レンズの四隅暗がりや裏蓋圧板の特性上、内側に大きめに写し込まれる特徴があります。<br>
      現行プリセットでは <code>font_scale: 1.20, margin: 1.50</code> と設定されています。
    </div>

    <div class="sheet-preview">
      <img src="contact_sheets/sheet_04_snap_balance.jpg" alt="写ルンですバランス比較">
    </div>

    <div class="grid-2">
"""
    for sn in snap_meta:
        html += f"""
      <div class="card">
        <div class="card-header">
          <span class="card-title">scale={sn['scale']:.2f}, margin={sn['margin']:.2f}</span>
          <span class="card-badge">{sn['desc']}</span>
        </div>
        <div class="card-img-wrap">
          <img src="sensitivity_snap_crops/crop_{sn['slug']}.jpg" alt="{sn['desc']}" loading="lazy">
        </div>
      </div>
"""
    html += f"""
    </div>
  </div>

  <!-- TAB 5: 縦構図 -->
  <div id="tab-vertical" class="tab-pane">
    <div class="info-box">
      <strong>【縦構図写真（1774x2560）での収まり】</strong><br>
      縦構図写真においても、フィルムサイズ基準として <code>min(w, h) = 1774px</code> を採用しているため、横写真と全く同じ絶対サイズ感とマージン比率で安定して描画されます。
    </div>

    <div class="sheet-preview">
      <img src="contact_sheets/sheet_05_vertical_comparison.jpg" alt="縦構図比較シート">
    </div>

    <div class="grid-2">
"""
    for v in vert_meta:
        html += f"""
      <div class="card">
        <div class="card-header">
          <span class="card-title">{v['name']} (縦構図)</span>
        </div>
        <div class="card-img-wrap">
          <img src="vertical_crops/crop_{v['slug']}.jpg" alt="{v['name']}" loading="lazy">
        </div>
        <div class="card-desc">
          <span>画像サイズ: 1774 x 2560</span>
          <a href="vertical_full/{v['slug']}.jpg" target="_blank">🔍 全体フル解像度</a>
        </div>
      </div>
"""
    html += f"""
    </div>
  </div>

  <!-- TAB 6: 明部ハイライト埋もれ -->
  <div id="tab-bright" class="tab-pane">
    <div class="info-box">
      <strong>【明部背景でのハイライト埋もれ（Headroom減衰）】</strong><br>
      背景の道路や壁が白く明るい写真（14539690754）に焼き付けた場合、フィルム乳剤の感光キャパシティ（Headroom）がすでに飽和しているため、文字が自然に白飛びして埋もれる光学現象が再現されます。
    </div>

    <div class="sheet-preview">
      <img src="contact_sheets/sheet_06_bright_headroom.jpg" alt="明部ハイライト埋もれ比較">
    </div>

    <div class="grid-2">
"""
    for b in bright_meta:
        html += f"""
      <div class="card">
        <div class="card-header">
          <span class="card-title">{b['name']} (明部背景)</span>
        </div>
        <div class="card-img-wrap">
          <img src="bright_crops/crop_{b['slug']}.jpg" alt="{b['name']}" loading="lazy">
        </div>
        <div class="card-desc">
          <span>右下平均輝度: 94.8</span>
          <a href="bright_full/{b['slug']}.jpg" target="_blank">🔍 全体フル解像度</a>
        </div>
      </div>
"""
    html += f"""
    </div>
  </div>

</div>

<script>
function switchTab(tabId) {{
  document.querySelectorAll('.tab-pane').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  
  const target = document.getElementById(tabId);
  if (target) target.classList.add('active');
  
  const btns = Array.from(document.querySelectorAll('.tab-btn'));
  const activeBtn = btns.find(b => b.getAttribute('onclick').includes(tabId));
  if (activeBtn) activeBtn.classList.add('active');
}}
</script>

</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
