"""
FDS7Strict シリーズ vs FDS7Classic (DSEG7改変) 徹底比較・検証レンダリングスクリプト
1980年代諏訪精工舎モジュール仕様（W/H=0.50, セグメント厚10%, ギャップ3.5%, 35°フラットカット, 浮遊ドットアポストロフィ）
と従来のデジタル時計フォント（DSEG7ベース）を、
1. 純粋マスク形状（グリフ骨格・内腔・アポストロフィ・記号比較）
2. FilmDateStamp v2.0 光学ハレーション合成（Amber Classic / Quartz Red、標準露光および強露光）
の両面から高解像度で視覚比較するレポート画像を生成する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp, render_date_mask, get_font_file_and_shear

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def load_jp_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def render_stamp_crop(
    font_type: str,
    date_str: str,
    preset_color: str,
    exposure: float = 1.05,
    core_glow: float = 0.90,
    halation: float = 1.15,
    irregularity: float = 0.85,
    crop_w: int = 580,
    crop_h: int = 120,
    bg_type: str = "dark_photo",
) -> Image.Image:
    """仮想写真 (1280x960) の右下にスタンプを焼き付け、拡大比較用にクロップする"""
    vw, vh = 1280, 960
    bg = Image.new("RGB", (vw, vh), (16, 18, 24))
    draw = ImageDraw.Draw(bg)

    # 右下クロップ領域の背景テクスチャ生成
    x0, y0 = vw - crop_w, vh - crop_h
    for x in range(x0, vw):
        rx = (x - x0) / max(1, crop_w)
        if bg_type == "dark_photo":
            r = int(16 + rx * 26)
            g = int(18 + rx * 22)
            b = int(24 + rx * 18)
        elif bg_type == "warm_film":
            r = int(38 + rx * 45)
            g = int(28 + rx * 30)
            b = int(22 + rx * 20)
        else:
            r = g = b = int(14 + rx * 20)
        draw.line([(x, y0), (x, vh)], fill=(r, g, b))

    cfg = DateStampConfig(
        font_type=font_type,
        date_string=date_str,
        preset_color=preset_color,
        exposure_intensity=exposure,
        core_glow=core_glow,
        halation=halation,
        irregularity=irregularity,
        show_time=(":" in date_str),
        font_scale=1.0,
        margin_x=0.75,
        margin_y=0.75,
        optical_burn=True,
    )
    stamped = render_film_date_stamp(bg, config=cfg, seed=42)
    return stamped.crop((x0, y0, vw, vh))


def generate_strict_comparison_report():
    W, H = 1600, 1420
    canvas = Image.new("RGB", (W, H), (15, 17, 22))
    draw = ImageDraw.Draw(canvas)

    f_title = load_jp_font(26)
    f_sub = load_jp_font(16)
    f_sec = load_jp_font(20)
    f_label = load_jp_font(17)
    f_small = load_jp_font(14)
    f_mono = ImageFont.truetype(os.path.join(PROJECT_DIR, "fonts/ShareTechMono-Regular.ttf"), 17)

    # ヘッダー
    draw.text(
        (40, 24),
        "FilmDateStamp - 『FDS7Strict』1980s 諏訪精工舎仕様 vs 現行『FDS7Classic (DSEG7)』光学比較検証レポート",
        fill=(245, 248, 255),
        font=f_title,
    )
    draw.text(
        (40, 64),
        "スリム比率 (W/H=0.50 vs 0.62)・控えめな前傾 (-7.0° vs -11.5°)・セグメント厚 (10.0% vs 12.4%)・ギャップ (3.5% vs 1.5%)・35°フラットカット・浮遊アポストロフィの検証",
        fill=(175, 185, 205),
        font=f_sub,
    )
    draw.line([(40, 98), (W - 40, 98)], fill=(55, 62, 78), width=2)

    # ==========================================================================
    # Section 1: コンパクト機（イタリック系）の比較 (-7.0° vs -11.5°)
    # ==========================================================================
    y_cursor = 115
    draw.text(
        (40, y_cursor),
        "【1】80年代コンパクトカメラ（Canon Autoboy / Nikon ピカイチ調）比較：Amber Classic 光学ハレーション合成",
        fill=(255, 200, 90),
        font=f_sec,
    )
    y_cursor += 36

    compact_rows = [
        {
            "title": "NEW: FDS7Strict-Compact (-7.0° / W:H=0.50 / 厚10% / 隙間3.5%)",
            "font_type": "FDS7_Strict_Compact (80s -7°)",
            "badge_color": (40, 160, 95),
            "note": "★実機準拠: 8や0の内腔（窓）が潰れず綺麗に抜け、-7°の自然な前傾と上部浮遊ドット（'）が本物の佇まいを再現",
        },
        {
            "title": "OLD: FDS7Classic-BoldItalic [DSEG7ベース] (-11.5° / W:H=0.62 / 厚12.4%)",
            "font_type": "DSEG7_Italic (7-Segment)",
            "badge_color": (130, 75, 60),
            "note": "▲従来版: 横に太く(-11.5°急傾斜)、ハレーション加算時にセグメント同士が干渉し「8」「9」の内腔が狭く詰まって見える",
        },
    ]

    for row in compact_rows:
        card_h = 165
        draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + card_h)], radius=8, fill=(24, 28, 36), outline=(52, 60, 76))
        draw.rounded_rectangle([(55, y_cursor + 12), (55 + 630, y_cursor + 42)], radius=4, fill=row["badge_color"])
        draw.text((65, y_cursor + 15), row["title"], fill=(255, 255, 255), font=f_label)
        draw.text((700, y_cursor + 17), row["note"], fill=(210, 220, 235), font=f_small)

        # 左プレビュー: 標準日付 ('88 12 24)
        crop1 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'88 12 24",
            preset_color="Amber Classic",
            exposure=1.05,
            core_glow=0.95,
            halation=1.15,
            crop_w=460,
            crop_h=96,
        )
        canvas.paste(crop1, (55, y_cursor + 54))
        draw.rectangle([(55, y_cursor + 54), (55 + 460, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((62, y_cursor + 58), "Standard Exposure ('88 12 24)", fill=(160, 170, 190), font=f_small)

        # 中央プレビュー: 強ハレーション & 8の連続 ('88 08 28) — 内腔（カウンター）の抜け検証
        crop2 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'88 08 28",
            preset_color="Amber Classic",
            exposure=1.25,
            core_glow=1.10,
            halation=1.55,
            crop_w=460,
            crop_h=96,
            bg_type="warm_film",
        )
        canvas.paste(crop2, (535, y_cursor + 54))
        draw.rectangle([(535, y_cursor + 54), (535 + 460, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((542, y_cursor + 58), "High Halation Cavities ('88 08 28)", fill=(255, 200, 130), font=f_small)

        # 右プレビュー: 時刻・コロン・ハイフン・ピリオド検証 (88-12.24 18:30)
        crop3 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'88 12 24 18:30",
            preset_color="Fuji Orange",
            exposure=1.05,
            core_glow=0.90,
            halation=1.10,
            crop_w=525,
            crop_h=96,
        )
        canvas.paste(crop3, (1015, y_cursor + 54))
        draw.rectangle([(1015, y_cursor + 54), (1015 + 525, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((1022, y_cursor + 58), "Date + Time ('88 12 24 18:30)", fill=(160, 170, 190), font=f_small)

        y_cursor += card_h + 14

    # ==========================================================================
    # Section 2: 一眼レフ データバック（0.0° 直立系）の比較
    # ==========================================================================
    y_cursor += 10
    draw.text(
        (40, y_cursor),
        "【2】80年代一眼レフ用データバック（Nikon MF-12/14/16 / Olympus Recordata 3調）比較：Quartz Red 光学合成",
        fill=(255, 110, 95),
        font=f_sec,
    )
    y_cursor += 36

    slr_rows = [
        {
            "title": "NEW: FDS7Strict-SLR (0.0° 直立 / W:H=0.50 / 35°先端フラットカット)",
            "font_type": "FDS7_Strict_SLR (80s 0°)",
            "badge_color": (40, 130, 175),
            "note": "★実機準拠: 精密計器のような端正なスリム直立字形。深紅のQuartz Red強露光でもセグメント間ギャップ(3.5%)が鮮明に分離",
        },
        {
            "title": "OLD: FDS7Classic-Bold [DSEG7ベース] (0.0° 直立 / W:H=0.62 / 45°尖頭角)",
            "font_type": "DSEG7_Classic (7-Segment)",
            "badge_color": (110, 75, 90),
            "note": "▲従来版: 置時計・電卓用の横広比率(0.62)のため、一眼レフデータバック特有の凝縮感・精密感が薄れる",
        },
    ]

    for row in slr_rows:
        card_h = 165
        draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + card_h)], radius=8, fill=(24, 28, 36), outline=(52, 60, 76))
        draw.rounded_rectangle([(55, y_cursor + 12), (55 + 630, y_cursor + 42)], radius=4, fill=row["badge_color"])
        draw.text((65, y_cursor + 15), row["title"], fill=(255, 255, 255), font=f_label)
        draw.text((700, y_cursor + 17), row["note"], fill=(210, 220, 235), font=f_small)

        # 左: Quartz Red ('83 10 24)
        crop1 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'83 10 24",
            preset_color="Quartz Red",
            exposure=1.10,
            core_glow=1.00,
            halation=1.30,
            crop_w=460,
            crop_h=96,
        )
        canvas.paste(crop1, (55, y_cursor + 54))
        draw.rectangle([(55, y_cursor + 54), (55 + 460, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((62, y_cursor + 58), "Quartz Red 655nm ('83 10 24)", fill=(255, 160, 160), font=f_small)

        # 中央: ハイフン・ピリオド表記 (83-10-24 / 24.10.83)
        crop2 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="83-10-24",
            preset_color="Amber Classic",
            exposure=1.00,
            core_glow=0.85,
            halation=1.00,
            crop_w=460,
            crop_h=96,
        )
        canvas.paste(crop2, (535, y_cursor + 54))
        draw.rectangle([(535, y_cursor + 54), (535 + 460, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((542, y_cursor + 58), "Hyphen Format (83-10-24)", fill=(160, 170, 190), font=f_small)

        # 右: ピリオド＋時刻表記 (24.10.83 12:05)
        crop3 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="24.10.83 12:05",
            preset_color="Quartz Red",
            exposure=1.05,
            core_glow=0.95,
            halation=1.15,
            crop_w=525,
            crop_h=96,
        )
        canvas.paste(crop3, (1015, y_cursor + 54))
        draw.rectangle([(1015, y_cursor + 54), (1015 + 525, y_cursor + 54 + 96)], outline=(80, 90, 110))
        draw.text((1022, y_cursor + 58), "European Period + Colon (24.10.83 12:05)", fill=(160, 170, 190), font=f_small)

        y_cursor += card_h + 14

    # ==========================================================================
    # Section 3: 純粋ベクターマスク拡大比較（全収録グリフ & 幾何学構造）
    # ==========================================================================
    y_cursor += 10
    draw.text(
        (40, y_cursor),
        "【3】純粋グリフ骨格・セグメント先端形状（35°カット＋18uフラット面）・全収録文字 (0-9, ', :, -, .) 拡大検証",
        fill=(130, 220, 255),
        font=f_sec,
    )
    y_cursor += 34

    box_h = 390
    draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + box_h)], radius=8, fill=(20, 23, 30), outline=(55, 65, 85))

    glyph_samples = [
        ("FDS7Strict-SLR (0.0° 直立)", "FDS7_Strict_SLR (80s 0°)", (120, 220, 255)),
        ("FDS7Strict-Compact (-7.0° 前傾)", "FDS7_Strict_Compact (80s -7°)", (255, 210, 110)),
        ("FDS7Classic-BoldItalic [旧 DSEG7 (-11.5°)]", "DSEG7_Italic (7-Segment)", (180, 150, 150)),
    ]

    sample_text = "'0123456789 - : ."
    for idx, (label, ftype, col) in enumerate(glyph_samples):
        ry = y_cursor + 18 + idx * 122
        draw.text((60, ry), label, fill=col, font=f_label)
        fpath, shear = get_font_file_and_shear(ftype)
        # 大きめのサイズでマスクを直接レンダリング
        mask, mw, mh = render_date_mask(sample_text, fpath, font_size=68, shear_deg=shear)
        mask_np = np.asarray(mask, dtype=np.float32) / 255.0
        rgb_mask = np.zeros((mh, mw, 3), dtype=np.uint8)
        rgb_mask[..., 0] = (mask_np * col[0]).astype(np.uint8)
        rgb_mask[..., 1] = (mask_np * col[1]).astype(np.uint8)
        rgb_mask[..., 2] = (mask_np * col[2]).astype(np.uint8)
        canvas.paste(Image.fromarray(rgb_mask), (60, ry + 32))

    out_path = os.path.join(ASSETS_DIR, "fds7_strict_comparison_report.png")
    canvas.save(out_path)
    print(f"[OK] Saved strict comparison report: {out_path}")


if __name__ == "__main__":
    generate_strict_comparison_report()
