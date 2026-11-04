"""
FilmDateStamp プロトタイプ描画・検証スクリプト
最新の film_stamp エンジンを使用してテストボードを生成し、assets/prototype_test.png を更新する。
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_DIR)

from film_config import DateStampConfig
from film_stamp import render_film_date_stamp

ASSETS_DIR = os.path.join(PROJECT_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def generate_test_board():
    """黒背景、グラデーション、写真風背景に日付を焼き付けたテストボードを生成"""
    board_w = 1200
    board_h = 800
    test_img = Image.new("RGB", (board_w, board_h), (20, 20, 24))
    
    # 上半分: 左（暗い背景）から右（明るいグラデーション〜白）
    draw = ImageDraw.Draw(test_img)
    for x in range(board_w):
        val = int((x / board_w) * 255)
        draw.line([(x, 0), (x, 390)], fill=(val, val, val))

    # 下半分: レトロ写真風の暗部と明部
    # 左下: 夜景風ディープブルー
    draw.rectangle([(0, 410), (590, board_h)], fill=(12, 18, 32))
    # 右下: 夕焼け風ウォームカラー
    draw.rectangle([(610, 410), (board_w, board_h)], fill=(180, 100, 70))

    # ラベル描画
    draw.text((30, 20), "FilmDateStamp - Optical Burn-in Model (Top: Dark to Bright Highlight Clip)", fill=(200, 200, 200))
    draw.text((30, 430), "Bottom-Left: Night Shadow (Deep Blue / Quartz Red)", fill=(180, 180, 180))
    draw.text((640, 430), "Bottom-Right: Sunset Glow (Warm Orange / Fuji Orange)", fill=(40, 40, 40))

    # 4箇所にテスト日付スタンプを焼き付け
    # 1. 上段左（暗部: Amber Classic / FDS7_Strict_Compact 80sコンパクト機調 -7.0°）
    test_sub1 = test_img.crop((0, 0, 400, 390))
    cfg1 = DateStampConfig(
        date_string="'98 12 24",
        preset_color="Amber Classic",
        font_type="FDS7_Strict_Compact (80s -7°)",
    )
    test_sub1 = render_film_date_stamp(test_sub1, config=cfg1)
    test_img.paste(test_sub1, (0, 0))

    # 2. 上段右（白飛びハイライト部 - 埋もれの検証 / FDS7_Strict_Compact）
    test_sub2 = test_img.crop((800, 0, 1200, 390))
    cfg2 = DateStampConfig(
        date_string="'98 12 24",
        preset_color="Amber Classic",
        font_type="FDS7_Strict_Compact (80s -7°)",
        optical_burn=True,
    )
    test_sub2 = render_film_date_stamp(test_sub2, config=cfg2)
    test_img.paste(test_sub2, (800, 0))

    # 3. 左下（夜景: Quartz Red / FDS7_Strict_SLR 80s一眼レフデータバック調 0.0°）
    test_sub3 = test_img.crop((0, 410, 590, board_h))
    cfg3 = DateStampConfig(
        date_string="'93  8 15",
        preset_color="Quartz Red",
        font_type="FDS7_Strict_SLR (80s 0°)",
    )
    test_sub3 = render_film_date_stamp(test_sub3, config=cfg3)
    test_img.paste(test_sub3, (0, 410))

    # 4. 右下（夕暮れ: Fuji Orange / VT323 ドットマトリクス）
    test_sub4 = test_img.crop((610, 410, board_w, board_h))
    cfg4 = DateStampConfig(
        date_string="10 24 '02",
        preset_color="Fuji Orange",
        font_type="VT323 (Dot Matrix)",
        font_scale=1.1,
    )
    test_sub4 = render_film_date_stamp(test_sub4, config=cfg4)
    test_img.paste(test_sub4, (610, 410))

    out_path = os.path.join(ASSETS_DIR, "prototype_test.png")
    test_img.save(out_path)
    print(f"Test board successfully saved to: {out_path}")


if __name__ == "__main__":
    generate_test_board()
