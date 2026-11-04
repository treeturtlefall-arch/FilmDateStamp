"""
FilmDateStamp ハイライト埋もれ実証シート生成スクリプト (パーフェクト版)
物理感光乳剤モデルによる「高輝度背景での白飛び埋もれ現象 (Emulsion Saturation Bleed-Through)」を
実写およびシームレス輝度グラデーションを用いて視覚的に実証・解説する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig, FONT_MAP
from film_stamp import (
    render_film_date_stamp,
    generate_light_map_cached_v2,
    get_font_file_and_shear,
    srgb_to_linear,
    linear_to_srgb,
)

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. 実写写真（金閣寺.JPG）の明暗部比較
kinkaku_path = os.path.join(PROJECT_DIR, "candidate", "金閣寺.JPG")
kinkaku_base = Image.open(kinkaku_path).convert("RGB")

# 暗部 (木陰・池付近: bottom_right)
cfg_dark = DateStampConfig(style_preset="Japanese Tokyo 90s")
cfg_dark.apply_style_preset_if_set()
cfg_dark.date_string = "'03 11  1"
cfg_dark.position = "bottom_right"
kinkaku_dark = render_film_date_stamp(kinkaku_base.copy(), cfg_dark)

# 明部 (青空・白飛び雲付近: top_left)
cfg_bright = DateStampConfig(style_preset="Japanese Tokyo 90s")
cfg_bright.apply_style_preset_if_set()
cfg_bright.date_string = "'03 11  1"
cfg_bright.position = "top_left"
cfg_bright.margin = 0.5
kinkaku_bright = render_film_date_stamp(kinkaku_base.copy(), cfg_bright)

# クロップ
dark_patch = kinkaku_dark.crop((990, 835, 1260, 955))
bright_patch = kinkaku_bright.crop((5, 5, 275, 125))

# 2. 輝度グラデーション（Luminance Ramp）バーの作成 (シームレス合成)
ramp_w = 1180
ramp_h = 135

# 0% (黒) から 100% (純白) への非線形グラデーション
ramp_arr = np.zeros((ramp_h, ramp_w, 3), dtype=np.float32)
for x in range(ramp_w):
    val = x / (ramp_w - 1)
    ramp_arr[:, x, :] = val

# スタンプの光マップを生成 (文字高さ ~42px)
font_path, shear_deg = get_font_file_and_shear("FDS7_Strict_Compact (80s -7°)")
light_lin, text_w, text_h, blur_pad = generate_light_map_cached_v2(
    date_text="'03 10  2",
    font_path=font_path,
    base_font_size=42,
    shear_deg=round(shear_deg, 2),
    preset_color="Amber Classic",
    exposure_intensity=1.0,
    core_glow=1.0,
    halation=1.0,
    irregularity=1.0,
    grain=1.0,
)

stamp_h_px, stamp_w_px = light_lin.shape[:2]

# 3箇所に配置
positions_x = [int(ramp_w * 0.14), int(ramp_w * 0.49), int(ramp_w * 0.83)]
target_y = (ramp_h - stamp_h_px) // 2

# バーA: FilmDateStamp (Optical Burn-in を直接適用)
bar_fds_arr = ramp_arr.copy()

for px in positions_x:
    target_x = px - stamp_w_px // 2
    x1 = max(0, target_x)
    y1 = max(0, target_y)
    x2 = min(ramp_w, target_x + stamp_w_px)
    y2 = min(ramp_h, target_y + stamp_h_px)

    sx1 = x1 - target_x
    sy1 = y1 - target_y
    sx2 = sx1 + (x2 - x1)
    sy2 = sy1 + (y2 - y1)

    sub_base_srgb = bar_fds_arr[y1:y2, x1:x2]
    sub_light_lin = light_lin[sy1:sy2, sx1:sx2]

    sub_base_lin = srgb_to_linear(sub_base_srgb)
    luma = (
        0.2126 * sub_base_lin[..., 0:1]
        + 0.7152 * sub_base_lin[..., 1:2]
        + 0.0722 * sub_base_lin[..., 2:3]
    )
    headroom = np.clip(1.0 - np.power(luma, 1.35) * 0.72, 0.12, 1.0)
    eff_light = sub_light_lin * headroom

    raw_sum = sub_base_lin + eff_light * 1.18
    compressed = 1.0 - np.exp(-raw_sum * 1.20) * (1.0 - sub_base_lin * np.exp(-eff_light * 2.0))
    t = np.clip((raw_sum - 0.45) / 0.75, 0.0, 1.0)
    combined_lin = np.clip(raw_sum * (1.0 - t) + compressed * t, 0.0, 1.0)

    bar_fds_arr[y1:y2, x1:x2] = linear_to_srgb(combined_lin)

bar_fds = Image.fromarray((bar_fds_arr * 255.0).astype(np.uint8))

# バーB: Standard Overlay (文字を単色アルファブレンド)
bar_std = Image.fromarray((ramp_arr * 255.0).astype(np.uint8))
bstd_draw = ImageDraw.Draw(bar_std)
font_size = 42
stamp_font = ImageFont.truetype(font_path, font_size)

for px in positions_x:
    tb = bstd_draw.textbbox((0, 0), "'03 10  2", font=stamp_font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    bstd_draw.text((px - tw // 2, (ramp_h - th) // 2), "'03 10  2", font=stamp_font, fill=(255, 130, 20))

# 3. シート全体のレイアウト (1280 x 800)
sheet_w = 1280
sheet_h = 800
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
font_sec_hdr = get_font("segoeuib", 18)
font_lbl = get_font("segoeuib", 13)
font_desc = get_font("segoeui", 13)
font_tag = get_font("segoeuib", 11)

# タイトル
draw.text((45, 28), "Emulsion Headroom & Realistic Highlight Bleed-Through", fill=(255, 255, 255), font=font_title)
draw.text((45, 65), "Faithfully simulates optical emulsion saturation: dates naturally wash out and melt into pure white highlights", fill=(180, 190, 205), font=font_subtitle)
draw.line([(45, 92), (sheet_w - 45, 92)], fill=(40, 48, 64), width=1)

# セクション1: 実写での明暗対比 (左: 暗部での発光, 右: 白飛び部での埋もれ)
sec1_y = 110
draw.text((45, sec1_y), "Case Study 1: Real-world Photo Exposure Comparison (Kinkaku-ji 2003)", fill=(240, 245, 255), font=font_sec_hdr)

card_w = 580
card_h = 205
patch_disp_w = 260
patch_disp_h = 120

# 左カード: 暗部 (Shadow Background)
c1_x = 45
c1_y = sec1_y + 30
draw.rounded_rectangle([(c1_x, c1_y), (c1_x + card_w, c1_y + card_h)], radius=10, fill=(18, 22, 30), outline=(50, 58, 75))
draw.text((c1_x + 18, c1_y + 16), "Low-Exposure Emulsion (Shadows)", fill=(255, 200, 100), font=font_lbl)
draw.text((c1_x + 18, c1_y + 38), "Full photosensitive headroom: stamp burns vividly with rich halation.", fill=(155, 165, 180), font=font_desc)

canvas.paste(dark_patch.resize((patch_disp_w, patch_disp_h), Image.Resampling.LANCZOS), (c1_x + 18, c1_y + 66))
dark_zoom = dark_patch.crop((95, 15, 260, 105)).resize((patch_disp_w, patch_disp_h), Image.Resampling.LANCZOS)
canvas.paste(dark_zoom, (c1_x + 18 + patch_disp_w + 18, c1_y + 66))
draw.rectangle([(c1_x + 18, c1_y + 66), (c1_x + 18 + patch_disp_w, c1_y + 66 + patch_disp_h)], outline=(70, 80, 100))
draw.rectangle([(c1_x + 18 + patch_disp_w + 18, c1_y + 66), (c1_x + 18 + patch_disp_w * 2 + 18, c1_y + 66 + patch_disp_h)], outline=(255, 160, 40), width=2)

# 右カード: 明部 (Saturated Highlight)
c2_x = sheet_w - 45 - card_w
c2_y = c1_y
draw.rounded_rectangle([(c2_x, c2_y), (c2_x + card_w, c2_y + card_h)], radius=10, fill=(18, 22, 30), outline=(50, 58, 75))
draw.text((c2_x + 18, c2_y + 16), "Saturated Emulsion (Overexposed Sky)", fill=(255, 130, 90), font=font_lbl)
draw.text((c2_x + 18, c2_y + 38), "Zero headroom: stamp photons blow out and melt into pure white.", fill=(155, 165, 180), font=font_desc)

canvas.paste(bright_patch.resize((patch_disp_w, patch_disp_h), Image.Resampling.LANCZOS), (c2_x + 18, c2_y + 66))
bright_zoom = bright_patch.crop((10, 10, 200, 110)).resize((patch_disp_w, patch_disp_h), Image.Resampling.LANCZOS)
canvas.paste(bright_zoom, (c2_x + 18 + patch_disp_w + 18, c2_y + 66))
draw.rectangle([(c2_x + 18, c2_y + 66), (c2_x + 18 + patch_disp_w, c2_y + 66 + patch_disp_h)], outline=(70, 80, 100))
draw.rectangle([(c2_x + 18 + patch_disp_w + 18, c2_y + 66), (c2_x + 18 + patch_disp_w * 2 + 18, c2_y + 66 + patch_disp_h)], outline=(255, 100, 60), width=2)

# セクション2: 連続輝度グラデーションテスト (Ramp Test)
sec2_y = 370
draw.text((45, sec2_y), "Case Study 2: Continuous Brightness Ramp Comparison (0% Shadow -> 100% Blown Highlight)", fill=(240, 245, 255), font=font_sec_hdr)

# バー1: FilmDateStamp
b1_y = sec2_y + 36
draw.text((45, b1_y), "FilmDateStamp (Physical Emulsion Model):", fill=(255, 190, 60), font=font_lbl)
draw.text((390, b1_y), "Naturally washes out as background brightness approaches 100% white", fill=(170, 180, 195), font=font_desc)
canvas.paste(bar_fds, (45, b1_y + 24))
draw.rectangle([(44, b1_y + 23), (45 + ramp_w, b1_y + 24 + ramp_h)], outline=(255, 160, 40), width=2)

# バー2: Standard Overlay
b2_y = b1_y + ramp_h + 45
draw.text((45, b2_y), "Standard Text Overlay (Flat Alpha Blend):", fill=(240, 100, 100), font=font_lbl)
draw.text((390, b2_y), "Unrealistically remains sharp & fully saturated over pure white backgrounds", fill=(170, 180, 195), font=font_desc)
canvas.paste(bar_std, (45, b2_y + 24))
draw.rectangle([(44, b2_y + 23), (45 + ramp_w, b2_y + 24 + ramp_h)], outline=(70, 80, 100), width=1)

# 保存
out_path = os.path.join(ASSETS_DIR, "highlight_bleedthrough_demo.png")
canvas.save(out_path, quality=95)
print(f"Perfect Highlight Bleed-through Demo saved to: {out_path}")
