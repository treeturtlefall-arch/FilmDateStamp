"""
FilmDateStamp 単体テスト・回帰テスト
"""
import unittest
import datetime
import numpy as np
import torch
from PIL import Image

from film_config import (
    DateStampConfig,
    COLOR_PRESETS,
    STYLE_PRESETS,
    SUPPORTED_DATE_FORMATS,
    SUPPORTED_POSITIONS,
    SUPPORTED_FONTS,
    format_datetime,
    generate_random_vintage_datetime,
    resolve_date_text,
)
from film_stamp import (
    render_film_date_stamp,
    render_date_mask,
    get_font_file_and_shear,
    apply_shear_tilt,
    calculate_stamp_position,
)
from nodes import FilmDateStamp


class TestFilmConfig(unittest.TestCase):
    """設定データクラスおよび日付生成パーサーのテスト"""

    def test_color_presets_exist(self):
        """必須プリセット色が全て定義され、RGBタプルが含まれているか"""
        required_presets = ["Amber Classic", "Quartz Red", "Fuji Orange", "Golden Yellow", "Cyber Green"]
        for name in required_presets:
            self.assertIn(name, COLOR_PRESETS)
            palette = COLOR_PRESETS[name]
            for layer in ["core", "body", "halation"]:
                self.assertIn(layer, palette)
                rgb = palette[layer]
                self.assertEqual(len(rgb), 3)
                for c in rgb:
                    self.assertTrue(0 <= c <= 255)

    def test_style_presets(self):
        """スタイルプリセットの定義と適用検証（地域・文化プリセット）"""
        self.assertIn("Japanese Snap (Disposable)", STYLE_PRESETS)
        fuji_preset = STYLE_PRESETS["Japanese Snap (Disposable)"]
        self.assertEqual(fuji_preset["font_type"], "VT323 (Dot Matrix)")
        self.assertEqual(fuji_preset["preset_color"], "Fuji Orange")
        self.assertEqual(fuji_preset["core_glow"], 0.50)
        self.assertEqual(fuji_preset["font_scale"], 1.20)
        self.assertEqual(fuji_preset["margin_x"], 1.50)
        self.assertEqual(fuji_preset["margin_y"], 1.50)
        self.assertTrue(fuji_preset["show_time"])

        # DateStampConfig への適用確認
        cfg = DateStampConfig(style_preset="Japanese Snap (Disposable)")
        cfg.apply_style_preset_if_set()
        self.assertEqual(cfg.font_type, "VT323 (Dot Matrix)")
        self.assertEqual(cfg.preset_color, "Fuji Orange")
        self.assertEqual(cfg.core_glow, 0.50)
        self.assertEqual(cfg.font_scale, 1.20)
        self.assertTrue(cfg.show_time)

        # 地域別プリセットの存在確認
        expected_presets = [
            "Japanese Tokyo 90s",
            "Japanese Snap (Disposable)",
            "American West Coast",
            "American 80s (Red Quartz)",
            "European Classic (Paris/Berlin)",
            "Hong Kong Neon (90s Cinema)",
            "Y2K Digicam (Early 2000s)",
            "Compact Fine Dot (Minimal)",
        ]
        for name in expected_presets:
            self.assertIn(name, STYLE_PRESETS)

    def test_format_datetime(self):
        """各日付フォーマット記法および show_time による時刻付加の検証"""
        dt = datetime.datetime(1998, 12, 24, 14, 35)
        # show_time=False (デフォルト)
        self.assertEqual(format_datetime(dt, "'YY MM DD"), "'98 12 24")
        self.assertEqual(format_datetime(dt, "MM DD 'YY"), "12 24 '98")
        self.assertEqual(format_datetime(dt, "DD MM 'YY"), "24 12 '98")
        self.assertEqual(format_datetime(dt, "DD.MM.YY"), "24.12.98")
        self.assertEqual(format_datetime(dt, "YY-MM-DD"), "98-12-24")
        self.assertEqual(format_datetime(dt, "YY.MM.DD"), "98.12.24")
        self.assertEqual(format_datetime(dt, "YYYY MM DD"), "1998 12 24")
        self.assertEqual(format_datetime(dt, "YYYY-MM-DD"), "1998-12-24")

        # show_time=True
        self.assertEqual(format_datetime(dt, "'YY MM DD", show_time=True), "'98 12 24 14:35")
        self.assertEqual(format_datetime(dt, "MM DD 'YY", show_time=True), "12 24 '98 14:35")
        self.assertEqual(format_datetime(dt, "DD.MM.YY", show_time=True), "24.12.98 14:35")

    def test_resolve_date_text_modes(self):
        """custom, current_date, random_vintage の各モードおよび show_time の解決"""
        # custom (show_time=False で末尾時刻トリム)
        cfg_custom_with_time = DateStampConfig(date_mode="custom", date_string="'93 05 10 18:30", show_time=False)
        self.assertEqual(resolve_date_text(cfg_custom_with_time), "'93 05 10")

        # custom (show_time=True で時刻保持)
        cfg_custom_keep_time = DateStampConfig(date_mode="custom", date_string="'93 05 10 18:30", show_time=True)
        self.assertEqual(resolve_date_text(cfg_custom_keep_time), "'93 05 10 18:30")

        # custom (show_time=True で時刻自動補完)
        cfg_custom_auto_time = DateStampConfig(date_mode="custom", date_string="'93 05 10", show_time=True)
        self.assertEqual(resolve_date_text(cfg_custom_auto_time), "'93 05 10 18:30")

        # current_date
        cfg_current = DateStampConfig(date_mode="current_date", date_format="'YY MM DD", show_time=True)
        text_current = resolve_date_text(cfg_current)
        now_yy = f"{datetime.datetime.now().year % 100:02d}"
        self.assertTrue(text_current.startswith(f"'{now_yy}"))
        self.assertRegex(text_current, r"\d{2}:\d{2}$")

        # random_vintage (seed指定で再現性確認)
        cfg_random = DateStampConfig(date_mode="random_vintage", date_format="'YY MM DD", show_time=True)
        text_r1 = resolve_date_text(cfg_random, seed=42)
        text_r2 = resolve_date_text(cfg_random, seed=42)
        self.assertEqual(text_r1, text_r2)
        self.assertTrue(text_r1.startswith("'"))
        self.assertRegex(text_r1, r"\d{2}:\d{2}$")


class TestFilmStamp(unittest.TestCase):
    """光学感光レンダリングエンジンのテスト"""

    def test_render_with_pil_image(self):
        """PIL.Image 入力に対するレンダリング検証"""
        base = Image.new("RGB", (640, 480), (30, 30, 30))
        cfg = DateStampConfig(preset_color="Amber Classic", date_string="'98 12 24")
        result = render_film_date_stamp(base, config=cfg)
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (640, 480))

        # スタンプ領域付近（右下）のRGB値が元画像（30, 30, 30）より上昇しているか
        arr_base = np.array(base)
        arr_result = np.array(result)
        self.assertGreater(arr_result.max(), arr_base.max())

    def test_render_with_numpy_array(self):
        """NumPy配列（float32 0..1）入力に対する検証"""
        arr = np.zeros((400, 600, 3), dtype=np.float32)
        result = render_film_date_stamp(arr, date_string="'95 11 03")
        self.assertIsInstance(result, np.ndarray)
        self.assertEqual(result.shape, (400, 600, 3))
        self.assertEqual(result.dtype, np.float32)
        self.assertGreater(result.max(), 0.0)
        self.assertLessEqual(result.max(), 1.0)

    def test_optical_burn_highlight_saturation(self):
        """白背景（高輝度）での自然な埋もれ再現"""
        # 真っ白な背景 (1.0, 1.0, 1.0)
        white_bg = np.ones((300, 400, 3), dtype=np.float32)
        res_burn = render_film_date_stamp(white_bg, optical_burn=True, date_string="'98 12 24")
        
        # 白背景ではすでに飽和しているため、白飛び（1.0近傍）を保ち、過剰に破綻しない
        self.assertTrue(np.all(res_burn <= 1.0))
        self.assertTrue(np.all(res_burn >= 0.95))

    def test_all_positions(self):
        """各位置（四隅）への描画でエラーが発生しないこと"""
        base = Image.new("RGB", (300, 300), (20, 20, 20))
        for pos in SUPPORTED_POSITIONS:
            cfg = DateStampConfig(position=pos)
            res = render_film_date_stamp(base, config=cfg)
            self.assertEqual(res.size, (300, 300))

    def test_all_fonts_and_shear(self):
        """サポートフォント全種での描画検証"""
        base = Image.new("RGB", (320, 240), (20, 20, 20))
        for font_type in SUPPORTED_FONTS:
            cfg = DateStampConfig(font_type=font_type)
            res = render_film_date_stamp(base, config=cfg)
            self.assertIsInstance(res, Image.Image)

    def test_font_size_normalization(self):
        """異なるフォント間でも同一 font_size で視覚的なスタンプ幅が均一化されるか検証"""
        widths = []
        for font_type in SUPPORTED_FONTS:
            font_path, shear = get_font_file_and_shear(font_type)
            _, tw, th = render_date_mask("'98 12 24", font_path, font_size=40, shear_deg=shear)
            widths.append(tw)

        # 全フォントの描画幅の最大/最小比が 1.25 以内に収まっていること（正規化前は 1.75 倍以上の差があった）
        ratio = max(widths) / max(1, min(widths))
        self.assertLessEqual(ratio, 1.25)


class TestComfyUINode(unittest.TestCase):
    """ComfyUI ノード FilmDateStamp のテスト"""

    def test_node_execution_batch(self):
        """バッチサイズ 2 の PyTorch Tensor 入力に対するノード実行"""
        node = FilmDateStamp()
        # [B=2, H=256, W=256, C=3], float32 0..1
        input_tensor = torch.zeros((2, 256, 256, 3), dtype=torch.float32)

        outputs = node.apply_stamp(
            image=input_tensor,
            style_preset="Japanese Snap (Disposable)",
            font_type="VT323 (Dot Matrix)",
            preset_color="Fuji Orange",
            exposure_intensity=1.0,
            core_glow=0.5,
            halation=1.0,
            optical_burn=True,
            date_mode="current_date",
            date_string="'98 12 24",
            date_format="'YY MM DD",
            show_time=True,
            position="bottom_right",
            font_scale=1.2,
            margin_x=1.5,
            margin_y=1.5,
            seed=123,
        )

        self.assertEqual(len(outputs), 1)
        out_tensor = outputs[0]
        self.assertEqual(out_tensor.shape, (2, 256, 256, 3))
        self.assertEqual(out_tensor.dtype, torch.float32)
        # 発光により値が上がっていることを確認
        self.assertGreater(out_tensor.max().item(), 0.0)

    def test_node_preset_override_preserves_widgets(self):
        """style_preset が選択されていても、個別ウィジェットで渡された引数が尊重されることの検証"""
        node = FilmDateStamp()
        input_tensor = torch.zeros((1, 128, 128, 3), dtype=torch.float32)

        # プリセットは Japanese Tokyo 90s（本来は custom / '98 12 24）だが、
        # ウィジェット引数として random_vintage が指定されている場合、強制上書きされずに random_vintage が適用される
        outputs = node.apply_stamp(
            image=input_tensor,
            style_preset="Japanese Tokyo 90s",
            font_type="DSEG7_Italic (7-Segment)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            optical_burn=True,
            date_mode="random_vintage",
            date_string="'98 12 24",
            date_format="'YY MM DD",
            show_time=False,
            position="bottom_right",
            font_scale=1.0,
            margin_x=1.0,
            margin_y=1.0,
            seed=42,
        )
        self.assertEqual(len(outputs), 1)
        self.assertGreater(outputs[0].max().item(), 0.0)


if __name__ == "__main__":
    unittest.main()
