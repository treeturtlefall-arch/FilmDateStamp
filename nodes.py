"""
FilmDateStamp - ComfyUI ノード定義層
PyTorch Tensor との相互変換および高速バッチ処理を行う。
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
    フィルム乳剤へのLED光学感光（Optical Burn-in）をシミュレートするクォーツデートスタンプノード。
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "style_preset": (list(STYLE_PRESETS.keys()), {"default": "Custom"}),
                # 光学・フォント設定 (プリセット連動項目)
                "font_type": (SUPPORTED_FONTS, {"default": "DSEG7_Classic (7-Segment)"}),
                "preset_color": (list(COLOR_PRESETS.keys()), {"default": "Amber Classic"}),
                "exposure_intensity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "core_glow": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 2.0, "step": 0.05}),
                "halation": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
                "optical_burn": ("BOOLEAN", {"default": True}),
                # 日付設定
                "date_mode": (["custom", "current_date", "random_vintage"], {"default": "custom"}),
                "date_string": ("STRING", {"default": "'98 12 24"}),
                "date_format": (SUPPORTED_DATE_FORMATS, {"default": "'YY MM DD"}),
                "show_time": ("BOOLEAN", {"default": False}),
                # レイアウト設定
                "position": (SUPPORTED_POSITIONS, {"default": "bottom_right"}),
                "font_scale": ("FLOAT", {"default": 1.0, "min": 0.5, "max": 2.5, "step": 0.05}),
                "margin_x": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
                "margin_y": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 3.0, "step": 0.1}),
            },
            "optional": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "apply_stamp"
    CATEGORY = "image/film"

    def apply_stamp(
        self,
        image: torch.Tensor,
        style_preset: str,
        font_type: str,
        preset_color: str,
        exposure_intensity: float,
        core_glow: float,
        halation: float,
        optical_burn: bool,
        date_mode: str,
        date_string: str,
        date_format: str,
        show_time: bool,
        position: str,
        font_scale: float,
        margin_x: float,
        margin_y: float,
        seed: int = 0,
    ):
        """
        バッチ画像 [B, H, W, C] に対して日付スタンプを焼き付ける。
        """
        config = DateStampConfig(
            style_preset=style_preset,
            date_mode=date_mode,
            date_string=date_string,
            date_format=date_format,
            show_time=show_time,
            font_type=font_type,
            preset_color=preset_color,
            exposure_intensity=exposure_intensity,
            core_glow=core_glow,
            halation=halation,
            optical_burn=optical_burn,
            position=position,
            font_scale=font_scale,
            margin_x=margin_x,
            margin_y=margin_y,
        )

        # ComfyUI フロントエンドではプリセット選択時に各ウィジェットが自動同期されるため、
        # ノード実行時はウィジェットから渡された現在の入力値をそのまま使用します（不要な再上書きを防止）。
        # ※ style_preset == "Custom" 以外で直接 API 実行された場合でも、渡された個別ウィジェット引数が尊重されます。

        batch_size = image.shape[0]
        out_list = []

        for b in range(batch_size):
            # PyTorch Tensor [H, W, C] -> NumPy float32
            img_np = image[b].cpu().numpy().copy()

            # バッチごとに異なるランダム日付を付与（seed + b）
            batch_seed = (seed + b) if seed is not None else None

            result_np = render_film_date_stamp(
                image=img_np,
                config=config,
                seed=batch_seed,
            )

            out_list.append(result_np)

        out_array = np.stack(out_list, axis=0)
        output_tensor = torch.from_numpy(out_array).to(image.device, dtype=image.dtype)
        return (output_tensor,)


NODE_CLASS_MAPPINGS = {
    "FilmDateStamp": FilmDateStamp,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilmDateStamp": "Film Date Stamp (Optical Burn-in)",
}
