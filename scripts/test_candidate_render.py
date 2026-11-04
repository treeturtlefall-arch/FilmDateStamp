import os
import sys
from PIL import Image

PROJECT_DIR = r"C:\Users\coffe\Documents\FilmDateStamp"
sys.path.insert(0, PROJECT_DIR)

from film_config import STYLE_PRESETS, DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# 1. DSC00004.JPG x Japanese Tokyo 90s
img_path = os.path.join(PROJECT_DIR, "candidate", "DSC00004.JPG")
img = Image.open(img_path).convert("RGB")

cfg_tokyo = DateStampConfig(style_preset="Japanese Tokyo 90s")
cfg_tokyo.apply_style_preset_if_set()
cfg_tokyo.date_string = "'03 10  2"
res_tokyo = render_film_date_stamp(img, cfg_tokyo)
out_tokyo = os.path.join(ASSETS_DIR, "preview_dsc00004_tokyo90s.png")
res_tokyo.save(out_tokyo)
print(f"Saved: {out_tokyo}")

# 2. DSC00004.JPG x Y2K Digicam
cfg_y2k = DateStampConfig(style_preset="Y2K Digicam (Early 2000s)")
cfg_y2k.apply_style_preset_if_set()
cfg_y2k.date_string = "'03 10  2 17:49"
res_y2k = render_film_date_stamp(img, cfg_y2k)
out_y2k = os.path.join(ASSETS_DIR, "preview_dsc00004_y2k.png")
res_y2k.save(out_y2k)
print(f"Saved: {out_y2k}")

# 3. 金閣寺.JPG x Japanese Snap (Disposable)
kinkaku_path = os.path.join(PROJECT_DIR, "candidate", "金閣寺.JPG")
kinkaku_img = Image.open(kinkaku_path).convert("RGB")

cfg_disp = DateStampConfig(style_preset="Japanese Snap (Disposable)")
cfg_disp.apply_style_preset_if_set()
cfg_disp.date_string = "'03 11  1"
res_disp = render_film_date_stamp(kinkaku_img, cfg_disp)
out_disp = os.path.join(ASSETS_DIR, "preview_kinkaku_disposable.png")
res_disp.save(out_disp)
print(f"Saved: {out_disp}")
