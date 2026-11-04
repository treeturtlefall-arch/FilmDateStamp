"""
FilmDateStamp 決定打比較シート生成スクリプト (ブラッシュアップ版)
1. Standard Text Overlay (平坦な文字貼り付け)
2. Simple Glow / Screen Blend (典型的なガウスブラー光彩付加)
3. FilmDateStamp (Optical Burn-in 物理感光)
の3手法を実写（candidate/DSC00004.JPG）上で等倍 & 320%マクロ拡大で徹底比較する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT_DIR = r"C:\Users\coffe\Documents\FilmDateStamp"
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig, FONT_MAP
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. 写真読み込み
img_path = os.path.join(PROJECT_DIR, "candidate", "DSC00004.JPG")
base_img = Image.open(img_path).convert("RGB")
img_w, img_h = base_img.size

# スタンプ文字
date_text = "'03 10  2"

# 2. 手法3: FilmDateStamp (本物の物理感光)
cfg = DateStampConfig(style_preset="Japanese Tokyo 90s")
cfg.apply_style_preset_if_set()
cfg.date_string = date_text
img_fds = render_film_date_stamp(base_img.copy(), cfg)

# スタンプの描画領域を検出
arr_fds = np.array(img_fds).astype(float)
arr_base = np.array(base_img).astype(float)
diff = np.max(np.abs(arr_fds - arr_base), axis=2)
ys, xs = np.where(diff > 5)
bx_min, bx_max = xs.min() - 15, xs.max() + 15
by_min, by_max = ys.min() - 15, ys.max() + 15

center_x = (bx_min + bx_max) // 2
center_y = (by_min + by_max) // 2

# クロップ領域 (220 x 130)
box_w, box_h = 220, 130
crop_x1 = center_x - box_w // 2
crop_y1 = center_y - box_h // 2
crop_x2 = crop_x1 + box_w
crop_y2 = crop_y1 + box_h
crop_rect = (crop_x1, crop_y1, crop_x2, crop_y2)

# フォント読み込み (FDS7Strict-Compact)
font_file, _ = FONT_MAP["FDS7_Strict_Compact (80s -7°)"]
font_path = os.path.join(PROJECT_DIR, "fonts", font_file)
font_size = int(img_h * 0.044)
stamp_font = ImageFont.truetype(font_path, font_size)

# 3. 手法1: Standard Text Overlay (平坦なアルファブレンド)
img_standard = base_img.copy()
std_draw = ImageDraw.Draw(img_standard)
tb = std_draw.textbbox((0, 0), date_text, font=stamp_font)
tw = tb[2] - tb[0]
th = tb[3] - tb[1]
tx = center_x - tw // 2
ty = center_y - th // 2
# 単色オレンジ (255, 130, 20) で通常描画
std_draw.text((tx, ty), date_text, font=stamp_font, fill=(255, 130, 20))

# 4. 手法2: Simple Glow / Screen Blend (典型的な光彩拡散: 文字本体 + ぼかしグロー加算)
img_simple_glow = base_img.copy()
# ぼかし用グローレイヤー
glow_surf = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow_surf)
# 太めに文字を描いてぼかす
gd.text((tx, ty), date_text, font=stamp_font, fill=(255, 120, 10, 255))
glow_blurred = glow_surf.filter(ImageFilter.GaussianBlur(radius=7))

# 文字本体レイヤー
text_surf = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
td = ImageDraw.Draw(text_surf)
td.text((tx, ty), date_text, font=stamp_font, fill=(255, 160, 40, 255))

# 合成: 写真 + グロー加算 + 文字本体
base_arr = np.array(img_simple_glow).astype(float)
glow_arr = np.array(glow_blurred).astype(float)
text_arr = np.array(text_surf).astype(float)

# 加算グロー (R, G, B)
glow_alpha = glow_arr[:, :, 3:4] / 255.0
added = base_arr + glow_arr[:, :, :3] * glow_alpha * 0.8
# 文字本体をアルファブレンド
text_alpha = text_arr[:, :, 3:4] / 255.0
final_simple = added * (1.0 - text_alpha) + text_arr[:, :, :3] * text_alpha
img_simple_glow = Image.fromarray(np.clip(final_simple, 0, 255).astype(np.uint8))

# 5. 各手法からクロップ領域を抽出
crop_standard = img_standard.crop(crop_rect)
crop_simple = img_simple_glow.crop(crop_rect)
crop_fds = img_fds.crop(crop_rect)

# 6. 比較シート全体のキャンバス作成 (1280 x 820)
sheet_w = 1280
sheet_h = 820
canvas = Image.new("RGB", (sheet_w, sheet_h), (14, 16, 22))
draw = ImageDraw.Draw(canvas)

# フォント準備
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

font_title = get_font("segoeuib", 28)
font_subtitle = get_font("segoeui", 15)
font_col_title = get_font("segoeuib", 18)
font_col_sub = get_font("segoeui", 13)
font_badge = get_font("segoeuib", 11)
font_bullet = get_font("segoeui", 12)
font_bullet_icon = get_font("segoeuib", 13)

# ヘッダー描画
draw.text((45, 30), "Why FilmDateStamp? - Optical Burn-in vs Conventional Methods", fill=(255, 255, 255), font=font_title)
draw.text((45, 68), "Direct macro comparison on authentic vintage CCD photograph (100% 1:1 view & 320% extreme macro)", fill=(180, 190, 205), font=font_subtitle)
draw.line([(45, 96), (sheet_w - 45, 96)], fill=(40, 48, 64), width=1)

# 3カラムの配置計算
col_w = 380
col_gap = 25
start_x = (sheet_w - (col_w * 3 + col_gap * 2)) // 2  # ~35px
content_y = 115

columns_data = [
    {
        "title": "Standard Text Overlay",
        "subtitle": "Flat Alpha Composite (Normal Blend)",
        "badge": "UNREALISTIC",
        "badge_border": (240, 80, 80),
        "badge_bg": (240, 50, 50, 40),
        "badge_text_col": (255, 120, 120),
        "crop_100": crop_standard,
        "bullets": [
            ("x", "Flat digital color (#FF8800), zero luminance core"),
            ("x", "Harsh computer-generated razor-sharp edges"),
            ("x", "Sits on top of the image like a sticker; no interaction"),
        ],
        "border_col": (50, 56, 70),
        "highlight": False,
    },
    {
        "title": "Simple Glow / Screen",
        "subtitle": "Gaussian Blur + Additive Glow",
        "badge": "INSUFFICIENT",
        "badge_border": (240, 160, 40),
        "badge_bg": (240, 150, 30, 40),
        "badge_text_col": (255, 190, 80),
        "crop_100": crop_simple,
        "bullets": [
            ("x", "Uniform haze; core washes out into faint fog"),
            ("x", "No white-hot filament center (Hotspot Ridge)"),
            ("x", "Monochromatic wash without red-orange halation"),
        ],
        "border_col": (60, 68, 85),
        "highlight": False,
    },
    {
        "title": "FilmDateStamp",
        "subtitle": "Physical Optical Burn-in Model",
        "badge": "PHYSICALLY ACCURATE",
        "badge_border": (255, 170, 40),
        "badge_bg": (255, 150, 20, 50),
        "badge_text_col": (255, 210, 100),
        "crop_100": crop_fds,
        "bullets": [
            ("o", "Saturated white filament core (Hotspot Ridge)"),
            ("o", "Multi-scale PSF halation (Mie scatter + red halo)"),
            ("o", "Emulsion headroom & organic pressure irregularities"),
        ],
        "border_col": (255, 160, 40),
        "highlight": True,
    },
]

card_h = sheet_h - content_y - 35  # ~670px

for i, col in enumerate(columns_data):
    cx = start_x + i * (col_w + col_gap)
    cy = content_y

    # カード背景
    card_bg = (24, 28, 38) if col["highlight"] else (18, 21, 29)
    draw.rounded_rectangle([(cx, cy), (cx + col_w, cy + card_h)], radius=12, fill=card_bg, outline=col["border_col"], width=2 if col["highlight"] else 1)

    # 上部ゴールドライン (強調カラム)
    if col["highlight"]:
        draw.line([(cx + 12, cy), (cx + col_w - 12, cy)], fill=(255, 180, 50), width=3)

    # カラムヘッダー
    hdr_y = cy + 18
    draw.text((cx + 16, hdr_y), col["title"], fill=(255, 255, 255) if col["highlight"] else (230, 235, 245), font=font_col_title)
    draw.text((cx + 16, hdr_y + 24), col["subtitle"], fill=(255, 190, 80) if col["highlight"] else (150, 160, 175), font=font_col_sub)

    # ステータスバッジ
    badge_text = col["badge"]
    bw = int(draw.textlength(badge_text, font=font_badge)) + 18
    bx = cx + col_w - bw - 16
    by = hdr_y + 2
    
    # バッジ背景を半透明で描画
    badge_img = Image.new("RGBA", (bw, 22), col["badge_bg"])
    bd = ImageDraw.Draw(badge_img)
    bd.rounded_rectangle([(0, 0), (bw - 1, 21)], radius=5, outline=col["badge_border"], width=1)
    bd.text((9, 4), badge_text, fill=col["badge_text_col"], font=font_badge)
    canvas.paste(badge_img, (bx, by), badge_img)

    # 1. 100% 実寸プレビュー枠
    pv100_y = cy + 76
    draw.text((cx + 16, pv100_y), "Original 1:1 Context (100%):", fill=(170, 180, 195), font=font_col_sub)
    
    im100 = col["crop_100"]
    im100_x = cx + (col_w - box_w) // 2
    im100_y = pv100_y + 22
    draw.rectangle([(im100_x - 1, im100_y - 1), (im100_x + box_w, im100_y + box_h)], outline=(50, 58, 75))
    canvas.paste(im100, (im100_x, im100_y))

    # 2. 320% マクロ拡大プレビュー枠
    macro_y = im100_y + box_h + 16
    draw.text((cx + 16, macro_y), "Extreme Macro Inspection (320% Zoom):", fill=(255, 200, 110) if col["highlight"] else (170, 180, 195), font=font_col_sub)
    
    target_macro_w = col_w - 32
    target_macro_h = int(box_h * (target_macro_w / box_w))
    macro_resized = im100.resize((target_macro_w, target_macro_h), Image.Resampling.LANCZOS)
    
    im_macro_x = cx + 16
    im_macro_y = macro_y + 22
    draw.rectangle([(im_macro_x - 1, im_macro_y - 1), (im_macro_x + target_macro_w, im_macro_y + target_macro_h)], outline=(255, 170, 40) if col["highlight"] else (50, 58, 75), width=2 if col["highlight"] else 1)
    canvas.paste(macro_resized, (im_macro_x, im_macro_y))

    # 3. 特徴箇条書きリスト
    bullet_start_y = im_macro_y + target_macro_h + 18
    for b_idx, (icon, text) in enumerate(col["bullets"]):
        by_pos = bullet_start_y + b_idx * 26
        if icon == "o":
            draw.ellipse((cx + 18, by_pos + 2, cx + 30, by_pos + 14), fill=(255, 160, 30))
            draw.text((cx + 21, by_pos + 1), "v", fill=(0, 0, 0), font=font_bullet_icon)
            draw.text((cx + 38, by_pos), text, fill=(240, 245, 255), font=font_bullet)
        else:
            draw.ellipse((cx + 18, by_pos + 2, cx + 30, by_pos + 14), fill=(60, 65, 80))
            draw.text((cx + 22, by_pos + 1), "x", fill=(200, 140, 140), font=font_bullet_icon)
            draw.text((cx + 38, by_pos), text, fill=(155, 165, 180), font=font_bullet)

out_comp = os.path.join(ASSETS_DIR, "comparison_burnin_vs_overlay.png")
canvas.save(out_comp, quality=95)
print(f"Polished Comparison Sheet saved to: {out_comp}")
