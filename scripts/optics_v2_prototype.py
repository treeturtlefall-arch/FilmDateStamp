"""
FilmDateStamp 光学エンジン v2 プロトタイプ
(Physical Emulsion Burn-in + Organic Irregularity)

依存: NumPy + Pillow のみ（scipy 非依存）。
ComfyUI 非依存の純粋関数群として設計し、将来の CLI / 単独アプリへのフォークを想定する。

パイプライン概要:
  Step 1  LED 光源プロファイル    : 近似距離変換による発光尾根（ホットスポット）
  Step 2  ① Macro ゆらぎ          : 文字・セグメント単位の光量ジッター + デートレンズ周辺減光
  Step 3  多重スケール PSF 散乱   : FFT ガウシアン（異方性・オフセット対応）
  Step 4  ② Meso ゆらぎ           : 圧板密着ムラ（雲状変調）+ ハレーション輪郭の波打ち（ドメインワープ）
  Step 5  ③ Micro ゆらぎ          : 銀塩グレイン + 色素雲（Dye Cloud）による裾野のちぎれ
  Step 6  H&D 分光感光            : 露光量に応じた 赤→橙→黄→白 の連続ブリーチ
  Step 7  リニア空間合成          : 乳剤感光余力 + フィルム肩特性
"""
import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np
from PIL import Image


# ==============================================================================
# 色空間変換 (sRGB <-> Linear)
# ==============================================================================
def srgb_to_linear(srgb: np.ndarray) -> np.ndarray:
    srgb = np.clip(srgb, 0.0, 1.0)
    return np.where(
        srgb <= 0.04045, srgb / 12.92, np.power((srgb + 0.055) / 1.055, 2.4)
    ).astype(np.float32)


def linear_to_srgb(linear: np.ndarray) -> np.ndarray:
    linear = np.clip(linear, 0.0, 1.0)
    return np.where(
        linear <= 0.0031308, linear * 12.92, 1.055 * np.power(linear, 1.0 / 2.4) - 0.055
    ).astype(np.float32)


# ==============================================================================
# 基本フィルタ群（NumPy のみ）
# ==============================================================================
def fft_gaussian_blur(
    arr: np.ndarray,
    sigma: float,
    sigma_minor: float = None,
    angle_deg: float = 0.0,
    shift_xy: Tuple[float, float] = (0.0, 0.0),
) -> np.ndarray:
    """
    FFT によるガウシアンブラー。
    - sigma_minor を指定すると楕円（異方性）カーネル、angle_deg でその主軸を回転
    - shift_xy でサブピクセル精度の平行移動（圧板の浮きによる滲みのオフセット）
    循環畳み込みの回り込みを防ぐため、内部で 3.5σ 分のゼロパディングを行う。
    """
    if sigma_minor is None:
        sigma_minor = sigma
    smax = max(sigma, sigma_minor)
    if smax < 0.05 and abs(shift_xy[0]) < 1e-3 and abs(shift_xy[1]) < 1e-3:
        return arr.astype(np.float32, copy=True)

    pad = int(math.ceil(3.5 * smax + abs(shift_xy[0]) + abs(shift_xy[1]))) + 2
    a = np.pad(arr.astype(np.float32), pad, mode="constant")
    h, w = a.shape

    fy = np.fft.fftfreq(h).astype(np.float32)[:, None]
    fx = np.fft.rfftfreq(w).astype(np.float32)[None, :]
    th = math.radians(angle_deg)
    u = fx * math.cos(th) + fy * math.sin(th)
    v = -fx * math.sin(th) + fy * math.cos(th)
    tf = np.exp(-2.0 * math.pi ** 2 * (sigma ** 2 * u ** 2 + sigma_minor ** 2 * v ** 2))
    if shift_xy[0] != 0.0 or shift_xy[1] != 0.0:
        tf = tf * np.exp(-2j * math.pi * (fx * shift_xy[0] + fy * shift_xy[1]))

    out = np.fft.irfft2(np.fft.rfft2(a) * tf, s=a.shape)
    return np.maximum(out[pad:-pad, pad:-pad], 0.0).astype(np.float32)


def approx_inner_distance(binary: np.ndarray, max_iter: int = 96) -> np.ndarray:
    """
    反復エロージョンによる近似距離変換（4近傍/8近傍を交互に使う八角形メトリック）。
    文字ストロークの太さ（数px〜十数px）程度なら十分高速。
    """
    dist = np.zeros(binary.shape, dtype=np.float32)
    cur = binary.astype(bool).copy()
    for i in range(max_iter):
        if not cur.any():
            break
        dist += cur
        p = np.pad(cur, 1, constant_values=False)
        er = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
        if i % 2 == 1:
            er &= p[:-2, :-2] & p[:-2, 2:] & p[2:, :-2] & p[2:, 2:]
        cur = er
    return dist


def value_noise(rng: np.random.Generator, shape: Tuple[int, int], cell_y: float, cell_x: float = None) -> np.ndarray:
    """格子乱数を Bicubic 補間した滑らかなノイズ（平均0・標準偏差1に正規化）"""
    h, w = shape
    cell_x = cell_y if cell_x is None else cell_x
    cell_y = max(1.0, float(cell_y))
    cell_x = max(1.0, float(cell_x))
    gh = int(math.ceil(h / cell_y)) + 4
    gw = int(math.ceil(w / cell_x)) + 4
    grid = rng.standard_normal((gh, gw)).astype(np.float32)
    up_w, up_h = int(math.ceil(gw * cell_x)), int(math.ceil(gh * cell_y))
    up = np.asarray(Image.fromarray(grid).resize((up_w, up_h), Image.BICUBIC), dtype=np.float32)
    oy = int(cell_y + rng.random() * cell_y)
    ox = int(cell_x + rng.random() * cell_x)
    out = up[oy:oy + h, ox:ox + w]
    std = float(out.std())
    return ((out - out.mean()) / std).astype(np.float32) if std > 1e-6 else np.zeros(shape, np.float32)


def fbm_noise(rng: np.random.Generator, shape: Tuple[int, int], cell: float, octaves: int = 3, gain: float = 0.5) -> np.ndarray:
    """多オクターブの雲状ノイズ（Fractal Brownian Motion）"""
    acc = np.zeros(shape, dtype=np.float32)
    amp, total = 1.0, 0.0
    for i in range(octaves):
        acc += value_noise(rng, shape, cell / (2 ** i)) * amp
        total += amp
        amp *= gain
    acc /= total
    std = float(acc.std())
    return (acc / std).astype(np.float32) if std > 1e-6 else acc


def bilinear_warp(field: np.ndarray, dx: np.ndarray, dy: np.ndarray) -> np.ndarray:
    """変位場 (dx, dy) によるドメインワープ（バイリニア再サンプリング）"""
    h, w = field.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    sx = np.clip(xx + dx, 0.0, w - 1.001)
    sy = np.clip(yy + dy, 0.0, h - 1.001)
    x0 = sx.astype(np.int32)
    y0 = sy.astype(np.int32)
    fx = sx - x0
    fy = sy - y0
    a = field[y0, x0]
    b = field[y0, x0 + 1]
    c = field[y0 + 1, x0]
    d = field[y0 + 1, x0 + 1]
    return (a * (1 - fx) * (1 - fy) + b * fx * (1 - fy) + c * (1 - fx) * fy + d * fx * fy).astype(np.float32)


# ==============================================================================
# 分光感光プロファイル
# ==============================================================================
PHYSICAL_SPECTRA = {
    "Amber Classic": {"sens": (3.20, 0.95, 0.38), "scatter": (1.00, 0.24, 0.02), "tint": (1.00, 0.98, 0.85)},
    "Quartz Red":    {"sens": (3.60, 0.32, 0.18), "scatter": (1.00, 0.06, 0.01), "tint": (1.00, 0.90, 0.84)},
    "Fuji Orange":   {"sens": (3.40, 0.82, 0.30), "scatter": (1.00, 0.28, 0.02), "tint": (1.00, 0.97, 0.80)},
    "Golden Yellow": {"sens": (3.00, 1.55, 0.45), "scatter": (1.00, 0.45, 0.04), "tint": (1.00, 0.99, 0.90)},
    "Cyber Green":   {"sens": (0.32, 3.20, 0.65), "scatter": (0.05, 1.00, 0.22), "tint": (0.90, 1.00, 0.92)},
}


@dataclass
class OpticsV2Params:
    preset_color: str = "Amber Classic"
    exposure_intensity: float = 1.0
    core_glow: float = 1.0
    halation: float = 1.0       # v2 基準: 旧プロトタイプ(1.1)の約 0.6 倍の強さ・0.85 倍の半径
    irregularity: float = 1.0   # 0 = 完全均一 / 1.0 = 実機相当の控えめなムラ / 2.0 = 誇張
    grain: float = 1.0          # 銀塩グレイン量
    seed: int = 0


# ==============================================================================
# 光量マップ生成（パディング付き、リニア RGB）
# ==============================================================================
def build_light_map(mask_l: Image.Image, base_font_size: int, p: OpticsV2Params) -> Tuple[np.ndarray, int]:
    fs = float(base_font_size)
    blur_pad = max(16, int(fs * 2.2))
    raw = np.pad(np.asarray(mask_l, dtype=np.float32) / 255.0, blur_pad, mode="constant")
    H, W = raw.shape

    irr = max(0.0, float(p.irregularity))
    hal = max(0.01, float(p.halation))
    E0 = float(p.exposure_intensity)
    cg = float(p.core_glow)

    # 用途ごとに独立した乱数系列（irregularity を変えてもグレイン模様が変わらないように）
    rng_macro = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 1])
    rng_meso = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 2])
    rng_micro = np.random.default_rng([int(p.seed) & 0xFFFFFFFF, 3])

    # ---- Step 1: LED 発光尾根 ----
    inside = raw > 0.30
    dist = approx_inner_distance(inside)
    dist = fft_gaussian_blur(dist, max(0.5, fs * 0.012)) * inside  # 八角形メトリックの段差を均す
    dmax = max(1.0, float(np.percentile(dist[inside], 92))) if inside.any() else 1.0
    ridge = np.power(np.clip(dist / dmax, 0.0, 1.25), 1.15)

    # ---- Step 2: ① Macro ゆらぎ（LED素子・セグメント個体差 + デートレンズ周辺減光） ----
    if irr > 0:
        n_char = value_noise(rng_macro, (H, W), cell_y=fs * 4.0, cell_x=fs * 0.55)  # 文字単位
        n_seg = value_noise(rng_macro, (H, W), fs * 0.22)                           # セグメント単位
        ang = rng_macro.uniform(0, 2 * math.pi)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        lens = math.cos(ang) * (xx - W / 2) / (W / 2) + math.sin(ang) * (yy - H / 2) / (H / 2)
        gain = np.clip(1.0 + irr * (0.09 * n_char + 0.06 * n_seg + 0.07 * lens), 0.55, 1.45)
    else:
        gain = np.ones((H, W), np.float32)

    slit = fft_gaussian_blur(raw, max(0.35, fs * 0.022))  # 投影スリットの回折・角の丸まり
    hot = ridge * gain
    source = (0.45 * slit * gain + 1.15 * hot * cg) * E0

    # ---- Step 3: 多重 PSF 散乱 ----
    psf_core = fft_gaussian_blur(hot, max(0.45, fs * 0.025))
    psf_narrow = fft_gaussian_blur(source, max(0.75, fs * 0.052))

    if irr > 0:
        # 圧板の浮き・フィルムのたわみ → 滲みが楕円化し、わずかに片側へずれる
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

    # ---- Step 4: ② Meso ゆらぎ（雲状変調 + 輪郭の波打ち） ----
    if irr > 0:
        # 圧板密着ムラは低周波（文字1〜2個分のスケール）。高周波にすると炎・圧縮ノイズ状になるので避ける
        cloud = fbm_noise(rng_meso, (H, W), fs * 1.4, octaves=2, gain=0.4)
        halo = halo * np.clip(1.0 + irr * 0.14 * cloud, 0.5, 1.5)
        wx = fbm_noise(rng_meso, (H, W), fs * 1.2, octaves=2) * (irr * fs * 0.055)
        wy = fbm_noise(rng_meso, (H, W), fs * 1.2, octaves=2) * (irr * fs * 0.055)
        halo = bilinear_warp(halo, wx, wy)
        # ボディ（狭角散乱）の輪郭もごく僅かに揺らす
        psf_narrow = bilinear_warp(psf_narrow, wx * 0.3, wy * 0.3)

    core_E = (0.85 * hot * raw + 0.55 * psf_core) * cg * E0
    body_E = (0.50 * slit * gain + 0.65 * psf_narrow) * E0

    # ---- Step 5: ③ Micro ゆらぎ（銀塩グレイン + 色素雲） ----
    total = core_E + body_E + halo
    mod = np.ones((H, W), np.float32)
    if p.grain > 0:
        fine = rng_micro.standard_normal((H, W)).astype(np.float32)
        clump = value_noise(rng_micro, (H, W), 2.2)
        grain_field = 0.55 * fine + 0.45 * clump
        env = np.clip(total * 2.2, 0.0, 1.0) * np.exp(-core_E * 1.6)
        mod *= 1.0 + 0.22 * float(p.grain) * grain_field * env
    if irr > 0:
        # 低露光の裾野だけを色素雲の塊でちぎれさせる
        dye = value_noise(rng_micro, (H, W), 1.8)
        tail = np.exp(-total * 6.0) * np.clip(total * 8.0, 0.0, 1.0)
        mod *= np.clip(1.0 + irr * 0.20 * dye * tail, 0.6, 1.4)

    # ---- Step 6: H&D 分光感光 ----
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


# ==============================================================================
# リニア空間合成
# ==============================================================================
def composite_linear(base_lin: np.ndarray, light: np.ndarray, origin_x: int, origin_y: int) -> np.ndarray:
    h, w = base_lin.shape[:2]
    sh, sw = light.shape[:2]
    dx1, dy1 = max(0, origin_x), max(0, origin_y)
    dx2, dy2 = min(w, origin_x + sw), min(h, origin_y + sh)
    if dx2 <= dx1 or dy2 <= dy1:
        return base_lin
    sx1, sy1 = dx1 - origin_x, dy1 - origin_y
    sub_b = base_lin[dy1:dy2, dx1:dx2]
    sub_l = light[sy1:sy1 + (dy2 - dy1), sx1:sx1 + (dx2 - dx1)]

    luma = 0.2126 * sub_b[..., 0:1] + 0.7152 * sub_b[..., 1:2] + 0.0722 * sub_b[..., 2:3]
    headroom = np.clip(1.0 - np.power(luma, 1.35) * 0.72, 0.12, 1.0)  # 乳剤の感光余力
    eff = sub_l * headroom
    raw_sum = sub_b + eff * 1.18
    compressed = 1.0 - np.exp(-raw_sum * 1.20) * (1.0 - sub_b * np.exp(-eff * 2.0))
    t = np.clip((raw_sum - 0.45) / 0.75, 0.0, 1.0)
    base_lin[dy1:dy2, dx1:dx2] = np.clip(raw_sum * (1.0 - t) + compressed * t, 0.0, 1.0)
    return base_lin
