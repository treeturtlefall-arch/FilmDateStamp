"""
光学エンジン比較ボード v2
  列1: 現行 (Legacy 3-Layer Gaussian)
  列2: 新物理モデル・均一 (irregularity = 0)
  列3: 新物理モデル・有機ゆらぎ (irregularity = 1.0)
  + シード違いのゆらぎバリエーション

依存: NumPy + Pillow のみ（scipy 非依存）
生成画像: assets/optical_model_comparison_v2.png
"""
import os
import sys
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from film_config import DateStampConfig, resolve_date_text
from film_stamp import (
    render_film_date_stamp,
    render_date_mask_cached,
    get_font_file_and_shear,
    calculate_stamp_position,
)
from optics_v2_prototype import (
    OpticsV2Params,
    build_light_map,
    composite_linear,
    srgb_to_linear,
    linear_to_srgb,
    fft_gaussian_blur,
)

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def render_v2(
    image: Image.Image,
    config: DateStampConfig,
    irregularity: float = 1.0,
    seed: int = 0,
    grain: float = 1.0,
) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """v2 エンジンで焼き付け。戻り値: (画像, (text_x, text_y, text_w, text_h))"""
    rgb = image.convert("RGB")
    w, h = rgb.size
    base_lin = srgb_to_linear(np.asarray(rgb, dtype=np.float32) / 255.0)
    s = min(w, h)

    date_text = resolve_date_text(config, seed=seed)
    font_path, shear_deg = get_font_file_and_shear(config.font_type)
    base_font_size = max(10, int(s * 0.032 * config.font_scale))
    mask, text_w, text_h = render_date_mask_cached(date_text, font_path, base_font_size, shear_deg)

    params = OpticsV2Params(
        preset_color=config.preset_color,
        exposure_intensity=config.exposure_intensity,
        core_glow=config.core_glow,
        halation=config.halation,
        irregularity=irregularity,
        grain=grain,
        seed=seed,
    )
    light, blur_pad = build_light_map(mask, base_font_size, params)

    tx, ty = calculate_stamp_position(
        w, h, text_w, text_h, config.position,
        int(s * 0.05 * config.margin_x), int(s * 0.04 * config.margin_y),
    )
    composite_linear(base_lin, light, tx - blur_pad, ty - blur_pad)
    out = Image.fromarray((linear_to_srgb(base_lin) * 255.0 + 0.5).astype(np.uint8))
    return out, (tx, ty, text_w, text_h)


def make_scene(w: int, h: int, scene: str) -> Image.Image:
    rng = np.random.default_rng(100)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn, yn = xx / w, yy / h
    if scene == "night":
        r, g, b = 0.05 + 0.04 * xn + 0.03 * yn, 0.06 + 0.05 * xn + 0.04 * yn, 0.09 + 0.06 * xn + 0.05 * yn
    elif scene == "foliage":
        r = 0.14 + 0.08 * np.sin(xn * 5.0) * np.cos(yn * 4.0)
        g = 0.18 + 0.09 * np.sin(xn * 5.0 + 0.5)
        b = 0.13 + 0.06 * yn
    elif scene == "highlight":
        grad = np.power(np.clip((xn - 0.15) / 0.78, 0.0, 1.0), 1.3)
        r, g, b = 0.08 + 0.88 * grad, 0.09 + 0.86 * grad, 0.11 + 0.83 * grad
    else:
        r = g = b = np.full((h, w), 0.1, np.float32)
    img = np.stack([r, g, b], axis=-1)
    noise = fft_gaussian_blur(rng.standard_normal((h, w)).astype(np.float32), 0.6)[..., None] * 0.018
    return Image.fromarray((np.clip(img + noise, 0, 1) * 255).astype(np.uint8))


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for cand in ("C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothM.ttc", "C:/Windows/Fonts/msgothic.ttc"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


VIRT_W, VIRT_H = 1200, 900
CROP_W, CROP_H = 500, 170


def render_case_crops(cfg: DateStampConfig, scene: str, seed: int = 7):
    full_bg = Image.new("RGB", (VIRT_W, VIRT_H), (15, 17, 22))
    full_bg.paste(make_scene(CROP_W, CROP_H, scene), (VIRT_W - CROP_W, VIRT_H - CROP_H))
    box = (VIRT_W - CROP_W, VIRT_H - CROP_H, VIRT_W, VIRT_H)

    legacy = render_film_date_stamp(full_bg.copy(), config=cfg).crop(box)
    uniform, pos = render_v2(full_bg.copy(), cfg, irregularity=0.0, seed=seed)
    organic, _ = render_v2(full_bg.copy(), cfg, irregularity=1.0, seed=seed)
    tx, ty, tw, th = pos
    local = (tx - box[0], ty - box[1], tw, th)
    return full_bg, box, legacy, uniform.crop(box), organic.crop(box), local


def zoom_crop(img: Image.Image, local, out_w: int, out_h: int, scale: float, fx: float = 0.5) -> Image.Image:
    tx, ty, tw, th = local
    sw, sh = int(out_w / scale), int(out_h / scale)
    cx, cy = tx + int(tw * fx), ty + th // 2
    x1 = max(0, min(img.width - sw, cx - sw // 2))
    y1 = max(0, min(img.height - sh, cy - sh // 2))
    return img.crop((x1, y1, x1 + sw, y1 + sh)).resize((out_w, out_h), Image.NEAREST)


def label(draw, xy, text, font, fg, bg):
    x, y = xy
    tw = int(draw.textlength(text, font=font)) + 14
    draw.rectangle([(x, y), (x + tw, y + 22)], fill=bg)
    draw.text((x + 7, y + 2), text, fill=fg, font=font)


def generate():
    f_title, f_sub, f_sec, f_lab = load_font(28), load_font(16), load_font(20), load_font(14)

    cases = [
        ("Case 1: 90s 7セグイタリック (Amber Classic / 夜景)",
         "均一モデルは全セグメントが同じ明るさ・同じ真円の滲み。有機モデルは文字ごとの光量差、楕円化・オフセットした滲み、裾野のちぎれが出る",
         "night",
         DateStampConfig(font_type="DSEG7_Italic (7-Segment)", date_string="'98 12 24", preset_color="Amber Classic",
                         exposure_intensity=1.05, core_glow=1.0, halation=1.0, margin_x=0.7, margin_y=0.7)),
        ("Case 2: 写ルンです ドットマトリクス (Fuji Orange / 木陰)",
         "ドットごとの発光ムラと、ドット同士の滲み合いの偏り",
         "foliage",
         DateStampConfig(font_type="VT323 (Dot Matrix)", date_string="'98 12 24 18:30", show_time=True,
                         preset_color="Fuji Orange", exposure_intensity=1.05, core_glow=0.8, halation=1.0,
                         font_scale=1.15, margin_x=0.7, margin_y=0.7)),
        ("Case 3: 80s クォーツレッド (Quartz Red / halation=1.3 プリセット相当)",
         "スライダーを上げた場合の広がり。v2 では halation=1.3 で旧プロトタイプの 1.1 よりまだ控えめ",
         "night",
         DateStampConfig(font_type="DSEG7_Classic (7-Segment)", date_string="'88  8 15", preset_color="Quartz Red",
                         exposure_intensity=1.10, core_glow=1.0, halation=1.3, margin_x=0.7, margin_y=0.7)),
        ("Case 4: 明暗境界・ハイライトへの埋もれ (Amber Classic)",
         "明るい側ほど乳剤の感光余力が減って沈み込む。ゆらぎにより埋もれ方も文字ごとに不揃いになる",
         "highlight",
         DateStampConfig(font_type="DSEG7_Italic (7-Segment)", date_string="'98 12 24 14:30", show_time=True,
                         preset_color="Amber Classic", exposure_intensity=1.05, core_glow=1.0, halation=1.0,
                         margin_x=0.7, margin_y=0.7)),
    ]

    margin, gap = 40, 30
    board_w = margin * 2 + CROP_W * 3 + gap * 2
    header_h = 120
    zoom_h = 150
    block_h = 76 + CROP_H + 12 + zoom_h + 26
    seed_block_h = 60 + (zoom_h + 34) * 2 + 20
    board_h = header_h + block_h * len(cases) + seed_block_h + 30

    board = Image.new("RGB", (board_w, board_h), (14, 16, 20))
    d = ImageDraw.Draw(board)
    d.text((margin, 22), "FilmDateStamp 光学エンジン比較 v2: 現行 / 新物理・均一 / 新物理・有機ゆらぎ", fill=(245, 248, 255), font=f_title)
    d.text((margin, 64),
           "v2 は NumPy + Pillow のみで実装。halation=1.0 を旧プロトタイプの約0.6倍に再基準化。下段は各列の 250% 拡大（NEAREST）",
           fill=(175, 188, 205), font=f_sub)
    d.line([(margin, 102), (board_w - margin, 102)], fill=(55, 62, 78), width=2)

    col_x = [margin, margin + CROP_W + gap, margin + (CROP_W + gap) * 2]
    col_meta = [
        ("現行 3-Layer Gaussian", (190, 200, 220), (15, 18, 24), (80, 88, 105)),
        ("v2 均一 (irregularity=0)", (170, 220, 255), (10, 24, 40), (70, 140, 210)),
        ("v2 有機ゆらぎ (irregularity=1.0)", (255, 200, 90), (40, 24, 10), (230, 140, 40)),
    ]

    seed_cfg = None
    for i, (title, desc, scene, cfg) in enumerate(cases):
        y0 = header_h + i * block_h
        d.rounded_rectangle([(margin - 12, y0), (board_w - margin + 12, y0 + block_h - 14)], radius=10,
                            fill=(24, 27, 34), outline=(48, 54, 68))
        d.text((margin + 6, y0 + 12), title, fill=(255, 215, 120), font=f_sec)
        d.text((margin + 6, y0 + 44), desc, fill=(190, 200, 215), font=f_lab)

        _, _, legacy, uniform, organic, local = render_case_crops(cfg, scene)
        py = y0 + 76
        zy = py + CROP_H + 12
        for (img, (name, fg, bg, ol)), x in zip(zip((legacy, uniform, organic), col_meta), col_x):
            board.paste(img, (x, py))
            d.rectangle([(x, py), (x + CROP_W, py + CROP_H)], outline=ol, width=2)
            label(d, (x, py), name, f_lab, fg, bg)
            board.paste(zoom_crop(img, local, CROP_W, zoom_h, 2.5), (x, zy))
            d.rectangle([(x, zy), (x + CROP_W, zy + zoom_h)], outline=ol, width=2)
            label(d, (x, zy), "250%", f_lab, fg, bg)
        if i == 0:
            seed_cfg = cfg

    # ---- シード違いバリエーション ----
    y0 = header_h + block_h * len(cases)
    d.rounded_rectangle([(margin - 12, y0), (board_w - margin + 12, y0 + seed_block_h - 10)], radius=10,
                        fill=(24, 27, 34), outline=(48, 54, 68))
    d.text((margin + 6, y0 + 12), "シード違いのゆらぎ（Case 1 設定・250% 拡大） 上段: irregularity=1.0 / 下段: irregularity=2.0（誇張）",
           fill=(255, 215, 120), font=f_sec)
    n = 4
    sw = (board_w - margin * 2 - gap * (n - 1)) // n
    full_bg = Image.new("RGB", (VIRT_W, VIRT_H), (15, 17, 22))
    full_bg.paste(make_scene(CROP_W, CROP_H, "night"), (VIRT_W - CROP_W, VIRT_H - CROP_H))
    box = (VIRT_W - CROP_W, VIRT_H - CROP_H, VIRT_W, VIRT_H)
    for row, irr in enumerate((1.0, 2.0)):
        ry = y0 + 60 + row * (zoom_h + 34)
        for k in range(n):
            seed = 101 + k * 37
            img, (tx, ty, tw, th) = render_v2(full_bg.copy(), seed_cfg, irregularity=irr, seed=seed)
            crop = img.crop(box)
            local = (tx - box[0], ty - box[1], tw, th)
            x = margin + k * (sw + gap)
            board.paste(zoom_crop(crop, local, sw, zoom_h, 2.5, fx=0.62), (x, ry))
            d.rectangle([(x, ry), (x + sw, ry + zoom_h)], outline=(230, 140, 40), width=2)
            label(d, (x, ry), f"seed={seed}  irr={irr:.1f}", f_lab, (255, 200, 90), (40, 24, 10))

    out = os.path.join(ASSETS_DIR, "optical_model_comparison_v2.png")
    board.save(out)
    print(f"Saved: {out}")


if __name__ == "__main__":
    generate()
