"""
FilmDateStamp - ComfyUI Node Layer
Handles PyTorch Tensor conversions, parameter dispatch, and batch processing.
"""
import torch
import numpy as np

try:
    from .film_config import (
        DateStampConfig,
        COLOR_PRESETS,
        STYLE_PRESETS,
        SUPPORTED_DATE_FORMATS,
        SUPPORTED_POSITIONS,
        SUPPORTED_FONTS,
    )
    from .film_stamp import render_film_date_stamp
except (ImportError, ValueError):
    from film_config import (
        DateStampConfig,
        COLOR_PRESETS,
        STYLE_PRESETS,
        SUPPORTED_DATE_FORMATS,
        SUPPORTED_POSITIONS,
        SUPPORTED_FONTS,
    )
    from film_stamp import render_film_date_stamp


class FilmDateStamp:
    """
    Simulates authentic film quartz date stamps with physical optical burn-in,
    multi-scale halation, and emulsion highlight headroom roll-off.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "style_preset": (list(STYLE_PRESETS.keys()), {"default": "Custom"}),
                # 光学・フォント設定 (プリセット連動項目)
                "font_type": (SUPPORTED_FONTS, {"default": "FDS7_Strict_Compact (80s -7°)"}),
                "preset_color": (list(COLOR_PRESETS.keys()), {"default": "Amber Classic"}),
                "exposure_intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "core_glow": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "halation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
                # 日付設定 (直接文字列 または "auto" / "today" / "random")
                "date_string": ("STRING", {"default": "'98 12 24"}),
                "date_format": (SUPPORTED_DATE_FORMATS, {"default": "'YY MM DD"}),
                "show_time": ("BOOLEAN", {"default": False}),
                # レイアウト設定
                "position": (SUPPORTED_POSITIONS, {"default": "bottom_right"}),
                "font_scale": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.5, "step": 0.05}),
                "margin": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "irregularity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("image", "mask", "date_text")
    FUNCTION = "apply_stamp"
    CATEGORY = "image/film"

    @classmethod
    def IS_CHANGED(cls, image, date_string="'98 12 24", **kwargs):
        """
        auto / today / now の場合、キャッシュによる固定化を防ぎ実行時の最新日時を反映する。
        """
        raw_key = str(date_string).strip().lower()
        if raw_key in ("auto", "today", "now"):
            return float("NaN")
        return ""

    def apply_stamp(
        self,
        image: torch.Tensor,
        style_preset: str,
        font_type: str,
        preset_color: str,
        exposure_intensity: float,
        core_glow: float,
        halation: float,
        date_string: str,
        date_format: str,
        show_time: bool,
        position: str,
        font_scale: float,
        margin: float,
        seed: int = 0,
        irregularity: float = 1.0,
    ):
        """
        バッチ画像 [B, H, W, C] に対して日付スタンプを焼き付ける。
        """
        config = DateStampConfig(
            style_preset=style_preset,
            date_string=date_string,
            date_format=date_format,
            show_time=show_time,
            font_type=font_type,
            preset_color=preset_color,
            exposure_intensity=exposure_intensity,
            core_glow=core_glow,
            halation=halation,
            position=position,
            font_scale=font_scale,
            margin=margin,
            irregularity=irregularity,
        )

        batch_size = image.shape[0]
        out_list = []
        mask_list = []
        date_text_list = []

        for b in range(batch_size):
            # PyTorch Tensor [H, W, C] -> NumPy float32
            img_np = image[b].cpu().numpy().copy()

            # バッチごとに異なるランダム日付・ゆらぎを付与（seed + b）
            batch_seed = (seed + b) if seed is not None else None

            result_np, mask_np, date_text = render_film_date_stamp(
                image=img_np,
                config=config,
                seed=batch_seed,
                return_details=True,
            )

            out_list.append(result_np)
            mask_list.append(mask_np)
            date_text_list.append(date_text)

        out_array = np.stack(out_list, axis=0)
        output_tensor = torch.from_numpy(out_array).to(image.device, dtype=image.dtype)

        mask_array = np.stack(mask_list, axis=0)
        output_mask_tensor = torch.from_numpy(mask_array).to(image.device, dtype=torch.float32)

        out_date_text = date_text_list[0] if date_text_list else ""

        return (output_tensor, output_mask_tensor, out_date_text)


NODE_CLASS_MAPPINGS = {
    "FilmDateStamp": FilmDateStamp,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilmDateStamp": "Film Date Stamp (Optical Burn-in)",
}
