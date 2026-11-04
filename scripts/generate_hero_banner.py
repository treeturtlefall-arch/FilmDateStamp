"""
FilmDateStamp 公式ヒーローバナー生成スクリプト (ブラッシュアップ版)
candidate/DSC00004.JPG (SO505i 2003年実写) をベースに、
プロ仕様のグラフィックデザイン・タイポグラフィ・ルーペ拡大（Macro View）を
統合した公式ヒーローバナー (assets/hero_banner.png) を生成する。
"""
import os
import sys
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. 写真読み込みとスタンプ焼き付け
img_path = os.path.join(PROJECT_DIR, "candidate", "DSC00004.JPG")
base_img = Image.open(img_path).convert("RGB")

# スタンプ設定: Japanese Tokyo 90s ('03 10  2)
cfg = DateStampConfig(style_preset="Japanese Tokyo 90s")
cfg.apply_style_preset_if_set()
cfg.date_string = "'03 10  2"
stamped_img = render_film_date_stamp(base_img, cfg)

# 2. ヒーローバナーのキャンバス作成 (1280 x 680)
banner_w = 1280
banner_h = 680
crop_y_start = 960 - banner_h  # 280
crop_box = (0, crop_y_start, 1280, 960)
banner = stamped_img.crop(crop_box)

# 3. ルーペ拡大 (Macro Inspection) の作成
# スタンプの中心: X=1158, Y_banner = 901 - 280 = 621
zoom_cx = 1158
zoom_cy = 621
crop_r = 105  # 半径105px (直径210px)

zoom_box = (zoom_cx - crop_r, zoom_cy - crop_r, zoom_cx + crop_r, zoom_cy + crop_r)
zoom_crop = banner.crop(zoom_box)

zoom_factor = 2.05
loupe_size = int(crop_r * 2 * zoom_factor)  # ~430px
zoom_resized = zoom_crop.resize((loupe_size, loupe_size), Image.Resampling.LANCZOS)

# 円形マスク
mask = Image.new("L", (loupe_size, loupe_size), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.ellipse((0, 0, loupe_size, loupe_size), fill=255)

# ルーペの配置座標 (美しく収まる位置: x=740, y=130)
loupe_x = 740
loupe_y = 130
loupe_radius = loupe_size // 2
loupe_center_x = loupe_x + loupe_radius
loupe_center_y = loupe_y + loupe_radius

# ルーペ外枠リングの作成 (多層シャドウ + ゴールド/アンバーリング)
ring_pad = 14
ring_img = Image.new("RGBA", (loupe_size + ring_pad * 2, loupe_size + ring_pad * 2), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring_img)

# 外側のドロップシャドウ (多層)
rd.ellipse((ring_pad - 8, ring_pad - 8, ring_pad + loupe_size + 8, ring_pad + loupe_size + 8), outline=(0, 0, 0, 140), width=10)
rd.ellipse((ring_pad - 3, ring_pad - 3, ring_pad + loupe_size + 3, ring_pad + loupe_size + 3), outline=(0, 0, 0, 220), width=4)

# メタルアクセントリング
rd.ellipse((ring_pad - 1, ring_pad - 1, ring_pad + loupe_size + 1, ring_pad + loupe_size + 1), outline=(255, 175, 55, 255), width=3)
rd.ellipse((ring_pad + 1, ring_pad + 1, ring_pad + loupe_size - 1, ring_pad + loupe_size - 1), outline=(255, 235, 190, 220), width=1)
rd.ellipse((ring_pad + 3, ring_pad + 3, ring_pad + loupe_size - 3, ring_pad + loupe_size - 3), outline=(130, 75, 20, 180), width=1)

# ルーペ画像をバナーに合成
banner.paste(zoom_resized, (loupe_x, loupe_y), mask)
banner.paste(ring_img, (loupe_x - ring_pad, loupe_y - ring_pad), ring_img)

# 引き出し線とターゲット精密ブラケット
bdraw = ImageDraw.Draw(banner)

# スタンプの精密ブラケット (四隅のL字マーカー)
bx1, by1 = 1066, 580
bx2, by2 = 1250, 662
arm_len = 10
bracket_col = (255, 185, 70, 220)

# 左上 L
bdraw.line([(bx1, by1), (bx1 + arm_len, by1)], fill=bracket_col, width=2)
bdraw.line([(bx1, by1), (bx1, by1 + arm_len)], fill=bracket_col, width=2)
# 右上 ⅂
bdraw.line([(bx2, by1), (bx2 - arm_len, by1)], fill=bracket_col, width=2)
bdraw.line([(bx2, by1), (bx2, by1 + arm_len)], fill=bracket_col, width=2)
# 左下 ᒻ
bdraw.line([(bx1, by2), (bx1 + arm_len, by2)], fill=bracket_col, width=2)
bdraw.line([(bx1, by2), (bx1, by2 - arm_len)], fill=bracket_col, width=2)
# 右下 ᒧ
bdraw.line([(bx2, by2), (bx2 - arm_len, by2)], fill=bracket_col, width=2)
bdraw.line([(bx2, by2), (bx2, by2 - arm_len)], fill=bracket_col, width=2)

# ルーペの円周上の正確な点からブラケット左上へ引き出し線を引く
angle_rad = math.atan2(by1 - loupe_center_y, bx1 - loupe_center_x)
# 円周上の接点
line_start_x = loupe_center_x + int((loupe_radius + 2) * math.cos(angle_rad))
line_start_y = loupe_center_y + int((loupe_radius + 2) * math.sin(angle_rad))

bdraw.line([(line_start_x, line_start_y), (bx1, by1)], fill=(255, 185, 70, 200), width=2)
bdraw.ellipse((bx1 - 3, by1 - 3, bx1 + 3, by1 + 3), fill=(255, 220, 120))

# フォントの準備
def get_font(name: str, size: int):
    candidates = [
        f"C:/Windows/Fonts/{name}.ttf",
        f"C:/Windows/Fonts/{name}.ttc",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_brand = get_font("segoeuib", 48)
font_sub = get_font("segoeui", 22)
font_tag = get_font("segoeuib", 13)
font_desc = get_font("segoeui", 14)
font_loupe_hdr = get_font("segoeuib", 15)
font_loupe_sub = get_font("segoeui", 12)

# 4. 左上のブランドカード（ダークサーフェス + グラスモーフィズム）
card_w = 540
card_h = 220
card_x = 45
card_y = 45

bg_region = banner.crop((card_x, card_y, card_x + card_w, card_y + card_h))
bg_blurred = bg_region.filter(ImageFilter.GaussianBlur(radius=8))

card_overlay = Image.new("RGBA", (card_w, card_h), (12, 15, 22, 215))
cd = ImageDraw.Draw(card_overlay)

# 外枠境界線
cd.rounded_rectangle([(0, 0), (card_w - 1, card_h - 1)], radius=14, outline=(255, 255, 255, 45), width=1)
cd.line([(14, 0), (card_w - 14, 0)], fill=(255, 185, 80, 180), width=2)  # トップゴールドライン

# カード内テキスト
cd.text((28, 24), "FilmDateStamp", fill=(255, 255, 255), font=font_brand)
# バージョンバッジ
cd.rounded_rectangle([(390, 30), (475, 58)], radius=6, fill=(255, 140, 20, 45), outline=(255, 160, 40, 160), width=1)
cd.text((404, 35), "v1.0.0", fill=(255, 200, 100), font=font_tag)

# サブタイトル
cd.text((28, 86), "Optical Burn-in Engine for ComfyUI", fill=(255, 190, 70), font=font_sub)

# 説明文
cd.text((28, 122), "Physical LED halation and photosensitive emulsion saturation model.", fill=(195, 205, 220), font=font_desc)

# 機能ピルバッジ群
pills = [
    ("Optical Burn-in", (255, 120, 20)),
    ("True Halation", (255, 70, 50)),
    ("Highlight Bleed", (255, 190, 40)),
    ("8 Hardware Fonts", (100, 210, 255)),
]

pill_x = 28
pill_y = 160
for text, col in pills:
    tw = int(cd.textlength(text, font=font_tag))
    pw = tw + 20
    ph = 26
    cd.rounded_rectangle([(pill_x, pill_y), (pill_x + pw, pill_y + ph)], radius=13, fill=(col[0], col[1], col[2], 30), outline=(col[0], col[1], col[2], 120), width=1)
    cd.text((pill_x + 10, pill_y + 5), text, fill=(240, 245, 255), font=font_tag)
    pill_x += pw + 10

bg_blurred.paste(card_overlay, (0, 0), card_overlay)
banner.paste(bg_blurred, (card_x, card_y))

# 5. ルーペの上部ラベルバッジ
lbl_w = 380
lbl_h = 56
lbl_x = loupe_center_x - lbl_w // 2
lbl_y = loupe_y - 66

lbl_overlay = Image.new("RGBA", (lbl_w, lbl_h), (14, 17, 25, 230))
ld = ImageDraw.Draw(lbl_overlay)
ld.rounded_rectangle([(0, 0), (lbl_w - 1, lbl_h - 1)], radius=10, outline=(255, 170, 50, 160), width=1)
ld.text((16, 10), "PHYSICAL EMULSION MACRO VIEW (205%)", fill=(255, 200, 100), font=font_loupe_hdr)
ld.text((16, 31), "Saturated Hotspot Filament  *  Mie & Dye-Cloud Scattering", fill=(185, 195, 210), font=font_loupe_sub)

banner.paste(lbl_overlay, (lbl_x, lbl_y), lbl_overlay)

# 6. 保存
out_path = os.path.join(ASSETS_DIR, "hero_banner.png")
banner.save(out_path, quality=95)
print(f"Polished Master Hero Banner saved to: {out_path}")
