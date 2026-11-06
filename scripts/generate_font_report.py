"""
FilmDateStamp 厳選フォント比較レポート生成スクリプト (日・英対応 / マクロ標本仕様)
自社製実機仕様4種 ＋ 液晶等幅1種 ＋ 空想3種の計8フォントの光学感光マクロ標本レポートを生成する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

FONT_CASES = [
    {
        "title": "1. FDS_Mechanical_70s",
        "badge_en": "IN-HOUSE STRICT • 70s",
        "badge_ja": "自社製実機準拠 • 70s",
        "badge_color": (190, 145, 75),
        "font_type": "FDS_Mechanical_70s (70s Mechanical)",
        "date": "74 12 25",
        "color": "Bulb Warm Ivory",
        "desc_en": "1970s mechanical engraved dial (DIN 1451 / JIS). Canon Canodate E / Datematic.",
        "desc_ja": "1970年代機械式活字彫刻（DIN 1451 / JIS準拠）。Canon Canodate E / Datematic 実機再現",
    },
    {
        "title": "2. FDS7_Strict_Compact",
        "badge_en": "IN-HOUSE STRICT • -7.0°",
        "badge_ja": "自社製実機準拠 • -7.0°",
        "badge_color": (225, 120, 30),
        "font_type": "FDS7_Strict_Compact (80s -7°)",
        "date": "'98 12 24",
        "color": "Amber Classic",
        "desc_en": "1980s–90s compact camera standard (Suwa Seikosha -7.0° slant, W/H=0.50). Autoboy / L35AD.",
        "desc_ja": "80〜90sコンパクト機黄金期標準（諏訪精工舎準拠・前傾-7.0°・W/H=0.50）。Autoboy / ピカイチ等",
    },
    {
        "title": "3. FDS7_Strict_SLR",
        "badge_en": "IN-HOUSE STRICT • 0.0°",
        "badge_ja": "自社製実機準拠 • 0.0°",
        "badge_color": (210, 55, 45),
        "font_type": "FDS7_Strict_SLR (80s 0°)",
        "date": "'88 12 24",
        "color": "Quartz Red",
        "desc_en": "1980s SLR camera data back upright geometry (0.0° slant). Nikon MF-12/14/16 / Recordata.",
        "desc_ja": "1980s一眼レフデータバック直立標準（直立0.0°・W/H=0.50）。Nikon MF-12/14/16 / Recordata等",
    },
    {
        "title": "4. FDS_Dot_Strict",
        "badge_en": "IN-HOUSE STRICT • 5×7 DOT",
        "badge_ja": "自社製実機準拠 • 5×7 DOT",
        "badge_color": (230, 95, 25),
        "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
        "date": "'98 12 24 18:30",
        "show_time": True,
        "color": "Fuji Orange",
        "desc_en": "1990s disposable & luxury compact 5×7 tall capsule dot matrix. QuickSnap / Utsurundesu.",
        "desc_ja": "1990s写ルンです・高級コンパクト機標準（5×7縦長カプセルドット・中空0・斜め2点アポストロフィ）",
    },
    {
        "title": "5. ShareTechMono",
        "badge_en": "DIGITAL LCD • MONO",
        "badge_ja": "デジタル液晶 • 等幅",
        "badge_color": (200, 155, 30),
        "font_type": "ShareTechMono (LCD Digital)",
        "date": "'03 08 15 14:20",
        "show_time": True,
        "color": "Golden Yellow",
        "desc_en": "Late 90s–2000s early compact digital camera & Casio G-SHOCK clean monospace LCD.",
        "desc_ja": "90〜2000年代初期コンデジ・カシオG-SHOCK液晶等幅。端正なデジタルタイポグラフィ",
    },
    {
        "title": "6. Michroma",
        "badge_en": "EXPRESSIVE • SCI-FI HUD",
        "badge_ja": "空想表現 • SFテレメトリ",
        "badge_color": (35, 175, 75),
        "font_type": "Michroma (Cyber Telemetry)",
        "date": "'98 12 24 23:59",
        "show_time": True,
        "color": "Cyber Green",
        "desc_en": "80s–90s space probe & sci-fi cinema ultra-wide geometric telemetry HUD.",
        "desc_ja": "80s-90s宇宙探査機・SF映画調テレメトリ。超ワイド幾何学HUDによるレーザー感光表現",
    },
    {
        "title": "7. MochiyPopOne",
        "badge_en": "EXPRESSIVE • Y2K POP",
        "badge_ja": "空想表現 • 平成レトロ",
        "badge_color": (215, 60, 145),
        "font_type": "MochiyPopOne (Y2K Pop)",
        "date": "'98 12 24 18:30",
        "show_time": True,
        "color": "Neo Pink",
        "desc_en": "Heisei retro rounded mochi-pop typography & Purikura photo booth neon exposure.",
        "desc_ja": "平成レトロ・お餅のように角が丸く膨らんだ極太ポップ丸文字。プリクラ電飾露光",
    },
    {
        "title": "8. EagleLake",
        "badge_en": "EXPRESSIVE • ARCANE",
        "badge_ja": "空想表現 • 魔導古文書",
        "badge_color": (185, 35, 45),
        "font_type": "EagleLake (Arcane Script)",
        "date": "'98 12 24",
        "color": "Crimson Red",
        "desc_en": "Alchemical ledger & ancient manuscript calligraphic script with crimson halation.",
        "desc_ja": "錬金術師の野帳・古文書インク筆記。生々しい毛筆の太細と深紅のハレーション刻印",
    },
]


def _make_specimen_strip(font_type: str, date_str: str, color_name: str, show_time: bool, target_w: int, target_h: int) -> Image.Image:
    """高解像度ベースで光学焼き付けを行い、文字が大きく鮮明に見えるよう右下領域をマクロクロップする"""
    render_w, render_h = 840, 360
    rng = np.random.default_rng(42)

    # フィルム暗部ベース + 微細な銀塩グレイン背景
    grad_x = np.linspace(0.0, 1.0, render_w, dtype=np.float32)[None, :]
    grad_y = np.linspace(0.0, 1.0, render_h, dtype=np.float32)[:, None]
    r = 14.0 + 18.0 * grad_x + 6.0 * grad_y
    g = 15.0 + 14.0 * grad_x + 5.0 * grad_y
    b = 20.0 + 12.0 * grad_x + 8.0 * grad_y
    base = np.stack([r, g, b], axis=-1)
    grain = rng.normal(0.0, 2.2, size=base.shape).astype(np.float32)
    base_uint8 = np.clip(base + grain, 0, 255).astype(np.uint8)
    bg_img = Image.fromarray(base_uint8, mode="RGB")

    cfg = DateStampConfig(
        font_type=font_type,
        date_string=date_str,
        show_time=show_time,
        preset_color=color_name,
        font_scale=2.25,
        margin=0.75,
        exposure_intensity=1.05,
        core_glow=0.55 if "EagleLake" in font_type else 1.00,
        halation=0.75 if "EagleLake" in font_type else 1.10,
    )
    stamped = render_film_date_stamp(bg_img, config=cfg, seed=42)

    # 右下のスタンプ領域をターゲット比率で切り出して拡大（マクロ観察）
    crop_h = 130
    crop_w = int(round(crop_h * (target_w / target_h)))
    left = max(0, render_w - crop_w - 8)
    top = max(0, render_h - crop_h - 6)
    cropped = stamped.crop((left, top, left + crop_w, top + crop_h))
    return cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)


def render_font_board(is_english: bool = False) -> Image.Image:
    card_w = 620
    card_h = 215
    cols = 2
    rows = (len(FONT_CASES) + cols - 1) // cols

    padding = 30
    header_h = 100
    total_w = padding * 3 + card_w * cols
    total_h = header_h + padding + (card_h + padding) * rows

    canvas = Image.new("RGB", (total_w, total_h), (14, 16, 22))
    draw = ImageDraw.Draw(canvas)

    code_font_path = os.path.join(PROJECT_DIR, "fonts/ShareTechMono-Regular.ttf")
    meta_font = ImageFont.truetype(code_font_path, 13) if os.path.exists(code_font_path) else ImageFont.load_default()

    if is_english:
        f_title = "C:/Windows/Fonts/segoeuib.ttf"
        f_sub = "C:/Windows/Fonts/segoeui.ttf"
        title_font = ImageFont.truetype(f_title, 26) if os.path.exists(f_title) else ImageFont.load_default()
        subtitle_font = ImageFont.truetype(f_sub, 15) if os.path.exists(f_sub) else ImageFont.load_default()
        card_title_font = ImageFont.truetype(f_title, 18) if os.path.exists(f_title) else ImageFont.load_default()
        card_desc_font = ImageFont.truetype(f_sub, 13) if os.path.exists(f_sub) else ImageFont.load_default()
        badge_font = ImageFont.truetype(f_title, 11) if os.path.exists(f_title) else ImageFont.load_default()

        hdr_title = "FilmDateStamp - Curated Typography Macro Specimens (8 Fonts)"
        hdr_sub = "4 In-House Hardware-Accurate Fonts + 1 Digital Monospace LCD + 3 Expressive / Sci-Fi Fonts (with Visual Size Normalization)"
    else:
        jp_candidates = ["C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/msgothic.ttc"]
        jp_path = next((c for c in jp_candidates if os.path.exists(c)), None)
        title_font = ImageFont.truetype(jp_path, 25) if jp_path else ImageFont.load_default()
        subtitle_font = ImageFont.truetype(jp_path, 14) if jp_path else ImageFont.load_default()
        card_title_font = ImageFont.truetype(jp_path, 17) if jp_path else ImageFont.load_default()
        card_desc_font = ImageFont.truetype(jp_path, 12) if jp_path else ImageFont.load_default()
        badge_font = ImageFont.truetype(jp_path, 11) if jp_path else ImageFont.load_default()

        hdr_title = "FilmDateStamp - 厳選8フォント 光学感光マクロ標本 (v1.0.0)"
        hdr_sub = "実機幾何学完全準拠の自社製フォント4種 ＋ 液晶等幅1種 ＋ 空想表現3種（視覚サイズ自動正規化対応）"

    draw.text((padding, 25), hdr_title, fill=(255, 255, 255), font=title_font)
    draw.text((padding, 65), hdr_sub, fill=(170, 180, 195), font=subtitle_font)
    draw.line([(padding, 95), (total_w - padding, 95)], fill=(40, 48, 64), width=1)

    for idx, tc in enumerate(FONT_CASES):
        col = idx % cols
        row = idx // cols

        x = padding + col * (card_w + padding)
        y = header_h + padding + row * (card_h + padding)

        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=12, fill=(20, 24, 32), outline=(48, 56, 72))

        # タイトル
        draw.text((x + 18, y + 14), tc["title"], fill=(245, 248, 255), font=card_title_font)

        # バッジ（右上）
        badge_text = tc["badge_en"] if is_english else tc["badge_ja"]
        bc = tc["badge_color"]
        bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
        bw = (bbox[2] - bbox[0]) + 20
        bh = 24
        bx = x + card_w - 18 - bw
        by = y + 14
        draw.rounded_rectangle(
            [(bx, by), (bx + bw, by + bh)],
            radius=6,
            fill=(int(bc[0] * 0.22), int(bc[1] * 0.22), int(bc[2] * 0.22)),
            outline=bc,
        )
        draw.text((bx + 10, by + 4), badge_text, fill=(250, 245, 240), font=badge_font)

        # 解説文
        desc = tc["desc_en"] if is_english else tc["desc_ja"]
        draw.text((x + 18, y + 44), desc, fill=(165, 175, 192), font=card_desc_font)

        # マクロ標本ストリップ
        pv_w = card_w - 36
        pv_h = 122
        pv_x = x + 18
        pv_y = y + 74

        specimen = _make_specimen_strip(tc["font_type"], tc["date"], tc["color"], tc.get("show_time", False), pv_w, pv_h)
        canvas.paste(specimen, (pv_x, pv_y))
        draw.rounded_rectangle([(pv_x, pv_y), (pv_x + pv_w, pv_y + pv_h)], radius=6, outline=(68, 78, 98))

        # ストリップ左上にメタ情報オーバーレイ
        meta_label = f"Palette: {tc['color']}  |  Input: \"{tc['date']}\""
        draw.text((pv_x + 12, pv_y + 10), meta_label, fill=(150, 162, 182), font=meta_font)

    return canvas


def generate_font_comparison_report():
    print("Generating Japanese font comparison report...")
    canvas_ja = render_font_board(is_english=False)
    out_ja = os.path.join(ASSETS_DIR, "font_comparison_report_v2.png")
    canvas_ja.save(out_ja, quality=95)
    print(f"Saved: {out_ja}")

    print("Generating English font comparison report...")
    canvas_en = render_font_board(is_english=True)
    out_en = os.path.join(ASSETS_DIR, "font_comparison_report_en.png")
    canvas_en.save(out_en, quality=95)
    print(f"Saved: {out_en}")


if __name__ == "__main__":
    generate_font_comparison_report()
