"""
FilmDateStamp 光学エンジン v2 - エバーハルト効果 (Eberhard / Border Effect) 検証スクリプト

フィルム現像時の「局所現像液疲労・臭化物抑制物質拡散」によるエッジ効果を検証する。
生成画像: assets/eberhard_effect_comparison.png
"""
import os
import sys
import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from film_config import DateStampConfig, resolve_date_text
from film_stamp import (
    render_date_mask_cached,
    get_font_file_and_shear,
    calculate_stamp_position,
)
from optics_v2_prototype import (
    PHYSICAL_SPECTRA,
    fft_gaussian_blur,
    approx_inner_distance,
    value_noise,
    fbm_noise,
    bilinear_warp,
    composite_linear,
    srgb_to_linear,
    linear_to_srgb,
)

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


@dataclass
class EberhardParams:
    preset_color: str = "Amber Classic"
    exposure_intensity: float = 1.05
    core_glow: float = 1.0
    halation: float = 1.0
    irregularity: float = 1.0
    grain: float = 1.0
    seed: int = 7
    eberhard_effect: float = 0.0  # 0.0 = オフ, 0.6 = 標準（実機現像）, 1.5 = 強調


def build_light_map_with_eberhard(
    mask_l: Image.Image,
    base_font_size: int,
    p: EberhardParams,
) -> Tuple[np.ndarray, int]:
    """
    エバーハルト効果（現像液の局所疲労・隣接効果）を組み込んだ光量マップ生成
    """
    fs = float(base_font_size)
    blur_pad = max(16, int(fs * 2.2))
    raw = np.pad(np.asarray(mask_l, dtype=np.float32) / 255.0, blur_pad, mode="constant")
    H, W = raw.shape

    irr = max(0.0, float(p.irregularity))
    hal = max(0.01, float(p.halation))
    E0 = float(p.exposure_intensity)
    cg = float(p.core_glow)
    ee = max(0.0, float(p.eberhard_effect))

    rng_macro = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 1])
    rng_meso = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 2])
    rng_micro = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 3])

    # 1. LED 発光尾根
    inside = raw > 0.30
    dist = approx_inner_distance(inside)
    dist = fft_gaussian_blur(dist, max(0.5, fs * 0.012)) * inside
    dmax = max(1.0, float(np.percentile(dist[inside], 92))) if inside.any() else 1.0
    ridge = np.power(np.clip(dist / dmax, 0.0, 1.25), 1.15)

    # 2. Macro ゆらぎ
    if irr > 0:
        n_char = value_noise(rng_macro, (H, W), cell_y=fs * 4.0, cell_x=fs * 0.55)
        n_seg = value_noise(rng_macro, (H, W), fs * 0.22)
        ang = rng_macro.uniform(0, 2 * math.pi)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        lens = math.cos(ang) * (xx - W / 2) / (W / 2) + math.sin(ang) * (yy - H / 2) / (H / 2)
        gain = np.clip(1.0 + irr * (0.09 * n_char + 0.06 * n_seg + 0.07 * lens), 0.55, 1.45)
    else:
        gain = np.ones((H, W), np.float32)

    slit = fft_gaussian_blur(raw, max(0.35, fs * 0.022))
    hot = ridge * gain
    source = (0.45 * slit * gain + 1.15 * hot * cg) * E0

    # 3. 多重 PSF 散乱
    psf_core = fft_gaussian_blur(hot, max(0.45, fs * 0.025))
    psf_narrow = fft_gaussian_blur(source, max(0.75, fs * 0.052))

    if irr > 0:
        aniso = 1.0 + irr * 0.16 * rng_meso.uniform(0.4, 1.0)
        hal_angle = rng_meso.uniform(0.0, 180.0)
        sh_ang = rng_meso.uniform(0, 2 * math.pi)
        sh_mag = irr * fs * 0.035
        shift = (math.cos(sh_ang) * sh_mag, math.sin(sh_ang) * sh_mag)
    else:
        aniso, hal_angle, shift = 1.0, 0.0, (0.0, 0.0)

    def halo_blur(sig: float, shift_scale: float) -> np.ndarray:
        return fft_gaussian_blur(
            source, sig * aniso, sig / aniso, hal_angle,
            (shift[0] * shift_scale, shift[1] * shift_scale),
        )

    psf_mid = halo_blur(max(1.4, fs * 0.12 * math.sqrt(hal)), 0.4)
    psf_wide = halo_blur(max(2.8, fs * 0.27 * hal), 1.0)
    psf_veil = halo_blur(max(5.5, fs * 0.58 * hal), 1.8)
    halo = (0.30 * psf_mid + 0.17 * psf_wide + 0.07 * psf_veil) * hal

    # 4. Meso ゆらぎ
    if irr > 0:
        cloud = fbm_noise(rng_meso, (H, W), fs * 1.4, octaves=2, gain=0.4)
        halo = halo * np.clip(1.0 + irr * 0.14 * cloud, 0.5, 1.5)
        wx = fbm_noise(rng_meso, (H, W), fs * 1.2, octaves=2) * (irr * fs * 0.055)
        wy = fbm_noise(rng_meso, (H, W), fs * 1.2, octaves=2) * (irr * fs * 0.055)
        halo = bilinear_warp(halo, wx, wy)
        psf_narrow = bilinear_warp(psf_narrow, wx * 0.3, wy * 0.3)

    core_E = (0.85 * hot * raw + 0.55 * psf_core) * cg * E0
    body_E = (0.50 * slit * gain + 0.65 * psf_narrow) * E0

    # -------------------------------------------------------------
    # ★ エバーハルト効果 (Eberhard / Neighborhood Border Effect)
    # -------------------------------------------------------------
    # 現像主薬の局所拡散半径 (r_dev) と現像抑制臭化物の蓄積場
    # 高露光部（露光量 E）の周囲に抑制物質が拡散し、局所コントラスト（境界段差）が生まれる
    if ee > 0.0:
        dev_r = max(0.8, fs * 0.055)  # 現像液の拡散有効半径
        exhaustion_field = fft_gaussian_blur(core_E + body_E * 0.5, dev_r)
        
        # エッジ勾配（High-pass / Laplacian 的成分）：
        # (未露光側から供給される新鮮な現像液) - (高濃度部直上での疲労)
        # 露光エッジの内側で +（現像促進）、直外側で -（現像抑制）
        local_laplacian = (core_E + body_E * 0.5) - exhaustion_field
        
        # エッジの内側（Border）をキュッと引き締め、外側のハレーション根本をごくわずかに抑制
        border_boost = np.clip(1.0 + (local_laplacian * 0.45 * ee), 0.65, 1.45)
        core_E = core_E * border_boost
        body_E = body_E * np.clip(1.0 + (local_laplacian * 0.25 * ee), 0.75, 1.35)

    # 5. Micro ゆらぎ
    total = core_E + body_E + halo
    mod = np.ones((H, W), np.float32)
    if p.grain > 0:
        fine = rng_micro.standard_normal((H, W)).astype(np.float32)
        clump = value_noise(rng_micro, (H, W), 2.2)
        grain_field = 0.55 * fine + 0.45 * clump
        env = np.clip(total * 2.2, 0.0, 1.0) * np.exp(-core_E * 1.6)
        mod *= 1.0 + 0.22 * float(p.grain) * grain_field * env
    if irr > 0:
        dye = value_noise(rng_micro, (H, W), 1.8)
        tail = np.exp(-total * 6.0) * np.clip(total * 8.0, 0.0, 1.0)
        mod *= np.clip(1.0 + irr * 0.20 * dye * tail, 0.6, 1.4)

    # 6. H&D 分光感光
    spec = PHYSICAL_SPECTRA.get(p.preset_color, PHYSICAL_SPECTRA["Amber Classic"])
    s_r, s_g, s_b = spec["sens"]
    k_r, k_g, k_b = spec["scatter"]
    bleach = np.power(np.clip(core_E, 0.0, 2.5), 1.5) * 1.35

    E_r = ((core_E + body_E) * s_r + halo * s_r * k_r * 1.35 + bleach) * mod
    E_g = ((core_E * 1.2 + body_E * 0.85) * s_g + halo * s_g * k_g * 0.70 + bleach * 0.95) * mod
    E_b = ((core_E * 1.8 + body_E * 0.25) * s_b + halo * s_b * k_b * 0.20 + bleach * 0.65) * mod
    E_rgb = np.maximum(np.stack([E_r, E_g, E_b], axis=-1), 0.0)

    light = 1.0 - np.exp(-np.power(E_rgb, 1.15))
    light *= np.asarray(spec["tint"], dtype=np.float32)[None, None, :]
    return light.astype(np.float32), blur_pad


def render_eberhard_sample(
    image: Image.Image,
    config: DateStampConfig,
    eberhard_effect: float,
    seed: int = 7,
) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    rgb = image.convert("RGB")
    w, h = rgb.size
    base_lin = srgb_to_linear(np.asarray(rgb, dtype=np.float32) / 255.0)
    s = min(w, h)

    date_text = resolve_date_text(config, seed=seed)
    font_path, shear_deg = get_font_file_and_shear(config.font_type)
    base_font_size = max(10, int(s * 0.032 * config.font_scale))
    mask, text_w, text_h = render_date_mask_cached(date_text, font_path, base_font_size, shear_deg)

    params = EberhardParams(
        preset_color=config.preset_color,
        exposure_intensity=config.exposure_intensity,
        core_glow=config.core_glow,
        halation=config.halation,
        irregularity=1.0,  # 有機ゆらぎは標準有効
        grain=1.0,
        seed=seed,
        eberhard_effect=eberhard_effect,
    )
    light, blur_pad = build_light_map_with_eberhard(mask, base_font_size, params)

    tx, ty = calculate_stamp_position(
        w, h, text_w, text_h, config.position,
        int(s * 0.05 * config.margin_x), int(s * 0.04 * config.margin_y),
    )
    composite_linear(base_lin, light, tx - blur_pad, ty - blur_pad)
    out = Image.fromarray((linear_to_srgb(base_lin) * 255.0 + 0.5).astype(np.uint8))
    return out, (tx, ty, text_w, text_h)


def make_scene_night(w: int, h: int) -> Image.Image:
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xn, yn = xx / w, yy / h
    r = 0.05 + 0.04 * xn + 0.03 * yn
    g = 0.06 + 0.05 * xn + 0.04 * yn
    b = 0.09 + 0.06 * xn + 0.05 * yn
    img = np.stack([r, g, b], axis=-1)
    rng = np.random.default_rng(100)
    noise = fft_gaussian_blur(rng.standard_normal((h, w)).astype(np.float32), 0.6)[..., None] * 0.018
    return Image.fromarray((np.clip(img + noise, 0, 1) * 255).astype(np.uint8))


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for cand in ("C:/Windows/Fonts/meiryo.ttc", "C:/Windows/Fonts/YuGothM.ttc", "C:/Windows/Fonts/msgothic.ttc"):
        if os.path.exists(cand):
            return ImageFont.truetype(cand, size)
    return ImageFont.load_default()


def generate_eberhard_comparison():
    f_title, f_sub, f_sec, f_lab = load_font(28), load_font(16), load_font(20), load_font(14)

    test_configs = [
        ("Case 1: 90s 7セグイタリック (Amber Classic)",
         "7セグの直線ストロークの輪郭がピリッと立ち、セグメントの芯とハレーションの分離が強調される",
         DateStampConfig(font_type="DSEG7_Italic (7-Segment)", date_string="'98 12 24",
                         preset_color="Amber Classic", exposure_intensity=1.05, core_glow=1.0, halation=1.0,
                         margin_x=0.7, margin_y=0.7)),
        ("Case 2: 写ルンです ドットマトリクス (Fuji Orange)",
         "丸いドットの粒立ちの芯が締まり、隣のドットと融合しつつも1粒ごとの存在感がくっきり残る",
         DateStampConfig(font_type="VT323 (Dot Matrix)", date_string="'98 12 24 18:30", show_time=True,
                         preset_color="Fuji Orange", exposure_intensity=1.05, core_glow=0.8, halation=1.0,
                         font_scale=1.15, margin_x=0.7, margin_y=0.7)),
    ]

    virt_w, virt_h = 1200, 900
    crop_w, crop_h = 500, 170
    margin, gap = 40, 30
    board_w = margin * 2 + crop_w * 3 + gap * 2
    header_h = 120
    zoom_h = 160
    block_h = 76 + crop_h + 12 + zoom_h + 26
    board_h = header_h + block_h * len(test_configs) + 30

    board = Image.new("RGB", (board_w, board_h), (14, 16, 20))
    d = ImageDraw.Draw(board)
    d.text((margin, 22), "FilmDateStamp エバーハルト効果 (Eberhard / Border Effect) 検証", fill=(245, 248, 255), font=f_title)
    d.text((margin, 64),
           "現像液の局所拡散疲労によるエッジ効果。左: オフ (0.0) / 中央: 自然な現像効果 (0.6) / 右: 強調現像 (1.4)。下段は 300% 拡大",
           fill=(175, 188, 205), font=f_sub)
    d.line([(margin, 102), (board_w - margin, 102)], fill=(55, 62, 78), width=2)

    col_x = [margin, margin + crop_w + gap, margin + (crop_w + gap) * 2]
    levels = [
        ("エバーハルト効果: OFF (0.0)", 0.0, (180, 200, 220), (20, 25, 35)),
        ("エバーハルト効果: リアル標準 (0.6)", 0.6, (255, 210, 100), (45, 30, 10)),
        ("エバーハルト効果: 強調 (1.4)", 1.4, (255, 140, 60), (50, 15, 10)),
    ]

    box = (virt_w - crop_w, virt_h - crop_h, virt_w, virt_h)

    for i, (title, desc, cfg) in enumerate(test_configs):
        y0 = header_h + i * block_h
        d.rounded_rectangle([(margin - 12, y0), (board_w - margin + 12, y0 + block_h - 14)], radius=10,
                            fill=(24, 27, 34), outline=(48, 54, 68))
        d.text((margin + 6, y0 + 12), title, fill=(255, 215, 120), font=f_sec)
        d.text((margin + 6, y0 + 44), desc, fill=(190, 200, 215), font=f_lab)

        full_bg = Image.new("RGB", (virt_w, virt_h), (15, 17, 22))
        full_bg.paste(make_scene_night(crop_w, crop_h), (virt_w - crop_w, virt_h - crop_h))

        py = y0 + 76
        zy = py + crop_h + 12

        local_pos = None
        for (col_title, ee_val, fg, bg), x in zip(levels, col_x):
            img_out, (tx, ty, tw, th) = render_eberhard_sample(full_bg.copy(), cfg, eberhard_effect=ee_val, seed=7)
            crop_img = img_out.crop(box)
            if local_pos is None:
                local_pos = (tx - box[0], ty - box[1], tw, th)

            # 実寸貼り付け
            board.paste(crop_img, (x, py))
            d.rectangle([(x, py), (x + crop_w, py + crop_h)], outline=fg, width=2)
            
            # ラベル
            tw_txt = int(d.textlength(col_title, font=f_lab)) + 14
            d.rectangle([(x, py), (x + tw_txt, py + 22)], fill=bg)
            d.text((x + 7, py + 2), col_title, fill=fg, font=f_lab)

            # 300% 拡大
            sw, sh = int(crop_w / 3.0), int(zoom_h / 3.0)
            cx = local_pos[0] + int(local_pos[2] * (0.62 if i == 0 else 0.45))
            cy = local_pos[1] + local_pos[3] // 2
            x1 = max(0, min(crop_w - sw, cx - sw // 2))
            y1 = max(0, min(crop_h - sh, cy - sh // 2))
            zoom_part = crop_img.crop((x1, y1, x1 + sw, y1 + sh)).resize((crop_w, zoom_h), Image.NEAREST)

            board.paste(zoom_part, (x, zy))
            d.rectangle([(x, zy), (x + crop_w, zy + zoom_h)], outline=fg, width=2)
            d.rectangle([(x, zy), (x + 75, zy + 22)], fill=bg)
            d.text((x + 7, zy + 2), "300% 拡大", fill=fg, font=f_lab)

    out_file = os.path.join(ASSETS_DIR, "eberhard_effect_comparison.png")
    board.save(out_file)
    print(f"Eberhard comparison saved: {out_file}")


if __name__ == "__main__":
    generate_eberhard_comparison()
