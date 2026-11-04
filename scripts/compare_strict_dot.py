"""
FDS-DotStrict (90s 実機 5×7 カプセルドットマトリクス) vs 現行ドット系フォント (VT323 / Silkscreen)
徹底比較・検証レンダリングスクリプト

検証ポイント:
1. FilmDateStamp v2.0 光学ハレーション合成（Fuji Golden Orange: (255, 115, 20)）における
   微小ギャップ（水平10u / 垂直20u）を介した「光学融合（Optical Coalescence）」の質感検証。
2. 純粋ベクターマスク形状での数字 `0`（斜線の有無）、`1`（ヒゲと台座）、`4`（クローズド三角型）、
   アポストロフィ `'`（斜め2ドット）、および縦長カプセル（Stadium: 65×80, R=32.5）形状の拡大検証。
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
    preset_color: str = "Fuji Orange",
    exposure: float = 1.05,
    core_glow: float = 0.65,
    halation: float = 1.05,
    irregularity: float = 0.85,
    font_scale: float = 1.15,
    crop_w: int = 490,
    crop_h: int = 104,
    bg_type: str = "warm_film",
) -> Image.Image:
    """仮想写真 (1280x960) の右下にスタンプを焼き付け、拡大比較用にクロップする"""
    vw, vh = 1280, 960
    bg = Image.new("RGB", (vw, vh), (18, 20, 26))
    draw = ImageDraw.Draw(bg)

    x0, y0 = vw - crop_w, vh - crop_h
    for x in range(x0, vw):
        rx = (x - x0) / max(1, crop_w)
        if bg_type == "warm_film":
            r = int(28 + rx * 34)
            g = int(22 + rx * 24)
            b = int(18 + rx * 18)
        elif bg_type == "daylight_foliage":
            r = int(22 + rx * 28)
            g = int(34 + rx * 36)
            b = int(24 + rx * 22)
        else:
            r = int(16 + rx * 24)
            g = int(18 + rx * 22)
            b = int(24 + rx * 18)
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
        font_scale=font_scale,
        margin_x=0.75,
        margin_y=0.75,
        optical_burn=True,
    )
    stamped = render_film_date_stamp(bg, config=cfg, seed=42)
    return stamped.crop((x0, y0, vw, vh))


def generate_strict_dot_comparison_report():
    W, H = 1600, 1480
    canvas = Image.new("RGB", (W, H), (15, 17, 22))
    draw = ImageDraw.Draw(canvas)

    f_title = load_jp_font(25)
    f_sub = load_jp_font(15)
    f_sec = load_jp_font(20)
    f_label = load_jp_font(17)
    f_small = load_jp_font(14)

    # ヘッダー
    draw.text(
        (40, 24),
        "FilmDateStamp - 『FDS-DotStrict』写ルンです・90sコンパクト機 実機ドットマトリクス光学比較検証レポート",
        fill=(245, 248, 255),
        font=f_title,
    )
    draw.text(
        (40, 62),
        "5×7 スリムグリッド (W/H=0.537)・縦長カプセルドット (65×80, R=32.5)・斜線なし中空『0』・斜め2ドット『'』・Fuji Golden Orange (255,115,20) 光学融合の検証",
        fill=(175, 185, 205),
        font=f_sub,
    )
    draw.line([(40, 96), (W - 40, 96)], fill=(55, 62, 78), width=2)

    # ==========================================================================
    # Section 1: FilmDateStamp v2.0 光学ハレーション＆光学融合（Optical Coalescence）比較
    # ==========================================================================
    y_cursor = 112
    draw.text(
        (40, y_cursor),
        "【1】光学ハレーション合成（Fuji Golden Orange: 255, 115, 20）比較：隣接ドットの「光学融合（Optical Coalescence）」検証",
        fill=(255, 175, 80),
        font=f_sec,
    )
    y_cursor += 34

    dot_rows = [
        {
            "title": "NEW: FDSDotStrict-Regular (5×7 カプセル 65×80 / W:H=0.537)",
            "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
            "badge_color": (210, 85, 20),
            "note": "★実機準拠: 斜線なしの中空『0』、鋭い斜め2ドット『'』、微小ギャップ(10u/20u)で隣接ドットが乳剤内で滑らかに光学融合",
        },
        {
            "title": "OLD 1: VT323-Regular [CRT画面用] (W:H≈0.62 / 斜線入りゼロ)",
            "font_type": "VT323 (Dot Matrix)",
            "badge_color": (120, 65, 55),
            "note": "▲従来版1: 数字『0』にパソコン画面用の斜線(ø)が入り、『80sメインフレーム画面』のように見えてリアリズムが崩壊",
        },
        {
            "title": "OLD 2: Silkscreen-Regular [Web用極小ピクセル] (正方形 / W:H≈0.70)",
            "font_type": "Silkscreen (Fine Dot)",
            "badge_color": (95, 75, 110),
            "note": "▲従来版2: 完全な正方形ドットで横広(W/H≈0.70)のため、ハレーションをかけてもファミコン画面のようなカクカク感が残る",
        },
    ]

    for row in dot_rows:
        card_h = 172
        draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + card_h)], radius=8, fill=(24, 28, 36), outline=(52, 60, 76))
        draw.rounded_rectangle([(55, y_cursor + 12), (55 + 610, y_cursor + 42)], radius=4, fill=row["badge_color"])
        draw.text((65, y_cursor + 15), row["title"], fill=(255, 255, 255), font=f_label)
        draw.text((680, y_cursor + 17), row["note"], fill=(215, 225, 240), font=f_small)

        # 左プレビュー: '98 07 25 (0と'の形状・標準露光)
        crop1 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'98 07 25",
            preset_color="Fuji Orange",
            exposure=1.00,
            core_glow=0.55,
            halation=1.00,
            crop_w=450,
            crop_h=102,
            bg_type="warm_film",
        )
        canvas.paste(crop1, (55, y_cursor + 54))
        draw.rectangle([(55, y_cursor + 54), (55 + 450, y_cursor + 54 + 102)], outline=(80, 90, 110))
        draw.text((62, y_cursor + 58), "Standard Snap ('98 07 25) - Check '0' & '''", fill=(255, 210, 150), font=f_small)

        # 中央プレビュー: '00 10 20 (ゼロ連続＆強露光での光学融合検証)
        crop2 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'00 10 20",
            preset_color="Fuji Orange",
            exposure=1.20,
            core_glow=0.85,
            halation=1.35,
            crop_w=450,
            crop_h=102,
            bg_type="daylight_foliage",
        )
        canvas.paste(crop2, (525, y_cursor + 54))
        draw.rectangle([(525, y_cursor + 54), (525 + 450, y_cursor + 54 + 102)], outline=(80, 90, 110))
        draw.text((532, y_cursor + 58), "Optical Coalescence ('00 10 20) - Hollow '0' vs Slashed '0'", fill=(180, 240, 190), font=f_small)

        # 右プレビュー: '98 12 24 18:30 (写ルンです日時フルフォーマット)
        crop3 = render_stamp_crop(
            font_type=row["font_type"],
            date_str="'98 12 24 18:30",
            preset_color="Fuji Orange",
            exposure=1.05,
            core_glow=0.65,
            halation=1.10,
            crop_w=545,
            crop_h=102,
            bg_type="dark_photo",
        )
        canvas.paste(crop3, (995, y_cursor + 54))
        draw.rectangle([(995, y_cursor + 54), (995 + 545, y_cursor + 54 + 102)], outline=(80, 90, 110))
        draw.text((1002, y_cursor + 58), "Disposable Full Date+Time ('98 12 24 18:30)", fill=(175, 195, 225), font=f_small)

        y_cursor += card_h + 14

    # ==========================================================================
    # Section 2: 純粋ベクターマスク拡大比較（全収録グリフ & カプセルドット幾何構造）
    # ==========================================================================
    y_cursor += 8
    draw.text(
        (40, y_cursor),
        "【2】純粋グリフマスク拡大比較：縦長カプセルドット（Stadium 65×80, R=32.5）と全収録文字 (0-9, ', :, -, ., /) の骨格検証",
        fill=(130, 220, 255),
        font=f_sec,
    )
    y_cursor += 34

    box_h = 440
    draw.rounded_rectangle([(40, y_cursor), (W - 40, y_cursor + box_h)], radius=8, fill=(20, 23, 30), outline=(55, 65, 85))

    glyph_samples = [
        (
            "NEW: FDSDotStrict-Regular (5×7 縦長カプセル / 中空『0』 / ヒゲ+台座『1』 / クローズド『4』 / 斜め2ドット『'』)",
            "FDS_Dot_Strict (90s Dot Matrix)",
            (255, 165, 70),
        ),
        (
            "OLD 1: VT323-Regular (CRTターミナル用 / 『0』に斜線が入る致命的欠陥 / アポストロフィが極小)",
            "VT323 (Dot Matrix)",
            (210, 130, 120),
        ),
        (
            "OLD 2: Silkscreen-Regular (Web用正方形ピクセル / カクカクした角ばり / 1が単なる縦棒でバランス不均一)",
            "Silkscreen (Fine Dot)",
            (175, 155, 210),
        ),
    ]

    sample_text = "'0123456789 - : . /"
    for idx, (label, ftype, col) in enumerate(glyph_samples):
        ry = y_cursor + 18 + idx * 140
        draw.text((60, ry), label, fill=col, font=f_label)
        fpath, shear = get_font_file_and_shear(ftype)
        mask, mw, mh = render_date_mask(sample_text, fpath, font_size=64, shear_deg=shear)
        mask_np = np.asarray(mask, dtype=np.float32) / 255.0
        rgb_mask = np.zeros((mh, mw, 3), dtype=np.uint8)
        rgb_mask[..., 0] = (mask_np * col[0]).astype(np.uint8)
        rgb_mask[..., 1] = (mask_np * col[1]).astype(np.uint8)
        rgb_mask[..., 2] = (mask_np * col[2]).astype(np.uint8)
        canvas.paste(Image.fromarray(rgb_mask), (60, ry + 34))

    # ==========================================================================
    # Section 3: ミクロ拡大検証（単一文字 '0と光学融合プロセスの可視化）
    # ==========================================================================
    micro_x = 1090
    micro_y = y_cursor + 20
    micro_w = 445
    micro_h = 400
    draw.rounded_rectangle([(micro_x, micro_y), (micro_x + micro_w, micro_y + micro_h)], radius=6, fill=(28, 32, 42), outline=(85, 100, 130))
    draw.text((micro_x + 16, micro_y + 12), "【ミクロ拡大】カプセル形状 ＆ 光学融合の仕組み", fill=(255, 220, 130), font=f_label)

    # FDSDotStrict の "'04" を超高解像度でマスク描画
    fds_path, _ = get_font_file_and_shear("FDS_Dot_Strict (90s Dot Matrix)")
    big_mask, bmw, bmh = render_date_mask("'04", fds_path, font_size=155, shear_deg=0.0)
    bm_np = np.asarray(big_mask, dtype=np.float32) / 255.0
    bm_rgb = np.zeros((bmh, bmw, 3), dtype=np.uint8)
    bm_rgb[..., 0] = (bm_np * 255).astype(np.uint8)
    bm_rgb[..., 1] = (bm_np * 180).astype(np.uint8)
    bm_rgb[..., 2] = (bm_np * 80).astype(np.uint8)
    canvas.paste(Image.fromarray(bm_rgb), (micro_x + 24, micro_y + 52))
    draw.text((micro_x + 24, micro_y + 58 + bmh), "▲ 純粋ベクター: 縦長カプセル (65×80, R=32.5)", fill=(200, 210, 230), font=f_small)

    # 光学融合後の拡大プレビュー
    fused_crop = render_stamp_crop(
        font_type="FDS_Dot_Strict (90s Dot Matrix)",
        date_str="'04 12",
        preset_color="Fuji Orange",
        exposure=1.15,
        core_glow=0.75,
        halation=1.20,
        font_scale=1.65,
        crop_w=395,
        crop_h=120,
        bg_type="warm_film",
    )
    canvas.paste(fused_crop, (micro_x + 24, micro_y + 225))
    draw.rectangle([(micro_x + 24, micro_y + 225), (micro_x + 24 + 395, micro_y + 225 + 120)], outline=(210, 110, 40))
    draw.text((micro_x + 24, micro_y + 355), "▲ 露光後: 隣接ドットが乳剤内で架橋・光学融合！", fill=(255, 185, 100), font=f_small)

    out_path = os.path.join(ASSETS_DIR, "fds_dot_strict_comparison_report.png")
    canvas.save(out_path)
    print(f"[OK] Saved strict dot comparison report: {out_path}")


if __name__ == "__main__":
    generate_strict_dot_comparison_report()
