"""
FilmDateStamp 厳選フォント比較レポート生成スクリプト
自社製実機仕様4種 ＋ 液晶等幅1種 ＋ 空想3種の計8フォントのレンダリング比較レポートを生成する。
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import SUPPORTED_FONTS, DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_font_comparison_report():
    w = 1200
    card_h = 135
    start_y = 120
    test_cases = [
        {
            "name": "1. FDS_Mechanical_70s (70s Mechanical)",
            "font_type": "FDS_Mechanical_70s (70s Mechanical)",
            "date": "74 12 25",
            "color": "Bulb Warm Ivory",
            "desc": "1970年代機械式活字彫刻（DIN 1451/JIS準拠）。Canon Canodate E / Datematic 実機再現",
        },
        {
            "name": "2. FDS7_Strict_Compact (80s -7°)",
            "font_type": "FDS7_Strict_Compact (80s -7°)",
            "date": "'98 12 24 14:35",
            "color": "Amber Classic",
            "desc": "1980〜90sコンパクトカメラ黄金期標準（諏訪精工舎モジュール準拠・前傾-7.0°・スリム比率W/H=0.50）",
        },
        {
            "name": "3. FDS7_Strict_SLR (80s 0°)",
            "font_type": "FDS7_Strict_SLR (80s 0°)",
            "date": "'88 12 24",
            "color": "Quartz Red",
            "desc": "1980s一眼レフデータバック直立標準（Nikon MF-12/14/16、Olympus Recordata準拠・直立0.0°）",
        },
        {
            "name": "4. FDS_Dot_Strict (90s Dot Matrix)",
            "font_type": "FDS_Dot_Strict (90s Dot Matrix)",
            "date": "'98 12 24 18:30",
            "color": "Fuji Orange",
            "desc": "1990年代写ルンです・高級コンパクト機（5×7縦長カプセルドット・斜線なし中空0・斜め2ドットアポストロフィ）",
        },
        {
            "name": "5. ShareTechMono (LCD Digital)",
            "font_type": "ShareTechMono (LCD Digital)",
            "date": "'03 08 15 14:20",
            "color": "Golden Yellow",
            "desc": "90〜2000年代コンデジ・カシオG-SHOCK液晶等幅。端正なデジタルタイポグラフィ",
        },
        {
            "name": "6. Michroma (Cyber Telemetry)",
            "font_type": "Michroma (Cyber Telemetry)",
            "date": "'98 12 24 23:59:59",
            "color": "Cyber Green",
            "desc": "80s-90s宇宙探査機・SF映画調テレメトリ。超ワイド幾何学HUD（高解像度レーザー露光）",
        },
        {
            "name": "7. MochiyPopOne (Y2K Pop)",
            "font_type": "MochiyPopOne (Y2K Pop)",
            "date": "'98 12 24 18:30",
            "color": "Neo Pink",
            "desc": "平成レトロ・お餅のように角が丸く膨らんだ極太ポップ丸文字。プリクラ電飾露光",
        },
        {
            "name": "8. EagleLake (Arcane Script)",
            "font_type": "EagleLake (Arcane Script)",
            "date": "'98 12 24",
            "color": "Crimson Red",
            "desc": "錬金術師の野帳・古文書インク筆記。生々しい毛筆の掠れと深紅の呪印刻印",
        },
    ]

    total_h = start_y + len(test_cases) * (card_h + 15) + 30
    canvas = Image.new("RGB", (w, total_h), (18, 20, 24))
    draw = ImageDraw.Draw(canvas)

    # フォントロード
    jp_candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
    ]
    jp_font_path = None
    for cand in jp_candidates:
        if os.path.exists(cand):
            jp_font_path = cand
            break

    title_font = ImageFont.truetype(jp_font_path, 24) if jp_font_path else ImageFont.load_default()
    card_title_font = ImageFont.truetype(jp_font_path, 17) if jp_font_path else ImageFont.load_default()
    desc_font = ImageFont.truetype(jp_font_path, 14) if jp_font_path else ImageFont.load_default()
    code_font = ImageFont.truetype(os.path.join(PROJECT_DIR, "fonts/ShareTechMono-Regular.ttf"), 16)

    draw.text((40, 25), "FilmDateStamp - 厳選フォント比較レポート (v1.0.0 Production)", fill=(255, 255, 255), font=title_font)
    draw.text((40, 68), "実機幾何学自社製フォント4種 ＋ 液晶等幅1種 ＋ 空想3種による光学感光レンダリング一覧", fill=(180, 190, 205), font=desc_font)
    draw.line([(40, 100), (w - 40, 100)], fill=(60, 65, 80), width=2)

    for i, tc in enumerate(test_cases):
        cy = start_y + i * (card_h + 15)
        card_w = w - 80
        draw.rounded_rectangle([(40, cy), (40 + card_w, cy + card_h)], radius=8, fill=(26, 30, 38), outline=(50, 56, 70))

        # ラベル＆解説
        draw.text((60, cy + 14), tc["name"], fill=(240, 245, 255), font=card_title_font)
        draw.text((60, cy + 45), f"Color Preset: {tc['color']}  |  Input: \"{tc['date']}\"", fill=(255, 185, 40), font=code_font)
        draw.text((60, cy + 78), tc["desc"], fill=(180, 190, 205), font=desc_font)

        # プレビュー切り出し
        pv_w = 420
        pv_h = 95
        pv_x = w - 40 - pv_w - 20
        pv_y = cy + 20

        pv_bg = Image.new("RGB", (pv_w, pv_h), (25, 28, 35))
        pvd = ImageDraw.Draw(pv_bg)
        for px in range(pv_w):
            factor = px / pv_w
            r = int(18 + 35 * factor)
            g = int(20 + 25 * factor)
            b = int(28 + 18 * factor)
            pvd.line([(px, 0), (px, pv_h)], fill=(r, g, b))

        cfg = DateStampConfig(
            font_type=tc["font_type"],
            date_string=tc["date"],
            preset_color=tc["color"],
            font_scale=1.0,
            margin=0.8,
        )
        stamped_pv = render_film_date_stamp(pv_bg, config=cfg)
        canvas.paste(stamped_pv, (pv_x, pv_y))
        draw.rounded_rectangle([(pv_x, pv_y), (pv_x + pv_w, pv_y + pv_h)], radius=4, outline=(70, 78, 95))

    out_file = os.path.join(ASSETS_DIR, "font_comparison_report_v2.png")
    canvas.save(out_file)
    print(f"Font comparison report saved to: {out_file}")


if __name__ == "__main__":
    generate_font_comparison_report()
