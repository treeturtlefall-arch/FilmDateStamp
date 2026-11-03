"""
FilmDateStamp 新プリセット・ショーケース画像生成スクリプト
全スタイルプリセット（Japanese, American, European, Hong Kong, Y2K など）を
実寸フィルム写真風キャンバスに焼き付けて一覧比較できる画像を生成する。
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import STYLE_PRESETS, DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_presets_showcase():
    presets_to_render = [
        ("Japanese Tokyo 90s", "90年代日本の街角・日常スナップ（'YY MM DD / 7セグ斜体 / アンバー）"),
        ("Japanese Snap (Disposable)", "写ルンです風使い捨てカメラ（'YY MM DD HH:MM / 縦長ドット / オレンジ）"),
        ("American West Coast", "90s西海岸・ロードトリップ（MM DD 'YY / 7セグ斜体 / ゴールデン）"),
        ("American 80s (Red Quartz)", "80年代モーテル・ホームビデオ感（MM DD 'YY / 7セグ直立 / クォーツレッド）"),
        ("European Classic (Paris/Berlin)", "欧州の石畳・上品な佇まい（DD.MM.YY / 7セグ直立 / 控えめアンバー）"),
        ("Hong Kong Neon (90s Cinema)", "90年代香港ネオン映画調（'YY MM DD / 14セグ斜体 / サイバーグリーン）"),
        ("Y2K Digicam (Early 2000s)", "2000年代初期コンデジLCD液晶（'YY MM DD HH:MM / 液晶等幅 / ゴールデン）"),
        ("Compact Fine Dot (Minimal)", "超高精細ドットマトリクス（'YY MM DD HH:MM / 高精細ドット / オレンジ）"),
    ]

    card_w = 620
    card_h = 240
    cols = 2
    rows = (len(presets_to_render) + cols - 1) // cols

    padding = 30
    header_h = 100
    total_w = padding * 3 + card_w * cols
    total_h = header_h + padding + (card_h + padding) * rows

    canvas = Image.new("RGB", (total_w, total_h), (18, 20, 24))
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

    title_font = ImageFont.truetype(jp_font_path, 26) if jp_font_path else ImageFont.load_default()
    subtitle_font = ImageFont.truetype(jp_font_path, 15) if jp_font_path else ImageFont.load_default()
    card_title_font = ImageFont.truetype(jp_font_path, 18) if jp_font_path else ImageFont.load_default()
    card_desc_font = ImageFont.truetype(jp_font_path, 13) if jp_font_path else ImageFont.load_default()

    draw.text((padding, 25), "FilmDateStamp - 新スタイルプリセット ショーケース", fill=(255, 255, 255), font=title_font)
    draw.text((padding, 65), "地域・文化・時代を想起させる日付スタンププリセットのレンダリング一覧", fill=(170, 180, 195), font=subtitle_font)
    draw.line([(padding, 95), (total_w - padding, 95)], fill=(50, 56, 70), width=2)

    for idx, (preset_name, desc) in enumerate(presets_to_render):
        col = idx % cols
        row = idx // cols

        x = padding + col * (card_w + padding)
        y = header_h + padding + row * (card_h + padding)

        # カード外枠
        draw.rounded_rectangle([(x, y), (x + card_w, y + card_h)], radius=10, fill=(26, 30, 38), outline=(50, 56, 70))

        # カードヘッダー情報
        draw.text((x + 18, y + 14), preset_name, fill=(240, 245, 255), font=card_title_font)
        draw.text((x + 18, y + 42), desc, fill=(150, 160, 175), font=card_desc_font)

        # プレビュー画像枠（右下にスタンプを配置）
        pv_w = card_w - 36
        pv_h = 160
        pv_x = x + 18
        pv_y = y + 66

        # 背景画像：夜景〜夕暮れ風グラデーションフィルム
        pv_img = Image.new("RGB", (pv_w, pv_h), (25, 28, 35))
        pvd = ImageDraw.Draw(pv_img)
        # 背景グラデーション
        for px in range(pv_w):
            factor = px / pv_w
            r = int(20 + 40 * factor)
            g = int(24 + 30 * factor)
            b = int(35 + 20 * factor)
            pvd.line([(px, 0), (px, pv_h)], fill=(r, g, b))

        # プリセット設定を適用してスタンプを焼き付け
        cfg = DateStampConfig(style_preset=preset_name)
        cfg.apply_style_preset_if_set()

        stamped_pv = render_film_date_stamp(pv_img, config=cfg)
        canvas.paste(stamped_pv, (pv_x, pv_y))
        # プレビュー枠線
        draw.rounded_rectangle([(pv_x, pv_y), (pv_x + pv_w, pv_y + pv_h)], radius=4, outline=(70, 78, 95))

    out_file = os.path.join(ASSETS_DIR, "presets_showcase.png")
    canvas.save(out_file)
    print(f"Showcase image successfully saved to: {out_file}")


if __name__ == "__main__":
    generate_presets_showcase()
