import sys
import os
import numpy as np
from PIL import Image

sys.path.insert(0, r"c:\Users\coffe\Documents\FilmDateStamp\scripts")
from compare_eberhard_effect import render_eberhard_sample, DateStampConfig, make_scene_night

virt_w, virt_h = 1200, 900
crop_w, crop_h = 500, 170
full_bg = Image.new('RGB', (virt_w, virt_h), (15, 17, 22))
full_bg.paste(make_scene_night(crop_w, crop_h), (virt_w - crop_w, virt_h - crop_h))

cfg = DateStampConfig(font_type='DSEG7_Italic (7-Segment)', date_string="'98 12 24", preset_color='Amber Classic')

img_off, _ = render_eberhard_sample(full_bg.copy(), cfg, eberhard_effect=0.0, seed=7)
img_mid, _ = render_eberhard_sample(full_bg.copy(), cfg, eberhard_effect=0.6, seed=7)
img_high, _ = render_eberhard_sample(full_bg.copy(), cfg, eberhard_effect=1.4, seed=7)

arr_off = np.array(img_off, dtype=np.float32)
arr_mid = np.array(img_mid, dtype=np.float32)
arr_high = np.array(img_high, dtype=np.float32)

diff_mid = np.abs(arr_mid - arr_off)
diff_high = np.abs(arr_high - arr_off)

max_m = float(diff_mid.max())
mean_m = float(diff_mid[diff_mid > 0].mean()) if np.any(diff_mid > 0) else 0.0

max_h = float(diff_high.max())
mean_h = float(diff_high[diff_high > 0].mean()) if np.any(diff_high > 0) else 0.0

print(f"OFF vs 0.6: Max diff = {max_m:.2f} / 255, Mean diff on active = {mean_m:.2f}")
print(f"OFF vs 1.4: Max diff = {max_h:.2f} / 255, Mean diff on active = {mean_h:.2f}")

# 差分を5倍に強調した画像を保存
diff_img = Image.fromarray(np.clip(diff_high * 5.0, 0, 255).astype(np.uint8))
box = (virt_w - crop_w, virt_h - crop_h, virt_w, virt_h)
diff_crop = diff_img.crop(box)
diff_crop.save(r"c:\Users\coffe\Documents\FilmDateStamp\assets\eberhard_diff_debug.png")
print("Saved diff debug image to assets/eberhard_diff_debug.png")
