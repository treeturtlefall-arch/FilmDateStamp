"""
FilmDateStamp 単体テスト・回帰テスト
"""
import unittest
import math
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

        # 特殊・空想カラー（Cyber Green, Neo Pink, Crimson Red）が末尾に配置されていることの検証
        preset_keys = list(COLOR_PRESETS.keys())
        self.assertIn("Cyber Green", preset_keys[-3:])
        self.assertIn("Neo Pink", preset_keys[-3:])
        self.assertIn("Crimson Red", preset_keys[-3:])
        # Bulb Amber が削除されていること
        self.assertNotIn("Bulb Amber", COLOR_PRESETS)

    def test_style_presets(self):
        """スタイルプリセットの定義と適用検証（地域・文化プリセット）"""
        self.assertIn("Japanese Snap (Disposable)", STYLE_PRESETS)
        fuji_preset = STYLE_PRESETS["Japanese Snap (Disposable)"]
        self.assertEqual(fuji_preset["font_type"], "FDS_Dot_Strict (90s Dot Matrix)")
        self.assertEqual(fuji_preset["preset_color"], "Fuji Orange")
        self.assertEqual(fuji_preset["core_glow"], 0.50)
        self.assertEqual(fuji_preset["font_scale"], 1.20)
        self.assertEqual(fuji_preset["margin"], 1.50)
        self.assertTrue(fuji_preset["show_time"])

        # DateStampConfig への適用確認
        cfg = DateStampConfig(style_preset="Japanese Snap (Disposable)")
        cfg.apply_style_preset_if_set()
        self.assertEqual(cfg.font_type, "FDS_Dot_Strict (90s Dot Matrix)")
        self.assertEqual(cfg.preset_color, "Fuji Orange")
        self.assertEqual(cfg.core_glow, 0.50)
        self.assertEqual(cfg.font_scale, 1.20)
        self.assertEqual(cfg.margin, 1.50)
        self.assertTrue(cfg.show_time)

        # 主要プリセットの存在確認およびマージン初期値の検証
        margin_115_presets = [
            "Japanese Tokyo 90s",
            "American West Coast",
            "American 80s (Red Quartz)",
            "European Classic (Paris/Berlin)",
            "Monochrome 70s (Canodate E)",
            "Vintage 70s Color (Datematic)",
        ]
        for name in margin_115_presets:
            self.assertIn(name, STYLE_PRESETS)
            self.assertEqual(STYLE_PRESETS[name]["margin"], 1.15)
            c = DateStampConfig(style_preset=name)
            c.apply_style_preset_if_set()
            self.assertEqual(c.margin, 1.15)

    def test_all_style_presets_values_in_supported_lists(self):
        """全スタイルプリセットで指定されている各値が SUPPORTED_* リストに含まれていることの検証"""
        for preset_name, preset_dict in STYLE_PRESETS.items():
            if preset_name == "Custom" or preset_dict is None:
                continue
            if "font_type" in preset_dict:
                self.assertIn(preset_dict["font_type"], SUPPORTED_FONTS, f"Invalid font_type in preset {preset_name}")
            if "preset_color" in preset_dict:
                self.assertIn(preset_dict["preset_color"], COLOR_PRESETS, f"Invalid preset_color in preset {preset_name}")
            if "date_format" in preset_dict:
                self.assertIn(preset_dict["date_format"], SUPPORTED_DATE_FORMATS, f"Invalid date_format in preset {preset_name}")
            if "position" in preset_dict:
                self.assertIn(preset_dict["position"], SUPPORTED_POSITIONS, f"Invalid position in preset {preset_name}")

    def test_format_datetime(self):
        """各日付フォーマット記法および show_time による時刻付加の検証"""
        dt = datetime.datetime(1998, 12, 24, 14, 35)
        # show_time=False (デフォルト)
        self.assertEqual(format_datetime(dt, "'YY MM DD"), "'98 12 24")
        self.assertEqual(format_datetime(dt, "YY MM DD"), "98 12 24")
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
        """direct string, auto, today, random の各キーワード解決および show_time の制御"""
        # 1. 直接指定 (show_time=False で末尾時刻トリム)
        cfg_custom_with_time = DateStampConfig(date_string="'93 05 10 18:30", show_time=False)
        self.assertEqual(resolve_date_text(cfg_custom_with_time), "'93 05 10")

        # 2. 直接指定 (show_time=True で時刻保持)
        cfg_custom_keep_time = DateStampConfig(date_string="'93 05 10 18:30", show_time=True)
        self.assertEqual(resolve_date_text(cfg_custom_keep_time), "'93 05 10 18:30")

        # 3. 直接指定 (show_time=True で時刻自動補完)
        cfg_custom_auto_time = DateStampConfig(date_string="'93 05 10", show_time=True)
        self.assertEqual(resolve_date_text(cfg_custom_auto_time), "'93 05 10 18:30")

        # 4. auto / today (現在日時の自動生成)
        for kw in ("auto", "today", "now"):
            cfg_auto = DateStampConfig(date_string=kw, date_format="'YY MM DD", show_time=True)
            text_auto = resolve_date_text(cfg_auto)
            now_yy = f"{datetime.datetime.now().year % 100:02d}"
            self.assertTrue(text_auto.startswith(f"'{now_yy}"))
            self.assertRegex(text_auto, r"\d{2}:\d{2}$")

        # 5. random (seed指定で再現性確認)
        cfg_random = DateStampConfig(date_string="random", date_format="'YY MM DD", show_time=True)
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

    def test_numpy_non_destructive(self):
        """入力 NumPy 配列がインプレースで書き換えられないことの検証"""
        orig = np.zeros((200, 200, 3), dtype=np.float32)
        orig_copy = orig.copy()
        result = render_film_date_stamp(orig, date_string="'98 12 24")
        # 元の配列が 0.0 のまま維持されていること
        self.assertEqual(float(orig.max()), 0.0)
        np.testing.assert_array_equal(orig, orig_copy)
        # 戻り値はスタンプが押されていること
        self.assertGreater(float(result.max()), 0.0)

    def test_optical_burn_highlight_saturation(self):
        """白背景（高輝度）での自然な埋もれ再現（常時光学モデル）"""
        # 真っ白な背景 (1.0, 1.0, 1.0)
        white_bg = np.ones((300, 400, 3), dtype=np.float32)
        res_burn = render_film_date_stamp(white_bg, date_string="'98 12 24")
        
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
        """厳選サポートフォント（実機5種＋空想3種＝計8種）での描画検証"""
        self.assertEqual(len(SUPPORTED_FONTS), 8)
        base = Image.new("RGB", (320, 240), (20, 20, 20))
        for font_type in SUPPORTED_FONTS:
            cfg = DateStampConfig(font_type=font_type)
            res = render_film_date_stamp(base, config=cfg)
            self.assertIsInstance(res, Image.Image)

    def test_font_size_normalization(self):
        """全厳選フォント8種間で同一 font_size で視覚的なスタンプ幅が均一化されるか検証"""
        widths = []
        for font_type in SUPPORTED_FONTS:
            font_path, shear = get_font_file_and_shear(font_type)
            _, tw, th = render_date_mask("'98 12 24", font_path, font_size=40, shear_deg=shear)
            widths.append(tw)

        ratio = max(widths) / max(1, min(widths))
        # 全8種（実機スリム7セグから超ワイド幾何学・カリグラフィまで）の最大/最小幅比率が25%以内に収まること
        self.assertLessEqual(ratio, 1.25)

    def test_strict_7seg_fonts_geometry_and_glyphs(self):
        """FDS7Strict-SLR / FDS7Strict-Compact フォントのメタデータ・収録文字・スリム比率検証"""
        import os
        from fontTools.ttLib import TTFont

        strict_fonts = [
            ("FDS7_Strict_SLR (80s 0°)", "FDS7Strict-SLR.ttf", 0.0),
            ("FDS7_Strict_Compact (80s -7°)", "FDS7Strict-Compact.ttf", -7.0),
        ]
        required_codepoints = [
            0x20, 0x27, 0x2D, 0x2E, 0x3A,
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
        ]
        for font_key, expected_file, expected_angle in strict_fonts:
            self.assertIn(font_key, SUPPORTED_FONTS)
            fpath, _ = get_font_file_and_shear(font_key)
            self.assertTrue(os.path.exists(fpath), f"Missing font file: {fpath}")
            self.assertTrue(fpath.endswith(expected_file))

            tt = TTFont(fpath)
            self.assertEqual(tt["head"].unitsPerEm, 1000)
            self.assertAlmostEqual(tt["post"].italicAngle, expected_angle, places=1)

            cmap = tt.getBestCmap()
            for cp in required_codepoints:
                self.assertIn(cp, cmap, f"Codepoint U+{cp:04X} missing in {expected_file}")

            # 0.0° 直立版の数字 '8' の描画バウンディングボックスが W=400, H=800 (W/H=0.500) であることを検証
            if expected_angle == 0.0:
                g8 = tt["glyf"]["eight"]
                w = g8.xMax - g8.xMin
                h = g8.yMax - g8.yMin
                self.assertEqual(w, 400)
                self.assertEqual(h, 800)
                self.assertAlmostEqual(w / h, 0.500, places=3)

    def test_strict_dot_font_geometry_and_glyphs(self):
        """FDSDotStrict-Regular.ttf の UPM 1000、直立角 0.0°、全収録文字、等幅480、およびアスペクト比 (W/H ≈ 0.537) 検証"""
        import os
        from fontTools.ttLib import TTFont

        font_key = "FDS_Dot_Strict (90s Dot Matrix)"
        self.assertIn(font_key, SUPPORTED_FONTS)
        fpath, shear = get_font_file_and_shear(font_key)
        self.assertTrue(os.path.exists(fpath), f"Missing font file: {fpath}")
        self.assertTrue(fpath.endswith("FDSDotStrict-Regular.ttf"))
        self.assertEqual(shear, 0.0)

        tt = TTFont(fpath)
        self.assertEqual(tt["head"].unitsPerEm, 1000)
        self.assertAlmostEqual(tt["post"].italicAngle, 0.0, places=1)
        self.assertEqual(tt["post"].isFixedPitch, 1)

        required_codepoints = [
            0x20, 0x27, 0x2D, 0x2E, 0x2F, 0x3A,
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
        ]
        cmap = tt.getBestCmap()
        for cp in required_codepoints:
            self.assertIn(cp, cmap, f"Codepoint U+{cp:04X} missing in FDSDotStrict-Regular.ttf")
            gname = cmap[cp]
            adv, _ = tt["hmtx"][gname]
            self.assertEqual(adv, 480, f"Glyph {gname} advance width should be 480, got {adv}")

        # 数字 '0' および '8' の描画寸法 W=365, H=680 (W/H ≈ 0.537) の検証
        for gname in ("zero", "eight"):
            g = tt["glyf"][gname]
            w = g.xMax - g.xMin
            h = g.yMax - g.yMin
            self.assertEqual(w, 365)
            self.assertEqual(h, 680)
            self.assertAlmostEqual(w / h, 0.537, places=3)

        # 数字 '0' が斜線なしの中空リング（16ドット＝16輪郭）であることの検証
        g0 = tt["glyf"]["zero"]
        self.assertEqual(g0.numberOfContours, 16)
        # アポストロフィ ''' が右上から左下への斜め2ドット（2輪郭）であることの検証
        g_apos = tt["glyf"]["quotesingle"]
        self.assertEqual(g_apos.numberOfContours, 2)

    def test_strict_mechanical_font_geometry_and_glyphs(self):
        """FDSMechanical70s-Regular.ttf の UPM 1000、直立角 0.0°、等幅 620、Cap Height 720、全収録文字、'0'カプセル形状、'1'カギ鼻の検証"""
        import os
        from fontTools.ttLib import TTFont

        font_key = "FDS_Mechanical_70s (70s Mechanical)"
        self.assertIn(font_key, SUPPORTED_FONTS)
        fpath, shear = get_font_file_and_shear(font_key)
        self.assertTrue(os.path.exists(fpath), f"Missing font file: {fpath}")
        self.assertTrue(fpath.endswith("FDSMechanical70s-Regular.ttf"))
        self.assertEqual(shear, 0.0)

        tt = TTFont(fpath)
        self.assertEqual(tt["head"].unitsPerEm, 1000)
        self.assertAlmostEqual(tt["post"].italicAngle, 0.0, places=1)
        self.assertEqual(tt["post"].isFixedPitch, 1)
        self.assertEqual(tt["OS/2"].sCapHeight, 720)

        required_codepoints = [
            0x20, 0x27, 0x2D, 0x2E, 0x2F, 0x3A,
            0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39,
        ]
        cmap = tt.getBestCmap()
        for cp in required_codepoints:
            self.assertIn(cp, cmap, f"Codepoint U+{cp:04X} missing in FDSMechanical70s-Regular.ttf")
            gname = cmap[cp]
            adv, _ = tt["hmtx"][gname]
            self.assertEqual(adv, 620, f"Glyph {gname} advance width should be 620, got {adv}")

        # 数字 '0' のカプセル形状検証 (W=380, H=720, W/H ≈ 0.528, 外周+内周の2輪郭)
        g0 = tt["glyf"]["zero"]
        w0 = g0.xMax - g0.xMin
        h0 = g0.yMax - g0.yMin
        self.assertEqual(w0, 380)
        self.assertEqual(h0, 720)
        self.assertAlmostEqual(w0 / h0, 380.0 / 720.0, places=3)
        self.assertEqual(g0.numberOfContours, 2)

        # 数字 '1' の左下45°カギ鼻ビーク検証 (メインステム幅 96 に対しカギ鼻突出により総幅 240, H=720, 台座なし単一輪郭)
        g1 = tt["glyf"]["one"]
        w1 = g1.xMax - g1.xMin
        h1 = g1.yMax - g1.yMin
        self.assertEqual(w1, 240)
        self.assertEqual(h1, 720)
        self.assertEqual(g1.numberOfContours, 1)
        self.assertLess(g1.xMin, 220)
        self.assertEqual(g1.xMax, 406)


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
            font_type="FDS_Dot_Strict (90s Dot Matrix)",
            preset_color="Fuji Orange",
            exposure_intensity=1.0,
            core_glow=0.5,
            halation=1.0,
            date_string="auto",
            date_format="'YY MM DD",
            show_time=True,
            position="bottom_right",
            font_scale=1.2,
            margin=1.5,
            seed=123,
        )

        self.assertEqual(len(outputs), 3)
        out_tensor, out_mask, out_text = outputs
        self.assertEqual(out_tensor.shape, (2, 256, 256, 3))
        self.assertEqual(out_tensor.dtype, torch.float32)
        # 発光により値が上がっていることを確認
        self.assertGreater(out_tensor.max().item(), 0.0)

        # MASK 出力の検証 [B, H, W]
        self.assertEqual(out_mask.shape, (2, 256, 256))
        self.assertEqual(out_mask.dtype, torch.float32)
        self.assertGreater(out_mask.max().item(), 0.0)
        self.assertLessEqual(out_mask.max().item(), 1.0)

        # STRING 出力の検証
        self.assertIsInstance(out_text, str)
        self.assertGreater(len(out_text), 0)

    def test_node_preset_override_preserves_widgets(self):
        """style_preset が選択されていても、個別ウィジェットで渡された引数が尊重されることの検証"""
        node = FilmDateStamp()
        input_tensor = torch.zeros((1, 128, 128, 3), dtype=torch.float32)

        outputs = node.apply_stamp(
            image=input_tensor,
            style_preset="Japanese Tokyo 90s",
            font_type="FDS7_Strict_Compact (80s -7°)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            date_string="88 88 88",
            date_format="'YY MM DD",
            show_time=False,
            position="top_left",
            font_scale=1.0,
            margin=1.0,
            seed=42,
        )
        self.assertEqual(len(outputs), 3)
        out, out_mask, out_text = outputs
        self.assertEqual(out_text, "88 88 88")
        # top_left (上半分・左半分) に光が存在し、bottom_right (右下) は空であることを検証
        self.assertGreater(out[0, 0:40, 0:60].max().item(), 0.1)
        self.assertEqual(out[0, 80:128, 60:128].max().item(), 0.0)
        # マスクも top_left にのみ値が存在することを確認
        self.assertGreater(out_mask[0, 0:40, 0:60].max().item(), 0.1)
        self.assertEqual(out_mask[0, 80:128, 60:128].max().item(), 0.0)

    def test_rgba_and_grayscale_input(self):
        """RGBA (4ch) や 1ch グレースケールテンソルが正常に処理され、チャンネル数が維持されることの検証"""
        node = FilmDateStamp()
        base_kwargs = dict(
            style_preset="Custom",
            font_type="FDS7_Strict_Compact (80s -7°)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            date_string="'98 12 24",
            date_format="'YY MM DD",
            show_time=False,
            position="bottom_right",
            font_scale=1.0,
            margin=1.0,
            seed=0,
        )
        # 1. RGBA (4ch)
        rgba_img = torch.zeros((1, 128, 128, 4), dtype=torch.float32)
        rgba_img[:, :, :, 3] = 0.75  # アルファ値
        out_rgba = node.apply_stamp(image=rgba_img, **base_kwargs)[0]
        self.assertEqual(out_rgba.shape, (1, 128, 128, 4))
        # アルファチャンネルが保持されているか
        self.assertAlmostEqual(out_rgba[0, 0, 0, 3].item(), 0.75, places=3)
        self.assertGreater(out_rgba[0, :, :, :3].max().item(), 0.0)

        # 2. 1ch グレースケール
        gray_img = torch.zeros((1, 128, 128, 1), dtype=torch.float32)
        out_gray = node.apply_stamp(image=gray_img, **base_kwargs)[0]
        self.assertEqual(out_gray.shape, (1, 128, 128, 1))
        self.assertGreater(out_gray.max().item(), 0.0)

    def test_hdr_overshoot_not_darkened(self):
        """1.01 を超える float 画像で、画像全体が誤って /255 されて暗転しないことの検証"""
        node = FilmDateStamp()
        img = torch.full((1, 128, 128, 3), 0.5, dtype=torch.float32)
        img[0, 0, 0, 0] = 1.05

        out = node.apply_stamp(
            image=img,
            style_preset="Custom",
            font_type="FDS7_Strict_Compact (80s -7°)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            date_string="'98 12 24",
            date_format="'YY MM DD",
            show_time=False,
            position="bottom_right",
            font_scale=1.0,
            margin=1.0,
            seed=0,
        )[0]
        # 背景（スタンプの影響のない左上）が ~0.5 を維持していること
        self.assertAlmostEqual(out[0, 10, 10, 0].item(), 0.5, places=2)

    def test_multiline_and_special_chars_sanitized(self):
        """改行やタブ、制御文字を含む文字列でもクラッシュせず安全に描画されることの検証"""
        node = FilmDateStamp()
        img = torch.zeros((1, 128, 128, 3), dtype=torch.float32)
        out = node.apply_stamp(
            image=img,
            style_preset="Custom",
            font_type="FDS7_Strict_Compact (80s -7°)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            date_string="'98\n12\t24",
            date_format="'YY MM DD",
            show_time=False,
            position="bottom_right",
            font_scale=1.0,
            margin=1.0,
            seed=0,
        )[0]
        self.assertGreater(out.max().item(), 0.0)

    def test_is_changed_auto_date(self):
        """date_string が 'auto' / 'today' / 'now' で再評価を促すため NaN が返ることの検証"""
        for kw in ("auto", "today", "now", "AUTO"):
            val_auto = FilmDateStamp.IS_CHANGED(torch.zeros((1, 1, 1, 3)), date_string=kw)
            self.assertTrue(math.isnan(val_auto))

        val_fixed = FilmDateStamp.IS_CHANGED(torch.zeros((1, 1, 1, 3)), date_string="'98 12 24")
        self.assertEqual(val_fixed, "")

    def test_js_and_python_presets_consistency(self):
        """web/js/film_date_stamp.js と film_config.py のプリセット定義が同期していることの検証"""
        import os
        js_path = os.path.join(os.path.dirname(__file__), "..", "web", "js", "film_date_stamp.js")
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        for preset_name, preset_dict in STYLE_PRESETS.items():
            if preset_name == "Custom" or preset_dict is None:
                continue
            self.assertIn(f'"{preset_name}"', js_content, f"Preset '{preset_name}' is missing in film_date_stamp.js")
            for key in ("date_string", "date_format", "font_type", "preset_color", "position"):
                expected_val = preset_dict[key]
                self.assertIn(f'"{expected_val}"', js_content, f"Value '{expected_val}' for key '{key}' in preset '{preset_name}' missing in JS")

    def test_official_workflow_widget_mapping(self):
        """公式ワークフロー JSON の FilmDateStamp ノードの widgets_values 順序が INPUT_TYPES と整合していることの検証"""
        import json, os
        wf_path = os.path.join(os.path.dirname(__file__), "..", "workflows", "film_date_stamp_workflow.json")
        with open(wf_path, "r", encoding="utf-8") as f:
            wf_data = json.load(f)

        fds_node = next((n for n in wf_data["nodes"] if n["type"] == "FilmDateStamp"), None)
        self.assertIsNotNone(fds_node, "FilmDateStamp node not found in official workflow")

        # INPUT_TYPES のウィジェット順
        input_types = FilmDateStamp.INPUT_TYPES()
        expected_widgets = list(input_types["required"].keys())
        if "image" in expected_widgets:
            expected_widgets.remove("image")  # 画像入力スロット
        if "optional" in input_types:
            expected_widgets.extend(list(input_types["optional"].keys()))

        values = fds_node["widgets_values"]
        # ComfyUI フロントエンドは seed ウィジェットの直後に control_after_generate を自動挿入するため、
        # widgets_values は len(expected_widgets) + 1 (末尾が 'fixed' 等) または len(expected_widgets)
        self.assertIn(
            len(values),
            (len(expected_widgets), len(expected_widgets) + 1),
            f"Workflow widgets_values length mismatch: expected {len(expected_widgets)} or {len(expected_widgets)+1}, got {len(values)}"
        )
        if len(values) == len(expected_widgets) + 1:
            self.assertIn(values[-1], ("fixed", "increment", "decrement", "randomize"))

        # widgets_values_named の検証
        if "widgets_values_named" in fds_node:
            named = fds_node["widgets_values_named"]
            for k in expected_widgets:
                self.assertIn(k, named, f"Missing widget '{k}' in widgets_values_named")

    def test_mask_and_string_outputs(self):
        """STRING および MASK 出力が正しく生成され、形式・値が適切であることの検証"""
        node = FilmDateStamp()
        img = torch.zeros((1, 100, 100, 3), dtype=torch.float32)

        out_img, out_mask, out_text = node.apply_stamp(
            image=img,
            style_preset="Custom",
            font_type="FDS7_Strict_Compact (80s -7°)",
            preset_color="Amber Classic",
            exposure_intensity=1.0,
            core_glow=1.0,
            halation=1.0,
            date_string="random",
            date_format="'YY MM DD",
            show_time=True,
            position="bottom_right",
            font_scale=1.0,
            margin=1.0,
            seed=777,
        )

        # 1. STRING 出力の検証 (例: '95 03 14 12:45 のようなフォーマット)
        self.assertTrue(out_text.startswith("'"), f"Unexpected date string format: {out_text}")
        self.assertIn(":", out_text, f"show_time=True should contain time: {out_text}")

        # 2. MASK 出力の検証
        self.assertEqual(out_mask.shape, (1, 100, 100))
        self.assertEqual(out_mask.dtype, torch.float32)
        # 背景（左上）はマスク値 0.0
        self.assertEqual(out_mask[0, 0:20, 0:20].max().item(), 0.0)
        # 文字配置位置（右下）はマスク値が 0.0 超〜1.0 以下
        self.assertGreater(out_mask[0, 50:100, 50:100].max().item(), 0.5)
        self.assertLessEqual(out_mask.max().item(), 1.0)


if __name__ == "__main__":
    unittest.main()
