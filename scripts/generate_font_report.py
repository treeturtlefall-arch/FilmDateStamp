"""
フォント比較およびアポストロフィ表示検証スクリプト (v2)
全フォントで '98 12 24 (および時刻) を実機相当の高解像度でレンダリングし、
スタンプ周辺をクロップして鮮明に比較できるレポート画像を生成する。
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_report():
    w, h = 1400, 1280
    canvas = Image.new("RGB", (w, h), (18, 20, 24))
    draw = ImageDraw.Draw(canvas)

    # タイトル・解説用フォント（Windows標準の日本語フォントを確実にロード）
    jp_font_candidates = [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Users/coffe/Documents/rec-frame-ComfyUI/fonts/ZenKakuGothicNew-Bold.ttf",
    ]
    jp_font_path = None
    for cand in jp_font_candidates:
        if os.path.exists(cand):
            jp_font_path = cand
            break

    title_font = ImageFont.truetype(jp_font_path, 26) if jp_font_path else ImageFont.load_default()
    desc_font = ImageFont.truetype(jp_font_path, 16) if jp_font_path else ImageFont.load_default()
    code_font = ImageFont.truetype(os.path.join(PROJECT_DIR, "fonts/ShareTechMono-Regular.ttf"), 19)

    draw.text((40, 25), "FilmDateStamp - フォント比較 & スマート・アポストロフィ検証レポート", fill=(255, 255, 255), font=title_font)
    draw.text((40, 68), "右側のプレビューは実寸写真 (1200x900) の右下スタンプ領域を拡大切り出ししたものです", fill=(180, 190, 205), font=desc_font)
    draw.line([(40, 105), (w - 40, 105)], fill=(60, 65, 80), width=2)

    test_cases = [
        {
            "name": "1. DSEG7_Classic (7-Segment)",
            "font_type": "DSEG7_Classic (7-Segment)",
            "date": "'98 12 24 14:35",
            "color": "Amber Classic",
            "desc": "昭和〜90年代標準7セグLED。公式アポストロフィ移植＆視覚サイズ自動正規化済み",
        },
        {
            "name": "2. DSEG7_Italic (7-Segment)",
            "font_type": "DSEG7_Italic (7-Segment)",
            "date": "'98 12 24 14:35",
            "color": "Amber Classic",
            "desc": "オートボーイ等に見られる傾斜7セグ。全フォント同一 font_scale=1.0 でサイズ統一",
        },
        {
            "name": "3. DSEG14_Classic (14-Segment)",
            "font_type": "DSEG14_Classic (14-Segment)",
            "date": "'98 12 24 14:35",
            "color": "Quartz Red",
            "desc": "高級機・オーディオ風14セグ。標準でアポストロフィ＆全記号をサポート",
        },
        {
            "name": "4. DSEG14_Italic (14-Segment)",
            "font_type": "DSEG14_Italic (14-Segment)",
            "date": "'98 12 24 14:35",
            "color": "Cyber Green",
            "desc": "傾斜14セグ。香港ネオン・ハイテク機材風の洗練された佇まい",
        },
        {
            "name": "5. VT323 (Dot Matrix) [継続採用]",
            "font_type": "VT323 (Dot Matrix)",
            "date": "'98 12 24 14:35",
            "color": "Fuji Orange",
            "desc": "写ルンですでお馴染みの縦長ドットマトリクス。温かみのある粒立ち",
        },
        {
            "name": "6. Silkscreen (Fine Dot) [新規追加]",
            "font_type": "Silkscreen (Fine Dot)",
            "date": "'98 12 24 14:35",
            "color": "Fuji Orange",
            "desc": "引き締まった超高精細スクエアドット。写ルンです以外のコンパクト機に最適",
        },
        {
            "name": "7. ShareTechMono (LCD Digital) [新規追加]",
            "font_type": "ShareTechMono (LCD Digital)",
            "date": "'98 12 24 14:35",
            "color": "Golden Yellow",
            "desc": "90〜2000年代コンデジ・カシオG-SHOCK液晶等幅。端正なアポストロフィ＆時刻",
        },
    ]

    card_h = 140
    start_y = 125

    for i, tc in enumerate(test_cases):
        cy = start_y + i * (card_h + 15)
        card_w = w - 80
        draw.rounded_rectangle([(40, cy), (40 + card_w, cy + card_h)], radius=8, fill=(28, 32, 40), outline=(50, 56, 70))

        # ラベル＆解説
        draw.text((60, cy + 16), tc["name"], fill=(240, 245, 255), font=title_font)
        draw.text((60, cy + 58), f"Color Preset: {tc['color']}  |  Input: \"{tc['date']}\"", fill=(255, 180, 50), font=code_font)
        draw.text((60, cy + 92), tc["desc"], fill=(185, 195, 210), font=desc_font)

        # スタンプ描画領域 (幅 540 x 高さ 116)
        stamp_box_x = 40 + card_w - 560
        stamp_box_y = cy + 12
        stamp_box_w = 540
        stamp_box_h = card_h - 24

        # 仮想写真 (1200x900) の右下領域として描画（フォントサイズが約36〜45pxになりディテールが鮮明に見える）
        virtual_w, virtual_h = 1200, 900
        virtual_bg = Image.new("RGB", (virtual_w, virtual_h), (18, 20, 26))
        v_draw = ImageDraw.Draw(virtual_bg)
        # 右下領域に少しグラデーションを入れる
        for x in range(virtual_w - stamp_box_w, virtual_w):
            rel_x = (x - (virtual_w - stamp_box_w)) / stamp_box_w
            val = int(14 + rel_x * 28)
            v_draw.line([(x, virtual_h - stamp_box_h), (x, virtual_h)], fill=(val, val + 2, val + 6))

        is_dot = "Dot" in tc["font_type"]
        cfg = DateStampConfig(
            font_type=tc["font_type"],
            date_string=tc["date"],
            preset_color=tc["color"],
            exposure_intensity=1.05,
            core_glow=0.50 if is_dot else 0.85,
            halation=1.0,
            font_scale=1.0,  # 全フォント共通の font_scale=1.0（自動サイズ正規化の検証）
            margin_x=0.8,
            margin_y=0.8,
            optical_burn=True,
        )

        stamped_full = render_film_date_stamp(virtual_bg, config=cfg)
        # 右下の (stamp_box_w x stamp_box_h) をクロップ
        cropped_stamp = stamped_full.crop((
            virtual_w - stamp_box_w,
            virtual_h - stamp_box_h,
            virtual_w,
            virtual_h,
        ))

        canvas.paste(cropped_stamp, (stamp_box_x, stamp_box_y))
        draw.rectangle(
            [(stamp_box_x, stamp_box_y), (stamp_box_x + stamp_box_w, stamp_box_y + stamp_box_h)],
            outline=(85, 95, 115),
            width=1,
        )

    out_path = os.path.join(ASSETS_DIR, "font_comparison_report_v2.png")
    canvas.save(out_path)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    generate_report()
