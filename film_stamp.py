"""
FilmDateStamp - コア光学露光レンダリングエンジン
Pillow / NumPy ベースで、フィルム乳剤への3層LED露光・光学感光・ハイライト飽和をシミュレートする。
"""
import os
import math
from functools import lru_cache
from typing import Tuple, Optional, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from .film_config import DateStampConfig, resolve_date_text, COLOR_PRESETS, FONT_MAP
except (ImportError, ValueError):
    from film_config import DateStampConfig, resolve_date_text, COLOR_PRESETS, FONT_MAP

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(MODULE_DIR, "fonts")


@lru_cache(maxsize=16)
def get_font_file_and_shear(font_type: str) -> Tuple[str, float]:
    """フォントファイルパスとシアー傾斜角度（度数）を返す"""
    if font_type in FONT_MAP:
        filename, shear_deg = FONT_MAP[font_type]
    else:
        # デフォルトフォールバック
        filename, shear_deg = "DSEG7Classic-Bold.ttf", 0.0

    font_path = os.path.join(FONTS_DIR, filename)
    if not os.path.exists(font_path):
        # 予備検索
        alt_path = os.path.join(MODULE_DIR, filename)
        if os.path.exists(alt_path):
            font_path = alt_path

    return font_path, shear_deg


@lru_cache(maxsize=32)
def get_cached_truetype_font(font_path: str, size: int) -> ImageFont.FreeTypeFont:
    """TrueTypeフォントインスタンスのLRUキャッシュ取得"""
    try:
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def apply_shear_tilt(img: Image.Image, shear_deg: float) -> Image.Image:
    """
    画像を右傾斜（イタリック調）にアフィン変換する。
    """
    if abs(shear_deg) < 0.01:
        return img

    w, h = img.size
    # tan(theta) での x 方向の変位
    shear_factor = math.tan(math.radians(shear_deg))
    offset_x = int(math.ceil(h * shear_factor))
    new_w = w + offset_x

    # PIL の transform は逆マッピング行列 (a, b, c, d, e, f)
    # x_src = a * x_dst + b * y_dst + c
    # y_src = d * x_dst + e * y_dst + f
    # ここで dst_x = src_x + (h - 1 - src_y) * shear_factor (文字下部基準)
    # したがって src_x = dst_x - (h - y_dst) * shear_factor
    matrix = (1, shear_factor, -shear_factor * h, 0, 1, 0)

    transformed = img.transform(
        (new_w, h),
        Image.AFFINE,
        matrix,
        resample=Image.BILINEAR
    )
    return transformed


def calculate_stamp_position(
    img_w: int,
    img_h: int,
    stamp_w: int,
    stamp_h: int,
    position: str,
    margin_x_px: int,
    margin_y_px: int,
) -> Tuple[int, int]:
    """配置指定に従ってスタンプ描画の左上座標 (pos_x, pos_y) を計算"""
    pos_key = position.lower().strip()

    if pos_key == "bottom_left":
        pos_x = margin_x_px
        pos_y = img_h - stamp_h - margin_y_px
    elif pos_key == "top_right":
        pos_x = img_w - stamp_w - margin_x_px
        pos_y = margin_y_px
    elif pos_key == "top_left":
        pos_x = margin_x_px
        pos_y = margin_y_px
    else:
        # デフォルト: bottom_right
        pos_x = img_w - stamp_w - margin_x_px
        pos_y = img_h - stamp_h - margin_y_px

    return pos_x, pos_y


# フォントごとの視覚サイズ正規化係数キャッシュ
_FONT_NORM_CACHE = {}

# 基準サイズ（100pt描画時の "88 88 88" の理想視覚バウンディングボックス）
_REF_TARGET_W = 360.0
_REF_TARGET_H = 65.0


def get_font_visual_norm_factor(font_path: str) -> float:
    """
    フォントごとの内部メトリクス（EM枠に対する実グリフの高さ・字幅比率）の差を吸収し、
    どのフォントを選んでも同じ font_scale で同じ視覚サイズになるよう正規化係数を算出する。
    """
    if font_path in _FONT_NORM_CACHE:
        return _FONT_NORM_CACHE[font_path]

    try:
        ref_font = get_cached_truetype_font(font_path, 100)
        bbox = ref_font.getbbox("88 88 88")
        w = max(1.0, float(bbox[2] - bbox[0]))
        h = max(1.0, float(bbox[3] - bbox[1]))
        # 横幅比率 (75%) と高さ比率 (25%) の加重幾何平均で視覚的な大きさを揃える
        norm_factor = ((_REF_TARGET_W / w) ** 0.75) * ((_REF_TARGET_H / h) ** 0.25)
        norm_factor = max(0.4, min(2.5, norm_factor))
    except Exception:
        norm_factor = 1.0

    _FONT_NORM_CACHE[font_path] = norm_factor
    return norm_factor


@lru_cache(maxsize=32)
def render_date_mask_cached(
    text: str,
    font_path: str,
    font_size: int,
    shear_deg: float = 0.0,
) -> Tuple[Image.Image, int, int]:
    """
    指定文字列のグレースケールマスク画像（Lモード）をキャッシュ生成する内部関数。
    戻り値: (mask_image, text_width, text_height)
    """
    norm_factor = get_font_visual_norm_factor(font_path)
    effective_font_size = max(10, int(round(font_size * norm_factor)))
    font = get_cached_truetype_font(font_path, effective_font_size)

    # テキストサイズの計測
    dummy_img = Image.new("L", (1, 1), 0)
    dummy_draw = ImageDraw.Draw(dummy_img)
    bbox = dummy_draw.textbbox((0, 0), text, font=font, anchor="lt")
    raw_w = max(1, bbox[2] - bbox[0])
    raw_h = max(1, bbox[3] - bbox[1])

    # 描画用の一時カンバス
    pad_y = max(4, int(effective_font_size * 0.4))
    pad_x = max(4, int(effective_font_size * 0.4))
    canvas_w = raw_w + pad_x * 2
    canvas_h = raw_h + pad_y * 2

    mask = Image.new("L", (canvas_w, canvas_h), 0)
    draw = ImageDraw.Draw(mask)
    draw.text((pad_x - bbox[0], pad_y - bbox[1]), text, fill=255, font=font, anchor="lt")

    # 斜体（シアー変形）の適用
    if abs(shear_deg) > 0.01:
        mask = apply_shear_tilt(mask, shear_deg)

    # 実際に点灯しているピクセルのタイトなバウンディングボックスで切り出す（フォント間の余白ズレを完全排除）
    tight_bbox = mask.getbbox()
    if tight_bbox is not None:
        mask = mask.crop(tight_bbox)

    text_w, text_h = mask.size
    return mask, max(1, text_w), max(1, text_h)


def render_date_mask(
    text: str,
    font_path: str,
    font_size: int,
    shear_deg: float = 0.0,
) -> Tuple[Image.Image, int, int]:
    """
    後方互換用公開インターフェース（キャッシュから取得してコピーを返す）。
    """
    mask, w, h = render_date_mask_cached(text, font_path, font_size, shear_deg)
    return mask.copy(), w, h


@lru_cache(maxsize=32)
def generate_light_map_cached(
    date_text: str,
    font_path: str,
    base_font_size: int,
    shear_deg: float,
    preset_color: str,
    exposure_intensity: float,
    core_glow: float,
    halation: float,
) -> Tuple[np.ndarray, int, int, int]:
    """
    3層光学ブラーと光量合成を行い、(light_rgb, text_w, text_h, blur_pad) をキャッシュ生成する。
    """
    mask_core, text_w, text_h = render_date_mask_cached(
        text=date_text,
        font_path=font_path,
        font_size=base_font_size,
        shear_deg=shear_deg,
    )

    blur_pad = max(10, int(base_font_size * 1.5))
    padded_w = mask_core.width + blur_pad * 2
    padded_h = mask_core.height + blur_pad * 2

    padded_mask = Image.new("L", (padded_w, padded_h), 0)
    padded_mask.paste(mask_core, (blur_pad, blur_pad))

    # 3層光学ブラーレイヤー
    r_hal = max(1.0, base_font_size * 0.25 * halation)
    layer_hal = padded_mask.filter(ImageFilter.GaussianBlur(r_hal))

    r_body = max(0.5, base_font_size * 0.08)
    layer_body = padded_mask.filter(ImageFilter.GaussianBlur(r_body))

    r_core = max(0.2, base_font_size * 0.03 * core_glow)
    layer_core = padded_mask.filter(ImageFilter.GaussianBlur(r_core))

    # NumPy 配列化 (float32 [H, W, 1])
    arr_hal = np.asarray(layer_hal, dtype=np.float32)[..., None] / 255.0
    arr_body = np.asarray(layer_body, dtype=np.float32)[..., None] / 255.0
    arr_core = np.asarray(layer_core, dtype=np.float32)[..., None] / 255.0

    palette = COLOR_PRESETS.get(preset_color, COLOR_PRESETS["Amber Classic"])
    c_hal = np.asarray(palette["halation"], dtype=np.float32) / 255.0
    c_body = np.asarray(palette["body"], dtype=np.float32) / 255.0
    c_core = np.asarray(palette["core"], dtype=np.float32) / 255.0

    # NumPy ベクトル化一括合成 (arr * color * factor)
    light_rgb = (
        arr_hal * (c_hal * (0.45 * halation))
        + arr_body * (c_body * (0.95 * exposure_intensity))
        + arr_core * (c_core * (1.10 * core_glow))
    )

    return light_rgb, text_w, text_h, blur_pad


def render_film_date_stamp(
    image: Union[Image.Image, np.ndarray],
    config: Optional[DateStampConfig] = None,
    seed: Optional[int] = None,
    **kwargs
) -> Union[Image.Image, np.ndarray]:
    """
    ベース画像に対してフィルム日付スタンプを光学的に露光・焼き付け合成する。

    Parameters:
        image: PIL.Image または NumPy配列 [H, W, 3] (float32 0..1 or uint8 0..255)
        config: DateStampConfig インスタンス（省略時はデフォルト）
        seed: random_vintage 用の乱数シード
        **kwargs: config を上書きする個別パラメータ
    """
    if config is None:
        config = DateStampConfig()

    # style_preset の適用
    if "style_preset" in kwargs:
        config.style_preset = kwargs["style_preset"]
    config.apply_style_preset_if_set()

    # kwargs による動的オーバーライド
    for k, v in kwargs.items():
        if k != "style_preset" and hasattr(config, k) and v is not None:
            setattr(config, k, v)

    # 入力の型判定
    is_numpy = isinstance(image, np.ndarray)
    if is_numpy:
        np_input = image
        if np_input.dtype == np.uint8:
            base_rgb = np_input.astype(np.float32) / 255.0
        else:
            if np_input.max() > 1.01:
                base_rgb = np_input.astype(np.float32) / 255.0
            else:
                base_rgb = np_input.astype(np.float32).copy()
        h, w = base_rgb.shape[:2]
    else:
        pil_img = image.convert("RGB")
        w, h = pil_img.size
        base_rgb = np.array(pil_img, dtype=np.float32) / 255.0

    s = min(w, h)

    # 1. 日付文字列の解決
    date_text = resolve_date_text(config, seed=seed)

    # 2. フォントとシアー設定
    font_path, shear_deg = get_font_file_and_shear(config.font_type)
    if config.italic_angle > 0.0:
        shear_deg = config.italic_angle

    # フォントサイズ (短辺の約 3.2% * font_scale)
    base_font_size = max(10, int(s * 0.032 * config.font_scale))

    # 3〜6. キャッシュ化された光量マップの高速取得（3層ブラー・NumPyベクトル演算）
    light_rgb, text_w, text_h, blur_pad = generate_light_map_cached(
        date_text=date_text,
        font_path=font_path,
        base_font_size=base_font_size,
        shear_deg=round(shear_deg, 2),
        preset_color=config.preset_color,
        exposure_intensity=round(float(config.exposure_intensity), 3),
        core_glow=round(float(config.core_glow), 3),
        halation=round(float(config.halation), 3),
    )

    stamp_h, stamp_w = light_rgb.shape[:2]

    # 7. 配置計算 (基準となるテキスト本体の矩形を考慮)
    margin_x_px = int(s * 0.05 * config.margin_x)
    margin_y_px = int(s * 0.04 * config.margin_y)

    text_pos_x, text_pos_y = calculate_stamp_position(
        img_w=w,
        img_h=h,
        stamp_w=text_w,
        stamp_h=text_h,
        position=config.position,
        margin_x_px=margin_x_px,
        margin_y_px=margin_y_px,
    )

    # パディング付きカンバス全体の配置原点
    origin_x = text_pos_x - blur_pad
    origin_y = text_pos_y - blur_pad

    # 貼り付け領域と切り出し境界のクリッピング
    dst_x1 = max(0, origin_x)
    dst_y1 = max(0, origin_y)
    dst_x2 = min(w, origin_x + stamp_w)
    dst_y2 = min(h, origin_y + stamp_h)

    src_x1 = max(0, -(origin_x))
    src_y1 = max(0, -(origin_y))
    src_x2 = src_x1 + (dst_x2 - dst_x1)
    src_y2 = src_y1 + (dst_y2 - dst_y1)

    if dst_x2 > dst_x1 and dst_y2 > dst_y1 and src_x2 > src_x1 and src_y2 > src_y1:
        sub_base = base_rgb[dst_y1:dst_y2, dst_x1:dst_x2]
        sub_light = light_rgb[src_y1:src_y2, src_x1:src_x2]

        if config.optical_burn:
            # フィルム感光露光式（加算 + Reinhard肩特性によるハイライト飽和圧縮）
            # 背景が暗い場所では鮮明に発光、背景が明るい白飛び部では光が溶け込んで埋もれる
            combined = sub_base + sub_light
            over = np.maximum(0.0, combined - 1.0)
            combined = combined / (1.0 + over * 0.8)
        else:
            # スクリーン合成
            combined = 1.0 - (1.0 - sub_base) * (1.0 - np.clip(sub_light, 0.0, 1.0))

        base_rgb[dst_y1:dst_y2, dst_x1:dst_x2] = np.clip(combined, 0.0, 1.0)

    if is_numpy:
        if np_input.dtype == np.uint8:
            return (base_rgb * 255.0).astype(np.uint8)
        return base_rgb
    else:
        return Image.fromarray((base_rgb * 255.0).astype(np.uint8))
